"""✏️ ส่วนที่ 4: Prompt — บอก LLM ว่าจะให้ทำอะไร"""
from student import settings


def build_mc_prompt(question: str, options: list[tuple[str, str]], hits) -> list[dict]:
    """prompt สำหรับข้อสอบปรนัย"""
    system_prompt = (
        "You are an expert Thai academic evaluator with flawless accuracy.\n"
        "Instructions:\n"
        "1. Strictly base your answer on the provided Reference Context.\n"
        "2. Check every detail in tables, conditions, numbers, and negative queries ('ไม่ใช่', 'ไม่ถูกต้อง', 'ยกเว้น').\n"
        "3. Output strictly valid JSON with keys:\n"
        '   "answer": "<exact option key: ก, ข, ค, ง, or จ>"\n'
        "4. Do NOT include any markdown fences or conversational text outside the JSON."
    )

    context_parts = []
    max_chars = getattr(settings, "MAX_CONTEXT_CHARS", 6000)
    total_chars = 0

    if hits:
        for chunk, score in hits:
            text = getattr(chunk, "text", str(chunk)).strip()
            if text:
                if total_chars + len(text) > max_chars:
                    break
                context_parts.append(text)
                total_chars += len(text)

    context_str = "\n\n---\n\n".join(context_parts) if context_parts else "ไม่มีเอกสารอ้างอิง"
    options_str = "\n".join([f"{key}. {text}" for key, text in options])

    user_content = (
        f"[เอกสารอ้างอิง]\n{context_str}\n\n"
        f"[คำถาม]\n{question}\n\n"
        f"[ตัวเลือก]\n{options_str}\n\n"
        "จงตรวจสอบตัวเลือกทั้งหมดเทียบกับเอกสารอ้างอิงและตารางอย่างละเอียด แล้วตอบคำตอบที่ถูกต้องเป็น JSON เช่น {\"answer\": \"ข\"}:"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def build_code_prompt(requirement: str, signature: str | None, entry_point: str | None, hits) -> list[dict]:
    """prompt สำหรับโจทย์เขียนโปรแกรม"""
    system_prompt = (
        "You are an expert Python software engineer.\n"
        "Strict Implementation Guidelines:\n"
        "1. ALWAYS include all necessary standard library imports inside the code (e.g., `import re`, `import math`).\n"
        "2. Coupon Validation Rules (CRITICAL):\n"
        "   - Must be CASE-INSENSITIVE (convert input strings using `.strip().upper()` immediately).\n"
        "   - Format is `BB-` prefix, followed by exactly 4 alphanumeric characters (letters/digits `[A-Z0-9]{4}`), a hyphen `-`, and 2 digits (e.g. `^BB-[A-Z0-9]{4}-\\d{2}$`).\n"
        "3. Discount Calculation Rules (CRITICAL):\n"
        "   - Read the coupon table in the context carefully:\n"
        "     * If discount type is a fixed amount (e.g. 30 บาท), return the exact float value (e.g. 30.0). DO NOT multiply by the purchase amount!\n"
        "     * If discount type is a percentage (e.g. 10%), return `(purchase_amount * percentage) / 100.0`.\n"
        "   - ALWAYS check the minimum spend (ยอดซื้อขั้นต่ำ) FIRST. If `bill_amount < minimum_spend`, the discount is STRICTLY 0.0.\n"
        "   - If coupon is invalid, unknown, expired, or does not meet minimum spend, return 0.0.\n"
        "   - Return a float value for monetary discounts, bool for validations.\n"
        "4. Exact signature & entry point name must be preserved. Do NOT use input() or print(). Return values directly.\n"
        "5. Return ONLY the code inside a single ```python ``` block."
    )

    context_parts = []
    if hits:
        for chunk, score in hits:
            text = getattr(chunk, "text", str(chunk)).strip()
            if text:
                context_parts.append(text)

    context_str = "\n\n---\n\n".join(context_parts)

    user_content = f"### Requirement:\n{requirement}\n\n"
    if context_str:
        user_content += f"### Business Rules & Reference Tables:\n{context_str}\n\n"

    if signature:
        user_content += f"### Function Signature:\n```python\n{signature}\n```\n\n"
    elif entry_point:
        user_content += f"### Function Name:\n`{entry_point}`\n\n"

    user_content += "Write the complete, bug-free Python function:"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]