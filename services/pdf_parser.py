"""
pdf_parser.py
--------------------------------------------------------------------------------
PDF Parsing Service using PyMuPDF (fitz) with OCR Fallback.
Extracts raw and normalized text from PDF resumes with robust error handling.

Dual-Stage Pipeline:
1. Native Text Extraction (PyMuPDF): Fast, direct extraction from searchable PDFs.
2. OCR Fallback (RapidOCR): Automatically triggered when a PDF contains little
   or no selectable text (scanned documents, image-only resumes, or screenshots).
--------------------------------------------------------------------------------
"""

import pymupdf as fitz  # PyMuPDF engine
import re
from typing import Tuple, Dict, Any, Union, Optional
import io

# Lazy-loaded singleton instance of RapidOCR to optimize startup performance
_ocr_engine = None


def get_ocr_engine():
    """
    Returns the initialized RapidOCR instance, loading it on-demand
    only when an image-based or scanned PDF is actually encountered.
    """
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _ocr_engine = RapidOCR()
        except Exception as e:
            # If RapidOCR fails to load (e.g. missing dependency)
            _ocr_engine = False
    return _ocr_engine if _ocr_engine is not False else None


def clean_extracted_text(raw_text: str) -> str:
    """
    Cleans and normalizes extracted resume text:
    - Removes null bytes and non-printable control characters.
    - Normalizes diverse bullet characters (•, -, *, etc.) to standard dashes.
    - Reduces multiple consecutive blank lines to single line breaks.
    - Trims leading/trailing whitespace.
    """
    if not raw_text:
        return ""

    # Replace null characters
    text = raw_text.replace("\x00", " ")

    # Standardize bullet points
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", "\n- ", text)

    # Standardize curly quotes and apostrophes
    text = text.replace("“", "\"").replace("”", "\"").replace("’", "'").replace("‘", "'")

    # Replace multiple horizontal spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace 3 or more consecutive newlines with 2 newlines (paragraph break)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_text_from_pdf(
    pdf_source: Union[bytes, io.BytesIO, str]
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Extracts text and metadata from a PDF file source with automatic OCR fallback.

    Parameters:
        pdf_source: Either raw bytes, BytesIO buffer (e.g. from Streamlit file_uploader),
                    or a local filepath string.

    Returns:
        Tuple of (clean_text, message_or_error, metadata_dict):
        - clean_text (str): Cleaned extracted text from the PDF.
        - message_or_error (str): Informative warning or error description.
        - metadata_dict (dict): Dictionary with page_count, word_count, char_count,
                                extraction_method ('normal' or 'ocr'), is_scanned, ocr_applied.
    """
    metadata: Dict[str, Any] = {
        "page_count": 0,
        "char_count": 0,
        "word_count": 0,
        "is_scanned": False,
        "ocr_applied": False,
        "extraction_method": "none"
    }

    try:
        # 1. Validate input source
        if pdf_source is None:
            return "", "No PDF file provided.", metadata

        # Handle Streamlit UploadedFile or BytesIO
        if hasattr(pdf_source, "getvalue"):
            file_bytes = pdf_source.getvalue()
        elif hasattr(pdf_source, "read"):
            file_bytes = pdf_source.read()
        elif isinstance(pdf_source, bytes):
            file_bytes = pdf_source
        elif isinstance(pdf_source, str):
            with open(pdf_source, "rb") as f:
                file_bytes = f.read()
        else:
            return "", "Unsupported file input format.", metadata

        if not file_bytes or len(file_bytes) == 0:
            return "", "The uploaded PDF file is completely empty (0 bytes).", metadata

        # 2. Open PDF with PyMuPDF
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            return "", f"Could not read PDF format. The file might be corrupted or not a valid PDF: {str(e)}", metadata

        metadata["page_count"] = len(doc)

        if len(doc) == 0:
            doc.close()
            return "", "The uploaded PDF contains no pages.", metadata

        # Check for password encryption
        if doc.is_encrypted:
            doc.close()
            return "", "The uploaded PDF is password-protected. Please upload an unlocked PDF.", metadata

        # 3. Stage 1: Try Native Text Extraction
        extracted_pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text") or ""
            extracted_pages.append(page_text)

        full_raw_text = "\n".join(extracted_pages)
        cleaned_text = clean_extracted_text(full_raw_text)
        native_word_count = len(cleaned_text.split())

        # 4. Check if native text is sufficient (Searchable text PDF)
        if native_word_count >= 25:
            doc.close()
            metadata["char_count"] = len(cleaned_text)
            metadata["word_count"] = native_word_count
            metadata["is_scanned"] = False
            metadata["ocr_applied"] = False
            metadata["extraction_method"] = "normal"
            return cleaned_text, "", metadata

        # 5. Stage 2: OCR Fallback for Scanned / Image-based PDF
        metadata["is_scanned"] = True
        ocr_engine = get_ocr_engine()

        if ocr_engine is None:
            doc.close()
            metadata["char_count"] = len(cleaned_text)
            metadata["word_count"] = native_word_count
            metadata["extraction_method"] = "normal"
            return (
                cleaned_text,
                "Warning: Scanned or image-based PDF detected, but OCR engine is not available. Please upload a searchable text PDF.",
                metadata
            )

        # Render PDF pages to high-resolution images and run RapidOCR
        ocr_extracted_lines = []
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Render page at 200 DPI for optimal OCR recognition accuracy
                pixmap = page.get_pixmap(dpi=200)
                img_bytes = pixmap.tobytes("png")

                # Perform OCR inference
                ocr_result, _ = ocr_engine(img_bytes)
                if ocr_result:
                    for item in ocr_result:
                        # item format: [box_coordinates, text_string, confidence_score]
                        if len(item) >= 2 and item[1]:
                            line_text = str(item[1]).strip()
                            if line_text:
                                ocr_extracted_lines.append(line_text)

            doc.close()

            full_ocr_text = "\n".join(ocr_extracted_lines)
            cleaned_ocr_text = clean_extracted_text(full_ocr_text)
            ocr_word_count = len(cleaned_ocr_text.split())

            if ocr_word_count >= 10:
                metadata["char_count"] = len(cleaned_ocr_text)
                metadata["word_count"] = ocr_word_count
                metadata["ocr_applied"] = True
                metadata["extraction_method"] = "ocr"
                return (
                    cleaned_ocr_text,
                    "Scanned document detected. Text extracted successfully using OCR Fallback Engine.",
                    metadata
                )
            else:
                # OCR ran but yielded very little recognizable text
                combined = cleaned_ocr_text if ocr_word_count > native_word_count else cleaned_text
                metadata["char_count"] = len(combined)
                metadata["word_count"] = len(combined.split())
                metadata["extraction_method"] = "ocr" if ocr_word_count > 0 else "normal"
                return (
                    combined,
                    "Warning: Scanned/image-based PDF detected. OCR fallback was applied, but text appears low-resolution or handwritten. Please check PDF quality.",
                    metadata
                )

        except Exception as ocr_err:
            doc.close()
            metadata["char_count"] = len(cleaned_text)
            metadata["word_count"] = native_word_count
            metadata["extraction_method"] = "normal"
            return (
                cleaned_text,
                f"Warning: Scanned PDF detected, but OCR processing encountered an issue: {str(ocr_err)}",
                metadata
            )

    except Exception as general_err:
        return "", f"Unexpected error while extracting PDF text: {str(general_err)}", metadata
