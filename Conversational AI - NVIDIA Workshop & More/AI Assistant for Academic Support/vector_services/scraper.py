import os
import re
import shutil
from datetime import datetime
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Import your embeddings constructor.
from langchain_openai import OpenAIEmbeddings
embeddings_constructor = lambda: OpenAIEmbeddings()

def scrape_preprocess_and_populate_folders(base_url: str,
                                           max_depth: int = 3,
                                           max_pages: int = 200,
                                           min_docs_per_category: int = 500,
                                           max_rounds: int = 20):
    """
    Scrapes the given base_url (via sitemap or recursive crawl) and saves each page's
    content as a Markdown file into its corresponding category folder within "usiu-knowledge-base".
    
    The process is repeated in rounds until every category folder has at least min_docs_per_category
    documents. (If no new pages are found in a round, the loop will break to avoid an infinite loop.)
    
    After all categories have been filled, the vector store is updated (or created) with all documents.
    If the vector store already exists, new data is appended.
    
    Parameters:
        base_url (str): The URL to start scraping.
        max_depth (int): Maximum recursive crawl depth.
        max_pages (int): Maximum pages to process per round.
        min_docs_per_category (int): Each category must have at least this many documents.
        max_rounds (int): Maximum scraping rounds to attempt (to avoid an infinite loop).
    """
    base_dir = "usiu-knowledge-base"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # Define all categories.
    all_categories = list({
        "admissions", "academics", "campus", "research", "student_support",
        "contact", "sports", "resources", "events", "news", "policies",
        "exchange", "academic_calendar", "tuition", "financial_aid", "scholarships", "about"
    }) + ["other"]
    
    # Ensure each category folder exists.
    for category in all_categories:
        os.makedirs(os.path.join(base_dir, category), exist_ok=True)
    
    print("Categories to scrape (all will be populated):", all_categories)
    
    # Define keywords for categorization.
    CATEGORY_KEYWORDS = {
        "admissions": ["admissions", "apply", "financial aid", "scholarship", "financial support", "cost", "tuition", "registration"],
        "academics": ["academic", "course", "program", "department", "faculty", "study"],
        "campus": ["campus", "facility", "location", "accommodation", "residence"],
        "research": ["research", "innovation", "experiment", "laboratory"],
        "student_support": ["support", "student services", "counsel", "career", "wellness", "assistance"],
        "contact": ["contact", "email", "phone", "information"],
        "sports": ["sports", "team", "coach", "player", "club", "uniform", "training"],
        "resources": ["resources", "library", "resource center", "bookstore", "resource management"],
        "events": ["events", "calendar", "program", "meeting", "seminar", "workshop"],
        "news": ["news", "announcements", "blog", "press release", "media"],
        "policies": ["policies", "policy", "regulations", "laws", "procedures"],
        "exchange": ["exchange", "student visa", "student loans", "student aid"],
        "academic_calendar": ["academic calendar", "schedule", "dates"],
        "tuition": ["tuition", "financial aid", "financial support", "cost"],
        "financial_aid": ["financial aid", "scholarship", "financial support", "cost"],
        "scholarships": ["scholarship", "financial aid", "scholarships", "cost"],
        "about": ["about usiu-africa", "mission", "vision", "history", "mission statement"],
    }
    
    def categorize_page(url: str, text: str) -> str:
        lower_url = url.lower()
        lower_text = text.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_url or kw in lower_text:
                    return category
        return "other"
    
    def process_page(url: str):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, timeout=60, headers=headers)
            if response.status_code != 200:
                return False
            if "text/html" not in response.headers.get("Content-Type", ""):
                return False
            html = response.text
        except Exception as e:
            print(f"Failed to retrieve {url}: {e}")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text(separator=" ", strip=True)
        if len(text_content) < 200:
            print(f"Skipping {url}: content too short ({len(text_content)} chars).")
            return False
        
        category = categorize_page(url, text_content)
        save_dir = os.path.join(base_dir, category)
        parsed_url = urlparse(url)
        filename_part = parsed_url.path.replace("/", "_").strip("_")
        if not filename_part:
            filename_part = "index"
        filename_part = re.sub(r'\W+', '_', filename_part)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename_part}.md"
        file_path = os.path.join(save_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                title_tag = soup.find("title")
                title_text = title_tag.get_text(strip=True) if title_tag else "No Title"
                f.write(f"# {title_text}\n")
                f.write(f"URL: {url}\n\n")
                f.write(text_content)
            print(f"Saved content from {url} to {file_path} under category '{category}'.")
            return True
        except Exception as e:
            print(f"Error saving {url}: {e}")
            return False
    
    # Attempt to retrieve URLs from a sitemap.
    sitemap_url = urljoin(base_url, "sitemap.xml")
    urls_to_process = []
    try:
        sitemap_response = requests.get(sitemap_url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
        if sitemap_response.status_code == 200 and "xml" in sitemap_response.headers.get("Content-Type", ""):
            tree = ET.fromstring(sitemap_response.content)
            urls_to_process = [elem.text for elem in tree.iter("loc") if elem.text.startswith(base_url)]
            print(f"Found sitemap with {len(urls_to_process)} URLs.")
    except Exception as e:
        print("Sitemap not found or could not be parsed, falling back to recursive crawl.")
    
    # Use a persistent visited set to avoid processing the same URL twice.
    visited = set()
    
    # Recursive crawl definition.
    def crawl(url: str, depth: int, pages_processed: list):
        if depth > max_depth:
            return
        if url in visited:
            return
        visited.add(url)
        if process_page(url):
            pages_processed.append(url)
        # Stop if we have reached the round limit.
        if len(pages_processed) >= max_pages:
            return
        try:
            response = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return
            if "text/html" not in response.headers.get("Content-Type", ""):
                return
            html = response.text
        except Exception as e:
            print(f"Failed to retrieve {url} during crawl: {e}")
            return
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(url, href)
            parsed_link = urlparse(absolute_url)
            if parsed_link.netloc != urlparse(base_url).netloc:
                continue
            absolute_url = absolute_url.split("#")[0]
            if absolute_url and absolute_url not in visited:
                crawl(absolute_url, depth + 1, pages_processed)
                if len(pages_processed) >= max_pages:
                    break

    def all_categories_filled():
        for category in all_categories:
            category_path = os.path.join(base_dir, category)
            md_files = [f for f in os.listdir(category_path) if f.endswith(".md")]
            if len(md_files) < min_docs_per_category:
                return False
        return True

    round_count = 0
    # Repeat scraping rounds until every category reaches the minimum document count
    while not all_categories_filled() and round_count < max_rounds:
        round_count += 1
        print(f"\n--- Scraping round {round_count} ---")
        pages_processed = []
        if urls_to_process:
            new_count = 0
            for url in urls_to_process:
                if url not in visited:
                    if process_page(url):
                        pages_processed.append(url)
                        new_count += 1
                    visited.add(url)
                    if new_count >= max_pages:
                        break
            print(f"Processed {new_count} new pages from sitemap in round {round_count}.")
        else:
            crawl(base_url, 0, pages_processed)
            print(f"Processed {len(pages_processed)} new pages via recursive crawl in round {round_count}.")
        
        if not pages_processed:
            print("No new pages found in this round. Exiting to avoid an infinite loop.")
            break  # safeguard if no new pages are discovered
        
        # Report current counts per category.
        for category in all_categories:
            category_path = os.path.join(base_dir, category)
            count = len([f for f in os.listdir(category_path) if f.endswith(".md")])
            print(f"Category '{category}' has {count} documents.")
    
    if not all_categories_filled():
        print("Warning: Not all categories reached the required document count after maximum rounds.")
    else:
        print("All categories have reached the required document count.")
    
    # --- Update (or create) the vector store using all documents ---
    # Prepare an "eligible" directory containing all category folders.
    eligible_base_dir = base_dir + "-eligible"
    if not os.path.exists(eligible_base_dir):
        os.makedirs(eligible_base_dir)
    
    for category in all_categories:
        src = os.path.join(base_dir, category)
        dst = os.path.join(eligible_base_dir, category)
        if os.path.exists(dst):
            # Copy over any new files.
            for file in os.listdir(src):
                if file.endswith(".md") and not os.path.exists(os.path.join(dst, file)):
                    shutil.copy(os.path.join(src, file), os.path.join(dst, file))
        else:
            shutil.copytree(src, dst)
    
    # Update (or create) the vector store.
    from data_curator import DataCurator
    curator = DataCurator(knowledge_base_dir=eligible_base_dir)
    curator.load_documents()
    curator.split_documents()
    
    if hasattr(curator, "vectorstore_exists") and curator.vectorstore_exists():
        vector_data = curator.update_vectorstore(embeddings_constructor)
        print("Updated existing vector store with new data.")
    else:
        vector_data = curator.create_vectorstore(embeddings_constructor)
        print("Created new vector store.")
    
    return vector_data

if __name__ == "__main__":
    website_url = "https://www.usiu.ac.ke/"
    scrape_preprocess_and_populate_folders(website_url,
                                           max_depth=3,
                                           max_pages=200,
                                           min_docs_per_category=500)
