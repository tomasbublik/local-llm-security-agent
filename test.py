import subprocess

resultTest = subprocess.run(
    ["/usr/local/bin/ollama", "ps"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print("=== ollama ps ===")
print(resultTest.stdout)
if resultTest.stderr:
    print("STDERR:", resultTest.stderr)

print("=== ollama run (might take a while, model is loading) ===")
result = subprocess.run(
    ["/usr/local/bin/ollama", "run", "qwen2.5-coder:14b", "Return JSON with key 'ok' = true"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    timeout=20  # 20 seconds – model must be loaded from disk
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
