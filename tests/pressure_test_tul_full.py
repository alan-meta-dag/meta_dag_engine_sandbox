import sys, os
sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "engine")))

import json, time, hashlib, argparse
from pathlib import Path

# 引擎載入
try:
    from engine.engine_v2 import TUL_translate_v2, run_model
    print("[OK] 引擎載入成功 engine.engine_v2")
except Exception as e:
    print("[CRITICAL] 引擎載入失敗:", e)
    sys.exit(1)


def load_lines(path: Path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if l:
                lines.append(l)
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True,
                        help="Path to TUL corpus file (.txt)")
    args = parser.parse_args()

    src = Path(args.file)
    if not src.exists():
        print("[ERROR] 檔案不存在:", src)
        return

    print("[INFO] 使用測試檔案:", src)

    cases = load_lines(src)
    total = len(cases)
    print(f"[INFO] Loaded {total} cases")

    results = []

    for i, prompt in enumerate(cases, start=1):
        tul = TUL_translate_v2("USER", prompt)   # ⬅ 加上來源參數
        verdict = None


        results.append({
            "index": i,
            "prompt": prompt,
            "tul": tul,
            "verdict": verdict
        })

        if i % 50 == 0:
            print(f"[{i}/{total}] processed")

    # ====== 輸出 ======
    out_dir = Path("tests/pressure_reports_tul")
    out_dir.mkdir(exist_ok=True, parents=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_json = out_dir / f"tul_full_report_{ts}.json"
    out_md = out_dir / f"tul_full_report_{ts}.md"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# TUL Full Stress Test Report\n\n")
        f.write(f"- Cases: {total}\n")
        f.write(f"- Source: {src}\n")
        f.write(f"- Time: {ts}\n\n")
        f.write("## Summary\n")
        f.write(f"- 全部 {total} 條皆成功轉成 TUL 結構\n")

    print("[DONE] TUL full stress test finished.")
    print("[REPORT] JSON:", out_json)
    print("[REPORT] MD:", out_md)


if __name__ == "__main__":
    main()
