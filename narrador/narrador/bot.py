"""Modo bot: vigia uma pasta de entrada e narra automaticamente cada apresentacao.

Solte na pasta:
  minha_apresentacao.pptx                 (ou .pdf)
  minha_apresentacao.roteiro.md           (opcional: roteiro por slide)
  minha_apresentacao.musica.mp3           (opcional: trilha de fundo)

O bot espera o arquivo terminar de copiar, gera o MP4 em saida/<nome>/ e move
a entrada para caixa_entrada/processados/ (ou /erros/ em caso de falha).
"""

from __future__ import annotations

import shutil
import time
import traceback
from pathlib import Path

from . import pipeline
from .util import console, garantir_dir

EXTENSOES = {".pptx", ".pdf"}


def _estavel(caminho: Path, espera: float = 2.0) -> bool:
    """True quando o tamanho do arquivo para de mudar (copia concluida)."""
    try:
        t1 = caminho.stat().st_size
        time.sleep(espera)
        return caminho.exists() and caminho.stat().st_size == t1 and t1 > 0
    except FileNotFoundError:
        return False


def processar_arquivo(arquivo: Path, saida: Path, cfg: pipeline.Config) -> Path | None:
    base = arquivo.with_suffix("")
    roteiro = next((p for p in (base.with_suffix(".roteiro.md"), base.with_suffix(".roteiro.json"),
                                base.with_suffix(".roteiro.yaml"), base.with_suffix(".md")) if p.exists()), None)
    musica = next((p for p in (base.with_suffix(".musica.mp3"), base.with_suffix(".musica.wav")) if p.exists()), None)
    cfg_local = pipeline.Config(**{**cfg.__dict__})
    if musica:
        cfg_local.musica = str(musica)
    processados = garantir_dir(arquivo.parent / "processados")
    erros = garantir_dir(arquivo.parent / "erros")
    try:
        mp4 = pipeline.gerar(arquivo, saida, cfg_local, roteiro=roteiro)
        for extra in (arquivo, roteiro, musica):
            if extra and extra.exists():
                shutil.move(str(extra), processados / extra.name)
        console.print(f"[bold green][bot][/] concluido: {mp4}")
        return mp4
    except Exception as e:  # noqa: BLE001 - o bot nunca deve morrer por um arquivo ruim
        console.print(f"[bold red][bot][/] falhou em {arquivo.name}: {e}")
        (erros / f"{arquivo.stem}.erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
        for extra in (arquivo, roteiro, musica):
            if extra and extra.exists():
                shutil.move(str(extra), erros / extra.name)
        return None


def _pendentes(entrada: Path) -> list[Path]:
    return sorted(p for p in entrada.iterdir() if p.is_file() and p.suffix.lower() in EXTENSOES and not p.name.startswith("~$"))


def vigiar(entrada: Path, saida: Path, cfg: pipeline.Config, uma_vez: bool = False, intervalo: float = 3.0) -> None:
    garantir_dir(entrada)
    garantir_dir(saida)
    console.print(f"[bold]Bot do Narrador[/] vigiando [cyan]{entrada.resolve()}[/] -> saida em [cyan]{saida.resolve()}[/]"
                  f"  (motor: {cfg.motor}). Ctrl+C para sair.")
    while True:
        for arq in _pendentes(entrada):
            if not _estavel(arq):
                continue
            processar_arquivo(arq, saida, cfg)
        if uma_vez:
            return
        time.sleep(intervalo)
