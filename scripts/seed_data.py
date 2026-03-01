import sys
sys.path.append(".")

from src.ingestion import scrape_multiple_schemes
from src.indexing import index_documents

# 10 popular schemes to start with
SCHEME_URLS = [
    "https://www.myscheme.gov.in/schemes/pmksny",
    "https://www.myscheme.gov.in/schemes/pmjdy",
    "https://www.myscheme.gov.in/schemes/pmjjby",
    "https://www.myscheme.gov.in/schemes/pmsby",
    "https://www.myscheme.gov.in/schemes/apy",
    "https://www.myscheme.gov.in/schemes/pmay-g",
    "https://www.myscheme.gov.in/schemes/nfbs",
    "https://www.myscheme.gov.in/schemes/ignoaps",
    "https://www.myscheme.gov.in/schemes/pmmvy",
    "https://www.myscheme.gov.in/schemes/bbbp",
]

if __name__ == "__main__":
    print("Step 1: Scraping schemes...")
    documents = scrape_multiple_schemes(SCHEME_URLS, delay=1.5)
    
    if not documents:
        print("No documents scraped. Check your internet connection.")
        sys.exit(1)
    
    print(f"\nStep 2: Indexing {len(documents)} schemes into Qdrant...")
    index_documents(documents)
    
    print("\nDone! Your bot now has data to answer questions.")