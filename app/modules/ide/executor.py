import subprocess
import tempfile

def run_python_code(code: str):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(code.encode())
            temp.flush()
            output = subprocess.check_output(["python", temp.name], stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return e.output
