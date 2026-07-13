# Build instructions

These instructions reproduce the Windows Nexus Mods Edition from the source repository.

## Supported build environment

- Windows 10 or Windows 11, 64-bit
- Python 3.11 or newer, 64-bit
- PowerShell 5.1 or newer
- Inno Setup 6
- Internet access while installing Python build dependencies
- A trusted Windows 64-bit FFmpeg build placed at `tools\ffmpeg.exe`

The finished application and installer do not require Python on the end user's computer.

## 1. Clone or download the source

Using Git:

```powershell
git clone https://github.com/YOUR-USERNAME/RetroRewind-Trailer-Creator.git
cd RetroRewind-Trailer-Creator
```

Alternatively, download the repository ZIP from GitHub and extract it completely.

## 2. Install Python

Install 64-bit Python from python.org. During installation, enable **Add Python to PATH**.

Verify it:

```powershell
py -3 --version
```

or:

```powershell
python --version
```

## 3. Create an isolated build environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
```

If PowerShell script execution is restricted, activate from Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

## 4. Supply FFmpeg

This repository does not present the third-party FFmpeg binary as project source code. Download a trusted Windows 64-bit FFmpeg build and copy the executable to:

```text
tools\ffmpeg.exe
```

The FFmpeg binary included in the reviewed V14.0.1 build had this SHA-256 digest:

```text
f0eda7a02b993403448da15baef9c00b9c882ae03eff9c4df47b5effd91c87ef
```

File size:

```text
102206976 bytes
```

The original binary was supplied to the project author. Its exact distributor and build configuration must be checked independently using:

```cmd
tools\ffmpeg.exe -version
```

The application checks for `tools\ffmpeg.exe` before building.

## 5. Install Inno Setup

Install Inno Setup 6 from its official website. The builder searches the common installation locations automatically.

Verify that this file exists, or an equivalent Inno Setup 6 installation is available:

```text
C:\Program Files (x86)\Inno Setup 6\ISCC.exe
```

## 6. Build the release

From the repository root, run:

```cmd
MAAK DEFINITIEVE SETUP.bat
```

The script performs these steps:

1. Checks the source tree and Python syntax.
2. Installs or verifies packages from `requirements-build.txt`.
3. Builds a PyInstaller **onedir** application without UPX.
4. Packages the application using Inno Setup.
5. Creates a Nexus-ready ZIP containing the installer and documentation.
6. Writes build output to `BUILD_SETUP_LOG.txt`.

## 7. Expected output

```text
release\RetroRewind Trailer Creator Setup V14.0.1.exe
release\RetroRewind Trailer Creator V14.0.1 Nexus Edition.zip
```

## Manual build commands

The release script is the authoritative process. For inspection, the equivalent core PyInstaller command is approximately:

```powershell
python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onedir `
  --optimize 2 `
  --name "RetroRewind Trailer Creator" `
  --icon "assets\RetroRewind Trailer Creator.ico" `
  --add-data "assets;assets" `
  --add-data "tools;tools" `
  --hidden-import yt_dlp `
  --hidden-import win32com.client `
  --hidden-import pythoncom `
  --hidden-import pywintypes `
  src\app.py
```

The resulting onedir application is then passed to:

```cmd
ISCC.exe /DSourceDir="<built-app-directory>" /DOutputDir="<release-directory>" /DAppVersion=14.0.1 installer\RetroRewind_Trailer_Creator.iss
```

## Verification

Before distribution:

```powershell
python -m py_compile src\app.py
Get-FileHash "release\RetroRewind Trailer Creator Setup V14.0.1.exe" -Algorithm SHA256
```

For a clean reproducibility test, delete `build`, `release`, and `.venv`, then repeat the steps above on a clean Windows virtual machine.
