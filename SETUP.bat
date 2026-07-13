@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Open de builder in een blijvend opdrachtvenster zodat fouten zichtbaar blijven.
if /I not "%~1"=="--build" (
    start "RetroRewind Setup Builder" cmd.exe /k ""%~f0" --build"
    exit /b 0
)

cd /d "%~dp0"
title RetroRewind Trailer Creator V14.0.1 - Nexus Setup Builder
set "LOGFILE=%~dp0BUILD_SETUP_LOG.txt"

>"%LOGFILE%" echo RetroRewind Trailer Creator V14.0.1 - buildlog
>>"%LOGFILE%" echo Gestart: %date% %time%
>>"%LOGFILE%" echo Projectmap: %CD%
>>"%LOGFILE%" echo.

cls
echo ================================================================
echo  RetroRewind Trailer Creator V14.0.1
echo  Nexus Mods Edition - Setup.exe bouwen
echo ================================================================
echo.
echo Het venster blijft open. Volledige details staan in:
echo %LOGFILE%
echo.

echo [1/5] Projectbestanden controleren...
call :require_file "tools\ffmpeg.exe" "FFmpeg ontbreekt"
if errorlevel 1 goto :failed
call :require_file "src\app.py" "De Python-broncode ontbreekt"
if errorlevel 1 goto :failed
call :require_file "scripts\build_final_setup.ps1" "Het PowerShell-buildscript ontbreekt"
if errorlevel 1 goto :failed
call :require_file "installer\RetroRewind_Trailer_Creator.iss" "Het Inno Setup-script ontbreekt"
if errorlevel 1 goto :failed
call :require_file "requirements-build.txt" "Het dependency-bestand ontbreekt"
if errorlevel 1 goto :failed
call :require_file "tools\ffmpeg.exe" "FFmpeg ontbreekt. Lees tools\README.md"
if errorlevel 1 goto :failed

rem De Nexus Edition heeft bewust GEEN RetroRewind_Trailer_Creator_Update.iss.
rem De volledige installer kan ook over een bestaande installatie heen updaten.

echo [2/5] Python zoeken...
where py.exe >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python.exe >nul 2>&1
    if errorlevel 1 goto :missing_python
    set "PYTHON_CMD=python"
)

echo Gevonden: !PYTHON_CMD!
>>"%LOGFILE%" echo Python-opdracht: !PYTHON_CMD!

echo [3/5] Python-broncode controleren...
call !PYTHON_CMD! -m py_compile "src\app.py" >>"%LOGFILE%" 2>&1
if errorlevel 1 goto :source_error

echo [4/5] Setup-builder starten...
echo Dit kan enkele minuten duren. Benodigdheden kunnen automatisch worden geinstalleerd.
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_final_setup.ps1" >>"%LOGFILE%" 2>&1
set "BUILD_RESULT=%ERRORLEVEL%"
if not "%BUILD_RESULT%"=="0" goto :build_error

echo [5/5] Build voltooid.
echo.
echo ================================================================
echo  KLAAR
echo ================================================================
echo De bestanden staan in:
echo %~dp0release
echo.
echo Upload naar Nexus uitsluitend:
echo release\RetroRewind Trailer Creator V14.0.1 Nexus Edition.zip
echo.
>>"%LOGFILE%" echo.
>>"%LOGFILE%" echo Build voltooid: %date% %time%
start "" explorer.exe "%~dp0release"
pause
exit /b 0

:require_file
if exist "%~1" exit /b 0
echo FOUT: %~2: %~1
echo FOUT: %~2: %~1>>"%LOGFILE%"
exit /b 1

:missing_python
echo.
echo FOUT: Python 3 werd niet gevonden op deze buildcomputer.
echo Installeer Python 3 en vink tijdens de installatie "Add Python to PATH" aan.
echo De uiteindelijke Setup.exe vereist geen Python bij gebruikers.
>>"%LOGFILE%" echo FOUT: Python 3 werd niet gevonden.
goto :failed

:source_error
echo.
echo FOUT: src\app.py kon niet worden gecontroleerd.
echo Bekijk BUILD_SETUP_LOG.txt voor details.
>>"%LOGFILE%" echo FOUT: Python-broncontrole mislukt.
goto :failed

:build_error
echo.
echo FOUT: De Setup-build is mislukt met foutcode %BUILD_RESULT%.
echo Bekijk BUILD_SETUP_LOG.txt voor de volledige foutmelding.
>>"%LOGFILE%" echo FOUT: Setup-build mislukt met foutcode %BUILD_RESULT%.
goto :failed

:failed
echo.
echo ================================================================
echo  BUILD NIET VOLTOOID
echo ================================================================
echo Logbestand:
echo %LOGFILE%
echo.
echo Druk op een toets om het venster te sluiten.
pause >nul
exit /b 1
