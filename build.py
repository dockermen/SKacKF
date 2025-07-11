import os
import subprocess
import sys

def install_requirements():
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    print("Building executable...")
    subprocess.check_call(["uv", "run", "PyInstaller", "db_manager.spec", "--clean"])

def main():
    # Install requirements
    # install_requirements()
    
    # Build the executable
    build_executable()
    
    print("\nBuild completed!")
    print("You can find the executable in the 'dist' folder")

if __name__ == "__main__":
    main()