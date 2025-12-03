# ============================================================
#  TUL v4.5 Short Stress Test (Engineering Auditable Version)
# ============================================================

import os
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys
import importlib

# ------------------------------------------------------------
# 0. 將專案根目錄加入 sys.path
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]   # D:\AlanProjects\meta_dag_engine_sandbox
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------
# 1. 基礎路徑設定（要在引擎載入前定義）
# ------------------------------------------------------------

BASE_DIR = ROOT                 # 專案根目錄
CASE_DIR = BASE_DIR / "tests" / "pressure_cases_tul"
REPORT_DIR = BASE_DIR / "tests" / "pressure_reports_tul"

# 自動建立必要資料夾
CASE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 2. 引擎載入（sandbox 安全模式）
# ------------------------------------------------------------

try:
    engine_mod = importlib.import_module("engine.engine_v2")
    run_model = getattr(engine_mod, "run_model")
    print("[OK] 引擎載入成功 engine.engine_v2.run_model")
except Exception as e:
    print("[ERROR] 無法載入 engine_v2.run_model:", e)
    raise SystemExit(1)

# 強制進入 sandbox 測試模式：不寫入正式 DAG
os.environ["META_DAG_TEST_MODE"] = "1"

# ------------------------------------------------------------
# 2. 路徑配置
# ------------------------------------------------------------

CASE_DIR = BASE_DIR / "tests" / "pressure_cases_tul"
REPORT_DIR = BASE_DIR / "tests" / "pressure_reports_tul"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 3. 語料庫載入
# ------------------------------------------------------------

def load_cases() -> List[Tuple[str, str]]:
    """
    回傳 list of (category, text)
    """
    cases = []
    for name in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        fpath = CASE_DIR / f"{name}.txt"
        if not fpath.exists():
            print(f"[WARN] 缺少語料: {name}.txt")
            continue

        with fpath.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cases.append((name, line))

    random.shuffle(cases)
    return cases


# ------------------------------------------------------------
# 4. 採樣 + 單筆測試
# ------------------------------------------------------------

def run_single(prompt: str) -> Dict[str, Any]:
    """
    執行 TUL + 仲裁 + PRA，並擷取結果
    """
    record = {
        "prompt": prompt,
        "tul_raw": None,
        "verdict": None,
        "risk": None,
        "pec": None,
        "error": None,
    }

    try:
        out = run_model(prompt)

        if isinstance(out, dict):
            record["tul_raw"] = out
            record["verdict"] = out.get("decision_status")
            record["risk"] = out.get("risk_level")
            record["pec"] = out.get("pec")
        else:
            record["tul_raw"] = str(out)

    except Exception as e:
        record["error"] = repr(e)

    return record


# ------------------------------------------------------------
# 5. 主程式：執行 50–80 筆短測試
# ------------------------------------------------------------

def run_suite():
    cases = load_cases()
    total = min(len(cases), 80)

    print(f"[INFO] Loaded {len(cases)} cases, using {total}.")

    selected = cases[:total]
    logs = []

    for idx, (cat, text) in enumerate(selected, start=1):
        rec = run_single(text)
        rec["index"] = idx
        rec["category"] = cat
        logs.append(rec)
        print(f"[{idx}/{total}] {cat} → verdict = {rec.get('verdict')}")

    return logs


# ------------------------------------------------------------
# 6. 報告輸出
# ------------------------------------------------------------

def write_report(logs: List[Dict[str, Any]]):
    ts = time.strftime("%Y%m%d_%H%M%S")
    jpath = REPORT_DIR / f"tul_short_report_{ts}.json"
    mpath = REPORT_DIR / f"tul_short_report_{ts}.md"

    summary = {
        "total_cases": len(logs),
        "errors": sum(1 for x in logs if x.get("error")),
        "pec3_count": sum(1 for x in logs if x.get("pec") == 3),
        "veto_count": sum(1 for x in logs if x.get("verdict") == "REJECTED_HARD_VETO"),
    }

    with jpath.open("w", encoding="utf-8") as f:
        json.dump({"summary": summary, "logs": logs}, f, ensure_ascii=False, indent=2)

    with mpath.open("w", encoding="utf-8") as f:
        f.write(f"# TUL Short Stress Test Report ({ts})\n\n")
        f.write(f"- Total cases: {summary['total_cases']}\n")
        f.write(f"- Errors: {summary['errors']}\n")
        f.write(f"- PEC-3 count: {summary['pec3_count']}\n")
        f.write(f"- Veto count: {summary['veto_count']}\n\n")
        f.write("## Sample Cases\n\n")

        for rec in logs[:10]:
            f.write(f"### Case #{rec['index']}\n")
            f.write(f"- Category: {rec['category']}\n")
            f.write(f"- Prompt: {rec['prompt']}\n")
            f.write(f"- Verdict: {rec.get('verdict')}\n")
            f.write(f"- PEC: {rec.get('pec')}\n")
            f.write(f"- Risk: {rec.get('risk')}\n\n")

    print(f"[REPORT] JSON: {jpath}")
    print(f"[REPORT] MD:   {mpath}")


# ------------------------------------------------------------
# 7. Entry
# ------------------------------------------------------------

if __name__ == "__main__":
    logs = run_suite()
    write_report(logs)
    print("[DONE] TUL Short Stress Test Finished.")
