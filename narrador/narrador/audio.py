"""Montagem e pos-processamento do audio de narracao.

- Junta os trechos sintetizados com pausas naturais entre frases/paragrafos.
- Remove ruido leve, corrige graves/ofegos, normaliza loudness (EBU R128)
  e reamostra para 48 kHz: resultado com "som de estudio" e volume uniforme.
- Prepara o audio de referencia da voz (mono, 24 kHz, sem silencios).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from .util import ErroNarrador, duracao_audio, ffmpeg, garantir_dir


def ler_wav(caminho: Path) -> tuple[np.ndarray, int]:
    dados, sr = sf.read(str(caminho), dtype="float32", always_2d=True)
    return dados.mean(axis=1), sr


def escrever_wav(caminho: Path, dados: np.ndarray, sr: int) -> Path:
    garantir_dir(caminho.parent)
    sf.write(str(caminho), np.clip(dados, -1.0, 1.0), sr, subtype="PCM_16")
    return caminho


def _reamostrar(dados: np.ndarray, sr_origem: int, sr_destino: int) -> np.ndarray:
    if sr_origem == sr_destino:
        return dados
    n_dest = int(round(len(dados) * sr_destino / sr_origem))
    x_orig = np.linspace(0.0, 1.0, num=len(dados), endpoint=False)
    x_dest = np.linspace(0.0, 1.0, num=n_dest, endpoint=False)
    return np.interp(x_dest, x_orig, dados).astype(np.float32)


def aparar_silencio(dados: np.ndarray, sr: int, limiar_db: float = -45.0,
                    margem: float = 0.05) -> np.ndarray:
    """Remove silencio nas pontas (mantem uma pequena margem)."""
    if len(dados) == 0:
        return dados
    limiar = 10 ** (limiar_db / 20)
    janela = max(1, int(sr * 0.01))
    env = np.abs(dados)
    # envelope por janela
    n = len(env) // janela
    if n == 0:
        return dados
    blocos = env[: n * janela].reshape(n, janela).max(axis=1)
    ativos = np.where(blocos > limiar)[0]
    if len(ativos) == 0:
        return dados
    ini = max(0, ativos[0] * janela - int(margem * sr))
    fim = min(len(dados), (ativos[-1] + 1) * janela + int(margem * sr))
    return dados[ini:fim]


def juntar_trechos(arquivos: list[Path], pausas: list[float], destino: Path,
                   sr: int = 24000, pausa_inicio: float = 0.35, pausa_fim: float = 0.6) -> Path:
    """Concatena wavs com silencios entre eles (pausas em segundos)."""
    if not arquivos:
        raise ErroNarrador("Nenhum trecho de audio para juntar.")
    partes = [np.zeros(int(sr * pausa_inicio), dtype=np.float32)]
    for arq, pausa in zip(arquivos, pausas):
        dados, sr_arq = ler_wav(arq)
        dados = _reamostrar(dados, sr_arq, sr)
        dados = aparar_silencio(dados, sr)
        partes.append(dados)
        if pausa > 0:
            partes.append(np.zeros(int(sr * pausa), dtype=np.float32))
    partes.append(np.zeros(int(sr * pausa_fim), dtype=np.float32))
    return escrever_wav(destino, np.concatenate(partes), sr)


def silencio(destino: Path, segundos: float, sr: int = 48000) -> Path:
    return escrever_wav(destino, np.zeros(int(sr * segundos), dtype=np.float32), sr)


def masterizar(entrada: Path, saida: Path, *, reduzir_ruido: bool = True,
               loudness_lufs: float = -16.0, sr: int = 48000) -> Path:
    """Cadeia de "masterizacao" leve para voz: limpa, equaliza e normaliza.

    - highpass 70 Hz: tira ronco/ofego grave
    - afftdn: reducao de ruido de fundo (suave, nao destroi a voz)
    - deesser leve e compressor suave: fala mais presente e uniforme
    - loudnorm -16 LUFS (padrao de podcast/YouTube), pico -1.5 dBTP
    """
    filtros = ["highpass=f=70", "lowpass=f=16000"]
    if reduzir_ruido:
        filtros.append("afftdn=nf=-28:nr=10:tn=1")
    filtros += [
        "deesser=i=0.15",
        "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=150:makeup=2",
        f"loudnorm=I={loudness_lufs}:TP=-1.5:LRA=11",
        f"aresample={sr}",
    ]
    garantir_dir(saida.parent)
    ffmpeg(["-i", entrada, "-af", ",".join(filtros), "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", saida])
    return saida


def preparar_referencia(entrada: Path, saida: Path, inicio: float | None = None,
                        duracao: float | None = None, sr: int = 24000) -> Path:
    """Converte qualquer audio para uma referencia de voz limpa (mono, 24 kHz).

    Recomendado: 6 a 15 segundos de fala continua, sem musica, sem eco,
    gravada perto do microfone. Esse clipe define o timbre da voz clonada.
    """
    if not entrada.exists():
        raise ErroNarrador(f"Audio de referencia nao encontrado: {entrada}")
    args: list[str | Path] = []
    if inicio is not None:
        args += ["-ss", str(inicio)]
    if duracao is not None:
        args += ["-t", str(duracao)]
    args += [
        "-i", entrada,
        "-af", "highpass=f=70,afftdn=nf=-30:nr=8,loudnorm=I=-20:TP=-2:LRA=9,"
               "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,"
               "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,areverse",
        "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", saida,
    ]
    garantir_dir(saida.parent)
    ffmpeg(args)
    dur = duracao_audio(saida)
    if dur < 3:
        raise ErroNarrador(f"Referencia muito curta ({dur:.1f}s). Use pelo menos 5 segundos de fala.")
    return saida
