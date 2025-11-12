@echo off
title Compilar Instalador - Pisk And Click
color 0B
cls

echo.
echo ================================================
echo    COMPILADOR DO INSTALADOR PISK AND CLICK
echo ================================================
echo.

REM Verificar Inno Setup
set INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO% (
    echo [ERRO] Inno Setup 6 nao encontrado!
    echo.
    echo Instale de: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

REM Verificar arquivos essenciais
echo [1/3] Verificando arquivos...
if not exist "pisk_and_click.py" (
    echo [ERRO] pisk_and_click.py nao encontrado!
    pause
    exit /b 1
)
if not exist "assets\logo.png" (
    echo [ERRO] assets\logo.png nao encontrado!
    pause
    exit /b 1
)
if not exist "assets\pisk_and_click.ico" (
    echo [ERRO] assets\pisk_and_click.ico nao encontrado!
    pause
    exit /b 1
)
if not exist "main.py" (
    echo [ERRO] main.py nao encontrado!
    pause
    exit /b 1
)
if not exist "python_installer\python-3.11.0-amd64.exe" (
    echo [AVISO] Instalador do Python nao encontrado!
    echo Baixe de: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
    echo Coloque em: python_installer\
    echo.
    pause
)
echo [OK] Arquivos verificados!

REM Limpar instalador antigo
echo.
echo [2/3] Limpando instalador antigo...
if exist "PiskAndClick_Setup.exe" del /f /q "PiskAndClick_Setup.exe"

REM Compilar
echo.
echo [3/3] Compilando instalador...
echo.
%INNO% "PiskAndClick_Installer.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo    SUCESSO!
    echo ================================================
    echo.
    echo Instalador criado: PiskAndClick_Setup.exe
    echo.
    for %%A in ("PiskAndClick_Setup.exe") do echo Tamanho: %%~zA bytes
    echo.
    echo Pronto para distribuir!
    echo ================================================
) else (
    echo.
    echo [ERRO] Falha na compilacao!
)

echo.
pause
