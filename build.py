"""
Build script for Warframe Trade Watch.
Creates a standalone executable for the current platform.
"""
import os
import platform
import subprocess
import sys


def build():
    system = platform.system()
    script = "gui.py"
    name = "WFTW"
    icon = os.path.join("Media", "Icon", "WFTW.ico" if system == "Windows" else "WFTW.png")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        name,
        "--windowed",
        "--onefile",
        "--add-data",
        f"Media{os.pathsep}Media",
        "--add-data",
        f"Logs{os.pathsep}Logs",
        "--hidden-import",
        "flet",
        "--icon",
        icon,
        script,
    ]

    print("Building with command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"\nBuild complete. Output is in the 'dist' folder.")
    else:
        print("\nBuild failed.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
