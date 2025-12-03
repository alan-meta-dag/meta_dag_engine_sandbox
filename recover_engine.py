import os
import shutil
import pathlib

# 路徑設定：目前所在資料夾 = sandbox 根目錄
ROOT = pathlib.Path.cwd()
BASE = ROOT / "baseline" / "v1.1_xstable" / "engine"
TARGET = ROOT / "engine"

print("[STEP] SANDBOX BASELINE RECOVERY")
print("[INFO] Baseline from:", BASE)
print("[INFO] Recover to   :", TARGET)

# 檢查 baseline 資料夾是否存在
if not BASE.exists():
    raise FileNotFoundError(f"[ERROR] Baseline folder not found: {BASE}")

# Step1: 清 __pycache__
for p in TARGET.rglob("__pycache__"):
    print("[DEL DIR]", p)
    shutil.rmtree(p, ignore_errors=True)

# Step2: 清不該存在的殘影檔案（你的 engine 內出現過的舊版本）
BAD = ["engine_v2_Final.py", "tul_map_v0.9.py", "tul_map_v0.9.1.py"]
for name in BAD:
    f = TARGET / name
    if f.exists():
        print("[DEL]", f)
        f.unlink()

# Step3: 覆蓋 baseline → engine/
for src in BASE.iterdir():
    dst = TARGET / src.name
    shutil.copy2(src, dst)
    print("[COPY]", src.name)

print("[DONE] SANDBOX RECOVERED OK")
