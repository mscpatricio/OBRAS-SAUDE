"""Linha de comando do Narrador.

    narrador gerar apresentacao.pptx --voz voz/minha_voz.wav
    narrador roteiro apresentacao.pptx            # exporta roteiro editavel
    narrador voz preparar gravacao.m4a            # limpa e corta a referencia
    narrador voz testar --voz voz/minha_voz.wav   # ouve uma frase clonada
    narrador bot --entrada caixa_entrada --voz voz/minha_voz.wav
    narrador motores
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.table import Table

from . import __version__, pipeline, slides
from .util import ErroNarrador, console, garantir_dir


def _tratar(fn):
    def wrapper(*a, **k):
        try:
            return fn(*a, **k)
        except ErroNarrador as e:
            console.print(f"[bold red]Erro:[/] {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido.[/]")
            sys.exit(130)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


def _parse_opcoes(itens: tuple[str, ...]) -> dict:
    saida: dict = {}
    for item in itens:
        if "=" not in item:
            raise click.BadParameter(f"use chave=valor, recebido: {item}")
        k, v = item.split("=", 1)
        saida[k.strip()] = v.strip()
    return saida


opt_config = click.option("--config", "-c", type=click.Path(path_type=Path), default=Path("narrador.yaml"),
                          show_default=True, help="Arquivo YAML com as opcoes padrao.")
opt_voz = click.option("--voz", type=click.Path(path_type=Path), help="WAV de referencia da sua voz (6-15 s).")
opt_transcricao = click.option("--transcricao", help="Texto dito no audio de referencia (ou caminho .txt).")
opt_motor = click.option("--motor", "-m", type=str, help="chatterbox | chatterbox-ptbr | qwen3 | f5-ptbr | xtts | elevenlabs | edge | silencio")
opt_dispositivo = click.option("--dispositivo", type=str, help="auto | cpu | cuda | mps")
opt_opcao = click.option("--opcao", "-o", multiple=True, help="Opcao do motor, ex.: -o exaggeration=0.4 -o cfg_weight=0.4")


@click.group(help="Narrador: narra slides com a sua voz clonada e gera MP4.")
@click.version_option(__version__)
def main() -> None:
    pass


@main.command()
@click.argument("origem", type=click.Path(exists=True, path_type=Path))
@click.option("--roteiro", "-r", type=click.Path(exists=True, path_type=Path), help="Roteiro .md/.json/.yaml (um bloco por slide).")
@click.option("--saida", "-s", type=click.Path(path_type=Path), default=Path("saida"), show_default=True)
@click.option("--nome", help="Nome do video/pasta de saida.")
@opt_config
@opt_voz
@opt_transcricao
@opt_motor
@opt_dispositivo
@opt_opcao
@click.option("--transicao", type=float, help="Duracao da transicao entre slides em segundos (0 desliga).")
@click.option("--movimento/--sem-movimento", default=None, help="Leve zoom nos slides (Ken Burns).")
@click.option("--legendas", "legendas_embutidas", is_flag=True, default=None, help="Embute as legendas no video (o .srt e sempre gerado).")
@click.option("--musica", type=click.Path(exists=True, path_type=Path), help="Musica de fundo (mp3/wav), com ducking automatico.")
@click.option("--volume-musica", type=float, help="Volume da musica 0..1 (padrao 0.10).")
@click.option("--sem-ruido/--com-ruido", "reduzir_ruido", default=None, help="Liga/desliga a reducao de ruido.")
@click.option("--ignorar-texto-slide", is_flag=True, help="Nao usar o texto visivel do slide quando nao houver notas/roteiro.")
@click.option("--resolucao", type=click.Choice(["1080p", "720p", "4k"]), help="Resolucao do video.")
@_tratar
def gerar(origem, roteiro, saida, nome, config, voz, transcricao, motor, dispositivo, opcao, transicao, movimento,
          legendas_embutidas, musica, volume_musica, reduzir_ruido, ignorar_texto_slide, resolucao):
    """Gera o MP4 narrado a partir de um .pptx, .pdf ou pasta de imagens."""
    cfg = pipeline.Config.de_arquivo(config)
    cfg.atualizar(voz=str(voz) if voz else None, transcricao=transcricao, motor=motor, dispositivo=dispositivo,
                  transicao=transicao, movimento=movimento, legendas_embutidas=legendas_embutidas,
                  musica=str(musica) if musica else None, volume_musica=volume_musica, reduzir_ruido=reduzir_ruido)
    if ignorar_texto_slide:
        cfg.usar_texto_slide = False
    if resolucao:
        cfg.largura, cfg.altura = {"1080p": (1920, 1080), "720p": (1280, 720), "4k": (3840, 2160)}[resolucao]
    if opcao:
        cfg.opcoes_motor = {**(cfg.opcoes_motor or {}), **_parse_opcoes(opcao)}
    if cfg.motor not in {"edge", "silencio", "elevenlabs"} and not cfg.voz:
        raise ErroNarrador("Informe --voz com o WAV da sua voz (ou use --motor edge para um teste sem clonagem).")
    pipeline.gerar(origem, saida, cfg, roteiro=roteiro, nome_saida=nome)


@main.command()
@click.argument("origem", type=click.Path(exists=True, path_type=Path))
@click.option("--saida", "-s", type=click.Path(path_type=Path), help="Arquivo .md de destino (padrao: <nome>.roteiro.md).")
@_tratar
def roteiro(origem, saida):
    """Extrai as notas do orador/texto dos slides para um roteiro editavel (.md)."""
    import tempfile

    trabalho = Path(tempfile.mkdtemp(prefix="narrador_roteiro_"))
    apr = slides.carregar(origem, trabalho, largura=640)
    destino = saida or origem.with_suffix(".roteiro.md")
    slides.escrever_roteiro_md(apr, destino)
    console.print(f"[green]Roteiro salvo em[/] {destino}. Edite e use com: narrador gerar {origem.name} -r {destino.name}")


@main.group()
def voz() -> None:
    """Preparar e testar a voz de referencia."""


@voz.command("preparar")
@click.argument("entrada", type=click.Path(exists=True, path_type=Path))
@click.option("--saida", "-s", type=click.Path(path_type=Path), default=Path("voz/minha_voz.wav"), show_default=True)
@click.option("--inicio", type=float, help="Segundo inicial do trecho a aproveitar.")
@click.option("--duracao", type=float, help="Duracao do trecho (ideal 8-12 s).")
@click.option("--transcricao", help="Texto exato falado no trecho (salvo em .txt ao lado; melhora Qwen3/F5).")
@_tratar
def voz_preparar(entrada, saida, inicio, duracao, transcricao):
    """Converte qualquer gravacao (mp3/m4a/wav/video) em referencia limpa de 24 kHz."""
    from . import audio

    garantir_dir(saida.parent)
    audio.preparar_referencia(entrada, saida, inicio, duracao)
    if transcricao:
        saida.with_suffix(".txt").write_text(transcricao.strip(), encoding="utf-8")
    dur = audio.duracao_audio(saida)
    console.print(f"[green]Referencia pronta:[/] {saida} ({dur:.1f}s)")
    if dur > 20:
        console.print("[yellow]Dica:[/] referencias de 8-15 s costumam clonar melhor; use --inicio/--duracao para recortar.")


@voz.command("testar")
@opt_voz
@opt_transcricao
@opt_motor
@opt_dispositivo
@opt_opcao
@opt_config
@click.option("--texto", "-t", default="Ola! Esta e uma amostra da minha voz clonada, narrando esta apresentacao com naturalidade.",
              show_default=True)
@click.option("--saida", "-s", type=click.Path(path_type=Path), default=Path("saida/teste_voz.wav"), show_default=True)
@_tratar
def voz_testar(voz, transcricao, motor, dispositivo, opcao, config, texto, saida):
    """Sintetiza uma frase para avaliar a qualidade da clonagem."""
    from .tts import VozReferencia, criar_motor

    cfg = pipeline.Config.de_arquivo(config)
    cfg.atualizar(voz=str(voz) if voz else None, transcricao=transcricao, motor=motor, dispositivo=dispositivo)
    if opcao:
        cfg.opcoes_motor = {**(cfg.opcoes_motor or {}), **_parse_opcoes(opcao)}
    ref = VozReferencia.de_arquivo(Path(cfg.voz), cfg.transcricao) if cfg.voz else None
    m = criar_motor(cfg.motor, ref, dispositivo=cfg.dispositivo, idioma=cfg.idioma, **(cfg.opcoes_motor or {}))
    garantir_dir(saida.parent)
    cache = garantir_dir(saida.parent / "cache_tts")
    pipeline.narrar_texto(m, texto, saida, cfg, cache)
    console.print(f"[green]Amostra gerada:[/] {saida}")


@main.command()
@click.option("--entrada", "-e", type=click.Path(path_type=Path), default=Path("caixa_entrada"), show_default=True,
              help="Pasta vigiada: solte .pptx/.pdf (e opcionalmente <nome>.roteiro.md) aqui.")
@click.option("--saida", "-s", type=click.Path(path_type=Path), default=Path("saida"), show_default=True)
@opt_config
@opt_voz
@opt_transcricao
@opt_motor
@opt_dispositivo
@opt_opcao
@click.option("--uma-vez", is_flag=True, help="Processa o que ja esta na pasta e sai (util em cron/CI).")
@_tratar
def bot(entrada, saida, config, voz, transcricao, motor, dispositivo, opcao, uma_vez):
    """Modo bot: vigia uma pasta e gera o MP4 de cada apresentacao que aparecer."""
    from .bot import vigiar

    cfg = pipeline.Config.de_arquivo(config)
    cfg.atualizar(voz=str(voz) if voz else None, transcricao=transcricao, motor=motor, dispositivo=dispositivo)
    if opcao:
        cfg.opcoes_motor = {**(cfg.opcoes_motor or {}), **_parse_opcoes(opcao)}
    if cfg.motor not in {"edge", "silencio", "elevenlabs"} and not cfg.voz:
        raise ErroNarrador("Informe --voz com o WAV da sua voz (ou configure 'voz:' no narrador.yaml).")
    vigiar(entrada, saida, cfg, uma_vez=uma_vez)


@main.command()
def motores() -> None:
    """Lista os motores de voz disponiveis e como instalar."""
    from .tts import INSTALACAO, MOTORES

    tabela = Table(title="Motores de voz")
    tabela.add_column("nome", style="bold")
    tabela.add_column("descricao")
    tabela.add_column("instalacao", style="dim")
    for nome, desc in MOTORES.items():
        tabela.add_row(nome, desc, INSTALACAO[nome])
    console.print(tabela)


if __name__ == "__main__":  # pragma: no cover
    main()
