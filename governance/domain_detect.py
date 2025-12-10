# governance/domain_detect.py

import re

# ================================
# 危險 / 風險語料清單
# ================================

# 高風險心理 / 自傷傾向
MH_CRISIS_PATTERNS = [
    r"不該存在",
    r"活著有什麼意義",
    r"活著有什麼用",
    r"活不下去",
    r"結束這一切",
    r"想死",
    r"去死",
    r"傷害自己",
    r"自殺",
    r"毀掉自己",
    r"我消失會不會比較好",
]

# 一般心理困擾
MH_GENERAL_PATTERNS = [
    r"好累",
    r"壓力好大",
    r"撐不住",
    r"情緒崩潰",
    r"過得很痛苦",
]

# 危險行為 / 違法
SAFETY_PATTERNS = [
    r"危險.*事",
    r"做.*危險",
    r"傷害別人",
    r"犯法",
    r"犯罪",
]

# 操控 / 欺騙（廣義）
MANIPULATION_PATTERNS = [
    r"(幫我|一起).*騙",
    r"騙(他|她|人)",
    r"說謊",
    r"瞞著",
    r"欺騙",
]

# 歸罪式威脅
BLAME_PATTERNS = [
    r"都是你害的",
    r"是你害的",
    r"如果我.*死.*你害的",
]

# 人際議題（低風險）
RELATION_PATTERNS = [
    r"幫我[瞞騙]",
]

# 技術治理領域
META_DAG_PATTERNS = [
    r"meta[\-\s]?dag",
    r"治理引擎",
    r"治理閾值",
    r"\bdrift\b",
    r"semantic\s+drift",
    r"tul[\s\-]*協(議|定)",
    r"t\.?u\.?l",  # ex: T.U.L / tul
]

# ================================
# utils
# ================================
def _match_any(text: str, patterns) -> bool:
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False

# ================================
# Domain 決策邏輯
# ================================
def detect_domain(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "GENERAL"

    # 風險優先順序：先高風險 → 後其他分類
    if _match_any(t, MANIPULATION_PATTERNS):
        return "MANIPULATION_COERCION"
    if _match_any(t, MH_CRISIS_PATTERNS):
        return "MENTAL_HEALTH_CRISIS"
    if _match_any(t, SAFETY_PATTERNS):
        return "SAFETY"
    if _match_any(t, BLAME_PATTERNS):
        return "BLAME_TRANSFER"
    if _match_any(t, MH_GENERAL_PATTERNS):
        return "MENTAL_HEALTH"
    if _match_any(t, META_DAG_PATTERNS):
        return "META_DAG"
    if _match_any(t, RELATION_PATTERNS):
        return "RELATIONSHIP"

    return "GENERAL"
