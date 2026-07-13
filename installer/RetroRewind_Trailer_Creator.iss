#ifndef SourceDir
  #error SourceDir was not supplied by the release builder.
#endif
#ifndef OutputDir
  #error OutputDir was not supplied by the release builder.
#endif
#ifndef AppVersion
  #define AppVersion "14.0.1"
#endif

#define MyAppName "RetroRewind Trailer Creator"
#define MyAppPublisher "RetroRewind"
#define MyAppExeName "RetroRewind Trailer Creator.exe"

[Setup]
; Nexus Mods Edition: one installer, no updater, no background update checks.
AppId={{736C1BCD-40D5-4FB7-AB12-1D4171435E2A}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
AppendDefaultDirName=no
DirExistsWarning=auto
CreateAppDir=yes
OutputDir={#OutputDir}
OutputBaseFilename=RetroRewind Trailer Creator Setup V{#AppVersion}
SetupIconFile=..\assets\RetroRewind Trailer Creator.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
UsePreviousTasks=yes
ChangesAssociations=no
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} installer

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
; Custom installer texts are language-specific, so the complete wizard changes
; immediately when the user selects another setup language.
dutch.MediaPageTitle=Locatie voor videobestanden
dutch.MediaPageDescription=Kies waar downloads, omgezette video's en eindvideo's worden opgeslagen.
dutch.MediaPageSubCaption=Standaard worden de drie mappen in de installatiemap aangemaakt. Kies hier eventueel een andere bovenliggende locatie.
dutch.MediaRootLabel=Bovenliggende locatie:
dutch.NewFolderName=Nieuwe map
dutch.InvalidMediaLocation=Kies een geldige locatie voor de videomappen.
dutch.CannotCreateMediaLocation=De gekozen locatie kon niet worden aangemaakt:

french.MediaPageTitle=Emplacement des fichiers vidéo
french.MediaPageDescription=Choisissez où enregistrer les téléchargements, les vidéos converties et les vidéos finales.
french.MediaPageSubCaption=Par défaut, les trois dossiers sont créés dans le dossier d'installation. Vous pouvez choisir ici un autre dossier parent.
french.MediaRootLabel=Dossier parent :
french.NewFolderName=Nouveau dossier
french.InvalidMediaLocation=Choisissez un emplacement valide pour les dossiers vidéo.
french.CannotCreateMediaLocation=L'emplacement choisi n'a pas pu être créé :

english.MediaPageTitle=Video file location
english.MediaPageDescription=Choose where downloads, converted videos and final videos are stored.
english.MediaPageSubCaption=By default, the three folders are created in the installation folder. You can choose a different parent location here.
english.MediaRootLabel=Parent location:
english.NewFolderName=New folder
english.InvalidMediaLocation=Choose a valid location for the video folders.
english.CannotCreateMediaLocation=The selected location could not be created:

german.MediaPageTitle=Speicherort für Videodateien
german.MediaPageDescription=Wählen Sie, wo Downloads, konvertierte Videos und fertige Videos gespeichert werden.
german.MediaPageSubCaption=Standardmäßig werden die drei Ordner im Installationsordner erstellt. Hier können Sie einen anderen übergeordneten Ordner auswählen.
german.MediaRootLabel=Übergeordneter Speicherort:
german.NewFolderName=Neuer Ordner
german.InvalidMediaLocation=Wählen Sie einen gültigen Speicherort für die Videoordner.
german.CannotCreateMediaLocation=Der ausgewählte Speicherort konnte nicht erstellt werden:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Visible media folders in the selected installation location. The user may
; later choose another parent location for each folder from the application.
Name: "{code:GetDownloadsDir}"; Permissions: users-modify
Name: "{code:GetConvertedDir}"; Permissions: users-modify
Name: "{code:GetFinalDir}"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--set-language={code:GetAppLanguage} --configure-media-root=""{code:GetMediaRoot}"""; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  MediaDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  MediaDirPage := CreateInputDirPage(
    wpSelectDir,
    ExpandConstant('{cm:MediaPageTitle}'),
    ExpandConstant('{cm:MediaPageDescription}'),
    ExpandConstant('{cm:MediaPageSubCaption}'),
    False,
    ExpandConstant('{cm:NewFolderName}'));
  MediaDirPage.Add(ExpandConstant('{cm:MediaRootLabel}'));
  MediaDirPage.Values[0] := WizardDirValue;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = MediaDirPage.ID) and
     ((MediaDirPage.Values[0] = '') or
      (CompareText(MediaDirPage.Values[0], ExpandConstant('{app}')) = 0)) then
    MediaDirPage.Values[0] := WizardDirValue;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  RootDir: String;
begin
  Result := True;
  if CurPageID = MediaDirPage.ID then
  begin
    RootDir := RemoveBackslashUnlessRoot(MediaDirPage.Values[0]);
    if RootDir = '' then
    begin
      MsgBox(ExpandConstant('{cm:InvalidMediaLocation}'), mbError, MB_OK);
      Result := False;
      Exit;
    end;
    if not ForceDirectories(RootDir) then
    begin
      MsgBox(ExpandConstant('{cm:CannotCreateMediaLocation}') + #13#10 + RootDir, mbError, MB_OK);
      Result := False;
      Exit;
    end;
    MediaDirPage.Values[0] := RootDir;
  end;
end;

function GetMediaRoot(Param: String): String;
begin
  if (MediaDirPage <> nil) and (Trim(MediaDirPage.Values[0]) <> '') then
    Result := RemoveBackslashUnlessRoot(MediaDirPage.Values[0])
  else
    Result := ExpandConstant('{app}');
end;

function GetDownloadsDir(Param: String): String;
begin
  Result := AddBackslash(GetMediaRoot('')) + '{#MyAppName} downloads';
end;

function GetConvertedDir(Param: String): String;
begin
  Result := AddBackslash(GetMediaRoot('')) + '{#MyAppName} converted videos';
end;

function GetFinalDir(Param: String): String;
begin
  Result := AddBackslash(GetMediaRoot('')) + '{#MyAppName} final';
end;

function GetAppLanguage(Param: String): String;
var
  SelectedLanguage: String;
begin
  SelectedLanguage := ActiveLanguage;
  if SelectedLanguage = 'french' then
    Result := 'fr'
  else if SelectedLanguage = 'german' then
    Result := 'de'
  else if SelectedLanguage = 'english' then
    Result := 'en'
  else
    Result := 'nl';
end;
