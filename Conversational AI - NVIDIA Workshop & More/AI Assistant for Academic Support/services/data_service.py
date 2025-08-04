# services/data_service.py
from services.system_prompts_service import SystemPromptsService

class DataService:
    """
    Data service that provides access to system prompts and manages data-related operations.
    """
    def __init__(self, retriever=None) -> None:
        self.prompts_service = SystemPromptsService()
        self.retriever = retriever
    
    def get_retriever(self):
        """Get the configured retriever for RAG"""
        return self.retriever