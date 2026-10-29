"""Montagem do MP4 com ffmpeg: slide parado (ou com leve movimento) + narracao.

Estrategia robusta: cada slide vira um segmento MP4 com duracao exata do
seu audio; depois os segmentos sao unidos com transicao (xfade/acrossfade)
ou por concatenacao direta. Legendas SRT e musica de fundo sao opcionais.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .util import ErroNarrador, console, duracao_audio, ffmpeg, garantir_dir


@dataclass
class Cena:
    imagem: Path
    audio: Path  # wav 48k mono, ja masterizado
    texto: str = ""


@dataclass
class OpcoesVideo:
    largura: int = 1920
    altura: int = 1080
    fps: int = 30
    transicao: float = 0.4          # segundos; 0 desliga
    movimento: bool = False         # leve zoom (Ken Burns)
    legendas_embutidas: bool = False
    musica: Path | None = None
    volume_musica: float = 0.10     # 0..1
    crf: int = 18
    preset: str = "medium"
    fundo: str = "black"


def _tempo_srt(seg: float) -> str:
    ms = int(round(seg * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def gerar_srt(cenas: list[Cena], duracoes: list[float], destino: Path,
              transicao: float = 0.0, max_chars: int = 84) -> Path:
    """Gera legendas: cada slide dividido em frases, com tempo proporcional ao texto."""
    import re

    linhas: list[str] = []
    idx = 1
    t = 0.0
    for cena, dur in zip(cenas, duracoes):
        frases = [f.strip() for f in re.split(r"(?<=[.!?…])\s+", cena.texto.strip()) if f.strip()]
        # quebra frases longas para caberem em 2 linhas
        pedacos: list[str] = []
        for f in frases:
            while len(f) > max_chars:
                corte = f.rfind(" ", 0, max_chars)
                corte = corte if corte > 20 else max_chars
                pedacos.append(f[:corte].strip())
                f = f[corte:].strip()
            if f:
                pedacos.append(f)
        # peso = caracteres + constante, para frases curtas ("Olá!") nao piscarem na tela
        pesos = [len(p) + 15 for p in pedacos]
        total = sum(pesos) or 1
        margem = 0.3
        util = max(dur - 2 * margem, 0.5)
        cursor = t + margem
        for p, peso in zip(pedacos, pesos):
            d = util * peso / total
            linhas += [str(idx), f"{_tempo_srt(cursor)} --> {_tempo_srt(cursor + d - 0.05)}",
                       _duas_linhas(p), ""]
            cursor += d
            idx += 1
        t += dur - transicao
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return destino


def _duas_linhas(texto: str) -> str:
    if len(texto) <= 42:
        return texto
    meio = texto.rfind(" ", 0, len(texto) // 2 + 10)
    if meio <= 0:
        return texto
    return texto[:meio] + "\n" + texto[meio + 1:]


def _filtro_imagem(op: OpcoesVideo, duracao: float) -> str:
    base = (
        f"scale={op.largura}:{op.altura}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={op.largura}:{op.altura}:(ow-iw)/2:(oh-ih)/2:color={op.fundo},"
        "setsar=1,format=yuv420p"
    )
    if op.movimento:
        frames = max(int(duracao * op.fps), 1)
        # zoom lento de 1.0 ate ~1.06 ao longo do slide, centrado
        base = (
            f"scale={op.largura * 2}:{op.altura * 2}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={op.largura * 2}:{op.altura * 2}:(ow-iw)/2:(oh-ih)/2:color={op.fundo},"
            f"zoompan=z='min(1+0.06*on/{frames},1.06)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={op.largura}x{op.altura}:fps={op.fps},setsar=1,format=yuv420p"
        )
    return base


def renderizar_segmento(cena: Cena, destino: Path, op: OpcoesVideo) -> float:
    dur = duracao_audio(cena.audio)
    if dur <= 0:
        raise ErroNarrador(f"Audio sem duracao: {cena.audio}")
    entrada_img = ["-loop", "1", "-framerate", str(op.fps), "-t", f"{dur:.3f}", "-i", cena.imagem]
    ffmpeg([
        *entrada_img,
        "-i", cena.audio,
        "-vf", _filtro_imagem(op, dur),
        "-r", str(op.fps),
        "-c:v", "libx264", "-preset", op.preset, "-crf", str(op.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart",
        destino,
    ])
    return dur


def _concatenar_simples(segmentos: list[Path], destino: Path) -> None:
    lista = destino.with_suffix(".txt")
    lista.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in segmentos), encoding="utf-8")
    ffmpeg(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", "-movflags", "+faststart", destino])
    lista.unlink(missing_ok=True)


def _concatenar_com_transicao(segmentos: list[Path], duracoes: list[float], destino: Path,
                              op: OpcoesVideo) -> None:
    if len(segmentos) == 1:
        _concatenar_simples(segmentos, destino)
        return
    entradas: list[str | Path] = []
    for s in segmentos:
        entradas += ["-i", s]
    tr = op.transicao
    filtros: list[str] = []
    v_ant, a_ant = "[0:v]", "[0:a]"
    offset = 0.0
    for i in range(1, len(segmentos)):
        offset += duracoes[i - 1] - tr
        v_out = f"[v{i}]" if i < len(segmentos) - 1 else "[vout]"
        a_out = f"[a{i}]" if i < len(segmentos) - 1 else "[aout]"
        filtros.append(f"{v_ant}[{i}:v]xfade=transition=fade:duration={tr:.3f}:offset={offset:.3f}{v_out}")
        filtros.append(f"{a_ant}[{i}:a]acrossfade=d={tr:.3f}:c1=tri:c2=tri{a_out}")
        v_ant, a_ant = v_out, a_out
    ffmpeg([
        *entradas,
        "-filter_complex", ";".join(filtros),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", op.preset, "-crf", str(op.crf), "-pix_fmt", "yuv420p", "-r", str(op.fps),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        destino,
    ])


def _misturar_musica(video: Path, musica: Path, destino: Path, volume: float) -> None:
    """Musica em loop sob a narracao, com ducking (abaixa quando ha voz) e fade final."""
    dur = duracao_audio(video)
    fade_ini = max(dur - 3.0, 0)
    filtro = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{dur:.3f},volume={volume:.3f},"
        f"afade=t=in:st=0:d=2,afade=t=out:st={fade_ini:.3f}:d=3[mus];"
        "[mus][0:a]sidechaincompress=threshold=0.02:ratio=6:attack=80:release=600[duck];"
        "[0:a][duck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    ffmpeg([
        "-i", video, "-i", musica,
        "-filter_complex", filtro,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", destino,
    ])


def _embutir_legendas(video: Path, srt: Path, destino: Path) -> None:
    estilo = "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=1.5,Shadow=0.5,MarginV=40"
    srt_txt = str(srt.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    ffmpeg([
        "-i", video,
        "-vf", f"subtitles='{srt_txt}':force_style='{estilo}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", destino,
    ])


def montar(cenas: list[Cena], destino: Path, op: OpcoesVideo, trabalho: Path) -> Path:
    """Renderiza o video final em `destino` (.mp4) e grava legendas .srt ao lado."""
    if not cenas:
        raise ErroNarrador("Nenhuma cena para montar o video.")
    seg_dir = garantir_dir(trabalho / "segmentos")
    segmentos: list[Path] = []
    duracoes: list[float] = []
    for i, cena in enumerate(cenas, start=1):
        seg = seg_dir / f"seg_{i:03d}.mp4"
        console.print(f"  [dim]renderizando slide {i}/{len(cenas)}[/]")
        duracoes.append(renderizar_segmento(cena, seg, op))
        segmentos.append(seg)

    garantir_dir(destino.parent)
    bruto = trabalho / "video_sem_extras.mp4"
    tr = op.transicao if len(cenas) > 1 and op.transicao > 0 else 0.0
    if tr > 0:
        if min(duracoes) <= tr * 2:
            console.print("[yellow]Aviso:[/] slide muito curto para a transicao; usando corte seco.")
            tr = 0.0
    if tr > 0:
        _concatenar_com_transicao(segmentos, duracoes, bruto, op)
    else:
        _concatenar_simples(segmentos, bruto)

    srt = destino.with_suffix(".srt")
    gerar_srt(cenas, duracoes, srt, transicao=tr)

    atual = bruto
    if op.musica:
        if not op.musica.exists():
            raise ErroNarrador(f"Musica nao encontrada: {op.musica}")
        com_musica = trabalho / "video_com_musica.mp4"
        _misturar_musica(atual, op.musica, com_musica, op.volume_musica)
        atual = com_musica
    if op.legendas_embutidas:
        com_leg = trabalho / "video_com_legendas.mp4"
        _embutir_legendas(atual, srt, com_leg)
        atual = com_leg

    if destino.exists():
        destino.unlink()
    atual.replace(destino)
    return destino
