@echo off
REM Script para verificar se Python está disponível

REM Tentar Python no PATH
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python encontrado no PATH
    exit /b 0
)

REM Tentar Python 3.11 instalado
"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python 3.11 encontrado
    exit /b 0
)

REM Aguardar e tentar novamente
timeout /t 5 /nobreak >nul
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python disponível após espera
    exit /b 0
)

echo Python não encontrado
exit /b 1
