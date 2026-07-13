# FFmpeg build dependency

Place a trusted 64-bit Windows FFmpeg executable here before building:

`tools\ffmpeg.exe`

The FFmpeg binary used for the reviewed V14.0.1 installer had:

- SHA-256: `f0eda7a02b993403448da15baef9c00b9c882ae03eff9c4df47b5effd91c87ef`
- Size: `102206976 bytes`

The original binary was supplied to the project author. Its exact origin and configuration were not independently verified in this preparation environment. Review `ffmpeg.exe -version` and comply with the applicable FFmpeg license before distribution.

The binary is intentionally ignored by Git in this source package because it is third-party software and may exceed convenient browser-upload limits. It may be added through Git LFS or supplied separately during the build review.
