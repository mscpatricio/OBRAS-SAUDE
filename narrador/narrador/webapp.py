"""Interface web do Narrador (Gradio): envie a voz e a apresentacao, baixe o MP4.

    narrador web                       # http://127.0.0.1:7860
    narrador web --compartilhar        # gera link publico temporario (Colab / mostrar para alguem)
"""

from __future__ import annotations

import os
import shutil
import tempfile
import traceback
from pathlib import Path

from . import audio, pipeline
from .tts import MOTORES
from .util import ErroNarrador, garantir_dir

MOTORES_WEB = ["chatterbox-online", "chatterbox-ptbr", "chatterbox", "gpt-sovits", "qwen3", "f5-ptbr", "xtts",
               "fish", "elevenlabs", "piper", "edge"]


def _parse_opcoes(texto: str) -> dict:
    saida = {}
    for linha in (texto or "").replace(";", "\n").splitlines():
        if "=" in linha:
            k, v = linha.split("=", 1)
            saida[k.strip()] = v.strip()
    return saida


def criar_app(cfg_base: pipeline.Config, saida_dir: Path):
    import gradio as gr

    saida_dir = garantir_dir(saida_dir)
    voz_dir = garantir_dir(saida_dir / "_voz")

    def preparar_voz(arquivo, transcricao, inicio, duracao):
        if arquivo is None:
            raise gr.Error("Envie uma gravacao da sua voz (mp3, m4a, wav ou video).")
        destino = voz_dir / "minha_voz.wav"
        try:
            audio.preparar_referencia(Path(arquivo), destino, inicio or None, duracao or None)
        except ErroNarrador as e:
            raise gr.Error(str(e))
        if transcricao:
            destino.with_suffix(".txt").write_text(transcricao.strip(), encoding="utf-8")
        return str(destino), f"Referencia pronta ({audio.duracao_audio(destino):.1f} s): {destino}"

    def testar(motor, texto, opcoes, hf_token):
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token.strip()
        ref = voz_dir / "minha_voz.wav"
        cfg = pipeline.Config(**{**cfg_base.__dict__})
        cfg.motor = motor
        cfg.voz = str(ref) if ref.exists() else None
        cfg.transcricao = str(ref.with_suffix(".txt")) if ref.with_suffix(".txt").exists() else None
        cfg.opcoes_motor = {**(cfg.opcoes_motor or {}), **_parse_opcoes(opcoes)}
        from .tts import VozReferencia, criar_motor
        try:
            v = VozReferencia.de_arquivo(ref, cfg.transcricao) if cfg.voz else None
            m = criar_motor(cfg.motor, v, dispositivo=cfg.dispositivo, idioma=cfg.idioma, **cfg.opcoes_motor)
            alvo = saida_dir / "_teste" / "teste_voz.wav"
            pipeline.narrar_texto(m, texto, alvo, cfg, garantir_dir(saida_dir / "_teste" / "cache_tts"))
            return str(alvo)
        except ErroNarrador as e:
            raise gr.Error(str(e))
        except Exception as e:  # noqa: BLE001
            raise gr.Error(f"{type(e).__name__}: {e}")

    def gerar(apresentacao, roteiro, musica, motor, opcoes, legendas, movimento, transicao, resolucao, hf_token,
              progress=gr.Progress(track_tqdm=True)):
        if apresentacao is None:
            raise gr.Error("Envie a apresentacao (.pptx ou .pdf).")
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token.strip()
        ref = voz_dir / "minha_voz.wav"
        cfg = pipeline.Config(**{**cfg_base.__dict__})
        cfg.motor = motor
        cfg.voz = str(ref) if ref.exists() else None
        cfg.transcricao = str(ref.with_suffix(".txt")) if ref.with_suffix(".txt").exists() else None
        cfg.opcoes_motor = {**(cfg.opcoes_motor or {}), **_parse_opcoes(opcoes)}
        cfg.legendas_embutidas = bool(legendas)
        cfg.movimento = bool(movimento)
        cfg.transicao = float(transicao)
        cfg.largura, cfg.altura = {"1080p": (1920, 1080), "720p": (1280, 720)}[resolucao]
        cfg.musica = musica if musica else None
        if motor not in {"piper", "edge", "silencio", "elevenlabs", "fish"} and not cfg.voz:
            raise gr.Error("Prepare a sua voz na aba 1 antes de gerar com um motor de clonagem.")
        # copia a entrada para um nome estavel
        entrada = Path(apresentacao)
        trabalho = garantir_dir(saida_dir / "_entrada")
        alvo = trabalho / entrada.name
        shutil.copy(entrada, alvo)
        progress(0.05, desc="Convertendo slides e narrando...")
        try:
            mp4 = pipeline.gerar(alvo, saida_dir, cfg, roteiro=Path(roteiro) if roteiro else None)
        except ErroNarrador as e:
            raise gr.Error(str(e))
        except Exception as e:  # noqa: BLE001
            raise gr.Error(f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}")
        srt = mp4.with_suffix(".srt")
        rot = mp4.parent / "roteiro_usado.md"
        return str(mp4), str(mp4), str(srt), str(rot)

    with gr.Blocks(title="Narrador") as app:
        gr.Markdown("# Narrador\nSlides narrados com a sua voz clonada. 1) prepare a voz, 2) teste, 3) gere o video.")
        with gr.Row():
            motor = gr.Dropdown(MOTORES_WEB, value=cfg_base.motor if cfg_base.motor in MOTORES_WEB else "chatterbox-online",
                                label="Motor de voz", info="; ".join(f"{k}: {v}" for k, v in MOTORES.items() if k in MOTORES_WEB[:4]))
            hf_token = gr.Textbox(label="HF_TOKEN (motor online)", type="password", value=os.getenv("HF_TOKEN", ""))
            opcoes = gr.Textbox(label="Opcoes do motor (chave=valor por linha)", lines=2,
                                value="exaggeration=0.45\ncfg_weight=0.5")
        with gr.Tab("1. Voz"):
            grav = gr.Audio(label="Gravacao da sua voz (8-15 s, limpa)", type="filepath")
            with gr.Row():
                inicio = gr.Number(label="Inicio (s)", value=0)
                duracao = gr.Number(label="Duracao (s), 0 = tudo", value=0)
            transc = gr.Textbox(label="Transcricao exata do trecho (recomendado)")
            btn_voz = gr.Button("Preparar voz", variant="primary")
            voz_out = gr.Audio(label="Referencia preparada")
            voz_msg = gr.Markdown()
            btn_voz.click(lambda a, t, i, d: preparar_voz(a, t, i or None, d or None),
                          [grav, transc, inicio, duracao], [voz_out, voz_msg])
        with gr.Tab("2. Teste"):
            txt = gr.Textbox(label="Frase de teste", value="Ola! Esta e uma amostra da minha voz clonada narrando esta apresentacao.")
            btn_t = gr.Button("Gerar amostra", variant="primary")
            amostra = gr.Audio(label="Amostra")
            btn_t.click(testar, [motor, txt, opcoes, hf_token], amostra)
        with gr.Tab("3. Video"):
            with gr.Row():
                apres = gr.File(label="Apresentacao (.pptx ou .pdf)", file_types=[".pptx", ".pdf"], type="filepath")
                rot = gr.File(label="Roteiro .md (opcional)", file_types=[".md", ".txt", ".json", ".yaml"], type="filepath")
                mus = gr.File(label="Musica de fundo (opcional)", file_types=[".mp3", ".wav", ".m4a"], type="filepath")
            with gr.Row():
                leg = gr.Checkbox(label="Legendas embutidas", value=True)
                mov = gr.Checkbox(label="Zoom suave", value=False)
                tr = gr.Slider(0, 1.5, value=0.4, step=0.1, label="Transicao (s)")
                res = gr.Radio(["1080p", "720p"], value="1080p", label="Resolucao")
            btn_g = gr.Button("Gerar video", variant="primary")
            video = gr.Video(label="Resultado")
            with gr.Row():
                dl_mp4 = gr.File(label="MP4")
                dl_srt = gr.File(label="Legendas .srt")
                dl_rot = gr.File(label="Roteiro usado")
            btn_g.click(gerar, [apres, rot, mus, motor, opcoes, leg, mov, tr, res, hf_token], [video, dl_mp4, dl_srt, dl_rot])
    return app


def iniciar(cfg: pipeline.Config, saida: Path, porta: int = 7860, compartilhar: bool = False, host: str = "127.0.0.1"):
    try:
        import gradio  # noqa: F401
    except ImportError as e:
        raise ErroNarrador("gradio nao instalado. Rode: pip install 'narrador[web]'  (ou pip install gradio)") from e
    app = criar_app(cfg, saida)
    app.queue().launch(server_name=host, server_port=porta, share=compartilhar, show_error=True, inbrowser=not compartilhar)
