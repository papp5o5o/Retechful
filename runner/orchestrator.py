import subprocess, json, base64, os, sys, urllib.request

SUBMISSION_ID = os.environ["SUBMISSION_ID"]
PROBLEM_ID = os.environ["PROBLEM_ID"]
CODE_B64 = os.environ["CODE_B64"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

# 1. 提出コードをデコードしてsol.cppに書き込む
code = base64.b64decode(CODE_B64).decode("utf-8")
with open("docker/cpp/sol.cpp", "w") as f:
    f.write(code)

# 2. Supabaseからテストケースを取得
url = f"{SUPABASE_URL}/rest/v1/test_case?problem_id=eq.{PROBLEM_ID}&select=input,output"
req = urllib.request.Request(url, headers={
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
})
try:
    with urllib.request.urlopen(req) as resp:
        test_cases = json.loads(resp.read())
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"Supabase error ({e.code}): {error_body}")
    os.makedirs("results", exist_ok=True)
    with open(f"results/{SUBMISSION_ID}.json", "w") as f:
        json.dump({
            "submission_id": SUBMISSION_ID,
            "status": "ERROR",
            "message": f"Supabase error: {error_body}"
        }, f, ensure_ascii=False)
    sys.exit(0)

os.makedirs("results", exist_ok=True)

if not test_cases:
    result = {"submission_id": SUBMISSION_ID, "status": "ERROR", "message": "test cases not found"}
    with open(f"results/{SUBMISSION_ID}.json", "w") as f:
        json.dump(result, f, ensure_ascii=False)
    sys.exit(0)

# 3. Dockerイメージをビルド
subprocess.run(["docker", "build", "-t", "judge-cpp", "-f", "docker/cpp/Dockerfile", "."], check=True)

case_results = []
overall_status = "AC"

for i, tc in enumerate(test_cases):
    try:
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", "--network", "none",
             "--memory=256m", "--cpus=1", "--pids-limit=64", "judge-cpp"],
            input=tc["input"], capture_output=True, text=True, timeout=10
        )
    except subprocess.TimeoutExpired:
        case_results.append({"case": i + 1, "verdict": "TLE"})
        overall_status = "TLE" if overall_status == "AC" else overall_status
        continue

    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        case_results.append({"case": i + 1, "verdict": "RE", "detail": proc.stderr[:500]})
        overall_status = "RE"
        continue

    expected = tc["output"].strip()
    actual = out.get("stdout", "").strip()
    verdict = "AC" if actual == expected else "WA"
    if verdict == "WA" and overall_status == "AC":
        overall_status = "WA"

    case_results.append({
        "case": i + 1,
        "verdict": verdict,
        "cpu_time_sec": out.get("cpu_time_sec"),
    })

result = {
    "submission_id": SUBMISSION_ID,
    "status": overall_status,
    "cases": case_results,
}

with open(f"results/{SUBMISSION_ID}.json", "w") as f:
    json.dump(result, f, ensure_ascii=False)
