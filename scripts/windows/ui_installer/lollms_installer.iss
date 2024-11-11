#define MyAppName "LOLLMS"
#define MyAppVersion "14.0"
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
DefaultDirName={userdocs}\lollms_webui
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
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\logo.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "runafterinstall"; Description: "Run LOLLMS after installation"

[Files]
Source: "lollmsenv_installer.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\lollms.bat"; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\lollms.bat"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon
Name: "{autoprograms}\{#MyAppName} CMD"; Filename: "{app}\lollms_cmd.bat"; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\{#MyAppName} CMD"; Filename: "{app}\lollms_cmd.bat"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\lollmsenv_installer.bat"; Parameters: "--dir ""{app}\lollmsenv"" -y"; StatusMsg: "Installing LollmsEnv..."; Flags: runhidden
Filename: "{app}\lollmsenv\bin\lollmsenv.bat"; Parameters: "create-env lollms_env"; StatusMsg: "Creating Python environment..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\activate.bat"; StatusMsg: "Activating Python environment..."; Flags: runhidden
Filename: "git"; Parameters: "clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git ""{app}\lollms-webui"""; StatusMsg: "Cloning LOLLMS repository..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -r ""{app}\lollms-webui\requirements.txt"""; StatusMsg: "Installing Python requirements..."; Flags: runhidden
Filename: "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe"; Parameters: "-m pip install -e ""{app}\lollms-webui\lollms_core"""; StatusMsg: "Installing LOLLMS core..."; Flags: runhidden
Filename: "{app}\lollms.bat"; Description: "Run LOLLMS"; Flags: postinstall nowait skipifsilent; Tasks: runafterinstall

[UninstallDelete]
Type: files; Name: "{app}\lollms.bat"
Type: files; Name: "{app}\lollms_cmd.bat"
Type: filesandordirs; Name: "{app}\lollmsenv"
Type: filesandordirs; Name: "{app}\lollms-webui"
Type: filesandordirs; Name: "{app}\lollmsenv_install"

[Code]
var
  BindingPage: TInputOptionWizardPage;
  PersonalFolderPage: TInputDirWizardPage;

function IsGitInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('git', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure CreateGitDownloadBat;
var
  BatContent: string;
begin
  BatContent := 
    '@echo off' + #13#10 +
    'echo Downloading Git installer...' + #13#10 +
    'powershell -Command "& {Invoke-WebRequest -Uri ''https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.2/Git-2.35.1.2-64-bit.exe'' -OutFile ''%TEMP%\GitInstaller.exe''}"' + #13#10 +
    'if %ERRORLEVEL% neq 0 (' + #13#10 +
    '    echo Failed to download Git installer.' + #13#10 +
    '    exit /b 1' + #13#10 +
    ')' + #13#10 +
    'echo Installing Git...' + #13#10 +
    'start /wait %TEMP%\GitInstaller.exe /VERYSILENT /NORESTART' + #13#10 +
    'if %ERRORLEVEL% neq 0 (' + #13#10 +
    '    echo Failed to install Git.' + #13#10 +
    '    exit /b 1' + #13#10 +
    ')' + #13#10 +
    'echo Git installed successfully.' + #13#10 +
    'exit /b 0';
  
  SaveStringToFile(ExpandConstant('{tmp}\DownloadAndInstallGit.bat'), BatContent, False);
end;

function DownloadAndInstallGit: Boolean;
var
  ResultCode: Integer;
begin
  CreateGitDownloadBat;
  
  if MsgBox('Git is not installed on your system. Do you want to install it now?', mbConfirmation, MB_YESNO) = IDYES then
  begin
    if Exec(ExpandConstant('{tmp}\DownloadAndInstallGit.bat'), '', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := (ResultCode = 0);
      if not Result then
        MsgBox('Failed to install Git. Please install it manually and restart the setup.', mbError, MB_OK);
    end
    else
    begin
      MsgBox('Failed to run the Git installer. Please install Git manually and restart the setup.', mbError, MB_OK);
      Result := False;
    end;
  end
  else
  begin
    MsgBox('Git is required for this installation. The setup will now exit.', mbInformation, MB_OK);
    Result := False;
  end;
end;

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

  PersonalFolderPage := CreateInputDirPage(BindingPage.ID,
    'Select Personal Folder', 'Choose where to store your personal data',
    'Select the folder in which to store your personal data, then click Next.',
    False, '');
  PersonalFolderPage.Add('');
  PersonalFolderPage.Values[0] := ExpandConstant('{userdocs}\lollms_personal');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  BindingScript: string;
  YamlContent: string;
  PersonalFolder: string;
begin
  if CurStep = ssInstall then
  begin
    if not IsGitInstalled then
    begin
      if not DownloadAndInstallGit then
        Abort;
    end;
  end;
  
  if CurStep = ssPostInstall then
  begin
    PersonalFolder := PersonalFolderPage.Values[0];
    if not DirExists(PersonalFolder) then
       ForceDirectories(PersonalFolder);
    
    // Create global_paths_cfg.yaml file
    YamlContent := 'lollms_path: ' + ExpandConstant('{app}\lollms-webui\lollms_core\lollms') + #13#10 +
                   'lollms_personal_path: ' + PersonalFolder ;
    SaveStringToFile(ExpandConstant('{app}\lollms-webui\global_paths_cfg.yaml'), YamlContent, False);

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
      // Execute the binding script in the correct directory
      Exec(ExpandConstant('{cmd}'),
           ExpandConstant('/c "cd /d "{app}\lollms-webui" && "{app}\lollmsenv\envs\lollms_env\Scripts\python.exe" "zoos\bindings_zoo\' + BindingScript + '\__init__.py""'),
           '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;

    SaveStringToFile(ExpandConstant('{app}\lollms.bat'),
      '@echo off' + #13#10 +
      'call "lollmsenv\envs\lollms_env\Scripts\activate.bat"' + #13#10 +
      'cd /d "lollms-webui"' + #13#10 +
      'python app.py %*' + #13#10 +
      'pause', False);

    SaveStringToFile(ExpandConstant('{app}\lollms_cmd.bat'),
      '@echo off' + #13#10 +
      'call "lollmsenv\envs\lollms_env\Scripts\activate.bat"' + #13#10 +
      'cd /d "lollms-webui"' + #13#10 +
      'cmd /k', False);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  PersonalFolder: string;
  YamlFilePath: string;
  YamlContent: TStringList;
  I: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Read the personal folder path from the YAML file
    YamlFilePath := ExpandConstant('{app}\lollms-webui\global_paths_cfg.yaml');
    if FileExists(YamlFilePath) then
    begin
      YamlContent := TStringList.Create;
      try
        YamlContent.LoadFromFile(YamlFilePath);
        for I := 0 to YamlContent.Count - 1 do
        begin
          if Pos('lollms_personal_path:', YamlContent[I]) = 1 then
          begin
            PersonalFolder := Trim(Copy(YamlContent[I], Length('lollms_personal_path:') + 1, MaxInt));
            // Remove surrounding quotes if present
            if (Length(PersonalFolder) > 1) and (PersonalFolder[1] = '"') and (PersonalFolder[Length(PersonalFolder)] = '"') then
              PersonalFolder := Copy(PersonalFolder, 2, Length(PersonalFolder) - 2);
            Break;
          end;
        end;
      finally
        YamlContent.Free;
      end;
    end;

    if PersonalFolder <> '' then
    begin
      if MsgBox('Do you want to remove your personal data?' + #13#10 +
                'WARNING: Your personal folder contains all your personal information and discussions with LOLLMS.' + #13#10 +
                'If you choose Yes, this data will be permanently deleted.' + #13#10 +
                'If you choose No, your personal data will be kept for future use.' + #13#10#13#10 +
                'Personal data folder: ' + PersonalFolder + #13#10#13#10 +
                'Do you want to delete this folder?', 
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        if DelTree(PersonalFolder, True, True, True) then
          Log('Personal data folder deleted: ' + PersonalFolder)
        else
          Log('Failed to delete personal data folder: ' + PersonalFolder);
      end
      else
      begin
        MsgBox('Your personal data has been kept at: ' + PersonalFolder, mbInformation, MB_OK);
      end;
    end;
  end;
end;
