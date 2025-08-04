import time
import json
import anthropic
import gradio as gr
import concurrent.futures
from typing import List, Dict, Any, Generator, Optional

from configs.config import GPT4O_MODEL
from api_gateway.gateway import get_service

class GeneralChatService:
    """Service for handling general academic enquiries with RAG support."""

    def __init__(self, system_prompt: str, model: str, retriever=None):
        self.system_prompt = system_prompt
        self.model = model
        self.retriever = retriever
        self.anthropic_client = anthropic.Anthropic()

    def summarize_context(self, text: str, summarization_model: str = GPT4O_MODEL) -> str:
        """Summarize the given text concisely while preserving key details."""
        summarization_prompt = (
            "Summarize the following text concisely while preserving the essential details:\n\n"
            f"{text}\n\nSummary:"
        )
        try:
            completion = self.anthropic_client.messages.create(
                model=summarization_model,
                messages=[{"role": "user", "content": summarization_prompt}],
                system=self.system_prompt,
                max_tokens=300,
                temperature=0.5,
                stream=True,
            )
            return completion.content[0].text.strip()
        except Exception as e:
            print(f"Summarization failed: {e}")
            return text[:500]  # Fallback

    def generate_initial_greeting(self) -> str:
        """Generate a dynamic greeting using the model."""
        try:
            completion = self.anthropic_client.messages.create(
                model=self.model,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )
            return completion.content[0].text.strip()
        except Exception as e:
            print(f"[Warning] could not generate dynamic greeting: {e}")
            return "Hello and welcome! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance."

    def chat(self, message: str, chat_history: list) -> Generator[str, None, None]:
        """Handle general chat with RAG enhancement and metrics tracking."""
        start_time = time.time()
        session_id = None
        user_id = "anonymous"

        if chat_history and isinstance(chat_history[0], dict) and "session_id" in chat_history[0]:
            session_id = chat_history[0]["session_id"]
            user_id = chat_history[0].get("user_id", "anonymous")
        else:
            session_id = f"general_{int(time.time())}"

        if chat_history is None:
            chat_history = []
        else:
            chat_history = [msg for msg in chat_history if msg is not None]

        if not chat_history:
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            conv_header = {
                "role": "header",
                "content": f"<div style='text-align: center; font-weight: bold; font-size: 16px; color: #000;'>Conversation started on {date_str}</div>",
                "session_id": session_id,
                "user_id": user_id
            }
            chat_history.insert(0, conv_header)

        msgs = []
        for entry in chat_history:
            if isinstance(entry, dict) and entry.get("role") != "header":
                msgs.append({"role": entry["role"], "content": entry["content"]})
            elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                human, assistant = entry
                msgs.extend([
                    {"role": "user", "content": human},
                    {"role": "assistant", "content": assistant},
                ])

        msgs.append({"role": "user", "content": message})
        chat_history.append({"role": "user", "content": message, "session_id": session_id})

        wandb_tracker = get_service("wandb_tracker")
        retrieved_docs = None

        # Optimized RAG Retrieval and Summarization Implementation
        if self.retriever is not None:
            try:
                print("Attempting RAG retrieval...")
                # Retrieve relevant documents
                docs = self.retriever.invoke(message)
                
                # Convert to list if it's a generator or any other iterable
                if docs is not None:
                    # Handle different types of return values
                    if hasattr(docs, '__iter__') and not isinstance(docs, (list, tuple, str)):
                        docs = list(docs)
                    elif not isinstance(docs, list):
                        docs = [docs] if docs else []
                else:
                    docs = []
                
                if docs and len(docs) > 0:
                    print(f"Retrieved {len(docs)} documents")
                    # Store document content for W&B logging
                    retrieved_docs = []
                    for doc in docs:
                        if hasattr(doc, 'page_content'):
                            retrieved_docs.append(doc.page_content[:200] + "...")
                    
                    # Only proceed if we have documents with content
                    if retrieved_docs:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(docs), 5)) as executor:
                            futures = []
                            for doc in docs:
                                if hasattr(doc, 'page_content'):
                                    futures.append(executor.submit(summarize_context, doc.page_content, GPT4O_MODEL))
                            
                            summarized_texts = []
                            for future in concurrent.futures.as_completed(futures):
                                try:
                                    result = future.result()
                                    if result and result.strip():
                                        summarized_texts.append(result.strip())
                                except Exception as e:
                                    print(f"Error summarizing document: {e}")
                        
                        if summarized_texts:
                            context_text = "\n\n".join(summarized_texts)
                            # Add context as a user message to Claude
                            context_message = {"role": "user", "content": f"Additional Context Summaries:\n{context_text}"}
                            msgs.insert(-1, context_message)  # Insert before the last user message
                            print("RAG context successfully added to conversation")
                        else:
                            print("No valid summaries were generated from retrieved documents.")
                else:
                    print("No documents retrieved for the query")
                    
            except Exception as e:
                print(f"RAG retrieval failed: {e}")
                if wandb_tracker:
                    wandb_tracker.log_error("rag_retrieval", str(e), session_id, message)
        else:
            print("GLOBAL_RETRIEVER is not initialized")

        # Claude API call with streaming
        final_response = ""
        try:
            stream = self.anthropic_client.messages.stream(
                model=self.model,
                system=self.system_prompt,
                messages=msgs,
                max_tokens=500,
                temperature=0.7,
            )
            
            # If we successfully created the stream, break out of retry loop
            with stream as s:
                for chunk in s.text_stream:
                    final_response += chunk
                    yield final_response

            end_time = time.time()
            response_time = end_time - start_time

            if wandb_tracker:
                token_estimate = len(message.split()) + len(final_response.split()) * 1.3
                wandb_tracker.log_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    chat_type="general",
                    query=message,
                    response=final_response,
                    context_used=retrieved_docs,
                    tokens=int(token_estimate),
                    response_time=response_time,
                    feedback=None
                )

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Claude generation error: {e}")
            if wandb_tracker:
                wandb_tracker.log_error("claude_generation", str(e), session_id, message)
            yield error_msg

    def log_feedback(self, message: str, response: str, flag: str) -> str:
        """Log user feedback to W&B."""
        try:
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                session_id = f"feedback_{int(time.time())}"
                user_id = "anonymous"

                feedback = "neutral"
                if flag == "Like":
                    feedback = "positive"
                elif flag == "Dislike":
                    feedback = "negative"

                wandb_tracker.log_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    chat_type="general",
                    query=message,
                    response=response,
                    feedback=feedback
                )
            return flag
        except Exception as e:
            print(f"Error logging feedback: {e}")
            return flag

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for general chat."""
        initial_greeting = self.generate_initial_greeting()
        initial_messages = [{"role": "assistant", "content": initial_greeting}]

        chatbot_comp = gr.Chatbot(
            value=initial_messages,
            type="messages",
            show_copy_button=True,
            avatar_images=("images/user-icon1.png", "images/chatbot-icon.png"),
            sanitize_html=True,
            allow_tags=["thinking"],
            height=600,
        )

        with gr.Blocks(elem_id="general-chat-interface", elem_classes="chat-interface-container") as interface:
            chat_interface = gr.ChatInterface(
                fn=self.chat,
                chatbot=chatbot_comp,
                editable=True,
                type="messages",
                save_history=True,
                title="General Enquiries",
                description="<div style='display:flex; justify-content:center;'>Hi there! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance.</div>",
                examples=[
                    ["What are the admission requirements for USIU?"],
                    ["Tell me about the available programs/courses"],
                    ["What facilities are available on campus?"],
                    ["How can I apply for financial aid?"]
                ],
                cache_examples=False,
                cache_mode="eager",
                flagging_mode="manual",
                flagging_options=("Like", "Dislike", "Neutral"),
                flagging_dir="user_feedback_study",
            )

            try:
                if hasattr(chat_interface, "flagging_callback"):
                    chat_interface.flagging_callback = self.log_feedback
            except Exception as e:
                print(f"Could not attach feedback handler: {e}")

        return interface.queue(default_concurrency_limit=1000)
