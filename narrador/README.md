# Narrador: slides narrados com a sua voz clonada, em MP4

Bot/CLI que pega uma apresentação (`.pptx`, `.pdf` ou pasta de imagens), narra cada slide
com **a sua voz clonada** (modelos gratuitos, sem som robótico) e monta um **vídeo MP4**
com transições, legendas `.srt` e música de fundo opcional.

```
PPTX/PDF ──► imagens dos slides + notas do orador (roteiro)
         ──► normalização do texto (números, R$, datas, siglas por extenso)
         ──► TTS com voz clonada, frase a frase (Chatterbox / Qwen3 / F5 / XTTS / ElevenLabs)
         ──► masterização do áudio (ruído, compressão suave, -16 LUFS, 48 kHz)
         ──► ffmpeg: slide + áudio, fade entre slides, legendas, música com ducking
         ──► saida/<nome>/<nome>.mp4  (+ .srt, roteiro usado, áudio por slide)
```

## Qual motor de voz usar? (pesquisa de outubro/2026)

| motor | licença / custo | clonagem | pt-BR | hardware | observações |
|---|---|---|---|---|---|
| **chatterbox-ptbr** (padrão recomendado) | MIT, grátis | sim, 6-15 s de áudio | pacote dedicado pt-BR | CPU (lento) ou GPU | Resemble AI Chatterbox Multilingual V3 + fine-tune pt-BR. Melhor relação qualidade/facilidade. |
| chatterbox | MIT, grátis | sim | sim (23 idiomas) | CPU/GPU | mesmo modelo, checkpoint multilíngue genérico |
| qwen3 | Apache 2.0, grátis | sim, 3 s | sim | GPU ~8 GB | Qwen3-TTS 1.7B Base. Qualidade de ponta, mais pesado. |
| f5-ptbr | CC-BY-NC (não comercial) | sim | fine-tune pt-BR | GPU recomendada | F5-TTS pt-BR. Muito natural com transcrição da referência. |
| xtts | CPML (não comercial) | sim | sim | CPU/GPU | Coqui XTTS v2, clássico |
| elevenlabs | freemium/pago | no painel deles | sim | nuvem | máxima qualidade; plano grátis não permite uso comercial |
| edge | grátis | **não** | vozes neurais pt-BR | nuvem | só para testar roteiro e vídeo rapidamente |

Resumo: para uso livre (inclusive institucional/comercial) com a sua voz, use **chatterbox-ptbr**.
Se tiver GPU e quiser o máximo de naturalidade em código aberto, compare com **qwen3**.

## Instalação

Requisitos: Python 3.10-3.12 (recomendado para os motores de IA), `ffmpeg` e, para `.pptx`,
LibreOffice (`soffice`).

```bash
# Ubuntu/Debian
sudo apt install ffmpeg libreoffice-impress

cd narrador
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                      # núcleo (sem motor de IA)
pip install -e '.[chatterbox]'        # motor recomendado (baixa ~2 GB de modelos na 1ª execução)
# outros: '.[qwen3]'  '.[f5]'  '.[xtts]'  '.[edge]'
```

> Python 3.13: se o `pip` falhar ao compilar `docopt` (dependência do `num2words`), rode antes
> `pip install docopt-ng` e depois `pip install --no-deps num2words`.

GPU NVIDIA: instale o PyTorch com CUDA antes do motor (`pip install torch --index-url https://download.pytorch.org/whl/cu124`).
Em CPU o Chatterbox funciona, mas leva cerca de 5-15x o tempo da fala.

## Passo 1: preparar a sua voz (uma vez)

Grave **8 a 15 segundos** de fala contínua, natural, perto do microfone, sem música nem eco
(pode ser pelo celular). Depois:

```bash
narrador voz preparar gravacao.m4a --inicio 2 --duracao 12 \
  --transcricao "Texto exato do que você disse no trecho."
# -> voz/minha_voz.wav (mono, 24 kHz, limpo) + voz/minha_voz.txt
```

Ouça uma amostra clonada antes de narrar tudo:

```bash
narrador voz testar --voz voz/minha_voz.wav --motor chatterbox-ptbr \
  -t "Olá! Esta é uma amostra da minha voz clonada." -s saida/teste.wav
```

Ajuste fino (Chatterbox): `-o exaggeration=0.4` (mais sóbrio) a `0.7` (mais animado);
`-o cfg_weight=0.3` (mais expressivo) a `0.6` (mais fiel ao ritmo da referência).

## Passo 2: gerar o vídeo

O texto narrado vem, nesta ordem de prioridade: roteiro externo > **notas do orador** do PPTX >
texto visível do slide.

