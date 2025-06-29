import os
import fitz  # PyMuPDF
import easyocr
from .db_utils import get_db_connection, initialize_db


def create_reader():
    """Create an easyocr Reader with Chinese and English languages."""
    return easyocr.Reader(['ch_sim', 'en'], gpu=True)


def ocr_pdf_to_db(pdf_path: str, reader: easyocr.Reader, conn):
    """Perform OCR on a single PDF and store results in the database."""
    pdf_document = fitz.open(pdf_path)
    cursor = conn.cursor()
    for i, page in enumerate(pdf_document):
        pix = page.get_pixmap(dpi=400)
        img_data = pix.tobytes('png')
        results = reader.readtext(img_data, detail=0, decoder='wordbeamsearch')
        text = ','.join(results)
        cursor.execute(
            "INSERT INTO ocr_results(pdf_file, page, text) VALUES (?,?,?)",
            (os.path.basename(pdf_path), i + 1, text)
        )
    conn.commit()


def scan_folder(folder_path: str, conn):
    """Scan folder for PDFs and run OCR on each."""
    reader = create_reader()
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    for pdf in pdf_files:
        pdf_path = os.path.join(folder_path, pdf)
        ocr_pdf_to_db(pdf_path, reader, conn)

