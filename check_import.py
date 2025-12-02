import sys
import traceback

try:
    from app.main import app
    print("Import successful")
except Exception:
    with open("import_error.log", "w") as f:
        traceback.print_exc(file=f)
    sys.exit(1)
