@echo off
echo ============================================
echo  Building Grinding Polisher EXE
echo ============================================
echo.
echo This will create a standalone EXE file.
echo It may take 2-5 minutes to complete.
echo.
echo Press any key to start...
pause > nul

echo.
echo [1/4] Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul
echo ✅ Clean complete!

echo.
echo [2/4] Installing PyInstaller if needed...
python -m pip install pyinstaller --quiet
echo ✅ PyInstaller ready!

echo.
echo [3/4] Building EXE...
echo This may take a few minutes...
python -m PyInstaller --onefile --windowed --name GrindingPolisher --add-data "reports;reports" --add-data "data;data" --hidden-import PyQt5 --hidden-import PyQt5.QtWidgets --hidden-import PyQt5.QtCore --hidden-import PyQt5.QtGui --hidden-import matplotlib --hidden-import matplotlib.backends.backend_qt5agg --hidden-import pandas --hidden-import numpy --hidden-import sqlalchemy --hidden-import reportlab --hidden-import openpyxl --hidden-import plotly --hidden-import seaborn --hidden-import database --hidden-import core --hidden-import ui --hidden-import visualization --hidden-import reports --collect-all matplotlib --collect-all pyqt5 --exclude-module tkinter --exclude-module tcl main.py

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo ✅ Build complete!

echo.
echo [4/4] Copying to alex-exe folder...
mkdir "C:\Users\DPROFESSOR\Desktop\alex\alex-exe" 2>nul
copy "dist\GrindingPolisher.exe" "C:\Users\DPROFESSOR\Desktop\alex\alex-exe\"
xcopy "data" "C:\Users\DPROFESSOR\Desktop\alex\alex-exe\data" /E /I /Y >nul
xcopy "reports" "C:\Users\DPROFESSOR\Desktop\alex\alex-exe\reports" /E /I /Y >nul

echo.
echo ============================================
echo ✅ EXE BUILD COMPLETE!
echo ============================================
echo 📁 Location: C:\Users\DPROFESSOR\Desktop\alex\alex-exe\
echo 📄 File: GrindingPolisher.exe
echo ============================================
echo.
echo To run the application:
echo   1. Go to C:\Users\DPROFESSOR\Desktop\alex\alex-exe
echo   2. Double-click GrindingPolisher.exe
echo.
pause