; InnoSetup Script for LOLLMS Installer
; Created by ParisNeo
; Licensed under Apache 2.0

#define MyAppName "LOLLMS"
#define MyAppVersion "V13 Feather"
#define MyAppPublisher "ParisNeo"
#define MyAppURL "https://github.com/ParisNeo/lollms-webui"

[Setup]
AppId={{LOLLMS-INSTALLER}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userdocs}\LOLLMS
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=.
OutputBaseFilename=LOLLMS_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "https://github.com/ParisNeo/LollmsEnv/releases/download/V1.3.2/lollmsenv_installer.bat"; DestDir: "{tmp}"; Flags: external

[Dirs]
Name: "{app}\lollms-webui"

[Run]
; Download and run LollmsEnv installer
Filename: "{tmp}\lollmsenv_installer.bat"; Parameters: "--dir ""{app}\lollmsenv"" -y"; StatusMsg: "Installing LollmsEnv..."; Flags: runhidden

; Clone lollms-webui repository
Filename: "git"; Parameters: "clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git ""{app}\lollms-webui"""; StatusMsg: "Cloning lollms-webui repository..."; Flags: runhidden

; Create and activate virtual environment
Filename: "{app}\lollmsenv\bin\lollmsenv.bat"; Parameters: "create-env lollms_env"; WorkingDir: "{app}"; StatusMsg: "Creating virtual environment..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\activate.bat"; WorkingDir: "{app}"; StatusMsg: "Activating virtual environment..."; Flags: runhidden

; Install requirements
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -r requirements.txt"; WorkingDir: "{app}\lollms-webui"; StatusMsg: "Installing requirements..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -e lollms_core"; WorkingDir: "{app}\lollms-webui"; StatusMsg: "Installing lollms_core..."; Flags: runhidden

[Code]
var
  BindingPage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  BindingPage := CreateInputOptionPage(wpSelectDir,
    'Select Default Binding', 'Choose the default binding to be installed',
    'Please select one of the following options:',
    True, False);
  BindingPage.Add('None (install the binding later)');
  BindingPage.Add('Local binding - ollama');
  BindingPage.Add('Local binding - python_llama_cpp');
  BindingPage.Add('Local binding - bs_exllamav2');
  BindingPage.Add('Remote binding - groq');
  BindingPage.Add('Remote binding - open_router');
  BindingPage.Add('Remote binding - open_ai');
  BindingPage.Add('Remote binding - mistral_ai');
  BindingPage.Add('Remote binding - gemini');
  BindingPage.Add('Remote binding - vllm');
  BindingPage.Add('Remote binding - xAI');
  BindingPage.Add('Remote binding - elf');
  BindingPage.Add('Remote binding - remote lollms');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
  BindingScript: string;
begin
  Result := True;
  if CurPageID = BindingPage.ID then
  begin
    case BindingPage.SelectedValueIndex of
      1: BindingScript := 'ollama';
      2: BindingScript := 'python_llama_cpp';
      3: BindingScript := 'bs_exllamav2';
      4: BindingScript := 'groq';
      5: BindingScript := 'open_router';
      6: BindingScript := 'open_ai';
      7: BindingScript := 'mistral_ai';
      8: BindingScript := 'gemini';
      9: BindingScript := 'vllm';
      10: BindingScript := 'xAI';
      11: BindingScript := 'elf';
      12: BindingScript := 'remote_lollms';
    else
      BindingScript := '';
    end;
    
    if BindingScript <> '' then
    begin
      if not Exec(ExpandConstant('{app}\lollmsenv\envs\lollms_env\Scripts\python.exe'),
                  ExpandConstant('zoos/bindings_zoo/' + BindingScript + '/__init__.py'),
                  ExpandConstant('{app}\lollms-webui'),
                  SW_HIDE,
                  ewWaitUntilTerminated,
                  ResultCode) then
      begin
        MsgBox('Error installing binding: ' + SysErrorMessage(ResultCode), mbError, MB_OK);
      end;
    end;
  end;
end;

[Icons]
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\lollms.bat"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\lollms.bat"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
