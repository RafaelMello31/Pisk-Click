[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName=Pisk And Click
AppVersion=1.0
AppPublisher=Pisk And Click Team
AppVerName=Pisk And Click v1.0
DefaultDirName={autopf}\PiskAndClick
DefaultGroupName=Pisk And Click
OutputDir=.
OutputBaseFilename=PiskAndClick_Setup_Final
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=assets\pisk_and_click.ico
UninstallDisplayIcon={app}\pisk_and_click_icon.ico
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
; Instalador do Python 3.11 (deve estar na pasta python_installer)
Source: "python_installer\python-3.11.0-amd64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: not IsPythonInstalled

; Arquivos principais do programa
Source: "pisk_and_click.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Módulos do sistema
Source: "user_profile_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_config_gui.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_calibration.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_profile_manager.py"; DestDir: "{app}"; Flags: ignoreversion

; Utilitários de instalação
Source: "mediapipe_installer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "fix_mediapipe.py"; DestDir: "{app}"; Flags: ignoreversion

; Recursos visuais
; Recursos visuais
; Copiar a partir de assets
Source: "assets\\logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\\pisk_and_click.ico"; DestDir: "{app}"; DestName: "pisk_and_click_icon.ico"; Flags: ignoreversion

[Dirs]
Name: "{app}\profiles"

[Icons]
Name: "{autodesktop}\Pisk & Click"; Filename: "{app}\PiskAndClick.bat"; WorkingDir: "{app}"; IconFilename: "{app}\pisk_and_click_icon.ico"
Name: "{group}\Pisk & Click"; Filename: "{app}\PiskAndClick.bat"; WorkingDir: "{app}"; IconFilename: "{app}\pisk_and_click_icon.ico"
Name: "{group}\Desinstalar Pisk & Click"; Filename: "{uninstallexe}"

[Run]
; Instalar Python 3.11 se necessário
Filename: "{tmp}\python-3.11.0-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1"; StatusMsg: "Instalando Python 3.11... Isso pode levar alguns minutos."; Check: not IsPythonInstalled; Flags: waituntilterminated

; Aguardar Python estar disponível
Filename: "{cmd}"; Parameters: "/c timeout /t 5 /nobreak"; StatusMsg: "Aguardando Python..."; Flags: runhidden waituntilterminated

; Criar ambiente virtual
Filename: "python"; Parameters: "-m venv ""{app}\venv"""; WorkingDir: "{app}"; StatusMsg: "Criando ambiente virtual..."; Flags: runhidden waituntilterminated

; Atualizar pip
Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install --upgrade pip"; WorkingDir: "{app}"; StatusMsg: "Atualizando pip..."; Flags: runhidden waituntilterminated

; Instalar dependências básicas primeiro
Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install numpy==1.24.0"; WorkingDir: "{app}"; StatusMsg: "Instalando NumPy..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install opencv-python==4.8.1.78"; WorkingDir: "{app}"; StatusMsg: "Instalando OpenCV..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install protobuf==3.20.0"; WorkingDir: "{app}"; StatusMsg: "Instalando Protobuf..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install pillow==10.0.0"; WorkingDir: "{app}"; StatusMsg: "Instalando Pillow..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install pyautogui==0.9.54"; WorkingDir: "{app}"; StatusMsg: "Instalando PyAutoGUI..."; Flags: runhidden waituntilterminated

; Instalar MediaPipe com instalador inteligente
Filename: "{app}\venv\Scripts\python.exe"; Parameters: """{app}\mediapipe_installer.py"""; WorkingDir: "{app}"; StatusMsg: "Instalando MediaPipe (pode levar alguns minutos)..."; Flags: runhidden waituntilterminated

[Code]
var
  PythonInstalled: Boolean;
  PythonPath: string;

function IsPythonInstalled(): Boolean;
var
  ResultCode: Integer;
  PythonExe: string;
  TempFile: string;
begin
  Result := False;
  PythonInstalled := False;
  
  // Verificar no registro (Python 3.11)
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonExe) then
  begin
    PythonPath := PythonExe + 'python.exe';
    if FileExists(PythonPath) then
    begin
      Result := True;
      PythonInstalled := True;
      Exit;
    end;
  end;
  
  // Verificar Python 3.10
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonExe) then
  begin
    PythonPath := PythonExe + 'python.exe';
    if FileExists(PythonPath) then
    begin
      Result := True;
      PythonInstalled := True;
      Exit;
    end;
  end;
  
  // Verificar Python 3.9
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.9\InstallPath', '', PythonExe) then
  begin
    PythonPath := PythonExe + 'python.exe';
    if FileExists(PythonPath) then
    begin
      Result := True;
      PythonInstalled := True;
      Exit;
    end;
  end;
  
  // Verificar comando python no PATH
  TempFile := ExpandConstant('{tmp}\python_check.txt');
  if Exec('cmd.exe', '/c python --version > "' + TempFile + '" 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if FileExists(TempFile) then
    begin
      PythonPath := 'python';
      Result := True;
      PythonInstalled := True;
      DeleteFile(TempFile);
      Exit;
    end;
  end;
end;

procedure InitializeWizard();
begin
  if IsPythonInstalled() then
  begin
    MsgBox('Python detectado no sistema!' + #13#10 + #13#10 + 
           'O Pisk & Click será instalado usando o Python existente.' + #13#10 +
           'Caminho: ' + PythonPath, mbInformation, MB_OK);
  end
  else
  begin
    MsgBox('Python não foi encontrado no sistema.' + #13#10 + #13#10 + 
           'Python 3.11 será instalado automaticamente.' + #13#10 +
           'Isso pode levar alguns minutos.', mbInformation, MB_OK);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchContent: string;
  VBSContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Criar arquivo batch para executar o programa
    BatchContent := '@echo off' + #13#10 +
                   'title Pisk And Click v1.0' + #13#10 +
                   'cd /d "%~dp0"' + #13#10 +
                   '' + #13#10 +
                   'REM Configurar variáveis de ambiente' + #13#10 +
                   'set MEDIAPIPE_DISABLE_GPU=1' + #13#10 +
                   'set GLOG_logtostderr=1' + #13#10 +
                   'set GLOG_v=0' + #13#10 +
                   '' + #13#10 +
                   'REM Verificar se MediaPipe está funcionando' + #13#10 +
                   'venv\Scripts\python.exe -c "import mediapipe" >nul 2>&1' + #13#10 +
                   'if %ERRORLEVEL% NEQ 0 (' + #13#10 +
                   '    echo MediaPipe precisa ser reinstalado...' + #13#10 +
                   '    venv\Scripts\python.exe mediapipe_installer.py' + #13#10 +
                   '    if %ERRORLEVEL% NEQ 0 (' + #13#10 +
                   '        echo ERRO: Falha ao instalar MediaPipe!' + #13#10 +
                   '        pause' + #13#10 +
                   '        exit /b 1' + #13#10 +
                   '    )' + #13#10 +
                   ')' + #13#10 +
                   '' + #13#10 +
                   'REM Executar programa principal' + #13#10 +
                   'venv\Scripts\python.exe pisk_and_click.py' + #13#10 +
                   '' + #13#10 +
                   'REM Se houver erro, mostrar mensagem' + #13#10 +
                   'if %ERRORLEVEL% NEQ 0 (' + #13#10 +
                   '    echo.' + #13#10 +
                   '    echo ERRO na execucao do programa!' + #13#10 +
                   '    echo Verifique se a webcam esta conectada.' + #13#10 +
                   '    pause' + #13#10 +
                   ')';
    
    SaveStringToFile(ExpandConstant('{app}\PiskAndClick.bat'), BatchContent, False);
    
    // Criar VBS para execução silenciosa (sem janela de console)
    VBSContent := 'Set WshShell = CreateObject("WScript.Shell")' + #13#10 +
                 'WshShell.Run chr(34) & "' + ExpandConstant('{app}') + '\PiskAndClick.bat" & Chr(34), 0' + #13#10 +
                 'Set WshShell = Nothing';
    
    SaveStringToFile(ExpandConstant('{app}\PiskAndClick_Silent.vbs'), VBSContent, False);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Deseja remover também os perfis de usuário salvos?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\profiles'), True, True, True);
    end;
  end;
end;
