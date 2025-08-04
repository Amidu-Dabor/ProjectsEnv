# vector_services/data_curator.py
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
import importlib.metadata

# Import from new modular structures
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Import OpenAI for rate limiting
try:
    import openai
except ImportError:
    # Fallback for newer OpenAI SDK versions
    from openai import RateLimitError as OpenAIRateLimitError
    openai = type('', (), {'RateLimitError': OpenAIRateLimitError})()

def check_versions():
    """Check and print versions of key dependencies."""
    try:
        versions = {
            "langchain-core": importlib.metadata.version("langchain-core"),
            "langchain-community": importlib.metadata.version("langchain-community"),
            "langchain-chroma": importlib.metadata.version("langchain-chroma"),
            "chromadb": importlib.metadata.version("chromadb"),
            "openai": importlib.metadata.version("openai"),
            "numpy": importlib.metadata.version("numpy"),
            "scikit-learn": importlib.metadata.version("scikit-learn"),
        }
        print("Dependency versions:")
        for pkg, ver in versions.items():
            print(f"  {pkg}: {ver}")
        return versions
    except Exception as e:
        print(f"Error checking versions: {e}")
        return {}

def assign_color(doc_type: str) -> str:
    """Assign a color based on document type for visualization."""
    COLOR_MAPPING = {
        "admissions": "blue",
        "academics": "green",
        "campus": "red",
        "research": "orange",
        "student_support": "purple",
        "contact": "brown",
        "sports": "pink",
        "resources": "cyan",
        "events": "magenta",
        "news": "yellow",
        "policies": "gray",
        "exchange": "lightblue",
        "academic_calendar": "lightgreen",
        "tuition": "lightpink",
        "financial_aid": "plum",
        "scholarships": "lightgray",
        "about": "tan",
    }
    return COLOR_MAPPING.get(doc_type.lower().strip(), "black")

def rate_limit_retry(func):
    """A retry wrapper to handle OpenAI rate limit errors."""
    def wrapper(*args, **kwargs):
        max_retries = 5
        base_delay = 5  # seconds to wait on a rate limit error
        retries = 0
        
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit indicators in the error message
                if "rate limit" in error_str or "429" in error_str:
                    retries += 1
                    wait_time = base_delay * (2 ** retries)  # Exponential backoff
                    yield f"Rate limit exceeded. Retrying ({retries}/{max_retries}). Waiting {wait_time} seconds..."
                    yield f"Service unavailable at the moment. Retrying ({retries}/{max_retries}). Waiting {wait_time} seconds..."
                    time.sleep(wait_time)
                    if retries == max_retries:
                        print(f"Failed after {max_retries} retries due to rate limits")
                        raise
                else:
                    # For other errors, we don't retry
                    print(f"Error in API call: {e}")
                    raise
                
    return wrapper

def safe_embeddings_constructor():
    """
    Return an instance of OpenAIEmbeddings with rate limit retry.
    This ensures compatibility with existing vector stores built with OpenAI embeddings.
    """
    try:
        from langchain.embeddings.openai import OpenAIEmbeddings
    except ImportError:
        try:
            from langchain.embeddings import OpenAIEmbeddings
        except ImportError:
            raise ModuleNotFoundError(
                "Could not import OpenAIEmbeddings from langchain: "
                "please ensure you have langchain>=0.3.23 installed and OpenAI API key is set"
            )

    class SafeOpenAIEmbeddings(OpenAIEmbeddings):
        @rate_limit_retry
        def embed_documents(self, texts):
            # Call the original embed_documents method
            return super().embed_documents(texts)
            
        @rate_limit_retry
        def embed_query(self, text):
            # Call the original embed_query method
            return super().embed_query(text)

    print("Using OpenAI embeddings (1536 dimensions)")
    return SafeOpenAIEmbeddings()


