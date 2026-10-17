"""✏️ ส่วนที่ 2: Embedding — แปลงข้อความเป็น vector

ใช้ embed() จาก core เพื่อเรียกโมเดล embedding (ค่า embed_model ใน manifest.json)
    from core.ollama_client import embed
    embed(["ข้อความ 1", "ข้อความ 2"])  ->  [[0.12, -0.03, ...], [...]]
"""
from core.ollama_client import embed
from student import settings


def embed_documents(texts: list[str]) -> list[list[float]]:
    """แปลง chunk ทั้งหมดของเอกสารเป็น vector (ถูกเรียกครั้งเดียวตอนรับ knowledge)"""
    if not texts:
        return []

    prefix = getattr(settings, "DOC_PREFIX", "search_document: ")
    prefixed_texts = [f"{prefix}{t}" for t in texts]

    # เรียก embed จาก core
    return embed(prefixed_texts)


def embed_query(text: str) -> list[float]:
    """แปลงคำค้น 1 ข้อความเป็น vector (ถูกเรียกทุกครั้งที่ถามคำถาม)"""
    if not text:
        return []

    prefix = getattr(settings, "QUERY_PREFIX", "search_query: ")
    prefixed_text = f"{prefix}{text}"

    # เรียก embed แล้วดึง vector ตัวแรก
    vectors = embed([prefixed_text])
    return vectors[0] if vectors else []