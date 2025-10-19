; Inno Setup Script para instalar PisckClick
; Gera um instalador único pronto para disponibilização

#define MyAppName "PisckClick"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "PisckClick Team"
#define MyAppURL "https://seu-site.exemplo/pisckclick"
#define MyAppExeName "PisckClickLauncher.exe"

[Setup]
AppId={{6731C271-41A1-4F06-9E28-7D1A5F4101C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=release
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
ArchitecturesInstallIn64BitMode=x64

; Opcional: se tiver um .ico
;SetupIconFile=icon.ico

[Languages]
Name: "brazilian_portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
; Binário principal (resultado de PyInstaller)
Source: "dist\\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Perfis: entregamos o default
Source: "profiles\\default.json"; DestDir: "{app}\\profiles"; Flags: ignoreversion

; Documentação (TXT)
Source: "release\\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Icons]
; Atalho principal
Name: "{group}\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"

; Atalho com modo principal diretamente
Name: "{group}\{#MyAppName} (Controle Principal)"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "--mode main"
; Atalho com modo calibração diretamente
Name: "{group}\{#MyAppName} (Calibração)"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "--mode calib"
; Atalho com modo configurações diretamente
Name: "{group}\{#MyAppName} (Configurações)"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "--mode config"

; Atalho opcional na área de trabalho
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Primeira execução opcional após instalar
;Filename: "{app}\\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Mantém dados do usuário, mas pode-se limpar se quiser
; Type: filesandordirs; Name: "{app}\\profiles"