class DataCurator:
    def __init__(self, knowledge_base_dir: str, persist_directory: str = "usiu_vector_db",
                 chunk_size: int = 2000, chunk_overlap: int = 200):
        """
        Initialize the DataCurator with paths and settings.
        
        Args:
            knowledge_base_dir: Directory containing the knowledge base documents
            persist_directory: Directory to persist the vector database
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between consecutive chunks
            collection_name: Name for the ChromaDB collection
        """
        self.knowledge_base_dir = knowledge_base_dir
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = []
        self.chunks = []
        self.vectorstore = None
        
        # Print dependency versions for debugging
        check_versions()

    def load_documents(self):
        """Load documents from the knowledge base directory."""
        base_dir = self.knowledge_base_dir
        
        # Check if directory exists
        if not os.path.exists(base_dir):
            raise ValueError(f"Knowledge base directory does not exist: {base_dir}")
            
        folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir)
                   if os.path.isdir(os.path.join(base_dir, d))]
        print("Loading documents from:", os.path.abspath(base_dir))
        
        for folder in folders:
            print(f"Folder: {os.path.basename(folder)}, Files: {len(os.listdir(folder))}")
        
        documents = []
        
        def load_folder(folder):
            """Load all documents from a folder with proper metadata."""
            doc_type = os.path.basename(folder)
            try:
                loader = DirectoryLoader(
                    folder,
                    glob="**/*.md",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                docs = loader.load()
                for doc in docs:
                    # Ensure document has metadata with source and type
                    doc.metadata["doc_type"] = doc_type
                    if "source" not in doc.metadata:
                        doc.metadata["source"] = doc.metadata.get("source", os.path.basename(folder))
                    
                print(f"Loaded {len(docs)} documents from '{doc_type}'")
                return docs
            except Exception as e:
                print(f"Error loading from {folder}: {e}")
                return []
        
        # Use thread pool to load documents in parallel
        with ThreadPoolExecutor() as executor:
            results = executor.map(load_folder, folders)
            for folder_docs in results:
                documents.extend(folder_docs)
        
        self.documents = documents
        print(f"Loaded {len(documents)} total documents from '{self.knowledge_base_dir}'.")
        return documents

    def split_documents(self):
        """Split documents into chunks for embedding."""
        splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        all_chunks = []
        docs_by_category = {}
        
        # Group documents by category for better logging
        for doc in self.documents:
            category = doc.metadata.get("doc_type", "other")
            docs_by_category.setdefault(category, []).append(doc)
        
        # Process each category
        for category, docs in docs_by_category.items():
            print(f"Processing category '{category}' with {len(docs)} documents...")
            chunks = splitter.split_documents(docs)
            print(f"Category '{category}' produced {len(chunks)} chunks.")
            all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        print(f"Total chunks generated: {len(self.chunks)}")
        return self.chunks

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for better embedding quality."""
        # Replace multiple whitespace with single space
        cleaned = re.sub(r'\s+', ' ', text)
        # Remove non-ASCII characters that might cause issues
        cleaned = re.sub(r'[^\x20-\x7E]+', ' ', cleaned)
        # Trim extra whitespace
        return cleaned.strip()

    def create_vectorstore(self, embeddings_constructor) -> dict:
        """Create a vector store from the processed document chunks."""
        # Process each chunk individually and preserve its metadata
        document_list = [
            Document(
                page_content=self.preprocess_text(chunk.page_content),
                metadata=chunk.metadata  # Preserve metadata including "doc_type"
            )
            for chunk in self.chunks
        ]
        
        metadata = {
            "num_docs": len(self.documents),
            "num_chunks": len(document_list),
            "total_characters": sum(len(doc.page_content) for doc in document_list)
        }
        print(f"Preparing {len(document_list)} documents for embedding.")
        
        # Check if persistence directory exists, create if not
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Creating the vector store with explicit collection name
        vectorstore = Chroma.from_documents(
            documents=document_list,
            embedding=embeddings_constructor(),
            persist_directory=self.persist_directory
        )
        
        print(f"Vectorstore created with {vectorstore._collection.count()} documents.")

        # Get sample embedding to verify dimensions
        collection = vectorstore._collection
        sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
        dimensions = len(sample_embedding)
        print(f"The vectors have {dimensions} dimensions.")
        
        self.vectorstore = vectorstore
        return {
            "metadata": metadata,
            "num_segments": len(document_list),
            "collection": collection
        }
    
    def load_vectorstore(self):
        """Load an existing vector store from disk."""
        # Use the same embeddings as when creating
        embeddings = safe_embeddings_constructor()
        
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        
        self.vectorstore = vectorstore
        count = vectorstore._collection.count()
        print(f"Loaded vector store with {count} documents from '{self.persist_directory}'.")
        
        if count == 0:
            print("Warning: Vector store is empty. You may need to create it first.")
            
        return vectorstore

    def get_retriever(self, search_type="mmr", k=10):
        """Get a retriever interface for the vector store."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Run load_vectorstore() or create_vectorstore() first.")
            
        # Return the retriever interface from the Chroma vector store
        # Using Maximum Marginal Relevance by default for better diversity
        return self.vectorstore.as_retriever(
            search_type=search_type, 
            search_kwargs={'k': k, 'lambda_mult': 0.6}
        )

       
if __name__ == "__main__":
    # Example usage
    curator = DataCurator(knowledge_base_dir="usiu-knowledge-base")
    curator.load_documents()
    curator.split_documents()
    vector_data = curator.create_vectorstore(safe_embeddings_constructor)
    
    # Loading an existing vector store
    # curator.load_vectorstore()
    
    # Get a retriever and test it
    # retriever = curator.get_retriever()
    # results = retriever.get_relevant_documents("What are some academic policies for international students?")
    # 
    # for i, doc in enumerate(results):
    #     print(f"Result {i+1}:")
    #     print(f"  Type: {doc.metadata.get('doc_type', 'unknown')}")
    #     print(f"  Content: {doc.page_content[:100]}...")
    #     print()