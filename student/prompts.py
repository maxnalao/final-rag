"""✏️ ส่วนที่ 4: Prompt — บอก LLM ว่าจะให้ทำอะไร"""
from student import settings


def build_mc_prompt(question: str, options: list[tuple[str, str]], hits) -> list[dict]:
    """prompt สำหรับข้อสอบปรนัย"""
    system_prompt = (
        "You are an expert Thai exam solver with meticulous reading comprehension.\n"
        "Your task is to identify the single correct multiple-choice option based strictly on the Reference Context.\n\n"
        "Rules:\n"
        "1. Context Authority: Base your decision entirely on the provided Context text and tables. Never guess.\n"
        "2. Table Interpretation: Check table row values, discount types, amounts, and minimum spends carefully.\n"
        "3. Negative Phrasing: Pay extreme attention if the question asks for NOT/FALSE ('ไม่ใช่', 'ไม่ถูกต้อง', 'ยกเว้น').\n"
        "4. Output Requirement: You must output ONLY a valid JSON object with the following schema:\n"
        '   {"answer": "<key>"}\n'
        "   where <key> is strictly one of the option letters provided (e.g. \"ก\", \"ข\", \"ค\", \"ง\", \"จ\").\n"
        "5. Do NOT include markdown blocks, reasons, or any conversational text. Return raw JSON only."
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

    # จัดรูปแบบตัวเลือกให้อ่านง่าย ชัดเจนทุกบรรทัด
    options_lines = [f"{key}. {text}" for key, text in options]
    options_str = "\n".join(options_lines)

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
        "You are an expert Python engineer.\n"
        "Strict Implementation Rules:\n"
        "1. ALWAYS include all necessary standard library imports inside the code (e.g. `import re`).\n"
        "2. Coupon Format & Validation:\n"
        "   - Standardize inputs with `.strip().upper()` immediately.\n"
        "   - The coupon code format is `BB-` followed by exactly 4 alphanumeric characters (letters/digits `[A-Z0-9]{4}`), hyphen `-`, and 2 digits (e.g. `^BB-[A-Z0-9]{4}-\\d{2}$`).\n"
        "3. Discount Rules (CRITICAL):\n"
        "   - Look at the table carefully to check the discount type:\n"
        "     * If discount is a FIXED AMOUNT (e.g. 30 บาท), return the exact fixed amount as a float (e.g. 30.0). DO NOT multiply the fixed amount by the purchase total!\n"
        "     * If discount is a PERCENTAGE (e.g. 10%), return `(purchase_amount * percentage) / 100.0`.\n"
        "   - ALWAYS check the minimum spend (ยอดซื้อขั้นต่ำ) FIRST. If `bill_amount < minimum_spend`, the discount is STRICTLY 0.0.\n"
        "   - If coupon is unknown, invalid, or does not meet minimum spend, return 0.0.\n"
        "   - Return a float value for the discount amount.\n"
        "4. Do NOT use input() or print(). Return values directly.\n"
        "5. Output ONLY the code inside a single ```python ``` block."
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