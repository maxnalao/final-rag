"""✏️ ส่วนที่ 1: Chunking — แบ่งเอกสารเป็นชิ้น (chunk)

เอกสารที่ได้รับเป็น markdown เช่น lecture note หรือ case study ที่มีหัวข้อ (#, ##), ตาราง และ code block
ชิ้นที่แบ่งแล้วจะถูกนำไปทำ embedding และใช้ค้นหาตอนตอบคำถาม
"""
import re
from student import settings


def _split_into_paragraphs(section_text: str) -> list[str]:
    """แยกข้อความย่อยตามย่อหน้า โดยไม่ตัดกลาง code block หรือ table"""
    lines = section_text.split("\n")
    blocks = []
    current_block = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block

        current_block.append(line)

        # ตัดย่อหน้าเมื่อเจอบรรทัดว่าง และไม่ได้อยู่ข้างใน code block
        if not in_code_block and line.strip() == "" and current_block:
            joined = "\n".join(current_block).strip()
            if joined:
                blocks.append(joined)
            current_block = []

    if current_block:
        joined = "\n".join(current_block).strip()
        if joined:
            blocks.append(joined)

    return blocks


def split(doc_id: str, text: str) -> list[str]:
    """แบ่งเอกสาร Markdown เป็น chunk โดยแยกตามหัวข้อและควบคุมขนาดไม่ให้ยาวเกินไป"""
    if not text or not text.strip():
        return [f"[{doc_id}]"]

    chunk_size = getattr(settings, "CHUNK_SIZE", 800)
    chunk_overlap = getattr(settings, "CHUNK_OVERLAP", 120)

    # 1. แยกตามหัวข้อ Markdown (#, ##, ###)
    header_pattern = r"(?=(?:\n|^)#{1,4}\s+)"
    raw_sections = re.split(header_pattern, text.strip())

    chunks = []

    for section in raw_sections:
        section = section.strip()
        if not section:
            continue

        # ถ้าขนาดยังไม่เกิน chunk_size ให้เก็บเป็น 1 chunk ทันที
        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        # ถ้าหัวข้อยาวเกินไป ให้ดึงชื่อหัวข้อมาติดไว้หน้าทุก chunk ย่อย
        first_line = section.split("\n", 1)[0]
        header_prefix = first_line if first_line.startswith("#") else ""

        # แยกย่อยตามย่อหน้า
        paragraphs = _split_into_paragraphs(section)
        current_chunk = header_prefix + "\n" if header_prefix else ""

        for p in paragraphs:
            # ถ้าเป็นบรรทัดหัวข้อเดิม ไม่ต้องใส่ซ้ำ
            if header_prefix and p.strip() == header_prefix.strip():
                continue

            if len(current_chunk) + len(p) + 1 <= chunk_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # เริ่ม chunk ใหม่พร้อมใส่ header_prefix และดึง overlap บางส่วนมาด้วย
                overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = f"{header_prefix}\n... {overlap_text}\n{p}\n\n" if header_prefix else f"... {overlap_text}\n{p}\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

    return chunks if chunks else [text.strip()]