# RetroRewind Trailer Creator

RetroRewind Trailer Creator is a Windows desktop utility for creating custom video channels for **Retro Rewind**. It can download user-requested online videos, trim and convert clips, arrange them in a chosen order, preview the sequence, and generate the game-ready `RR_Channel_Public.mp4` file used by in-game televisions.

## Current version

**14.0.1 — Nexus Mods Edition**

This repository contains the complete application source code, installer definition, build scripts, documentation, and third-party notices required to review and reproduce the Windows release.

## Main features

- User-initiated YouTube downloads through `yt-dlp`
- Video trimming and conversion through FFmpeg
- Separate views for pending and converted clips
- Thumbnail generation and built-in preview playback
- Ordering and previewing a complete Game Video sequence
- Generation of `RR_Channel_Public.mp4`
- Multiple VCR-inspired themes
- Dutch, English, French, and German interface languages
- Custom and Steam game-folder support

## Security and network behaviour

- The application performs **no automatic update checks**.
- It performs **no background network requests**.
- Network access occurs only when the user explicitly starts a YouTube download.
- It does not inject into, patch, or modify the Retro Rewind executable.
- It does not install drivers or services.
- It does not collect analytics, telemetry, credentials, or personal information.
- FFmpeg is started locally for media processing.

More details are available in [SECURITY.md](SECURITY.md) and [NEXUS_REVIEW.md](NEXUS_REVIEW.md).

## Building

See [BUILD.md](BUILD.md) for complete Windows build instructions.

The normal build creates:

```text
release/RetroRewind Trailer Creator Setup V14.0.1.exe
release/RetroRewind Trailer Creator V14.0.1 Nexus Edition.zip
```

End users do not need Python, PowerShell, or Inno Setup. These are required only on the development computer that builds the installer.

## Repository structure

```text
src/          Application source code
assets/       Application icon and artwork
docs/         User manual, screenshots, and archived change logs
installer/    Inno Setup installer definition
scripts/      Windows release build script
tools/        Instructions for supplying FFmpeg
licenses/     Application and third-party notices
```

## Third-party projects

- [FFmpeg](https://ffmpeg.org/) — media decoding, conversion, thumbnails, and preview processing
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — user-initiated online video downloads
- [PyInstaller](https://pyinstaller.org/) — Windows application packaging
- [Inno Setup](https://jrsoftware.org/isinfo.php) — Windows installer creation
- Python, Tkinter, and pywin32

See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.

## License

The project source code is provided under the MIT License. See [LICENSE](LICENSE).

Retro Rewind and related names belong to their respective owners. This project is an unofficial community utility and is not affiliated with the game developers or publishers.
