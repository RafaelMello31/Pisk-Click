[Setup]
; Informações do aplicativo
AppId={{F8A3B2C1-D4E5-6F78-9A0B-1C2D3E4F5A6B}}
AppName=Pisk And Click
AppVersion=1.0
AppPublisher=TCC - Controle Facial
AppVerName=Pisk And Click v1.0
DefaultDirName={autopf}\PiskAndClick
DefaultGroupName=Pisk And Click
OutputDir=.
OutputBaseFilename=PiskAndClick_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=assets\pisk_and_click.ico
UninstallDisplayIcon={app}\pisk_and_click.ico
DisableProgramGroupPage=yes
DisableWelcomePage=no
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
; Instalador do Python 3.11
Source: "python_installer\python-3.11.0-amd64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: not IsPythonInstalled

; Arquivos Python do programa
Source: "pisk_and_click.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "user_profile_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_config_gui.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_calibration.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "modern_profile_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "mediapipe_installer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "fix_mediapipe.py"; DestDir: "{app}"; Flags: ignoreversion

; Recursos
Source: "assets\\logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\\pisk_and_click.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "verificar_python.bat"; DestDir: "{app}"; Flags: ignoreversion deleteafterinstall

[Dirs]
Name: "{app}\profiles"
Name: "{app}\venv"

[Icons]
Name: "{autodesktop}\Pisk & Click"; Filename: "{app}\Iniciar_PiskAndClick.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\pisk_and_click.ico"
Name: "{group}\Pisk & Click"; Filename: "{app}\Iniciar_PiskAndClick.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\pisk_and_click.ico"
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"

[Run]
; 1. Instalar Python se necessário
Filename: "{tmp}\python-3.11.0-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0"; StatusMsg: "Instalando Python 3.11..."; Check: not IsPythonInstalled; Flags: waituntilterminated

; 2. Aguardar e verificar Python
Filename: "{app}\verificar_python.bat"; StatusMsg: "Verificando Python..."; Flags: runhidden waituntilterminated

; 3. Criar ambiente virtual (tentar caminho completo primeiro)
Filename: "{cmd}"; Parameters: "/c ""C:\Program Files\Python311\python.exe"" -m venv ""{app}\venv"" || python -m venv ""{app}\venv"""; WorkingDir: "{app}"; StatusMsg: "Criando ambiente virtual..."; Flags: runhidden waituntilterminated

; 4. Atualizar pip
Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install --upgrade pip --quiet"; WorkingDir: "{app}"; StatusMsg: "Atualizando pip..."; Flags: runhidden waituntilterminated

; 5. Instalar dependências (ordem correta)
Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install numpy==1.24.0 --quiet"; WorkingDir: "{app}"; StatusMsg: "Instalando NumPy..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install protobuf==3.20.0 --quiet"; WorkingDir: "{app}"; StatusMsg: "Instalando Protobuf..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install opencv-python==4.8.1.78 --quiet"; WorkingDir: "{app}"; StatusMsg: "Instalando OpenCV..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install pillow==10.0.0 --quiet"; WorkingDir: "{app}"; StatusMsg: "Instalando Pillow..."; Flags: runhidden waituntilterminated

Filename: "{app}\venv\Scripts\python.exe"; Parameters: "-m pip install pyautogui==0.9.54 --quiet"; WorkingDir: "{app}"; StatusMsg: "Instalando PyAutoGUI..."; Flags: runhidden waituntilterminated

; 6. Instalar MediaPipe (instalador inteligente)
Filename: "{app}\venv\Scripts\python.exe"; Parameters: """{app}\mediapipe_installer.py"""; WorkingDir: "{app}"; StatusMsg: "Instalando MediaPipe..."; Flags: runhidden waituntilterminated

[Code]
var
  PythonInstalled: Boolean;
  PythonPath: string;

function IsPythonInstalled(): Boolean;
var
  ResultCode: Integer;
  PythonExe: string;
begin
  Result := False;
  PythonInstalled := False;
  
  // Verificar Python 3.11
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
  
  // Verificar comando python
  if Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
  begin
    PythonPath := 'python';
    Result := True;
    PythonInstalled := True;
  end;
end;

procedure InitializeWizard();
begin
  if IsPythonInstalled() then
  begin
    MsgBox('Python detectado!' + #13#10 + #13#10 + 
           'O Pisk & Click usará o Python existente.', mbInformation, MB_OK);
  end
  else
  begin
    MsgBox('Python não encontrado.' + #13#10 + #13#10 + 
           'Python 3.11 será instalado automaticamente.' + #13#10 + #13#10 +
           'IMPORTANTE: A instalação pode levar 5-10 minutos.' + #13#10 +
           'Aguarde até o final sem fechar o instalador.', mbInformation, MB_OK);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchContent: string;
  VBSContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Criar script BAT
    BatchContent := '@echo off' + #13#10 +
                   'title Pisk And Click' + #13#10 +
                   'cd /d "%~dp0"' + #13#10 +
                   'set MEDIAPIPE_DISABLE_GPU=1' + #13#10 +
                   'set GLOG_logtostderr=1' + #13#10 +
                   'set GLOG_v=0' + #13#10 +
                   'venv\Scripts\python.exe pisk_and_click.py' + #13#10 +
                   'if %ERRORLEVEL% NEQ 0 (' + #13#10 +
                   '    echo Erro ao executar!' + #13#10 +
                   '    pause' + #13#10 +
                   ')';
    
    SaveStringToFile(ExpandConstant('{app}\Iniciar_PiskAndClick.bat'), BatchContent, False);
    
    // Criar script VBS (execução silenciosa)
    VBSContent := 'Set WshShell = CreateObject("WScript.Shell")' + #13#10 +
                 'WshShell.Run chr(34) & "' + ExpandConstant('{app}') + '\Iniciar_PiskAndClick.bat" & Chr(34), 0, False' + #13#10 +
                 'Set WshShell = Nothing';
    
    SaveStringToFile(ExpandConstant('{app}\Iniciar_PiskAndClick.vbs'), VBSContent, False);
    
    // Mensagem final
    MsgBox('Instalação concluída com sucesso!' + #13#10 + #13#10 +
           'Use o atalho "Pisk & Click" na área de trabalho para iniciar.', mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Deseja remover os perfis de usuário?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\profiles'), True, True, True);
      DelTree(ExpandConstant('{app}\venv'), True, True, True);
    end;
  end;
end;
