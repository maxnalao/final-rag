"""✏️ ส่วนที่ 3: Retrieval — ค้นหา chunk ที่เกี่ยวข้องกับคำถาม"""
import re
from core.types import Chunk
from core.utils import cosine_many
from student import settings


def make_query(question: str, options: list[str]) -> str:
    """สร้างคำค้นหา"""
    if not question:
        return "query"

    # สำหรับข้อสอบที่มีตัวเลือก ให้นำคีย์เวิร์ดในตัวเลือกมารวมด้วย
    if options:
        opt_text = " ".join([o.strip() for o in options if o.strip()])
        return f"{question.strip()} {opt_text}"

    return question.strip()


def _extract_keywords(text: str) -> set[str]:
    """สกัดคำสำคัญทั้งไทย อังกฤษ ตัวเลข และรหัสพิเศษ"""
    words = re.findall(r"[\u0E00-\u0E7Fa-zA-Z0-9_\-]+", text.lower())
    return {w for w in words if len(w) >= 2}


def search(chunks: list[Chunk], query_text: str, query_vector: list[float] | None, k: int) -> list[tuple[Chunk, float]]:
    """ค้นหา chunk ที่ตรงที่สุดโดยผสม Vector + Keyword matching"""
    if not chunks:
        return []

    # ดึง chunk เพิ่มขึ้นเล็กน้อยเพื่อให้ LLM เห็นข้อมูลครบทุกหน้า (เช่น 4-6 chunks)
    top_k = getattr(settings, "TOP_K", max(k, 5))
    hybrid_weight = getattr(settings, "HYBRID_WEIGHT", 0.5)

    has_vectors = query_vector is not None and all(c.vector is not None for c in chunks)
    if has_vectors:
        doc_vectors = [c.vector for c in chunks]
        vector_scores = cosine_many(query_vector, doc_vectors)
    else:
        vector_scores = [0.0] * len(chunks)

    query_tokens = _extract_keywords(query_text)

    scored_chunks: list[tuple[Chunk, float]] = []
    for i, chunk in enumerate(chunks):
        v_score = vector_scores[i] if has_vectors else 0.0

        chunk_tokens = _extract_keywords(chunk.text)
        if query_tokens and chunk_tokens:
            intersection = query_tokens.intersection(chunk_tokens)
            kw_score = len(intersection) / len(query_tokens)
        else:
            kw_score = 0.0

        final_score = (v_score * hybrid_weight) + (kw_score * (1.0 - hybrid_weight))
        scored_chunks.append((chunk, final_score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]