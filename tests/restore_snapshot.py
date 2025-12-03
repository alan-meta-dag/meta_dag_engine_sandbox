"""
restore_snapshot.py
從壓縮快照 (backup/*.zip) 恢復 engine_copy/
安全可審計版本
"""

import os
import shutil
import zipfile

ENGINE_COPY = "./engine_copy"
SNAPSHOT_DIR = "./backup"


def list_snapshots():
    zips = [f for f in os.listdir(SNAPSHOT_DIR) if f.endswith(".zip")]
    zips.sort()
    return zips


def restore(snapshot_name):
    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)

    if not os.path.exists(snapshot_path):
        print(f"[ERROR] 找不到快照檔：{snapshot_path}")
        return

    # 清空 engine_copy（安全重建）
    if os.path.exists(ENGINE_COPY):
        shutil.rmtree(ENGINE_COPY)
    os.makedirs(ENGINE_COPY, exist_ok=True)

    # 解壓 snapshot
    with zipfile.ZipFile(snapshot_path, "r") as z:
        z.extractall(ENGINE_COPY)

    print(f"[RESTORE] 已成功恢復至快照：{snapshot_name}")
    print(f"[RESTORE] engine_copy/ 已與該 snapshot 同步。")


if __name__ == "__main__":
    snaps = list_snapshots()

    if not snaps:
        print("[ERROR] 沒有任何 snapshot 可用")
        exit()

    print("=== 可用 Snapshot 列表 ===")
    for i, s in enumerate(snaps, 1):
        print(f"{i}. {s}")

    idx = input("\n請輸入要恢復的編號： ")

    try:
        idx = int(idx) - 1
        restore(snaps[idx])
    except:
        print("[ERROR] 無效選擇")
