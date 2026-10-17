"""✏️ ส่วนที่ 3: Retrieval — ค้นหา chunk ที่เกี่ยวข้องกับคำถาม (Enhanced Hybrid Search)"""
import re
from core.types import Chunk
from core.utils import cosine_many
from student import settings


def make_query(question: str, options: list[str]) -> str:
    """สร้างคำค้นหาที่ครอบคลุมคำถามและตัวเลือกทั้งหมด"""
    if not question:
        return "query"

    use_options = getattr(settings, "QUERY_WITH_OPTIONS", True)
    if use_options and options:
        opts_cleaned = " ".join([opt.strip() for opt in options if opt and opt.strip()])
        return f"{question.strip()} {opts_cleaned}"

    return question.strip()


def _get_ngrams(text: str, n: int = 3) -> set[str]:
    """สร้าง character n-grams สำหรับภาษาไทยและอังกฤษเพื่อแก้ปัญหาการตัดคำภาษาไทย"""
    cleaned = re.sub(r"\s+", "", text.lower())
    if len(cleaned) < n:
        return {cleaned} if cleaned else set()
    return {cleaned[i:i + n] for i in range(len(cleaned) - n + 1)}


def _calculate_ngram_similarity(query: str, text: str) -> float:
    """คำนวณความคล้ายของคำแบบ n-gram overlap"""
    q_ngrams = _get_ngrams(query, 3)
    if not q_ngrams:
        return 0.0

    t_ngrams = _get_ngrams(text, 3)
    if not t_ngrams:
        return 0.0

    intersection = q_ngrams.intersection(t_ngrams)
    return len(intersection) / len(q_ngrams)


def search(chunks: list[Chunk], query_text: str, query_vector: list[float] | None, k: int) -> list[tuple[Chunk, float]]:
    """ค้นหา chunk ด้วย Hybrid Search (Dense Vector + Character 3-Gram Overlap)"""
    if not chunks:
        return []

    top_k = getattr(settings, "TOP_K", k)
    hybrid_weight = getattr(settings, "HYBRID_WEIGHT", 0.6)
    min_score = getattr(settings, "MIN_SCORE", 0.0)

    # 1. คำนวณ Vector Score
    has_vectors = query_vector is not None and all(c.vector is not None for c in chunks)
    if has_vectors:
        doc_vectors = [c.vector for c in chunks]
        vector_scores = cosine_many(query_vector, doc_vectors)
    else:
        vector_scores = [0.0] * len(chunks)

    # 2. คำนวณ Keyword / N-gram Score
    scored_chunks: list[tuple[Chunk, float]] = []
    for i, chunk in enumerate(chunks):
        v_score = vector_scores[i] if has_vectors else 0.0
        kw_score = _calculate_ngram_similarity(query_text, chunk.text)

        if has_vectors:
            final_score = (v_score * hybrid_weight) + (kw_score * (1.0 - hybrid_weight))
        else:
            final_score = kw_score

        if final_score >= min_score:
            scored_chunks.append((chunk, final_score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]