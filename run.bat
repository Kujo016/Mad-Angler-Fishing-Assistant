@echo off

REM Change directory to the location of the currently running .bat file
cd /d %~dp0

REM Now call python on initGUI.py (which is presumably in this same directory)
python initGUI.py

pause
