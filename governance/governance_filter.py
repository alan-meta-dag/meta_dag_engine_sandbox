# governance/governance_filter.py
# 多領域治理輸出過濾：限制冗長、移除人格化語氣、域內壓縮

import re
from typing import Tuple

from governance.domain_detect import detect_domain


def _basic_sanitize(text: str) -> str:
    """通用層：限制長度 + 移除常見人格化句子。"""
    if not text:
        return ""

    # 1) 限制前幾行，避免模型一直講
    lines = text.splitlines()
    # 保留前 8 行，遇到極度冗長時仍可看出結構
    lines = lines[:8]
    text = "\n".join(lines)

    # 2) 移除人格化 / 客套話
    patterns = [
        r"\bAs an AI\b",
        r"\bAs a language model\b",
        r"\bI'm excited\b",
        r"\bI am excited\b",
        r"\bI'm happy to\b",
        r"\bI would be happy to\b",
        r"\bI don't have feelings\b",
        r"\bIt's nice to meet you\b",
        r"\bI don't have personal experiences\b",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    # 收斂多餘空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _meta_dag_filter(text: str) -> str:
    """Meta-DAG 領域：偏工程、短句、避免廢話。"""
    if not text:
        return ""

    # 只保留第一或第二個句子（避免長篇歷史故事）
    parts = re.split(r"(?<=[。.!?])\s+", text)
    short = " ".join(parts[:2]).strip()

    # 加上簡短標記說明這是治理後的簡述
    if "Meta-DAG" not in short and "meta-dag" not in short.lower():
        short += " (Meta-DAG brief)"

    return short


def _governance_filter(text: str) -> str:
    """治理 / policy 類：允許條列，但仍做壓縮與去 emoji。"""
    if not text:
        return ""

    # 去掉 emoji 類字元（簡化處理）
    text = re.sub(r"[^\w\s\-\.\,\:\;\(\)\[\]{}\/\u4e00-\u9fff]", "", text)

    # 限制總長度
    if len(text) > 400:
        text = text[:400] + " ..."

    return text.strip()


def _code_filter(text: str) -> str:
    """程式碼領域：盡量保留 code block，略縮說明文字。"""
    if not text:
        return ""

    # 優先抓 ``` 區塊
    code_block = re.search(r"```.*?```", text, flags=re.DOTALL)
    if code_block:
        code = code_block.group(0)
        # 前面加一行單句說明（如果有）
        first_line = text.splitlines()[0].strip()
        if len(first_line) > 120:
            first_line = first_line[:120] + " ..."
        return (first_line + "\n\n" + code).strip()

    # 沒有 code block，就只留前幾行
    lines = text.splitlines()[:10]
    return "\n".join(lines).strip()


def _finance_filter(text: str) -> str:
    """財經領域：保留結構，但避免看起來像具體操作建議。"""
    if not text:
        return ""

    # 移除過度肯定／命令式句子（極簡版）
    text = re.sub(
        r"(必買|一定會漲|保證獲利|all[- ]in|all in)",
        "[filtered]",
        text,
        flags=re.IGNORECASE,
    )

    if len(text) > 400:
        text = text[:400] + " ..."

    return text.strip()


def filter_response(user_input: str, model_output: str) -> Tuple[str, str]:
    """
    多領域治理主入口：
    - 根據 user_input 判斷 domain
    - 先走 basic_sanitize
    - 再走 domain-specific filter
    回傳: (domain, filtered_text)
    """
    domain = detect_domain(user_input)
    raw = (model_output or "").strip()

    base = _basic_sanitize(raw)

    if domain == "META_DAG":
        final = _meta_dag_filter(base)
    elif domain == "GOVERNANCE":
        final = _governance_filter(base)
    elif domain == "CODE":
        final = _code_filter(base)
    elif domain == "FINANCE":
        final = _finance_filter(base)
    else:
        # GENERAL：只做 basic sanitize + 適度壓縮
        final = base
        if len(final) > 400:
            final = final[:400] + " ..."

    final = final.strip()
    if not final:
        final = "[Meta-DAG Engine Empty Response]"

    return domain, final
