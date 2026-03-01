import requests
from bs4 import BeautifulSoup
import pymupdf
from pathlib import Path
import time

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    doc = pymupdf.open(str(pdf_path))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def scrape_scheme_from_myscheme(scheme_url: str) -> dict:
    """Scrape a single scheme page from myscheme.gov.in."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"
    }
    try:
        response = requests.get(scheme_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.find("h1")
        title_text = title.get_text(strip=True) if title else "Unknown Scheme"

        # Extract main content paragraphs
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        return {
            "title": title_text,
            "url": scheme_url,
            "content": content,
            "source": "myscheme.gov.in"
        }
    except Exception as e:
        print(f"Failed to scrape {scheme_url}: {e}")
        return None


def load_all_pdfs() -> list[dict]:
    """Load and extract text from all PDFs in raw_pdfs directory."""
    documents = []
    pdf_files = list(RAW_PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs found in data/raw_pdfs/")
        return documents

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        text = extract_text_from_pdf(pdf_path)
        if text:
            documents.append({
                "title": pdf_path.stem,
                "content": text,
                "source": pdf_path.name
            })

    print(f"Loaded {len(documents)} PDFs")
    return documents


def scrape_multiple_schemes(urls: list[str], delay: float = 1.0) -> list[dict]:
    """Scrape multiple scheme pages with a polite delay."""
    results = []
    for url in urls:
        print(f"Scraping: {url}")
        data = scrape_scheme_from_myscheme(url)
        if data:
            results.append(data)
        time.sleep(delay)
    print(f"Scraped {len(results)} schemes")
    return results