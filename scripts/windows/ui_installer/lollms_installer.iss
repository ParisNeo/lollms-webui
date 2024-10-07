#define MyAppName "LOLLMS"
#define MyAppVersion "13.0"
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
DefaultDirName={userpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=.
OutputBaseFilename=lollms_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "lollmsenv_installer.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\lollms.bat"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\lollms.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\lollmsenv_installer.bat"; Parameters: "--dir ""{app}\lollmsenv"" -y"; StatusMsg: "Installing LollmsEnv..."; Flags: runhidden
Filename: "{app}\lollmsenv\bin\lollmsenv.bat"; Parameters: "create-env lollms_env"; StatusMsg: "Creating Python environment..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\activate.bat"; StatusMsg: "Activating Python environment..."; Flags: runhidden
Filename: "git"; Parameters: "clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git ""{app}\lollms-webui"""; StatusMsg: "Cloning LOLLMS repository..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -r ""{app}\lollms-webui\requirements.txt"""; StatusMsg: "Installing Python requirements..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -e ""{app}\lollms-webui\lollms_core"""; StatusMsg: "Installing LOLLMS core..."; Flags: runhidden

[Code]
var
  BindingPage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  BindingPage := CreateInputOptionPage(wpSelectDir,
    'Select Binding', 'Choose the default binding to install',
    'Please select one of the following bindings:',
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
  BindingPage.SelectedValueIndex := 0;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  BindingScript: string;
begin
  if CurStep = ssPostInstall then
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
      Exec(ExpandConstant('{app}\lollmsenv\envs\lollms_env\Scripts\python.exe'),
           ExpandConstant('"{app}\lollms-webui\zoos\bindings_zoo\' + BindingScript + '\__init__.py"'),
           '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;

    SaveStringToFile(ExpandConstant('{app}\lollms.bat'),
      '@echo off' + #13#10 +
      'call "' + ExpandConstant('{app}') + '\lollmsenv\envs\lollms_env\Scripts\activate.bat"' + #13#10 +
      'cd "' + ExpandConstant('{app}') + '\lollms-webui"' + #13#10 +
      'python app.py %*' + #13#10 +
      'pause', False);

    SaveStringToFile(ExpandConstant('{app}\lollms_cmd.bat'),
      '@echo off' + #13#10 +
      'call "' + ExpandConstant('{app}') + '\lollmsenv\envs\lollms_env\Scripts\activate.bat"' + #13#10 +
      'cd "' + ExpandConstant('{app}') + '\lollms-webui"' + #13#10 +
      'cmd /k', False);
  end;
end;
