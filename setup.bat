@echo off
REM *************************************************************
REM install_python_and_libs.bat
REM
REM This script checks if Python is installed. If not, it downloads
REM and installs Python silently, then installs or upgrades
REM the required libraries via pip.
REM *************************************************************

echo Checking if Python is installed...
python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading the Python installer...
    powershell -Command "Start-BitsTransfer -Source https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe -Destination python-installer.exe"
    
    IF EXIST python-installer.exe (
        echo Installing Python 3.11.2 (silent mode)...
        start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        del python-installer.exe
    ) ELSE (
        echo Failed to download the Python installer. Exiting.
        exit /b 1
    )
) ELSE (
    echo Python is already installed.
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required libraries...
python -m pip install --upgrade ^
    pytz ^
    requests ^
    geocoder ^
    pandas ^
    matplotlib ^
    pillow ^
    tzlocal

echo.
echo Installation complete!
echo Press any key to exit.
pause >nul
