import json
import time
import hashlib
import shutil
from pathlib import Path

# ======================================
# Meta-DAG Baseline Builder v1.1-XSTABLE
# - 來源：目前 sandbox 專案的 engine 版本
# - 目標：在 sandbox + 正式專案各自建立 baseline 封存
# ======================================

BASELINE_VERSION = "v1.1-XSTABLE"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_for_root(source_root: Path, target_root: Path) -> dict:
    """
    source_root: 來源（目前信任的 sandbox 根目錄）
    target_root: 要建立 baseline 的根 (sandbox / 正式)
    """
    result = {
        "root": str(target_root),
        "ok": False,
        "engine_files": [],
        "baseline_dir": None,
        "errors": [],
    }

    if not target_root.exists():
        result["errors"].append(f"Target root not found: {target_root}")
        return result

    engine_dir = source_root / "engine"
    if not engine_dir.exists():
        result["errors"].append(f"Source engine dir not found: {engine_dir}")
        return result

    # 要封存的 4 個核心模組（來源一律從 sandbox）
    engine_files = {
        "engine_v2.py": engine_dir / "engine_v2.py",
        "phase2_memory_engine.py": engine_dir / "phase2_memory_engine.py",
        "phase4_collab.py": engine_dir / "phase4_collab.py",
        "tul_map.py": engine_dir / "tul_map.py",
    }

    for name, p in engine_files.items():
        if not p.exists():
            result["errors"].append(f"Missing engine file: {p}")
            return result

    # baseline 目錄：{root}/baseline/v1.1_xstable/
    baseline_root = target_root / "baseline" / "v1.1_xstable"
    engine_out = baseline_root / "engine"
    docs_out = baseline_root / "docs"

    baseline_root.mkdir(parents=True, exist_ok=True)
    engine_out.mkdir(parents=True, exist_ok=True)
    docs_out.mkdir(parents=True, exist_ok=True)

    # 複製檔案 + 計算 SHA
    sha_map = {}
    for name, src in engine_files.items():
        dst = engine_out / name
        shutil.copy2(src, dst)
        sha = compute_sha256(dst)
        sha_map[f"engine/{name}"] = sha
        result["engine_files"].append(
            {"name": name, "src": str(src), "dst": str(dst), "sha256": sha}
        )

    # 產生 SHA256_SUMS.txt
    sha_file = baseline_root / "SHA256_SUMS.txt"
    with sha_file.open("w", encoding="utf-8") as f:
        for rel, sha in sha_map.items():
            f.write(f"{sha}  {rel}\n")

    # VERSION.lock
    version_file = baseline_root / "VERSION.lock"
    with version_file.open("w", encoding="utf-8") as f:
        f.write(f"META_DAG_ENGINE_BASELINE={BASELINE_VERSION}\n")
        f.write(f"CREATED_AT={time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
        f.write(f"TARGET_ROOT={target_root}\n")
        f.write("SOURCE_ROOT_IS_SANDBOX=1\n")

    # CHANGELOG.txt（附上簡短紀錄）
    changelog = baseline_root / "CHANGELOG.txt"
    with changelog.open("a", encoding="utf-8") as f:
        f.write("=============================================\n")
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {BASELINE_VERSION}\n")
        f.write(" - Source: sandbox engine (after 2000-case X級壓力測試通過)\n")
        f.write(f" - Target Root: {target_root}\n")
        f.write(" - Files: engine_v2.py, phase2_memory_engine.py, "
                "phase4_collab.py, tul_map.py\n")

    # baseline_info.md
    baseline_info = docs_out / "baseline_info.md"
    with baseline_info.open("w", encoding="utf-8") as f:
        f.write(f"# Meta-DAG Engine Baseline {BASELINE_VERSION}\n\n")
        f.write("此封存為 **Meta-DAG Engine** 在完成「2000 句 X 級壓力測試」後，\n")
        f.write("由 sandbox 專案中的 engine 目錄建立的「穩定可重建」基準版本。\n\n")
        f.write("## 來源 (Source)\n")
        f.write(f"- Source Root (sandbox): `{source_root}`\n")
        f.write("- 狀態：TUL + Phase2 Memory + Phase4 Collab 已通過壓力測試\n\n")
        f.write("## 內容 (Included Files)\n")
        for rel, sha in sha_map.items():
            f.write(f"- `{rel}`\n")
            f.write(f"    - SHA256: `{sha}`\n")
        f.write("\n")
        f.write("## 用途 (Usage)\n")
        f.write("1. 當作未來任何版本的 **重建起點 (baseline)**。\n")
        f.write("2. 如遇到殘影 / 污染懷疑時，可以直接從此 baseline 重置 engine 模組。\n")
        f.write("3. 正式壓力測試與治理設計可標記為：\n")
        f.write(f"   - `engine_baseline={BASELINE_VERSION}`。\n")

    # architecture_map.md
    arch_map = docs_out / "architecture_map.md"
    with arch_map.open("w", encoding="utf-8") as f:
        f.write("# Architecture Map (Baseline Engine)\n\n")
        f.write("```text\n")
        f.write(f"{target_root.name}/\n")
        f.write("└─ baseline/\n")
        f.write("   └─ v1.1_xstable/\n")
        f.write("      ├─ engine/\n")
        f.write("      │  ├─ engine_v2.py\n")
        f.write("      │  ├─ phase2_memory_engine.py\n")
        f.write("      │  ├─ phase4_collab.py\n")
        f.write("      │  └─ tul_map.py\n")
        f.write("      ├─ docs/\n")
        f.write("      │  ├─ baseline_info.md\n")
        f.write("      │  └─ architecture_map.md\n")
        f.write("      ├─ SHA256_SUMS.txt\n")
        f.write("      ├─ VERSION.lock\n")
        f.write("      └─ CHANGELOG.txt\n")
        f.write("```\n")

    result["baseline_dir"] = str(baseline_root)
    result["ok"] = True
    return result


def main():
    # 目前這支檔案預期放在 sandbox 根目錄
    sandbox_root = Path(__file__).resolve().parent
    formal_root = sandbox_root.with_name("meta_dag_engine")

    print("=====================================")
    print("  Meta-DAG Baseline Builder")
    print(f"  Version: {BASELINE_VERSION}")
    print("=====================================\n")

    print(f"[INFO] Sandbox Root : {sandbox_root}")
    print(f"[INFO] Formal  Root : {formal_root}")
    print()

    source_root = sandbox_root  # 一律以 sandbox 當作「來源真相」

    results = []

    # 1) sandbox 自身 baseline
    print("[STEP] Building baseline for SANDBOX ...")
    results.append(build_for_root(source_root, sandbox_root))

    # 2) 正式專案 baseline（若存在）
    if formal_root.exists():
        print("\n[STEP] Building baseline for FORMAL PROJECT ...")
        results.append(build_for_root(source_root, formal_root))
    else:
        print("\n[WARN] Formal project folder not found, skip:", formal_root)

    print("\n=====================================")
    print("  Build Summary")
    print("=====================================")

    for r in results:
        print(f"\nTarget Root: {r['root']}")
        if r["ok"]:
            print("  Status     : OK ✅")
            print(f"  Baseline   : {r['baseline_dir']}")
            print("  Engine Files:")
            for ef in r["engine_files"]:
                print(f"   - {ef['name']}")
                print(f"       src : {ef['src']}")
                print(f"       dst : {ef['dst']}")
                print(f"       sha : {ef['sha256']}")
        else:
            print("  Status     : ERROR ❌")
            for err in r["errors"]:
                print("   -", err)

    print("\n[DONE] Baseline build finished.")


if __name__ == "__main__":
    main()
