# Narrador no Windows

## Instalacao (uma vez)

1. Abra o **PowerShell como administrador**.
2. Rode:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
Invoke-WebRequest https://raw.githubusercontent.com/mscpatricio/OBRAS-SAUDE/claude/eloquent-babbage-8sxcoq/narrador/windows/instalar.ps1 -OutFile instalar.ps1
.\instalar.ps1                    # Narrador + motor online (Hugging Face) + Piper
# .\instalar.ps1 -ComGptSovits    # + GPT-SoVITS (pacote integrado, ~8 GB)
# .\instalar.ps1 -ComChatterbox   # + Chatterbox pt-BR local (GPU NVIDIA)
```

Tudo fica em `C:\narrador`.

## Uso diario

| Acao | Como |
|---|---|
| Preparar a sua voz | arraste a gravacao (mp3/m4a/wav) para `preparar_voz.bat` |
| Narrar uma apresentacao | arraste o `.pptx` para `narrar.bat`; o MP4 sai em `C:\narrador\saida\<nome>\` |
| Interface no navegador | `abrir_web.bat` e acesse http://127.0.0.1:7860 |
| Trocar motor/opcoes | edite `C:\narrador\narrador.yaml` |
| Token do Hugging Face (motor online) | cole o token em `C:\narrador\hf_token.txt` |

Se o LibreOffice nao for instalado, o Narrador usa o PowerPoint instalado para converter os slides.

## GPT-SoVITS no Windows

1. `iniciar_gpt_sovits.bat` sobe o servidor `api_v2` em http://127.0.0.1:9880 (deixe a janela aberta).
2. Em `narrador.yaml`, defina `motor: gpt-sovits` e `text_lang` (en, zh, ja, ko ou yue).
3. Para a voz identica (fine-tune com 1 minuto de audio): `treinar_voz_gpt_sovits.bat` abre a WebUI
   oficial; siga as abas 0 (fatiar audio, ASR), 1A (formatar dataset), 1B (treinar SoVITS e GPT).
   Depois aponte `gpt_weights` e `sovits_weights` no `narrador.yaml` para os arquivos gerados em
   `GPT_weights_v2Pro\` e `SoVITS_weights_v2Pro\`.

**Limite importante:** o GPT-SoVITS oficial **nao tem portugues**. Para narrar em pt-BR use
`motor: chatterbox-online` (sem GPU) ou `motor: chatterbox-ptbr` (GPU NVIDIA). O motor `gpt-sovits`
fica pronto para o dia em que um frontend pt-BR for publicado (basta `text_lang: pt`).
