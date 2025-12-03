import shutil
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

FOLDERS = [
    "engine",
    "state",
    "manifest"
]


def run_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(BACKUP_DIR, f"backup_{ts}")
    os.makedirs(session_dir)

    for folder in FOLDERS:
        src = os.path.join(BASE_DIR, folder)
        if os.path.exists(src):
            shutil.copytree(src, os.path.join(session_dir, folder))


    print(f"[✅] Backup complete: {session_dir}")

if __name__ == "__main__":
    run_backup()
