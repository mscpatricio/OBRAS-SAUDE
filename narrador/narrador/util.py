"""Utilitarios compartilhados: ffmpeg, hashing, logging."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from rich.console import Console

console = Console()


class ErroNarrador(RuntimeError):
    """Erro com mensagem pronta para o usuario (sem traceback)."""


def exigir_binario(nome: str, dica: str = "") -> str:
    caminho = shutil.which(nome)
    if not caminho:
        raise ErroNarrador(
            f"O programa '{nome}' nao foi encontrado no PATH. {dica}".strip()
        )
    return caminho


def rodar(cmd: list[str], *, silencioso: bool = True) -> subprocess.CompletedProcess:
    """Executa um comando e levanta ErroNarrador com o stderr em caso de falha."""
    proc = subprocess.run(
        [str(c) for c in cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-25:])
        raise ErroNarrador(
            f"Comando falhou ({proc.returncode}): {' '.join(map(str, cmd[:4]))} ...\n{tail}"
        )
    if not silencioso and proc.stdout:
        console.print(proc.stdout)
    return proc


def ffmpeg(args: Iterable[str | Path]) -> None:
    exigir_binario("ffmpeg", "Instale com: sudo apt install ffmpeg (ou brew install ffmpeg).")
    rodar(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)])


def duracao_audio(caminho: Path) -> float:
    """Duracao em segundos via ffprobe."""
    exigir_binario("ffprobe", "O ffprobe acompanha o ffmpeg.")
    proc = rodar(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(caminho),
        ]
    )
    dados = json.loads(proc.stdout or "{}")
    return float(dados.get("format", {}).get("duration", 0.0))


def hash_conteudo(*partes: str | bytes | Path) -> str:
    """Hash estavel de textos e arquivos, usado para cache de sintese."""
    h = hashlib.sha256()
    for p in partes:
        if isinstance(p, Path):
            h.update(b"file:")
            if p.exists():
                h.update(p.read_bytes())
        elif isinstance(p, bytes):
            h.update(p)
        else:
            h.update(str(p).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:16]


def garantir_dir(caminho: Path) -> Path:
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def limpar_nome(nome: str) -> str:
    seguro = "".join(c if c.isalnum() or c in "-_." else "_" for c in nome.strip())
    return seguro.strip("._") or "apresentacao"
