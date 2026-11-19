import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

def clean_text(text: str) -> str:
    """Normalize whitespace and strip unprintable characters."""
    text = re.sub(r'[\r\n]{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def extract_text_from_file(file_path: Path) -> str:
    """Extract raw text from various document formats."""
    ext = file_path.suffix.lower()
    
    if ext in ['.txt', '.md', '.markdown', '.json', '.csv']:
        for encoding in ['utf-8', 'utf-8-sig', 'gb18030', 'gbk', 'big5', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return clean_text(f.read())
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Unable to decode text file: {file_path.name}")
        
    elif ext == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ''
                if text.strip():
                    pages.append(f"--- Page {i+1} ---\n{text.strip()}")
            return clean_text('\n\n'.join(pages))
        except Exception as e:
            raise ValueError(f"Error parsing PDF file: {e}")

    elif ext in ['.docx', '.doc']:
        try:
            import docx
            doc = docx.Document(str(file_path))
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paras.append(row_text)
            return clean_text('\n\n'.join(paras))
        except Exception as e:
            raise ValueError(f"Error parsing DOCX file: {e}")

    elif ext in ['.pptx', '.ppt']:
        try:
            from pptx import Presentation
            prs = Presentation(str(file_path))
            slides_text = []
            for i, slide in enumerate(prs.slides):
                slide_content = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_content.append(shape.text.strip())
                if slide_content:
                    slides_text.append(f"--- Slide {i+1} ---\n" + "\n".join(slide_content))
            return clean_text('\n\n'.join(slides_text))
        except Exception as e:
            raise ValueError(f"Error parsing PPTX file: {e}")

    elif ext in ['.xlsx', '.xls']:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(file_path), data_only=True)
            sheets_text = []
            for sheet in wb.worksheets:
                rows_text = []
                for row in sheet.iter_rows(values_only=True):
                    row_vals = [str(val).strip() for val in row if val is not None and str(val).strip()]
                    if row_vals:
                        rows_text.append(" | ".join(row_vals))
                if rows_text:
                    sheets_text.append(f"--- Sheet: {sheet.title} ---\n" + "\n".join(rows_text))
            return clean_text('\n\n'.join(sheets_text))
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {e}")

    else:
        # Fallback to binary/text attempt
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return clean_text(f.read())
        except Exception as e:
            raise ValueError(f"Unsupported file type {ext}: {e}")

def chunk_document(text: str, target_chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
    """
    Split text into semantic chunks for retrieval and inline citations.
    Returns list of dict with 'index', 'content', 'offset'.
    """
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    current_offset = 0
    chunk_index = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > target_chunk_size and current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "chunk_index": chunk_index,
                "content": chunk_text,
                "char_offset": current_offset
            })
            chunk_index += 1
            current_offset += len(chunk_text)
            
            # Keep overlap if possible
            if len(current_chunk) > 1:
                current_chunk = [current_chunk[-1], para]
                current_len = len(current_chunk[0]) + para_len
            else:
                current_chunk = [para]
                current_len = para_len
        else:
            current_chunk.append(para)
            current_len += para_len

    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        chunks.append({
            "chunk_index": chunk_index,
            "content": chunk_text,
            "char_offset": current_offset
        })

    return chunks
