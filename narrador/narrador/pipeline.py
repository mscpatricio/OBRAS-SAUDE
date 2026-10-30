"""Orquestracao: apresentacao -> narracao por slide -> MP4."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from . import audio, slides, texto, video
from .tts import VozReferencia, criar_motor
from .util import ErroNarrador, console, duracao_audio, garantir_dir, hash_conteudo, limpar_nome


@dataclass
class Config:
    motor: str = "chatterbox"
    voz: str | None = None               # caminho do wav de referencia
    transcricao: str | None = None       # texto (ou .txt) do que e dito na referencia
    idioma: str = "pt"
    dispositivo: str = "auto"
    opcoes_motor: dict = field(default_factory=dict)
    # texto/audio
    max_chars_trecho: int = 220
    pausa_frase: float = 0.35
    pausa_paragrafo: float = 0.7
    pausa_inicio: float = 0.4
    pausa_fim: float = 0.8
    reduzir_ruido: bool = True
    loudness: float = -16.0
    duracao_slide_mudo: float = 4.0
    usar_texto_slide: bool = True
    # video
    largura: int = 1920
    altura: int = 1080
    fps: int = 30
    transicao: float = 0.4
    movimento: bool = False
    legendas_embutidas: bool = False
    musica: str | None = None
    volume_musica: float = 0.10
    crf: int = 18
    preset: str = "medium"

    @classmethod
    def de_arquivo(cls, caminho: Path | None) -> "Config":
        cfg = cls()
        if caminho and Path(caminho).exists():
            dados = yaml.safe_load(Path(caminho).read_text(encoding="utf-8")) or {}
            for k, v in dados.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
                else:
                    console.print(f"[yellow]Aviso:[/] opcao desconhecida no config: {k}")
        return cfg

    def atualizar(self, **kw) -> "Config":
        for k, v in kw.items():
            if v is not None and hasattr(self, k):
                setattr(self, k, v)
        return self


def narrar_texto(motor, texto_bruto: str, destino: Path, cfg: Config, cache_dir: Path) -> Path:
    """Sintetiza um texto completo (varios trechos), junta e masteriza em `destino`."""
    normalizado = texto.normalizar(texto_bruto)
    trechos = texto.dividir(normalizado, cfg.max_chars_trecho, cfg.pausa_frase, cfg.pausa_paragrafo)
    if not trechos:
        raise ErroNarrador("Texto vazio para narrar.")
    arquivos: list[Path] = []
    pausas: list[float] = []
    for i, tr in enumerate(trechos, start=1):
        frase = texto.garantir_pontuacao(tr.texto)
        chave = hash_conteudo(motor.identidade(), frase)
        wav = cache_dir / f"{chave}.wav"
        if not wav.exists():
            console.print(f"    [dim]{i}/{len(trechos)}[/] {frase[:70]}{'...' if len(frase) > 70 else ''}")
            tmp = wav.with_suffix(".tmp.wav")
            motor.sintetizar(frase, tmp)
            tmp.replace(wav)
        arquivos.append(wav)
        pausas.append(tr.pausa_depois)
    bruto = destino.with_name(destino.stem + "_bruto.wav")
    audio.juntar_trechos(arquivos, pausas, bruto, sr=24000,
                         pausa_inicio=cfg.pausa_inicio, pausa_fim=cfg.pausa_fim)
    audio.masterizar(bruto, destino, reduzir_ruido=cfg.reduzir_ruido, loudness_lufs=cfg.loudness)
    bruto.unlink(missing_ok=True)
    return destino


def gerar(origem: Path, saida_dir: Path, cfg: Config, roteiro: Path | None = None,
          nome_saida: str | None = None) -> Path:
    """Pipeline completo. Retorna o caminho do MP4."""
    inicio = time.time()
    origem = Path(origem)
    nome = limpar_nome(nome_saida or (origem.stem if origem.is_file() else origem.name))
    trabalho = garantir_dir(Path(saida_dir) / nome)
    cache_dir = garantir_dir(trabalho / "cache_tts")

    console.rule(f"[bold]Narrador[/] - {nome}")
    apr = slides.carregar(origem, trabalho, roteiro=roteiro, usar_texto_slide=cfg.usar_texto_slide, largura=cfg.largura)
    slides.escrever_roteiro_md(apr, trabalho / "roteiro_usado.md")
    console.print(f"[green]{len(apr.slides)} slides carregados.[/] Roteiro salvo em {trabalho / 'roteiro_usado.md'}")

    voz = None
    if cfg.voz:
        voz = VozReferencia.de_arquivo(Path(cfg.voz), cfg.transcricao)
    motor = criar_motor(cfg.motor, voz, dispositivo=cfg.dispositivo, idioma=cfg.idioma, **(cfg.opcoes_motor or {}))
    if motor.nome == "silencio":
        console.print("[bold yellow]ATENCAO:[/] motor 'silencio' gera o video SEM narracao (so para testar a montagem). "
                      "Para voz real use --motor piper (offline) ou --motor chatterbox-ptbr (voz clonada).")
    elif not motor.precisa_clonagem:
        console.print(f"[yellow]Aviso:[/] motor '{motor.nome}' usa uma voz generica, nao a sua voz clonada.")

    dir_audio = garantir_dir(trabalho / "audio")
    cenas: list[video.Cena] = []
    for s in apr.slides:
        destino = dir_audio / f"slide_{s.numero:03d}.wav"
        if s.texto:
            console.print(f"[bold cyan]Slide {s.numero}[/] {s.titulo}")
            narrar_texto(motor, s.texto, destino, cfg, cache_dir)
        else:
            audio.silencio(destino, cfg.duracao_slide_mudo)
        cenas.append(video.Cena(imagem=s.imagem, audio=destino, texto=s.texto))

    op = video.OpcoesVideo(
        largura=cfg.largura, altura=cfg.altura, fps=cfg.fps, transicao=cfg.transicao,
        movimento=cfg.movimento, legendas_embutidas=cfg.legendas_embutidas,
        musica=Path(cfg.musica) if cfg.musica else None, volume_musica=cfg.volume_musica,
        crf=cfg.crf, preset=cfg.preset,
    )
    console.print("[cyan]Montando o video...[/]")
    mp4 = video.montar(cenas, trabalho / f"{nome}.mp4", op, trabalho)

    resumo = {
        "video": str(mp4), "legendas": str(mp4.with_suffix(".srt")), "slides": len(apr.slides),
        "motor": motor.nome, "duracao_total_s": round(sum(duracao_audio(c.audio) for c in cenas), 1),
        "config": asdict(cfg), "tempo_processamento_s": round(time.time() - inicio, 1),
    }
    (trabalho / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"[bold green]Pronto![/] {mp4}  ({resumo['duracao_total_s']}s de video, "
                  f"{resumo['tempo_processamento_s']}s de processamento)")
    return mp4
