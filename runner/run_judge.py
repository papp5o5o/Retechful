import subprocess, resource, json, sys

def run_with_rusage(cmd, stdin_data, timeout=5):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = subprocess.run(cmd, input=stdin_data, capture_output=True, timeout=timeout, text=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_time = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    return proc.stdout, proc.returncode, cpu_time

if __name__ == "__main__":
    stdin_data = sys.stdin.read()
    stdout, code, cpu_time = run_with_rusage(["./sol"], stdin_data)
    result = {
        "stdout": stdout,
        "exit_code": code,
        "cpu_time_sec": round(cpu_time, 4)
    }
    print(json.dumps(result, ensure_ascii=False))
