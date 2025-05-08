import importlib.util
import subprocess
import sys


def check_packages():
    for package in ["requests", "colorama"]:
        if importlib.util.find_spec(package) is None:
            print(f"'{package}' not found. Installing via pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
