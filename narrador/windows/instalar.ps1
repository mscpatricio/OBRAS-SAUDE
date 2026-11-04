<#
  Instalador do Narrador para Windows 10/11 (PowerShell).

  O que faz:
    1. Instala Python 3.11, Git, ffmpeg, 7-Zip e LibreOffice via winget (se faltarem)
    2. Baixa o Narrador (este repositorio) e cria um ambiente virtual em C:\narrador
    3. (Opcional) Baixa o pacote integrado do GPT-SoVITS (~8 GB) e configura o servidor api_v2
    4. Cria atalhos: narrar.bat, iniciar_gpt_sovits.bat, abrir_web.bat

  Uso (PowerShell como administrador):
    Set-ExecutionPolicy -Scope Process Bypass -Force
    .\instalar.ps1                     # Narrador + motores online/piper
    .\instalar.ps1 -ComGptSovits       # tambem baixa o GPT-SoVITS (8 GB)
    .\instalar.ps1 -ComChatterbox      # tambem instala o Chatterbox pt-BR local (precisa GPU NVIDIA)
#>
param(
    [string]$Destino = "C:\narrador",
    [switch]$ComGptSovits,
    [switch]$ComChatterbox,
    [string]$PacoteGptSovits = "GPT-SoVITS-v2pro-20250604.7z",
    [string]$Branch = "claude/eloquent-babbage-8sxcoq"
)
$ErrorActionPreference = "Stop"
function Passo($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function TemComando($c) { return [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Winget($id) {
    if (-not (TemComando winget)) { throw "winget nao encontrado. Atualize o 'Instalador de Aplicativo' na Microsoft Store." }
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements | Out-Null
}

Passo "Dependencias do sistema (winget)"
if (-not (TemComando python) -or -not ((python --version 2>&1) -match "3\.1[012]")) { Winget "Python.Python.3.11" }
if (-not (TemComando git))    { Winget "Git.Git" }
if (-not (TemComando ffmpeg)) { Winget "Gyan.FFmpeg" }
if (-not (Test-Path "C:\Program Files\7-Zip\7z.exe")) { Winget "7zip.7zip" }
if (-not (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe")) {
    try { Winget "TheDocumentFoundation.LibreOffice" } catch { Write-Warning "LibreOffice nao instalado; o Narrador usara o PowerPoint, se existir." }
}
# recarrega o PATH da sessao
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Passo "Baixando o Narrador em $Destino"
New-Item -ItemType Directory -Force -Path $Destino | Out-Null
$repo = Join-Path $Destino "OBRAS-SAUDE"
if (-not (Test-Path $repo)) {
    git clone -b $Branch https://github.com/mscpatricio/OBRAS-SAUDE.git $repo
} else {
    git -C $repo pull
}
$narr = Join-Path $repo "narrador"

Passo "Ambiente Python"
$venv = Join-Path $Destino "venv"
if (-not (Test-Path $venv)) { python -m venv $venv }
$py = Join-Path $venv "Scripts\python.exe"
& $py -m pip install --upgrade pip wheel | Out-Null
& $py -m pip install docopt-ng
& $py -m pip install --no-deps num2words
$extras = "online,piper,web"
if ($ComChatterbox) { $extras += ",chatterbox" }
& $py -m pip install -e "$narr[$extras]"
if ($ComChatterbox) {
    Write-Host "Instalando PyTorch com CUDA 12.4 para o Chatterbox..."
    & $py -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
}

if ($ComGptSovits) {
    Passo "GPT-SoVITS: baixando o pacote integrado ($PacoteGptSovits, ~8 GB)"
    $gsvDir = Join-Path $Destino "GPT-SoVITS"
    $sete = Join-Path $Destino $PacoteGptSovits
    if (-not (Test-Path $gsvDir)) {
        if (-not (Test-Path $sete)) {
            $url = "https://huggingface.co/lj1995/GPT-SoVITS-windows-package/resolve/main/$PacoteGptSovits?download=true"
            Write-Host "URL: $url"
            Start-BitsTransfer -Source $url -Destination $sete -DisplayName "GPT-SoVITS"
        }
        & "C:\Program Files\7-Zip\7z.exe" x $sete "-o$Destino" -y | Out-Null
        $extraido = Get-ChildItem $Destino -Directory | Where-Object { $_.Name -like "GPT-SoVITS*" -and $_.Name -ne "GPT-SoVITS" } | Select-Object -First 1
        if ($extraido) { Rename-Item $extraido.FullName $gsvDir }
        Remove-Item $sete -Force
    }
    $bat = @"
@echo off
title GPT-SoVITS api_v2 (porta 9880)
cd /d "$gsvDir"
runtime\python.exe api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS\configs\tts_infer.yaml
pause
"@
    Set-Content -Path (Join-Path $Destino "iniciar_gpt_sovits.bat") -Value $bat -Encoding ASCII
    $batUi = @"
@echo off
title GPT-SoVITS WebUI (treino da sua voz)
cd /d "$gsvDir"
call go-webui.bat
"@
    Set-Content -Path (Join-Path $Destino "treinar_voz_gpt_sovits.bat") -Value $batUi -Encoding ASCII
}

Passo "Atalhos"
$narrar = @"
@echo off
rem Arraste um .pptx ou .pdf para este arquivo, ou: narrar.bat apresentacao.pptx
cd /d "$Destino"
if "%~1"=="" ( echo Uso: arraste a apresentacao .pptx para este arquivo & pause & exit /b 1 )
set HF_TOKEN_FILE=$Destino\hf_token.txt
if exist "%HF_TOKEN_FILE%" ( set /p HF_TOKEN=<"%HF_TOKEN_FILE%" )
"$py" -m narrador.cli gerar "%~1" --config "$Destino\narrador.yaml" --saida "$Destino\saida" --legendas
pause
"@
Set-Content -Path (Join-Path $Destino "narrar.bat") -Value $narrar -Encoding ASCII
$web = @"
@echo off
title Narrador - interface web (http://127.0.0.1:7860)
cd /d "$Destino"
set HF_TOKEN_FILE=$Destino\hf_token.txt
if exist "%HF_TOKEN_FILE%" ( set /p HF_TOKEN=<"%HF_TOKEN_FILE%" )
"$py" -m narrador.cli web --config "$Destino\narrador.yaml"
pause
"@
Set-Content -Path (Join-Path $Destino "abrir_web.bat") -Value $web -Encoding ASCII
$vozbat = @"
@echo off
rem Arraste a gravacao da sua voz (mp3/m4a/wav) para este arquivo
cd /d "$Destino"
if "%~1"=="" ( echo Uso: arraste a gravacao da sua voz para este arquivo & pause & exit /b 1 )
"$py" -m narrador.cli voz preparar "%~1" --saida "$Destino\voz\minha_voz.wav"
pause
"@
Set-Content -Path (Join-Path $Destino "preparar_voz.bat") -Value $vozbat -Encoding ASCII

$cfg = Join-Path $Destino "narrador.yaml"
if (-not (Test-Path $cfg)) {
    $motor = if ($ComChatterbox) { "chatterbox-ptbr" } else { "chatterbox-online" }
    @"
# Configuracao do Narrador (Windows). Edite a vontade.
motor: $motor            # chatterbox-online | chatterbox-ptbr | gpt-sovits | piper
voz: $Destino\voz\minha_voz.wav
transcricao: $Destino\voz\minha_voz.txt
idioma: pt
opcoes_motor:
  exaggeration: 0.45
  cfg_weight: 0.5
  # Para o GPT-SoVITS (motor: gpt-sovits), descomente:
  # url: http://127.0.0.1:9880
  # text_lang: en          # zh | en | ja | ko | yue (sem portugues no GPT-SoVITS oficial)
  # gpt_weights: $Destino\GPT-SoVITS\GPT_weights_v2Pro\minha_voz-e15.ckpt
  # sovits_weights: $Destino\GPT-SoVITS\SoVITS_weights_v2Pro\minha_voz_e8_s200.pth
legendas_embutidas: true
transicao: 0.4
"@ | Set-Content -Path $cfg -Encoding UTF8
}
New-Item -ItemType Directory -Force -Path (Join-Path $Destino "voz"), (Join-Path $Destino "saida") | Out-Null

Write-Host "`nPronto!" -ForegroundColor Green
Write-Host "Pasta: $Destino"
Write-Host "  1. Salve seu token do Hugging Face em $Destino\hf_token.txt (para o motor online)"
Write-Host "  2. Arraste a gravacao da sua voz para preparar_voz.bat"
Write-Host "  3. Arraste a apresentacao .pptx para narrar.bat   (ou abra abrir_web.bat)"
if ($ComGptSovits) { Write-Host "  4. GPT-SoVITS: iniciar_gpt_sovits.bat (servidor) e treinar_voz_gpt_sovits.bat (WebUI de treino)" }
