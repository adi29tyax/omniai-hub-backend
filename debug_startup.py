import sys
import traceback
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app.main...")
    from app.main import app
    print("App imported successfully")
except Exception:
    traceback.print_exc()
