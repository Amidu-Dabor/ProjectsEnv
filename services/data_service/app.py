from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import chromadb
from typing import List
import os

app = Flask(__name__)
VECTOR_STORE = None  # Global vector store

def scrape_website(url: str) -> List[str]:
    texts = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if not href.startswith("http"):
                href = requests.compat.urljoin(url, href)
            try:
                res = requests.get(href, timeout=5)
                sub_soup = BeautifulSoup(res.text, 'html.parser')
                paragraphs = sub_soup.find_all('p')
                text = " ".join(p.get_text() for p in paragraphs)
                if text:
                    texts.append(text)
            except Exception:
                continue
    except Exception as e:
        print(f"Scraping error: {e}")
    return texts

def preprocess_and_store(texts: List[str]) -> None:
    global VECTOR_STORE
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(texts)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_STORE = Chroma.from_documents(docs, embeddings, collection_name="usiu_data")

@app.route('/scrape', methods=['GET'])
def scrape():
    url = "https://www.usiu.ac.ke/"
    texts = scrape_website(url)
    if texts:
        preprocess_and_store(texts)
        return jsonify({"status": "Scraping and indexing complete", "documents": len(texts)})
    return jsonify({"error": "Failed to scrape website"}), 500

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    global VECTOR_STORE
    data = request.json
    query = data.get("query", "")
    if VECTOR_STORE is None:
        return jsonify({"data": "Vector store not initialized. Run /scrape endpoint."})
    results = VECTOR_STORE.similarity_search(query, k=3)
    context = " ".join([doc.page_content for doc in results])
    return jsonify({"data": context})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5004))
    app.run(port=port, debug=True)
