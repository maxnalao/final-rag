"""✏️ ค่าที่ปรับจูนได้ — รวมไว้ที่เดียว แก้ที่นี่แล้วรัน selfcheck ดูผล"""

# ---------- Chunking (student/chunking.py) ----------
CHUNK_SIZE = 800            # ความยาวสูงสุดของ chunk (ตัวอักษร)
CHUNK_OVERLAP = 120         # ส่วนที่ซ้อนกันระหว่าง chunk
SPLIT_BY_HEADING = True     # แบ่งตามหัวข้อ markdown (#) ก่อน
INCLUDE_HEADING = True      # ใส่ชื่อหัวข้อไว้ต้น chunk

# ---------- Embedding (student/embedding.py) ----------
DOC_PREFIX = "search_document: "    # prefix สำหรับเอกสาร
QUERY_PREFIX = "search_query: "     # prefix สำหรับคำค้น

# ---------- Retrieval (student/retrieval.py) ----------
TOP_K = 6                   # จำนวน chunk ที่ดึงมาส่งให้ LLM
QUERY_WITH_OPTIONS = True   # รวมข้อความตัวเลือกเข้าไปในคำค้น
HYBRID_WEIGHT = 0.4         # น้ำหนัก keyword 40% (ช่วยดึงคำไทย ตัวเลข รหัสคูปอง)
MIN_SCORE = 0.0             # คะแนนขั้นต่ำ

# ---------- Prompt (student/prompts.py) ----------
MAX_CONTEXT_CHARS = 5000    # ความยาวรวมของเอกสารใน prompt (ปลอดภัย ไม่เกิน context window)