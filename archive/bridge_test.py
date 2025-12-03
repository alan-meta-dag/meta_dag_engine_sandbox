import subprocess

msg = "Hello from Meta-DAG Engine"

result = subprocess.run(
    ["ollama", "run", "gemma3:4b"],
    input=msg,
    text=True,
    encoding="utf-8",
    capture_output=True
)

print("=== MODEL OUTPUT ===")
print(result.stdout)
