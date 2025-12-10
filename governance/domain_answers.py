# ============================================
# domain_answers.py — Safety Governed Answer System v3
# ============================================

from governance.domain_detect import detect_domain

# --------------------------------------------------
# Crisis & Support Templates
# --------------------------------------------------

CRISIS_TEMPLATE = (
    "我看得出來你現在真的很辛苦，會說出這樣的話，一定已經撐了很久了。\n\n"
    "此刻最重要的是：**先確保你的安全**。\n"
    "如果你有立即的危險或傷害自己的衝動，請馬上尋求身邊可信任的人，或聯絡緊急服務協助。\n\n"
    "你願意告訴我最讓你覺得撐不住的是什麼嗎？我會陪你一起面對。"
)

MENTAL_HEALTH_TEMPLATE = (
    "我感覺你現在承受了不少壓力。\n"
    "你想說說看最近發生了什麼嗎？我會在這裡聽你，也陪你一起找更好的方式面對。"
)

SAFETY_TEMPLATE = (
    "我希望你是安全的，也不希望你因為衝動或危險的行為受傷。\n"
    "如果你願意，我們可以一起想一些更安全、更長遠的做法來處理現在的狀況。"
)

RELATIONSHIP_TEMPLATE = (
    "感覺你希望事情可以順利一些，不過我無法幫忙欺騙或操控其他人。\n"
    "或許我們可以一起找一種誠實、但不傷害彼此的方式去面對這個狀況？"
)

MANIPULATION_TEMPLATE = (
    "我不會協助欺騙或操控別人，因為那可能會造成更多傷害。\n"
    "你真正擔心的是什麼？我們可以從那裡開始想辦法。"
)

BLAME_TRANSFER_TEMPLATE = (
    "我聽得出來你現在情緒非常強烈，但我不會承擔你可能做出的危險行為的責任。\n"
    "重要的還是你的安全。你願意告訴我現在最難受的是什麼嗎？"
)

GENERAL_TEMPLATE = (
    "你願意多說一點嗎？我在聽你。"
)

# --------------------------------------------------
# Inline Crisis Detection (temporary local version)
# --------------------------------------------------

CRISIS_KEYWORDS = [
    "想死", "去死", "自殺", "活不下去", "撐不下去", "結束這一切", "毀掉自己",
    "消失比較好", "我是不是不該存在"
]


def is_mental_health_crisis(text: str) -> bool:
    return any(x in text for x in CRISIS_KEYWORDS)


# --------------------------------------------------
# Main Answer Select
# --------------------------------------------------

def answer(prompt: str) -> str:
    text = prompt.strip()

    # 1) Highest risk check
    if is_mental_health_crisis(text):
        return CRISIS_TEMPLATE

    # 2) Domain detect path
    d = detect_domain(text)

    if d == "MENTAL_HEALTH_CRISIS":
        return CRISIS_TEMPLATE
    if d == "MENTAL_HEALTH":
        return MENTAL_HEALTH_TEMPLATE
    if d == "SAFETY":
        return SAFETY_TEMPLATE
    if d == "RELATIONSHIP":
        return RELATIONSHIP_TEMPLATE
    if d == "MANIPULATION_COERCION":
        return MANIPULATION_TEMPLATE
    if d == "BLAME_TRANSFER":
        return BLAME_TRANSFER_TEMPLATE

    # Default: warm support
    return GENERAL_TEMPLATE
