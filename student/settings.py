"""✏️ ค่าที่ปรับจูนได้"""

# ---------- Chunking ----------
CHUNK_SIZE = 850
CHUNK_OVERLAP = 150
SPLIT_BY_HEADING = True
INCLUDE_HEADING = True

# ---------- Embedding ----------
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "

# ---------- Retrieval ----------
TOP_K = 6
QUERY_WITH_OPTIONS = True
HYBRID_WEIGHT = 0.6          # ให้น้ำหนัก Vector 60% และ Character 3-Gram Overlap 40%
MIN_SCORE = 0.0

# ---------- Prompt ----------
MAX_CONTEXT_CHARS = 5500