```bash
# PPTX com notas do orador
narrador gerar apresentacao.pptx --voz voz/minha_voz.wav --motor chatterbox-ptbr

# PDF ou pasta de imagens + roteiro em Markdown
narrador gerar slides.pdf --roteiro roteiro.md --voz voz/minha_voz.wav

# extras: zoom suave, legendas embutidas, música de fundo, 720p
narrador gerar apresentacao.pptx --voz voz/minha_voz.wav --movimento --legendas \
  --musica fundo.mp3 --resolucao 720p
```

Saída em `saida/<nome>/`: `<nome>.mp4`, `<nome>.srt`, `roteiro_usado.md`, `audio/slide_NNN.wav`,
`slides/slide_NNN.png`, `resumo.json`. Trechos já sintetizados ficam em cache: se você corrigir
só um slide, apenas ele é regravado.

### Roteiro editável

```bash
narrador roteiro apresentacao.pptx        # gera apresentacao.roteiro.md a partir das notas
# edite o .md e rode:
narrador gerar apresentacao.pptx -r apresentacao.roteiro.md --voz voz/minha_voz.wav
```

Formato (veja `exemplos/roteiro.exemplo.md`): um bloco `## Slide N` por slide; parágrafos separados
por linha em branco viram pausas maiores. Números, `R$`, `%`, datas, horas e siglas (SUS, UTI,
CNPJ...) são convertidos para a forma falada automaticamente.

## Modo bot (pasta vigiada)

```bash
narrador bot --entrada caixa_entrada --saida saida --voz voz/minha_voz.wav --motor chatterbox-ptbr
```

Solte na pasta `caixa_entrada/`:

- `relatorio.pptx` (ou `.pdf`)
- `relatorio.roteiro.md` (opcional)
- `relatorio.musica.mp3` (opcional)

O bot espera o arquivo terminar de copiar, gera `saida/relatorio/relatorio.mp4` e move a entrada
para `caixa_entrada/processados/` (ou `erros/` com o log da falha). Use `--uma-vez` para rodar em
cron/CI. Para rodar como serviço no Linux, um `systemd` simples basta:

```ini
[Service]
WorkingDirectory=/caminho/narrador
ExecStart=/caminho/narrador/.venv/bin/narrador bot --config narrador.yaml
Restart=always
```

## Configuração

Copie `narrador.exemplo.yaml` para `narrador.yaml` (lido automaticamente) e ajuste motor, voz,
pausas, loudness, transição, resolução etc. Qualquer opção da linha de comando sobrescreve o YAML.

## Dicas para voz natural, "de estúdio"

1. **Referência boa = clone bom.** Fala limpa, sem ruído, com a entonação que você quer no vídeo
   (uma leitura animada gera narração animada).
2. **Frases curtas no roteiro.** O Narrador já quebra em ~220 caracteres, mas pontuação boa
   (vírgulas, pontos) dá ritmo e respiração reais.
3. **Transcrição da referência** melhora muito Qwen3 e F5 (e não atrapalha os outros).
4. **Masterização** é automática: passa-alta 70 Hz, redução de ruído suave, de-esser, compressão
   leve e normalização a -16 LUFS (padrão YouTube/podcast). Desligue a redução de ruído com
   `--com-ruido` se a referência já for de estúdio.
5. Se um trecho sair estranho (alucinação do modelo), edite o roteiro daquele slide e rode de novo:
   só ele será regravado.

## Testar sem GPU e sem clonagem

```bash
python exemplos/criar_pptx_exemplo.py saida/exemplo.pptx
narrador gerar saida/exemplo.pptx --motor edge        # vozes neurais pt-BR da Microsoft (sem clonagem)
narrador gerar saida/exemplo.pptx --motor silencio    # só valida slides/vídeo/legendas
```

## Estrutura

```
narrador/
  narrador/
    cli.py        comandos: gerar, roteiro, voz preparar|testar, bot, motores
    pipeline.py   orquestração + cache de síntese
    slides.py     PPTX/PDF/imagens -> PNG; notas do orador; leitura de roteiro .md/.json/.yaml
    texto.py      normalização pt-BR (num2words) e divisão em frases
    audio.py      junção com pausas, masterização (ffmpeg), preparo da referência
    video.py      segmentos por slide, xfade/acrossfade, SRT, música com ducking, legendas embutidas
    bot.py        pasta vigiada
    tts/          motores: chatterbox, qwen3, f5, xtts, elevenlabs, edge, silencio
  exemplos/       roteiro de exemplo e gerador de PPTX de teste
  narrador.exemplo.yaml
```

## Licenças dos modelos (atenção para uso institucional)

- Chatterbox (MIT) e Qwen3-TTS (Apache 2.0): uso livre, inclusive comercial.
- F5-TTS pt-BR (CC-BY-NC 4.0) e XTTS v2 (CPML): **somente não comercial**.
- Clone apenas a **sua própria voz** ou vozes com autorização expressa da pessoa.
