# ================================================
#  attack_test.py (Final Executable Version)
# ================================================

import sys
import os
import json
import time
import random
from pathlib import Path
import importlib
from typing import List, Dict, Any, Optional, Tuple

# --- FIX: ensure parent folder is importable ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --------------------------------
# 1. Imports - dynamic engine load
# --------------------------------

try:
    from engine.engine_v2 import run_model
except ImportError:
    ENGINE_MODULE = importlib.import_module("engine.engine_v2")
    run_model = getattr(ENGINE_MODULE, "run_model")



# -------------------
# 2. Constants / Paths
# -------------------

BASE_DIR = Path(__file__).resolve().parent

CASE_DIR = BASE_DIR / "attack_cases"
REPORT_DIR = BASE_DIR / "attack_reports"
SNAPSHOT_DIR = BASE_DIR.parent / "state"

TOTAL_TARGET = 2000
SNAPSHOT_EVERY = 100
PRA_LOG_CHECK_EVERY = 200

# *** IMPORTANT: corrected PRA file path ***
PRA_STATE_FILE = SNAPSHOT_DIR / "pra_log.json"
PRA_LOG_FILE = SNAPSHOT_DIR / "pra_log.json"   # same file; size monitor


# --------------- 
# 3. Load Cases
# ---------------

def load_cases() -> List[str]:
    CASE_DIR.mkdir(parents=True, exist_ok=True)

    names = [f"C{i}" for i in range(1, 7)] + ["H", "S"]
    all_lines = set()

    for name in names:
        fp = CASE_DIR / f"{name}.txt"
        if not fp.exists():
            continue

        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_lines.add(line)

    cases = list(all_lines)
    random.shuffle(cases)
    return cases


# ---------------------------
# 4. PRA Snapshot / Diff
# ---------------------------

def snapshot_pra(tag: str) -> Optional[Path]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = SNAPSHOT_DIR / f"attack_pra_snapshot_{tag}.json"

    if PRA_STATE_FILE.exists():
        try:
            with PRA_STATE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            data = {"error": f"PRA read error: {e}", "tag": tag}
    else:
        data = {"info": "PRA does not exist", "tag": tag}

    try:
        with snapshot_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return snapshot_path
    except Exception:
        return None


def diff_pra(prev_path: Path, curr_path: Path) -> Dict[str, Any]:
    diff_result = {
        "prev": prev_path.name,
        "curr": curr_path.name,
        "changed_keys": [],
        "added_keys": [],
        "removed_keys": [],
    }

    if not (prev_path.exists() and curr_path.exists()):
        diff_result["error"] = "Snapshot missing"
        return diff_result

    try:
        with prev_path.open("r", encoding="utf-8") as f:
            prev_data = json.load(f)
        with curr_path.open("r", encoding="utf-8") as f:
            curr_data = json.load(f)
    except Exception as e:
        diff_result["error"] = f"Load error: {e}"
        return diff_result

    prev_keys = set(prev_data.keys())
    curr_keys = set(curr_data.keys())

    diff_result["added_keys"] = sorted(list(curr_keys - prev_keys))
    diff_result["removed_keys"] = sorted(list(prev_keys - curr_keys))

    common = prev_keys & curr_keys
    changed = []
    for k in common:
        if prev_data.get(k) != curr_data.get(k):
            changed.append(k)

    diff_result["changed_keys"] = sorted(changed)
    return diff_result


# ----------------------------
# 5. Single Case Executor
# ----------------------------

def run_single_case(prompt: str) -> Dict[str, Any]:
    rec = {
        "prompt": prompt,
        "output": None,
        "error": None,
        "timestamp": time.time(),
    }
    try:
        rec["output"] = run_model(prompt)
    except Exception as e:
        rec["error"] = str(e)
    return rec


# ----------------------
# 6. Batch Runner
# ----------------------

def get_pra_log_size() -> Optional[int]:
    if PRA_LOG_FILE.exists():
        try:
            return PRA_LOG_FILE.stat().st_size
        except Exception:
            return None
    return None


def run_attack_suite() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    cases = load_cases()
    total_available = len(cases)
    limit = min(TOTAL_TARGET, total_available)

    print(f"[INFO] Loaded {total_available} cases, using {limit}.")

    selected_cases = cases[:limit]

    results = []
    pra_diffs = []
    pra_sizes = []

    prev_snapshot = None
    start = time.time()
    err_count = 0

    for idx, prompt in enumerate(selected_cases, start=1):
        rec = run_single_case(prompt)
        rec["index"] = idx
        results.append(rec)

        if rec["error"]:
            err_count += 1

        if idx % SNAPSHOT_EVERY == 0:
            tag = f"case_{idx}"
            snap = snapshot_pra(tag)
            print(f"[INFO] Snapshot {tag}")

            if prev_snapshot and snap:
                diff = diff_pra(prev_snapshot, snap)
                diff["index"] = idx
                pra_diffs.append(diff)
                print(f"[INFO] PRA diff #{idx}")

            prev_snapshot = snap

        if idx % PRA_LOG_CHECK_EVERY == 0:
            size = get_pra_log_size()
            pra_sizes.append({"index": idx, "size_bytes": size})
            print(f"[INFO] PRA log size at {idx}: {size}")

    duration = time.time() - start

    meta = {
        "total_cases_available": total_available,
        "total_cases_run": limit,
        "total_errors": err_count,
        "duration_seconds": duration,
        "snapshots": len(pra_diffs),
        "log_size_checks": len(pra_sizes),
        "pra_diffs": pra_diffs,
        "pra_log_sizes": pra_sizes,
    }

    return results, meta


# -----------------------
# 7. Report Writer
# -----------------------

def write_reports(results, metadata):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    json_path = REPORT_DIR / f"attack_report_{ts}.json"
    md_path = REPORT_DIR / f"attack_report_{ts}.md"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "results": results},
                  f, ensure_ascii=False, indent=2)

    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Attack Test Report ({ts})\n\n")
        f.write(f"- Total cases run: {metadata['total_cases_run']}\n")
        f.write(f"- Errors: {metadata['total_errors']}\n")
        f.write(f"- Duration: {metadata['duration_seconds']:.2f}s\n\n")
        f.write("## PRA Diffs\n")
        for d in metadata["pra_diffs"]:
            f.write(f"- Case {d['index']}: {d['prev']} → {d['curr']}\n")
            f.write(f"  Changed: {d['changed_keys']}\n")
            f.write(f"  Added: {d['added_keys']}\n")
            f.write(f"  Removed: {d['removed_keys']}\n\n")


# --------------
# 8. Main
# --------------

if __name__ == "__main__":
    results, meta = run_attack_suite()
    write_reports(results, meta)
    print("[INFO] Attack Test Completed")
