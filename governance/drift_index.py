# governance/drift_index.py
import random

def compute_drift_index() -> float:
    """
    MVP: 假資料，之後會接 baseline 差異算法
    """
    return round(random.uniform(0.0, 1.0), 3)
