$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.Windows.Forms

$Root = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$AppName = "RetroRewind Trailer Creator"
$AppVersion = "14.0.1"
$BuildRoot = Join-Path $Root "build"
$DistRoot = Join-Path $BuildRoot "dist"
$WorkRoot = Join-Path $BuildRoot "pyinstaller-work"
$SpecRoot = Join-Path $BuildRoot "spec"
$AppBuildDir = Join-Path $DistRoot $AppName
$ReleaseDir = Join-Path $Root "release"
$EntryFile = Join-Path $Root "src\app.py"
$IconFile = Join-Path $Root "assets\RetroRewind Trailer Creator.ico"
$AssetsDir = Join-Path $Root "assets"
$ToolsDir = Join-Path $Root "tools"
$InstallerScript = Join-Path $Root "installer\RetroRewind_Trailer_Creator.iss"
$RequirementsFile = Join-Path $Root "requirements-build.txt"
$FFmpegFile = Join-Path $ToolsDir "ffmpeg.exe"
$SetupFile = Join-Path $ReleaseDir "RetroRewind Trailer Creator Setup V14.0.1.exe"
$NexusDir = Join-Path $ReleaseDir "Nexus Mods Upload V14.0.1"
$NexusZip = Join-Path $ReleaseDir "RetroRewind Trailer Creator V14.0.1 Nexus Edition.zip"

function Show-Dialog {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $true)][System.Windows.Forms.MessageBoxIcon]$Icon,
        [System.Windows.Forms.MessageBoxButtons]$Buttons = [System.Windows.Forms.MessageBoxButtons]::OK
    )

    $owner = New-Object System.Windows.Forms.Form
    $owner.TopMost = $true
    $owner.ShowInTaskbar = $false
    $owner.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $owner.Size = New-Object System.Drawing.Size(1, 1)
    $owner.Opacity = 0
    $owner.Show()
    $owner.Activate()
    try {
        return [System.Windows.Forms.MessageBox]::Show($owner, $Message, $AppName, $Buttons, $Icon)
    }
    finally {
        $owner.Close()
        $owner.Dispose()
    }
}

function Stop-WithError {
    param([Parameter(Mandatory = $true)][string]$Message)
    [void](Show-Dialog -Message $Message -Icon ([System.Windows.Forms.MessageBoxIcon]::Error))
    exit 1
}

function Show-Information {
    param([Parameter(Mandatory = $true)][string]$Message)
    [void](Show-Dialog -Message $Message -Icon ([System.Windows.Forms.MessageBoxIcon]::Information))
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Description
    )

    Write-Host $Description -ForegroundColor Cyan
    & $Executable @Arguments
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) { $exitCode = 0 }
    if ($exitCode -ne 0) {
        throw "$Description is mislukt (foutcode $exitCode)."
    }
}

function Find-Python {
    $py = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($py) {
        return @{ Executable = $py.Source; Prefix = @("-3") }
    }

    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($python) {
        return @{ Executable = $python.Source; Prefix = @() }
    }

    return $null
}

function Find-InnoCompiler {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 7\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 7\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }

    return $candidates | Select-Object -First 1
}

