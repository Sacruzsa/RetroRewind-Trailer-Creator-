# Third-party software and licenses

RetroRewind Trailer Creator uses the following third-party projects. Their inclusion or use does not imply endorsement.

## FFmpeg

Website: https://ffmpeg.org/

FFmpeg is used for media inspection, trimming, conversion, thumbnail extraction, preview processing, and merging. FFmpeg builds can be licensed under LGPL 2.1-or-later or GPL 2-or-later depending on their configuration.

The repository does not treat `ffmpeg.exe` as original project source. Review the exact build with:

```cmd
ffmpeg.exe -version
```

Distributors must comply with the license and source-offer requirements applicable to the specific FFmpeg build they ship.

## yt-dlp

Repository: https://github.com/yt-dlp/yt-dlp

The Python package is installed as a build/runtime dependency and is used only for user-initiated video downloads. yt-dlp is distributed under The Unlicense.

## PyInstaller

Website: https://pyinstaller.org/

PyInstaller packages the Python application into a Windows onedir distribution. PyInstaller is GPL-licensed with an exception that permits distribution of bundled applications under other licenses.

## Inno Setup

Website: https://jrsoftware.org/isinfo.php

Inno Setup creates the Windows installer. Its license is published by the Inno Setup project.

## Python and Tkinter

Website: https://www.python.org/

Python is distributed under the Python Software Foundation License. Tkinter uses the Tcl/Tk components supplied with Python.

## pywin32

Repository: https://github.com/mhammond/pywin32

pywin32 is used for optional Windows integration such as shortcut and mail-client handling. See the project repository for its license notices.
