# Security policy

## Supported version

Security reports currently apply to version 14.0.1 and later releases derived from this repository.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the project maintainer rather than publishing exploit details in a public issue. Include:

- affected version;
- reproduction steps;
- relevant files or logs;
- expected and observed behaviour;
- potential impact.

## Application behaviour

RetroRewind Trailer Creator:

- does not collect telemetry or analytics;
- does not access stored browser credentials;
- does not install services, drivers, browser extensions, or scheduled tasks;
- does not inject into or patch game processes;
- does not perform automatic update checks;
- does not contact a server in the background;
- accesses the internet only after the user starts a video download;
- starts FFmpeg locally for media processing;
- writes only to user-selected media folders, application settings locations, temporary preview files, and the selected Retro Rewind video location.

## Antivirus and quarantine notices

Unsigned applications built with PyInstaller or packaged with media-downloading and conversion tools can trigger heuristic antivirus detections. Such a detection must not automatically be treated as proof of malicious code, but it should always be investigated.

Reviewers can inspect the complete source, reproduce the build using `BUILD.md`, compare hashes, and independently scan the resulting files.
