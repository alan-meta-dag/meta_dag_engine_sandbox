import json
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "tests" / "attack_reports"


def _diff_json(a, b, path="") -> List[str]:
    """非常簡單的 JSON diff，用於偵測明顯變化。"""
    diffs: List[str] = []

    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a.keys()) | set(b.keys())
        for k in sorted(keys):
            pa = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append(f"+ {pa} (only in B)")
            elif k not in b:
                diffs.append(f"- {pa} (only in A)")
            else:
                diffs.extend(_diff_json(a[k], b[k], pa))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"~ {path} : len(A)={len(a)}, len(B)={len(b)}")
    else:
        if a != b:
            diffs.append(f"~ {path} : A={repr(a)} B={repr(b)}")

    return diffs


def diff_snapshots(snap_a: Path, snap_b: Path) -> Path:
    """比較兩個 snapshot JSON，輸出簡易 Markdown 報告。"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(snap_a, "r", encoding="utf-8") as f:
        A = json.load(f)
    with open(snap_b, "r", encoding="utf-8") as f:
        B = json.load(f)

    lines: List[str] = []
    lines.append("# B-Phase Snapshot Diff Report\n")
    lines.append(f"- A: `{snap_a.name}` (tag={A.get('tag')}, ts={A.get('timestamp')})")
    lines.append(f"- B: `{snap_b.name}` (tag={B.get('tag')}, ts={B.get('timestamp')})")
    lines.append("")

    all_diffs: List[str] = []
    files_a = A.get("files", {})
    files_b = B.get("files", {})

    keys = set(files_a.keys()) | set(files_b.keys())
    for name in sorted(keys):
        fa = files_a.get(name)
        fb = files_b.get(name)
        lines.append(f"## File: {name}")
        if fa is None and fb is None:
            lines.append("- both missing")
        elif fa is None:
            lines.append("- only in B")
        elif fb is None:
            lines.append("- only in A")
        else:
            diffs = _diff_json(fa, fb, path=name)
            if not diffs:
                lines.append("- no observable diff")
            else:
                for d in diffs[:100]:
                    lines.append(f"- {d}")
                if len(diffs) > 100:
                    lines.append(f"- ... {len(diffs)-100} more diffs omitted ...")
            all_diffs.extend(diffs)
        lines.append("")

    out_name = f"b_phase_diff_{snap_a.stem}_vs_{snap_b.stem}.md"
    out_path = REPORT_DIR / out_name
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m tests.b_phase_diff SNAPSHOT_A SNAPSHOT_B")
    else:
        p = diff_snapshots(Path(sys.argv[1]), Path(sys.argv[2]))
        print(f"Diff report: {p}")
