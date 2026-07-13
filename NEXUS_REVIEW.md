# Nexus Mods security review notes

This document is intended to help Nexus Mods moderators review RetroRewind Trailer Creator V14.0.1.

## Purpose

The utility creates custom video content for the televisions inside Retro Rewind. Its primary output is:

```text
RR_Channel_Public.mp4
```

## Network access

The application imports `yt-dlp` and performs network access only after the user explicitly enters a URL and starts a download. There is no automatic update service, analytics, telemetry, advertising, or background connection.

## External processes

The application executes the bundled/local `ffmpeg.exe` for:

- media inspection;
- thumbnail extraction;
- trimming and conversion;
- preview frame/audio generation;
- merging clips into the final Game Video.

The command construction is visible in `src/app.py`. FFmpeg is not downloaded or replaced by the running application.

## Files written by the application

The application writes only:

- application settings;
- user-requested downloads;
- converted video files;
- generated Game Video files;
- temporary preview files;
- optional shortcuts requested by the user.

The application does not alter the Retro Rewind executable. It can copy or save the generated MP4 into the configured game media directory.

## Installer

The Windows installer is defined in:

```text
installer/RetroRewind_Trailer_Creator.iss
```

It installs the PyInstaller onedir output, creates optional shortcuts, creates writable media directories, and starts the application once to apply the chosen language/media-root configuration.

## Build process

The authoritative build steps are documented in `BUILD.md`. The process uses:

- Python;
- PyInstaller in onedir mode without UPX;
- Inno Setup 6.

The Nexus upload contains no standalone updater and the application contains no automatic update checker.

## Source transparency

No source obfuscation or source-protection step is included in this repository. The complete application logic is available in `src/app.py`.
