import csv
import os
import re
import time
import requests
import PyPDF2
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Constants
BASE_URL = "https://papers.nips.cc"
OUTPUT_DIR = "E:/nips_scrapper/pdfs/"
CSV_FILE = "E:/nips_scrapper/output.csv"
THREAD_COUNT = 50  # Number of concurrent threads
MAX_RETRIES = 3  # Maximum retry attempts
TIMEOUT = 60  # Request timeout in seconds
TARGET_YEARS = { "2023", "2022", "2021", "2020"}  # Years to scrape

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def initialize_csv():
    """Initialize the CSV file with headers if it does not exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Year", "Title", "PDF URL", "Abstract"])

def get_soup(url):
    """Fetch and parse the HTML content of a URL with retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"[Attempt {attempt}] Failed to fetch {url}: {e}")
            if attempt == MAX_RETRIES:
                return None
            time.sleep(2)

def sanitize_filename(filename):
    """Replace invalid filename characters with underscores."""
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def download_pdf(pdf_url, filename):
    """Download and save a PDF file."""
    filepath = os.path.join(OUTPUT_DIR, filename + ".pdf")
    
    if os.path.exists(filepath):  # Skip if already downloaded
        print(f"Skipping existing file: {filepath}")
        return filepath

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with requests.get(pdf_url, stream=True, timeout=TIMEOUT) as response:
                response.raise_for_status()
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(8192):
                        file.write(chunk)
            print(f"Saved PDF: {filepath}")
            return filepath
        except requests.RequestException as e:
            print(f"[Attempt {attempt}] Failed to download {pdf_url}: {e}")
            if attempt == MAX_RETRIES:
                print(f"Giving up on {pdf_url}")
            time.sleep(2)
    return None

def extract_abstract(pdf_path):
    """Extract the abstract from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
            # Extract first 1000 characters as abstract (adjust as needed)
            abstract = text[:1000].strip()
            return abstract if abstract else "Abstract not found"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return "Abstract not found"

def process_paper(paper_url, year):
    """Process a single paper page to find and download the PDF, and extract its abstract."""
    print(f"Processing paper: {paper_url}")
    soup = get_soup(paper_url)
    if not soup:
        return

    # Extract and sanitize the paper title
    title_tag = soup.find("title")
    paper_title = sanitize_filename(title_tag.text.strip()) if title_tag else "unknown_title"

    # Find the PDF link
    pdf_link = soup.select_one("a[href*='.pdf']")
    if pdf_link:
        pdf_url = BASE_URL + pdf_link["href"]
        print(f"Found PDF: {pdf_url}")
        
        # Download the PDF
        pdf_path = download_pdf(pdf_url, paper_title)
        
        # Extract abstract
        abstract = extract_abstract(pdf_path) if pdf_path else "PDF not found"

        # Write the metadata to CSV
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([year, paper_title, pdf_url, abstract])
    else:
        print(f"No PDF found for: {paper_url}")

def process_year(year_url, year):
    """Count the number of papers available for a given year."""
    print(f"Checking papers in year: {year_url}")
    soup = get_soup(year_url)
    if not soup:
        return 0

    paper_links = soup.select("a[href*='Abstract']")
    print(f"Year {year} has {len(paper_links)} papers.")
    
    # Process papers using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for paper_link in paper_links:
            paper_url = BASE_URL + paper_link["href"]
            executor.submit(process_paper, paper_url, year)

    return len(paper_links)

def main():
    """Main function to scrape papers from NeurIPS."""
    print(f"Connecting to {BASE_URL}")
    soup = get_soup(BASE_URL)
    if not soup:
        print("Failed to fetch the main page.")
        return

    # Initialize CSV file with headers
    initialize_csv()

    year_links = soup.select("a[href^='/paper_files/paper/']")
    total_papers = {}

    for year_link in year_links:
        year_url = BASE_URL + year_link["href"]
        year = year_url.split("/")[-1]
        
        if year in TARGET_YEARS:
            paper_count = process_year(year_url, year)
            total_papers[year] = paper_count

    print("\nExpected paper counts per year:", total_papers)

if __name__ == "__main__":
    main()
