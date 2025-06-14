import subprocess
import tempfile

def lang_suffix(language):
    return {
        "python": ".py",
        "cpp": ".cpp",
        "c": ".c",
        "java": ".java"
    }.get(language, ".txt")

def run_code(code, language, input_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=lang_suffix(language)) as tmp:
        tmp.write(code.encode('utf-8'))
        tmp.flush()

        if language == "python":
            cmd = ["python3", tmp.name]
        elif language == "cpp":
            exec_file = tmp.name.replace(".cpp", "")
            subprocess.run(["g++", tmp.name, "-o", exec_file], stderr=subprocess.PIPE)
            cmd = [exec_file]
        elif language == "c":
            exec_file = tmp.name.replace(".c", "")
            subprocess.run(["gcc", tmp.name, "-o", exec_file], stderr=subprocess.PIPE)
            cmd = [exec_file]
        elif language == "java":
            java_file = tmp.name
            subprocess.run(["javac", java_file], stderr=subprocess.PIPE)
            cmd = ["java", java_file.replace(".java", "")]
        else:
            return False, "Unsupported language"

        try:
            process = subprocess.run(cmd, input=input_data.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            output = process.stdout.decode() or process.stderr.decode()
        except subprocess.TimeoutExpired:
            output = "Time Limit Exceeded"

    return True, output
