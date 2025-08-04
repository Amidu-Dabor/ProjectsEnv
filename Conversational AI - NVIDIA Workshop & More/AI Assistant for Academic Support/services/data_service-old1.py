# services/data_service.py
from services.system_prompts_service import SystemPromptsService
from services.response_service import ResponseService
from configs.config import GPT4O_MODEL, CLAUDE_MODEL, GPT4O_API_KEY, CLAUDE_API_KEY
from services.general_chat_service import GeneralChatService  
from services.study_support_service import StudySupportService
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

class DataService:
    """
    Data service that routes user queries to the appropriate agent:
      - General academic inquiries use GPT-4o via RAG if a retriever is provided,
        using the general_chat function from GeneralChatService.
      - Study support inquiries use Claude 3.5 Sonnet.
    """
    def __init__(self, retriever=None) -> None:
        self.prompts_service = SystemPromptsService()
        self.response_service = ResponseService()
        
        # If a retriever is provided as a string (e.g., a directory path),
        # convert it into a proper retriever object.
        if retriever and isinstance(retriever, str):
            embeddings = OpenAIEmbeddings(openai_api_key=GPT4O_API_KEY)
            vectorstore = Chroma(persist_directory=retriever, embedding_function=embeddings)
            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 40, 'lambda_mult': 0.6}
            )

        self.general_chat_service = GeneralChatService(
            model=GPT4O_MODEL,
            api_key=GPT4O_API_KEY,
            system_prompt=self.prompts_service.get_prompt()[0],
            retriever=retriever  # RAG will be used if this is a valid retriever object.
        )
        self.study_support_service = StudySupportService(
            model=CLAUDE_MODEL,
            api_key=CLAUDE_API_KEY,
            system_prompt=self.prompts_service.get_prompt()[1]
        )

    def route_query(self, query: str, chat_history: any, query_type: str = "general") -> str:
        """
        Routes the user query to the appropriate service based on query type.
        - If query_type is "study", the study support service is used.
        - Otherwise, the general chat service (using general_chat) is used.
        The final response is formatted via the response_service.
        """
        if query_type == "study":
            response = self.study_support_service.ask(query)
        else:
            # Call the general_chat function which streams responses.
            # Convert the generator into a list, and use the final yielded value.
            responses = list(self.general_chat_service.general_chat(query, chat_history))
            response = responses[-1] if responses else ""
        return self.response_service.format_response(response)
