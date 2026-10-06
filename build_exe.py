"""
build_exe.py - Build standalone EXE for Grinding Polisher
"""

import os
import sys
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build files"""
    print("🧹 Cleaning previous builds...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✅ Removed {dir_name}/")
    
    # Remove .spec files
    for file in Path('.').glob('*.spec'):
        file.unlink()
        print(f"  ✅ Removed {file.name}")
    
    print("✅ Clean complete!\n")

def build_exe():
    """Build the EXE file"""
    print("=" * 60)
    print("  BUILDING GRINDING POLISHER EXE")
    print("=" * 60)
    print()
    
    # Clean previous builds
    clean_build()
    
    # Get Python path
    python_path = sys.executable
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single EXE file
        '--windowed',                   # No console window (GUI only)
        '--name', 'GrindingPolisher',   # Output name
        '--icon', 'NONE',               # Add icon if you have one
        '--add-data', f'reports{os.pathsep}reports',  # Include reports directory
        '--add-data', f'data{os.pathsep}data',        # Include data directory
        '--hidden-import', 'PyQt5',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'matplotlib.backends.backend_qt5agg',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'sqlalchemy',
        '--hidden-import', 'reportlab',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'plotly',
        '--hidden-import', 'seaborn',
        '--hidden-import', 'database',
        '--hidden-import', 'core',
        '--hidden-import', 'ui',
        '--hidden-import', 'visualization',
        '--hidden-import', 'reports',
        '--collect-all', 'matplotlib',
        '--collect-all', 'pyqt5',
        '--exclude-module', 'tkinter',
        '--exclude-module', 'tcl',
        'main.py'
    ]
    
    # Run PyInstaller
    print("🔨 Building EXE...")
    print("   This may take 2-5 minutes...")
    print()
    
    import subprocess
    result = subprocess.run(' '.join(cmd), shell=True)
    
    if result.returncode == 0:
        print("\n✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"📁 EXE Location: dist/GrindingPolisher.exe")
        print("=" * 60)
        
        # Copy to alex-exe folder
        copy_to_alex_exe()
    else:
        print("\n❌ Build failed!")
        print("   Check the error messages above.")

def copy_to_alex_exe():
    """Copy the EXE to alex-exe folder in root"""
    try:
        # Create alex-exe folder in root (C:\Users\DPROFESSOR\Desktop\alex)
        root_dir = Path('C:/Users/DPROFESSOR/Desktop/alex')
        exe_dir = root_dir / 'alex-exe'
        exe_dir.mkdir(exist_ok=True)
        
        # Copy EXE
        src_exe = Path('dist/GrindingPolisher.exe')
        dst_exe = exe_dir / 'GrindingPolisher.exe'
        
        if src_exe.exists():
            shutil.copy2(src_exe, dst_exe)
            print(f"\n📁 EXE copied to: {dst_exe}")
            
            # Copy data and reports folders
            for folder in ['data', 'reports']:
                src_folder = Path(folder)
                dst_folder = exe_dir / folder
                if src_folder.exists():
                    if dst_folder.exists():
                        shutil.rmtree(dst_folder)
                    shutil.copytree(src_folder, dst_folder)
                    print(f"📁 Copied {folder}/ to alex-exe/")
            
            # Create a simple run script
            create_run_script(exe_dir)
            
            print("\n" + "=" * 60)
            print("✅ EXE READY FOR USE!")
            print(f"📍 Location: {exe_dir}")
            print("=" * 60)
        else:
            print("⚠️  EXE not found in dist/")
            
    except Exception as e:
        print(f"⚠️  Error copying to alex-exe: {e}")

def create_run_script(exe_dir):
    """Create a batch file to run the EXE"""
    run_bat = exe_dir / 'run_app.bat'
    with open(run_bat, 'w') as f:
        f.write("""@echo off
title Grinding Polisher
echo ============================================
echo  Grinding Polisher - Metallographic System
echo  Federal University of Technology, Minna
echo ============================================
echo.
echo Starting application...
echo.
start "" "GrindingPolisher.exe"
echo Application started!
echo.
pause
""")
    print(f"📝 Created: {run_bat}")

def create_requirements_script():
    """Create a requirements installer for the EXE"""
    script = """@echo off
echo ============================================
echo  Installing Grinding Polisher EXE
echo ============================================
echo.
echo This will install the standalone EXE
echo to C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe
echo.
echo Press any key to continue...
pause > nul

:: Create directory if not exists
mkdir "C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe" 2>nul

:: Copy the EXE
if exist "dist\\GrindingPolisher.exe" (
    copy "dist\\GrindingPolisher.exe" "C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe\\"
    echo ✅ EXE copied successfully!
) else (
    echo ❌ EXE not found. Please run build_exe.py first.
    pause
    exit /b 1
)

:: Copy supporting folders
xcopy "data" "C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe\\data" /E /I /Y >nul
xcopy "reports" "C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe\\reports" /E /I /Y >nul

echo.
echo ✅ Installation complete!
echo 📁 Location: C:\\Users\\DPROFESSOR\\Desktop\\alex\\alex-exe
echo.
pause
"""
    
    with open('install_exe.bat', 'w') as f:
        f.write(script)
    print("📝 Created: install_exe.bat")

if __name__ == "__main__":
    build_exe()