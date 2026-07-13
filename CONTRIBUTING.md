# Contributing

Contributions that improve reliability, accessibility, translations, documentation, and compatibility are welcome.

## Development setup

1. Follow `BUILD.md` through the virtual-environment and dependency-installation steps.
2. Make focused changes in a separate Git branch.
3. Run the syntax check:

```powershell
python -m py_compile src\app.py
```

4. Test downloading, conversion, preview, clip ordering, final video generation, language changes, theme changes, and settings persistence on Windows.
5. Do not add automatic update checks, telemetry, hidden network requests, obfuscated code, or bundled executables without documenting their origin and license.

## Pull requests

Explain:

- what changed;
- why it changed;
- how it was tested;
- whether network, file-system, subprocess, installer, or third-party dependency behaviour changed.
