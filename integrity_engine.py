import argparse
import hashlib
import json
import os
# 掃描模式
# "light" = 只掃核心檔案（快、穩定）
# "full"  = 掃整個專案（Debug 用）
# "auto"  = 根據指令自動切換（推薦）
SCAN_MODE = "auto"
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]  # 專案根目錄 = 上一層
VERSION_LOCK = ROOT / "version.lock"

def get_include_paths(mode: str):
    if mode == "light":
        return [
            "engine_v2.py",
            "meta_dag.core.json",
            "meta_dag.runtime.json",
            "version.lock",
        ]
    elif mode == "full":
        return [
            ".",  # 掃描整個專案
        ]
    else:
        # auto 預設使用 light
        return [
            "engine/engine_v2.py",
            "state/meta_dag_memory.json",
            "state/veto_index.json",
            "manifest/version_marker.txt",
            "version.lock",
]

        ]



def iter_files(root: Path, include_paths):
    """
    依照固定順序列出所有要計算 hash 的檔案。
    只包含 include_paths 底下的檔案。
    """
    files = []
    for rel in include_paths:
        base = root / rel
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                files.append(p)
    # 用相對路徑排序，確保每次順序一致
    files.sort(key=lambda p: str(p.relative_to(root)))
    return files


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_structure_hash(root: Path, include_paths):
    """
    回傳：
      - global_hash: 整體結構 hash
      - file_hashes: {relative_path: sha256}
    """
    paths = get_include_paths(SCAN_MODE)
    files = iter_files(root, paths)
    file_hashes = {}

    for f in files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        file_hashes[rel] = file_sha256(f)

    # 用「檔名 + 單檔 hash」再組成一個總 hash
    h = hashlib.sha256()
    for rel in sorted(file_hashes.keys()):
        h.update(rel.encode("utf-8"))
        h.update(file_hashes[rel].encode("utf-8"))
    global_hash = h.hexdigest()

    return global_hash, file_hashes


def load_version_lock():
    if not VERSION_LOCK.exists():
        return None
    with VERSION_LOCK.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_version_lock(project_name: str, version: str, global_hash: str, file_hashes: dict):
    info = {
        "project_name": project_name,
        "version": version,
        "sealed_at": datetime.now().isoformat(timespec="seconds"),
        "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "engine_version": "integrity_engine_v0.1",
        "structure_hash": global_hash,
        "files": file_hashes,
    }
    with VERSION_LOCK.open("w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"[OK] version.lock 已更新：{VERSION_LOCK}")


def cmd_seal(args):
    global SCAN_MODE
    if args.full:
        SCAN_MODE = "full"
    else:
        SCAN_MODE = "light"

    
    """
    建立 / 更新 version.lock：
    - 計算目前 engine + state 結構的 hash
    - 寫入 version.lock
    """
    project_name = args.project_name or "AlanCoreProject"
    version = args.version or "0.1.0"

    print(f"[INFO] 開始 sealing，project={project_name}, version={version}")
    paths = get_include_paths(SCAN_MODE)
    global_hash, file_hashes = compute_structure_hash(ROOT, paths)

    print(f"[INFO] 結構 hash = {global_hash}")
    save_version_lock(project_name, version, global_hash, file_hashes)
    print("[DONE] Seal 完成。")


def cmd_verify(args):
    global SCAN_MODE
    if args.full:
        SCAN_MODE = "full"
    else:
        SCAN_MODE = "light"

    
    """
    驗證目前檔案結構是否與 version.lock 一致。
    """
    lock = load_version_lock()
    if not lock:
        print("[ERR] 找不到 version.lock，無法驗證。請先執行 seal。")
        return

    print("[INFO] 讀取 version.lock 中的結構 hash ...")
    expected_hash = lock.get("structure_hash")
    expected_files = lock.get("files", {})

    paths = get_include_paths(SCAN_MODE)
    current_hash, current_files = compute_structure_hash(ROOT, paths)


    print(f"[INFO] version.lock 中的 hash = {expected_hash}")
    print(f"[INFO] 目前計算的 hash   = {current_hash}")

    # 比對整體 hash
    if current_hash != expected_hash:
        print("[WARN] 整體結構 hash 不一致！開始檢查差異...")

        # 檔案集合差異
        expected_set = set(expected_files.keys())
        current_set = set(current_files.keys())

        missing = expected_set - current_set
        extra = current_set - expected_set
        changed = set()

        for rel in expected_set & current_set:
            if expected_files[rel] != current_files[rel]:
                changed.add(rel)

        if missing:
            print("\n[DIFF] 遺失的檔案：")
            for rel in sorted(missing):
                print("  -", rel)

        if extra:
            print("\n[DIFF] 多出來的檔案：")
            for rel in sorted(extra):
                print("  +", rel)

        if changed:
            print("\n[DIFF] 內容被修改的檔案：")
            for rel in sorted(changed):
                print("  *", rel)

        print("\n[RESULT] ❌ 結構不一致，需人工確認。")
    else:
        print("[RESULT] ✅ 結構完全一致，未偵測到變動。")


def main():
    parser = argparse.ArgumentParser(description="Alan System Core - Integrity Engine")
    sub = parser.add_subparsers(dest="cmd")

    # seal
    p_seal = sub.add_parser("seal", help="產生 / 更新 version.lock")
    p_seal.add_argument("--project-name", type=str, help="專案名稱")
    p_seal.add_argument("--version", type=str, help="版本號，例如 0.1.0")
    p_seal.set_defaults(func=cmd_seal)
    p_seal.add_argument("--full", action="store_true", help="使用完整掃描模式")


    # verify
    p_verify = sub.add_parser("verify", help="驗證檔案結構是否與 version.lock 一致")
    p_verify.set_defaults(func=cmd_verify)
    p_verify.add_argument("--full", action="store_true", help="使用完整掃描模式")


    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
