import json
from pathlib import Path
from typing import List, Dict, Any


def compute_metrics(snapshot_paths: List[Path]) -> Dict[str, Any]:
    """
    從多個 snapshot JSON 中計算簡單指標：
      - pra_log 長度序列
      - tul_log 長度序列
      - 是否單調遞增（無回滾）
    """
    pra_lengths = []
    tul_lengths = []

    for p in snapshot_paths:
        with open(p, "r", encoding="utf-8") as f:
            snap = json.load(f)
        files = snap.get("files", {})
        pra = files.get("pra_log.json") or []
        tul = files.get("tul_log.json") or []
        if isinstance(pra, list):
            pra_lengths.append(len(pra))
        else:
            pra_lengths.append(None)
        if isinstance(tul, list):
            tul_lengths.append(len(tul))
        else:
            tul_lengths.append(None)

    def is_monotonic(seq: List[int]) -> bool:
        clean = [x for x in seq if isinstance(x, int)]
        return all(b >= a for a, b in zip(clean, clean[1:]))

    return {
        "snapshot_count": len(snapshot_paths),
        "pra_lengths": pra_lengths,
        "tul_lengths": tul_lengths,
        "pra_monotonic": is_monotonic(pra_lengths),
        "tul_monotonic": is_monotonic(tul_lengths),
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    if len(sys.argv) < 2:
        print("Usage: python -m tests.b_phase_metrics SNAPSHOT1 SNAPSHOT2 ...")
    else:
        snaps = [Path(p) for p in sys.argv[1:]]
        m = compute_metrics(snaps)
        print(json.dumps(m, indent=2, ensure_ascii=False))
