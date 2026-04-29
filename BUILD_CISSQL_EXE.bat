@echo off
rem ============================================================
rem   CISSQL.exe — One-click Windows .exe builder
rem   Produces a SINGLE portable file: CISSQL.exe
rem ============================================================

title Building CISSQL.exe ...
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"
set "APPDIR=%~dp0_app"

echo.
echo  ============================================================
echo    Building CISSQL.exe
echo    Source: %APPDIR%\cis_sql_course.py
echo  ============================================================
echo.

rem -- Find Python ------------------------------------------------------------
set "PYCMD="
where py     >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD (
    where python >nul 2>&1 && set "PYCMD=python"
)
if not defined PYCMD (
    echo  [ERROR] Python is not on your PATH.
    echo          Install from https://www.python.org/downloads/
    pause
    exit /b 1
)
%PYCMD% --version

echo.
echo  [1/4] Installing PyInstaller (silent)...
%PYCMD% -m pip install --upgrade pip                    >nul 2>&1
%PYCMD% -m pip install --upgrade pyinstaller            >nul
if errorlevel 1 (
    echo  [ERROR] Failed to install PyInstaller.
    pause & exit /b 1
)

echo  [2/4] Cleaning previous build folders...
if exist "%APPDIR%\build"           rd /s /q "%APPDIR%\build"
if exist "%APPDIR%\dist"            rd /s /q "%APPDIR%\dist"
if exist "%APPDIR%\CISSQL.spec"     del /q  "%APPDIR%\CISSQL.spec"

echo  [3/4] Compiling .exe (this takes a couple of minutes)...
pushd "%APPDIR%"
%PYCMD% -m PyInstaller ^
    --name "CISSQL" ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --add-data "content;content" ^
    --hidden-import sqlite3 ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    cis_sql_course.py
set "PIRC=%ERRORLEVEL%"
popd
if not "%PIRC%"=="0" (
    echo  [ERROR] PyInstaller failed (exit %PIRC%).
    pause
    exit /b %PIRC%
)

echo  [4/4] Promoting the .exe to the main folder...
set "OUTEXE=%~dp0CISSQL.exe"
if exist "%OUTEXE%" del /q "%OUTEXE%"
move /y "%APPDIR%\dist\CISSQL.exe" "%OUTEXE%" >nul

if exist "%APPDIR%\build"        rd /s /q "%APPDIR%\build"
if exist "%APPDIR%\dist"         rd /s /q "%APPDIR%\dist"
if exist "%APPDIR%\CISSQL.spec"  del /q  "%APPDIR%\CISSQL.spec"

echo.
echo  ============================================================
echo    BUILD COMPLETE
echo    %~dp0CISSQL.exe
echo  ============================================================
echo.
endlocal
