# contests/utils.py

import subprocess
import tempfile
import os

def lang_suffix(language):
    return {
        "python": ".py",
        "cpp": ".cpp",
        "c": ".c",
        "java": ".java"
    }.get(language, ".txt")

def run_code(code, language, input_data):
    """
    Runs user code in a temporary file using subprocess.
    WARNING: Not safe for production use.
    """

    suffix = lang_suffix(language)

    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "Main" + suffix)

        # Write code to file
        with open(code_file, "w") as f:
            f.write(code)

        # Build commands based on language
        if language == "python":
            cmd = ["python3", code_file]
        elif language == "cpp":
            exe_file = os.path.join(tmpdir, "a.out")
            compile_result = subprocess.run(["g++", code_file, "-o", exe_file],
                                            stderr=subprocess.PIPE)
            if compile_result.returncode != 0:
                return False, compile_result.stderr.decode()
            cmd = [exe_file]
        elif language == "c":
            exe_file = os.path.join(tmpdir, "a.out")
            compile_result = subprocess.run(["gcc", code_file, "-o", exe_file],
                                            stderr=subprocess.PIPE)
            if compile_result.returncode != 0:
                return False, compile_result.stderr.decode()
            cmd = [exe_file]
        elif language == "java":
            compile_result = subprocess.run(["javac", code_file], stderr=subprocess.PIPE)
            if compile_result.returncode != 0:
                return False, compile_result.stderr.decode()
            class_name = "Main"
            cmd = ["java", "-cp", tmpdir, class_name]
        else:
            return False, "Unsupported language"

        # Execute with input, timeout for safety
        try:
            result = subprocess.run(
                cmd,
                input=input_data.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5  # seconds
            )
            output = result.stdout.decode() + result.stderr.decode()
            return True, output
        except subprocess.TimeoutExpired:
            return False, "Time Limit Exceeded"

# ✅ Add this alias so views.py import works
run_code_safely = run_code
