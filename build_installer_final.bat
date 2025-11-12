@echo off
title Compilar Instalador Pisk And Click - FINAL
color 0A
echo.
echo ========================================
echo   COMPILADOR DO INSTALADOR FINAL
echo   Pisk And Click v1.0
echo ========================================
echo.

REM Verificar se Inno Setup está instalado
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_PATH%" (
    echo [ERRO] Inno Setup 6 nao encontrado!
    echo.
    echo Por favor, instale o Inno Setup 6:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

REM Verificar arquivos necessários
echo [1/5] Verificando arquivos necessarios...
set MISSING=0

if not exist "pisk_and_click.py" (
    echo   [X] pisk_and_click.py NAO ENCONTRADO
    set MISSING=1
)
if not exist "main.py" (
    echo   [X] main.py NAO ENCONTRADO
    set MISSING=1
)
if not exist "config.py" (
    echo   [X] config.py NAO ENCONTRADO
    set MISSING=1
)
if not exist "mediapipe_installer.py" (
    echo   [X] mediapipe_installer.py NAO ENCONTRADO
    set MISSING=1
)
if not exist "assets\logo.png" (
    echo   [X] assets\logo.png NAO ENCONTRADO
    set MISSING=1
)
if not exist "assets\pisk_and_click.ico" (
    echo   [X] assets\pisk_and_click.ico NAO ENCONTRADO
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo [ERRO] Arquivos necessarios nao encontrados!
    pause
    exit /b 1
)
echo   [OK] Todos os arquivos principais encontrados!

REM Verificar instalador do Python
echo.
echo [2/5] Verificando instalador do Python...
if not exist "python_installer\python-3.11.0-amd64.exe" (
    echo   [AVISO] Instalador do Python nao encontrado!
    echo.
    echo   O instalador sera criado, mas o Python precisara ser
    echo   instalado manualmente pelos usuarios.
    echo.
    echo   Para incluir o Python no instalador:
    echo   1. Baixe: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
    echo   2. Coloque em: python_installer\python-3.11.0-amd64.exe
    echo.
    pause
) else (
    echo   [OK] Instalador do Python encontrado!
)

REM Limpar instaladores antigos
echo.
echo [3/5] Limpando instaladores antigos...
if exist "PiskAndClick_Setup_Final.exe" (
    del /f /q "PiskAndClick_Setup_Final.exe"
    echo   [OK] Instalador antigo removido
)

REM Compilar instalador
echo.
echo [4/5] Compilando instalador...
echo   Isso pode levar alguns minutos...
echo.
"%INNO_PATH%" "PiskAndClick_Installer_Final.iss"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha na compilacao!
    pause
    exit /b 1
)

REM Verificar resultado
echo.
echo [5/5] Verificando resultado...
if exist "PiskAndClick_Setup_Final.exe" (
    echo.
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo.
    echo Instalador criado com sucesso:
    echo   PiskAndClick_Setup_Final.exe
    echo.
    
    REM Mostrar tamanho do arquivo
    for %%A in ("PiskAndClick_Setup_Final.exe") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo Tamanho: !sizeMB! MB
    )
    
    echo.
    echo O instalador inclui:
    echo   - Programa Pisk And Click completo
    echo   - Todos os modulos necessarios
    echo   - Instalador inteligente do MediaPipe
    echo   - Deteccao automatica do Python
    echo   - Instalacao do Python 3.11 (se necessario)
    echo.
    echo Pronto para distribuir!
    echo ========================================
) else (
    echo.
    echo [ERRO] Instalador nao foi criado!
    pause
    exit /b 1
)

echo.
pause
