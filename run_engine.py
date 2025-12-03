import sys, os, runpy

# 1) 確保 sandbox 根目錄在 import 最前面
ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# 2) 強制 import engine.engine_v2 來檢查是否載入成功
try:
    import engine.engine_v2 as e
    print("[BOOT] Loaded engine module:", os.path.abspath(e.__file__))
except Exception as ex:
    print("[BOOT ERROR] Failed to load engine.engine_v2:", ex)
    sys.exit(1)

# 3) 嘗試取得 main()
if hasattr(e, "main"):
    print("[BOOT] main() detected, launching engine...")
    e.main()
else:
    print("[BOOT] No main() in engine_v2, running engine_v2 as script...")
    runpy.run_path(os.path.abspath(e.__file__), run_name="__main__")
