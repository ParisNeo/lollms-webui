[Setup]
AppName=L🪶LLMS
AppVersion=1.0
DefaultDirName={pf}\L🪶LLMS
DefaultGroupName=L🪶LLMS
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "lollmsenv_installer.bat"; DestDir: "{app}"; Flags: external

[Code]
const
  LollmsEnvInstallerUrl = 'https://github.com/ParisNeo/LollmsEnv/releases/download/V1.2.13/lollmsenv_installer.bat';

function DownloadFile(Url, FileName: string): Boolean;
var
  ResultCode: Integer;
begin
  if not FileExists(FileName) then
  begin
    Result := True;
    if not Exec(ExpandConstant('{sys}\powershell.exe'),
        Format('-Command "Invoke-WebRequest -Uri ''{0}'' -OutFile ''{1}''"', [Url, FileName]),
        '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := False;
    end;
  end
  else
    Result := True;
end;

procedure InstallLollmsEnv;
var
  ResultCode: Integer;
begin
  if Exec(ExpandConstant('{app}\lollmsenv_installer.bat'), 
      '--dir "' + ExpandConstant('{app}\lollmsenv') + '" -y', 
      '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
  begin
    // LollmsEnv installed successfully
  end
  else
  begin
    MsgBox('Failed to install LollmsEnv', mbError, MB_OK);
  end;
end;

procedure CreatePythonEnvironment;
var
  ResultCode: Integer;
begin
  if Exec(ExpandConstant('{app}\lollmsenv\bin\lollmsenv.bat'), 
      'create-env lollms_env', 
      '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
  begin
    // Python environment created successfully
  end
  else
  begin
    MsgBox('Failed to create Python environment', mbError, MB_OK);
  end;
end;

// Add more procedures for other installation steps...

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then 
  begin
    if DownloadFile(LollmsEnvInstallerUrl, ExpandConstant('{app}\lollmsenv_installer.bat')) then
    begin
      InstallLollmsEnv;
      CreatePythonEnvironment;
      // Call other installation procedures...
    end
    else
    begin
      MsgBox('Failed to download LollmsEnv installer', mbError, MB_OK);
    end;
  end;
end;

[Run]
Filename: "{app}\lollms.bat"; Description: "Run L🪶LLMS"; Flags: postinstall nowait skipifsilent