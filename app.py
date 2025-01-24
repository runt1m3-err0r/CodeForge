from flask import Flask, render_template, request, jsonify
import subprocess
import time
import os
import uuid
import json

app = Flask(__name__)

problem_data = json.load(open('problem/problem1.json'))

@app.route('/')
def index():
    return render_template('index.html', problem=problem_data)

@app.route('/compile_run', methods=['POST'])
def compile_run():
    # Get the code submitted by the user
    code = request.form.get('code', '').strip()
    if not code:
        return jsonify({"status": "error", "message": "Code cannot be empty!"})
    test_cases = problem_data.get('test_cases', [])
    if not test_cases:
        return jsonify({"status": "error", "message": "No test cases available in the problem data!"})
    filename = f"temp_{uuid.uuid4().hex}"
    c_file = f"problem/{filename}.c"
    executable = f"problem/{filename}.out"
    try:
        scanner_command = [
            "python3", "problem/Scanner.py",
            c_file,
            json.dumps(problem_data),
            code,
            open('problem/input.txt', 'r').read()
        ]
        scanner_process = subprocess.run(scanner_command, capture_output=True, text=True)
        if scanner_process.returncode != 0:
            error_message = scanner_process.stderr.replace('\n', '<br>')
            return jsonify({"status": "error", "message": f"Scanner Error:<br>{error_message}"})
        t1 = time.time()
        compile_process = subprocess.run(["gcc", c_file, "-o", executable], capture_output=True, text=True)
        t2 = time.time()

        if compile_process.returncode != 0:
            error_message = compile_process.stderr.replace('\n', '<br>')
            return jsonify({"status": "error", "message": f"Compilation Failed:<br>{error_message}"})

        compile_time = f"Compilation successful! (Time: {t2 - t1:.2f} seconds)"
        results = []
        for test_case in test_cases:
            try:
                run_process = subprocess.run(
                    [f"./{executable}"],
                    input=test_case['input'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = run_process.stdout.strip()
                status = "success" if output == test_case['output'] else "failure"

                results.append({
                    "test_case": test_case['id'],
                    "input": test_case['input'],
                    "expected_output": test_case['output'],
                    "actual_output": output,
                    "status": status,
                    "explanation": test_case.get('explanation', '')
                })
            except subprocess.TimeoutExpired:
                results.append({
                    "test_case": test_case['id'],
                    "input": test_case['input'],
                    "expected_output": test_case['output'],
                    "actual_output": "Time Limit Exceeded",
                    "status": "error",
                    "explanation": test_case.get('explanation', '')
                })

        return jsonify({"status": "success", "compile_time": compile_time, "results": results})

    finally:
        if os.path.exists(c_file):
            os.remove(c_file)
        if os.path.exists(executable):
            os.remove(executable)

if __name__ == '__main__':
    app.run(debug=True)
