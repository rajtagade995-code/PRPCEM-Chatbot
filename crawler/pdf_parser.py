"""
PRPCEM College Assistant - PDF Parser
Safely downloads official PRPCEM PDFs and extracts text using pypdf/PyPDF2.
"""

import os
import io
import requests
import config

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

class PDFParser:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or config.PDF_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def extract_text_from_url(self, pdf_url):
        """Downloads PDF from official URL and extracts clean textual content."""
        result = {
            "url": pdf_url,
            "title": os.path.basename(pdf_url.split("?")[0]) or "PRPCEM Official Document",
            "content": "",
            "category": "Official Documents",
            "success": False,
            "page_count": 0
        }

        try:
            headers = {"User-Agent": config.CRAWLER_USER_AGENT}
            response = requests.get(pdf_url, headers=headers, timeout=config.REQUEST_TIMEOUT, stream=True)
            if response.status_code != 200:
                result["content"] = f"Official PRPCEM Document available at: {pdf_url}"
                return result

            # Limit download size to 15MB
            pdf_bytes = io.BytesIO()
            total_downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    pdf_bytes.write(chunk)
                    total_downloaded += len(chunk)
                    if total_downloaded > 15 * 1024 * 1024:
                        break

            pdf_bytes.seek(0)
            extracted_pages = []

            if PYPDF_AVAILABLE:
                try:
                    reader = pypdf.PdfReader(pdf_bytes)
                    result["page_count"] = len(reader.pages)
                    if reader.metadata and reader.metadata.title:
                        result["title"] = reader.metadata.title

                    # Read up to 40 pages
                    for idx in range(min(len(reader.pages), 40)):
                        page = reader.pages[idx]
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text)
                    result["success"] = True
                except Exception:
                    pass

            # Fallback to PyPDF2 if needed
            if not extracted_pages and PYPDF2_AVAILABLE:
                try:
                    pdf_bytes.seek(0)
                    reader = PyPDF2.PdfReader(pdf_bytes)
                    result["page_count"] = len(reader.pages)
                    for idx in range(min(len(reader.pages), 40)):
                        page = reader.pages[idx]
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text)
                    result["success"] = True
                except Exception:
                    pass

            if extracted_pages:
                full_text = "\n\n".join(extracted_pages).strip()
                result["content"] = full_text
            else:
                # If PDF text extraction fails (e.g., scanned image PDF),
                # Requirement #9: Store the PDF URL and display it as official source. Do NOT invent information.
                result["content"] = f"Official PRPCEM document available at: {pdf_url}"

            return result

        except Exception as e:
            result["content"] = f"Official PRPCEM document link: {pdf_url}"
            return result
