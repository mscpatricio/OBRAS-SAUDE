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

## GPT-SoVITS em português do Brasil (Windows)

O instalador (`-ComGptSovits`) baixa o pacote integrado e aplica o **patch pt-BR** do Narrador
(`narrador/gptsovits_ptbr/`), que ensina o GPT-SoVITS a ler português.

1. **Treine a sua voz** (obrigatório para boa qualidade): grave 5 a 20 minutos lendo textos em português,
   coloque os arquivos numa pasta e arraste a pasta para `treinar_voz_ptbr.bat`. Leva 20-60 min numa GPU
   NVIDIA de 6 GB ou mais. Ao final ele imprime os caminhos dos pesos (`SoVITS_weights_v2Pro\...pth` e
   `GPT_weights_v2Pro\...ckpt`).
2. Em `C:\narrador\narrador.yaml`, defina `motor: gpt-sovits`, `text_lang: pt`, `gpt_weights` e `sovits_weights`
   com esses caminhos.
3. `iniciar_gpt_sovits.bat` sobe o servidor (deixe a janela aberta) e `narrar.bat` / `abrir_web.bat` geram o vídeo.

Para pronúncia melhor com pouco áudio seu, treine antes o modelo-base de português (uma hora de leituras
públicas) e parta dele: na pasta `C:\narrador\GPT-SoVITS`, `runtime\python.exe baixar_corpus_pt.py --minutos 60 --saida corpus_pt`,
`runtime\python.exe treinar_ptbr.py --lista corpus_pt\corpus_pt.list --nome ptbr_base --epocas-sovits 0 --epocas-gpt 6` e então
`runtime\python.exe treinar_ptbr.py --audio C:\voz --nome minha_voz --base-gpt GPT_weights_v2Pro\ptbr_base-e6.ckpt`.

Sem treinar (zero-shot) o português sai com sotaque forte e palavras trocadas: serve só para testar o fluxo.
Para quem não tem GPU, o caminho é o notebook `exemplos/narrador_gptsovits_ptbr_treino.ipynb` no Google Colab
ou os motores `chatterbox-online` / `chatterbox-ptbr`.