try {
    foreach ($requiredFile in @($EntryFile, $IconFile, $InstallerScript, $RequirementsFile, $FFmpegFile)) {
        if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
            throw "Verplicht bestand ontbreekt: $requiredFile"
        }
    }
    foreach ($requiredDirectory in @($AssetsDir, $ToolsDir)) {
        if (-not (Test-Path -LiteralPath $requiredDirectory -PathType Container)) {
            throw "Verplichte map ontbreekt: $requiredDirectory"
        }
    }

    $python = Find-Python
    if (-not $python) {
        throw "Python is alleen nodig op deze ontwikkelcomputer om de definitieve Setup.exe te bouwen. Installeer Python 3 en activeer de optie Add Python to PATH."
    }

    New-Item -ItemType Directory -Force -Path $BuildRoot, $ReleaseDir | Out-Null
    foreach ($directory in @($DistRoot, $WorkRoot, $SpecRoot)) {
        if (Test-Path -LiteralPath $directory) {
            Remove-Item -LiteralPath $directory -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    foreach ($releaseFile in @($SetupFile, $NexusZip)) {
        if (Test-Path -LiteralPath $releaseFile) { Remove-Item -LiteralPath $releaseFile -Force }
    }

    $pipArguments = @($python.Prefix) + @(
        "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "-r", $RequirementsFile
    )
    Invoke-CheckedCommand -Executable $python.Executable -Arguments $pipArguments -Description "Benodigdheden voor de releasebuilder controleren en installeren..."

    $addAssets = "$AssetsDir;assets"
    $addTools = "$ToolsDir;tools"
    $pyInstallerArguments = @($python.Prefix) + @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--optimize", "2",
        "--name", $AppName,
        "--icon", $IconFile,
        "--add-data", $addAssets,
        "--add-data", $addTools,
        "--hidden-import", "yt_dlp",
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        "--hidden-import", "pywintypes",
        "--workpath", $WorkRoot,
        "--distpath", $DistRoot,
        "--specpath", $SpecRoot,
        $EntryFile
    )
    Invoke-CheckedCommand -Executable $python.Executable -Arguments $pyInstallerArguments -Description "Zelfstandige Windows-applicatie bouwen..."

    $builtExe = Join-Path $AppBuildDir "$AppName.exe"
    if (-not (Test-Path -LiteralPath $builtExe -PathType Leaf)) {
        $possibleExe = Get-ChildItem -LiteralPath $DistRoot -Filter "$AppName.exe" -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($possibleExe) {
            $AppBuildDir = $possibleExe.Directory.FullName
            $builtExe = $possibleExe.FullName
        }
        else {
            throw "PyInstaller meldde een geslaagde build, maar de applicatie werd niet gevonden in: $DistRoot"
        }
    }

    Write-Host "Gebouwde applicatie gevonden: $builtExe" -ForegroundColor Green

    $iscc = Find-InnoCompiler
    if (-not $iscc) {
        $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue
        if ($winget) {
            $answer = Show-Dialog `
                -Message "Inno Setup is nodig om de definitieve Setup.exe te maken. Wilt u Inno Setup nu automatisch installeren?" `
                -Icon ([System.Windows.Forms.MessageBoxIcon]::Question) `
                -Buttons ([System.Windows.Forms.MessageBoxButtons]::YesNo)

            if ($answer -ne [System.Windows.Forms.DialogResult]::Yes) {
                throw "Inno Setup werd niet geïnstalleerd."
            }

            Invoke-CheckedCommand -Executable $winget.Source -Arguments @(
                "install", "--id", "JRSoftware.InnoSetup", "-e", "-s", "winget",
                "--accept-package-agreements", "--accept-source-agreements", "--silent"
            ) -Description "Inno Setup installeren..."
            $iscc = Find-InnoCompiler
        }
    }

    if (-not $iscc) {
        Start-Process "https://jrsoftware.org/isdl.php"
        throw "Inno Setup kon niet automatisch worden gevonden. Installeer Inno Setup 6 en start daarna MAAK DEFINITIEVE SETUP.bat opnieuw."
    }

    $innoArguments = @(
        "/Qp",
        "/DSourceDir=$AppBuildDir",
        "/DOutputDir=$ReleaseDir",
        "/DAppVersion=$AppVersion",
        $InstallerScript
    )
    Invoke-CheckedCommand -Executable $iscc -Arguments $innoArguments -Description "Professionele Setup.exe maken..."


    if (-not (Test-Path -LiteralPath $SetupFile -PathType Leaf)) {
        $foundSetup = Get-ChildItem -LiteralPath $ReleaseDir -Filter "*Setup*.exe" -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($foundSetup) {
            $SetupFile = $foundSetup.FullName
        }
        else {
            throw "Inno Setup werd uitgevoerd, maar de definitieve Setup.exe werd niet gevonden in: $ReleaseDir"
        }
    }

    if (Test-Path -LiteralPath $NexusDir) { Remove-Item -LiteralPath $NexusDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $NexusDir | Out-Null
    Copy-Item -LiteralPath $SetupFile -Destination $NexusDir -Force
    Copy-Item -LiteralPath (Join-Path $Root "NEXUS_README.txt") -Destination $NexusDir -Force
    Copy-Item -LiteralPath (Join-Path $Root "docs\CHANGELOG_V14_0_1.txt") -Destination $NexusDir -Force
    Copy-Item -LiteralPath (Join-Path $Root "licenses") -Destination $NexusDir -Recurse -Force
    if (Test-Path -LiteralPath $NexusZip) { Remove-Item -LiteralPath $NexusZip -Force }
    Compress-Archive -Path (Join-Path $NexusDir "*") -DestinationPath $NexusZip -CompressionLevel Optimal

    Start-Process "explorer.exe" -ArgumentList "`"$ReleaseDir`""
    Show-Information "De Nexus Mods Edition is klaar.`r`n`r`nSetup:`r`n$SetupFile`r`n`r`nNexus-upload:`r`n$NexusZip`r`n`r`nDe eindgebruiker heeft geen Python, BAT, PowerShell of aparte updater nodig."
    exit 0
}
catch {
    $message = $_.Exception.Message
    Write-Host "" 
    Write-Host "FOUT: $message" -ForegroundColor Red
    Stop-WithError "Het maken van de Setup.exe is mislukt.`r`n`r`n$message"
}
