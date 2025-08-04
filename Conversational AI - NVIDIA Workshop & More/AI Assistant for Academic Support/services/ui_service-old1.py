# services/ui_service.py

import re
import os
import time
import json
import openai
import anthropic
import gradio as gr
import threading
import concurrent.futures
from typing import List, Dict, Any, Tuple, Optional, Generator, Union

from configs.config import GPT4O_MODEL
from services.auth_service import (
    authenticate, create_session, get_session, update_session_activity, 
    end_session, is_session_active, get_session_remaining_time, should_show_warning,
    INACTIVITY_TIMEOUT, WARNING_TIMEOUT
)
from services.file_service import FileProcessor
from api_gateway.gateway import route_request, get_service
from .custom_css import custom_css


claude_client = anthropic.Anthropic()

# Will be set when dashboard_ui is called (during runtime)
GLOBAL_RETRIEVER = None

# ----------------- Session Management Functions -----------------
def check_session_status(session_id):
    """Check session status and return relevant information."""
    if not session_id:
        return json.dumps({"valid": False, "remaining": 0, "show_warning": False})
    
    session = get_session(session_id)
    if not session:
        return json.dumps({"valid": False, "remaining": 0, "show_warning": False})
    
    remaining = get_session_remaining_time(session_id)
    show_warning = should_show_warning(session_id)
    
    return json.dumps({
        "valid": remaining > 0,
        "remaining": remaining,
        "show_warning": show_warning,
        "user_id": session.get("user_id", "")
    })

def keep_session_alive(session_id):
    """Update session activity and return new status."""
    success = update_session_activity(session_id)
    
    if success:
        status = check_session_status(session_id)
    else:
        status = json.dumps({"valid": False})
        
    return json.dumps({
        "success": success,
        "status": status
    })


# ----------------- Summarization Helper -----------------
def summarize_context(text: str, summarization_model: str = GPT4O_MODEL) -> str:
    """
    Summarize the given text concisely while preserving key details.
    Uses the provided summarization model (e.g., GPT-4o or llama-3-8b).
    """
    summarization_prompt = (
        "Summarize the following text concisely while preserving the essential details:\n\n"
        f"{text}\n\nSummary:"
    )
    try:
        # Non-streaming call to get the summary
        response = openai.chat.completions.create(
            model=summarization_model,
            messages=[{"role": "system", "content": summarization_prompt}],
            max_tokens=150,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print("Summarization failed:", e)
        # Fallback: return a truncated version if summarization fails
        return text[:500]

# ----------------- Notification Helpers -----------------

def show_success(message: str, duration: float = 8, visible: bool = True, title: str = "Success") -> None:
    """Display a success notification"""
    styled_message = (
        f'<span style="color: #2e7d32; background-color: #c8e6c9; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Success(styled_message, duration=duration, visible=visible, title=title)
    # Add a small delay to help the modal appear
    time.sleep(0.1)

def show_error(message: str, duration: float = 10, visible: bool = True, title: str = "Error") -> None:
    """Display an error notification"""
    styled_message = (
        f'<span style="color: #c62828; background-color: #ffcdd2; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Error(styled_message, duration=duration, visible=visible, title=title)
    # Add a small delay to help the modal appear
    time.sleep(0.1)

# ----------------- Login Form UI -----------------

def login_form_ui():
    """Create and return the login form interface"""
    with gr.Blocks() as login_form:
        gr.Markdown("## Please Login")
        user_id_input = gr.Textbox(
            placeholder="Enter your User ID", 
            label="User ID", 
            type="email", 
            autofocus=True
        )
        # Error message for invalid user ID
        user_id_error = gr.Markdown("", visible=True)
        
        password_input = gr.Textbox(
            placeholder="Enter your Password", 
            label="Password", 
            type="password"
        )
        # Error message for invalid password
        password_error = gr.Markdown("", visible=True)
        
        login_btn = gr.Button("Login")
        # Error message for invalid credentials
        login_msg = gr.Markdown("")
        proceed_btn = gr.Button("Proceed", visible=False)
        back_btn = gr.Button("Back to Dashboard")
        
        # Hidden field to store session ID
        session_id = gr.Textbox(visible=False)
    # Return the login form along with the necessary components in order.
    return login_form, user_id_input, user_id_error, password_input, password_error, login_btn, login_msg, proceed_btn, back_btn, session_id

# ----------------- Authentication Logic -----------------

def handle_login(user_id, password):
    """
    Validates login fields and the User ID (which must end with '@usiu.ac.ke').
    Returns appropriate error messages and updates UI components.
    """
    try:
        user_id = user_id.strip() if user_id else ""
        password = password.strip() if password else ""

        # Both fields empty:
        if user_id == "" and password == "":
            show_error("Please enter your User ID and Password.")
            return (
                "<span style='color:#c62828;'>Please enter your User ID and Password.</span>",
                "",   # No field-specific error for User ID.
                "",   # No field-specific error for Password.
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        # User ID is empty:
        elif user_id == "":
            show_error("User ID is required.")
            return (
                "", 
                "<span style='color:#c62828;'>User ID is required.</span>",
                "",
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        # Password is empty:
        elif password == "":
            show_error("Password is required.")
            return (
                "",
                "",
                "<span style='color:#c62828;'>Password is required.</span>",
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        else:
            # Validate the User ID: must end with "@usiu.ac.ke"
            email_regex = r'^[\w\.-]+@usiu\.ac\.ke$'
            if not re.match(email_regex, user_id):
                show_error("User ID must be a valid \"@usiu.ac.ke\" email address.")
                return (
                    "",
                    "<span style='color:#c62828;'>User ID must be a valid @usiu.ac.ke email address.</span>",
                    "",
                    gr.update(visible=False),
                    gr.update(visible=True),
                    ""    # No session ID since login failed
                )
            # Attempt authentication.
            if authenticate(user_id, password):
                # Create a session for the authenticated user
                session_id = create_session(user_id)
                
                show_success("Login successful! Click 'Proceed' to continue!", duration=10)
                return (
                    "", 
                    "",
                    "",
                    gr.update(visible=True), # Show Proceed button.
                    gr.update(visible=False), # Hide Login button.
                    session_id   # Return the session ID for the new session
                )
            else:
                show_error("Invalid credentials. Please try again.")
                return (
                    "<span style='color:#c62828;'>Invalid credentials. Please try again.</span>",
                    "",
                    "",
                    gr.update(visible=False),
                    gr.update(visible=True),
                    ""    # No session ID since login failed
                )
    except Exception as e:
        show_error(f"System error: {str(e)}. Please ensure required modules are imported.")
        return (
            "<span style='color:#c62828;'>System error encountered.</span>",
            "",
            "",
            gr.update(visible=False),
            gr.update(visible=True),
            ""    # No session ID since login failed
        )

# def generate_initial_greeting_general(system_prompt: str, model: str) -> str:
#     """Ask the LLM to craft a friendly, creative greeting."""
#     try:
#         response = openai.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role":"system",  "content": system_prompt},
#                 {"role":"user",    "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
#             ],
#             max_tokens=200,
#             temperature=0.9
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"[Warning] could not generate dynamic greeting: {e}")
#         return "Hello there! How can I assist you today?"
    
def generate_initial_greeting_general(system_prompt: str, model: str) -> str:
    """Ask the AI engine to craft a friendly, creative greeting."""
    try:
        response = claude_client.messages.create(
            model=model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
            ],
            max_tokens=250,
            temperature=0.9
        )
        
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[Warning] could not generate dynamic greeting with Claude: {e}")
        return "Hello there! How can I assist you today?"
    
def generate_initial_greeting_study(system_prompt: str, model: str) -> str:
    """Ask Claude to craft a friendly, creative greeting."""
    try:
        response = claude_client.messages.create(
            model=model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
            ],
            max_tokens=250,
            temperature=0.9
        )
        
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[Warning] could not generate dynamic greeting with Claude: {e}")
        return "Hello there! How can I assist you today?"

# ----------------- Chat Interfaces with W&B Integration -----------------

# def general_chat_ui(system_prompt: str, model: str):
#     """Creates a Gradio ChatInterface for general academic chat with RAG and W&B tracking."""

#     def general_chat(message: str, chat_history) -> str:
#         start_time = time.time()
        
#         # Get a session ID (either from headers or generate a new one)
#         session_id = None
#         user_id = "anonymous"
        
#         # Try to extract session ID from chat history
#         if chat_history and isinstance(chat_history[0], dict) and "session_id" in chat_history[0]:
#             session_id = chat_history[0]["session_id"]
#             user_id = chat_history[0].get("user_id", "anonymous")
#         else:
#             # Create a fallback session ID
#             session_id = f"general_{int(time.time())}"
        
#         # Ensure chat_history is a list and filter out any None items.
#         if chat_history is None:
#             chat_history = []
#         else:
#             chat_history = [msg for msg in chat_history if msg is not None]

#         # If this is a new conversation, insert a conversation header with session info.
#         if not chat_history:
#             date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime())
#             conv_header = {
#                 "role": "header",
#                 "content": (
#                     f"<div style='text-align: center; font-weight: bold; font-size: 16px; color: #000;'>"
#                     f"Conversation started on {date_str}"
#                     f"</div>"
#                 ),
#                 "session_id": session_id,
#                 "user_id": user_id
#             }
#             chat_history.insert(0, conv_header)  # Insert at the beginning

#         # Start with the initial system prompt.
#         messages = [{"role": "system", "content": system_prompt}]

#         # Add chat history to messages (all messages, including header).
#         if chat_history:
#             # If the first element is a tuple/list with two elements, assume pair format.
#             if isinstance(chat_history[0], (tuple, list)) and len(chat_history[0]) == 2:
#                 for human, assistant in chat_history:
#                     messages.append({"role": "user", "content": human})
#                     messages.append({"role": "assistant", "content": assistant})
#             # Otherwise, if they are dicts, ensure each has a 'role' field.
#             elif isinstance(chat_history[0], dict):
#                 for msg in chat_history:
#                     # Skip header messages.
#                     if msg.get("role") == "header":
#                         continue
                    
#                     # Extract the role and content
#                     role = msg.get("role", "user")
#                     content = msg.get("content", "")
                    
#                     # Add to messages
#                     messages.append({"role": role, "content": content})

#         # Try to get the W&B tracker service
#         wandb_tracker = get_service("wandb_tracker")
        
#         # Optimized RAG Retrieval and Summarization Implementation:
#         retrieved_docs = []
#         if GLOBAL_RETRIEVER is not None:
#             try:
#                 # Retrieve relevant documents.
#                 docs = GLOBAL_RETRIEVER.invoke(message)
#                 if docs:
#                     # Store document content for W&B logging
#                     retrieved_docs = [doc.page_content[:200] + "..." for doc in docs]
                    
#                     with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(docs), 5)) as executor:
#                         futures = [executor.submit(summarize_context, doc.page_content, GPT4O_MODEL)
#                                    for doc in docs]
#                         summarized_texts = []
#                         for future in concurrent.futures.as_completed(futures):
#                             result = future.result()
#                             if result and result.strip():
#                                 summarized_texts.append(result.strip())
#                     if summarized_texts:
#                         context_text = "\n\n".join(summarized_texts)
#                         messages.insert(1, {
#                             "role": "system",
#                             "content": f"Additional Context Summaries:\n{context_text}"
#                         })
#                     else:
#                         print("No valid summaries were generated.")
#             except Exception as e:
#                 print("RAG retrieval failed:", e)
#                 if wandb_tracker:
#                     wandb_tracker.log_error("rag_retrieval", str(e), session_id, message)

#         # Append the user's current message.
#         chat_history.append({"role": "user", "content": message, "session_id": session_id})
#         messages.append({"role": "user", "content": message})

#         # Call OpenAI's ChatCompletion with streaming enabled.
#         try:
#             completion = openai.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 max_tokens=500,
#                 temperature=0.7,
#                 stream=True,
#             )

#             response = ""
#             for chunk in completion:
#                 token = chunk.choices[0].delta.content or ""
#                 response += token
#                 yield response
                
#             # Log to W&B after response is complete
#             end_time = time.time()
#             response_time = end_time - start_time
            
#             if wandb_tracker:
#                 # Estimate token count (rough estimate)
#                 token_estimate = len(message.split()) + len(response.split()) * 1.3
                
#                 wandb_tracker.log_conversation(
#                     session_id=session_id,
#                     user_id=user_id,
#                     chat_type="general",
#                     query=message,
#                     response=response,
#                     context_used=retrieved_docs,
#                     tokens=int(token_estimate),
#                     response_time=response_time,
#                     feedback=None  # Will be updated if user provides feedback
#                 )
        
#         except Exception as e:
#             error_msg = f"Error generating response: {str(e)}"
#             print(error_msg)
#             if wandb_tracker:
#                 wandb_tracker.log_error("openai_generation", str(e), session_id, message)
#             yield error_msg

#     # Define feedback logging function
#     def log_feedback(message, response, flag):
#         """Log user feedback to W&B"""
#         try:
#             wandb_tracker = get_service("wandb_tracker")
#             if wandb_tracker:
#                 # Try to extract session ID from chat history or use a fallback
#                 session_id = f"feedback_{int(time.time())}"
#                 user_id = "anonymous"
                
#                 # Convert flag value to feedback type
#                 feedback = "neutral"
#                 if flag == "Like":
#                     feedback = "positive"
#                 elif flag == "Dislike":
#                     feedback = "negative"
                
#                 # Log the feedback
#                 wandb_tracker.log_conversation(
#                     session_id=session_id,
#                     user_id=user_id,
#                     chat_type="general",
#                     query=message,
#                     response=response,
#                     feedback=feedback
#                 )
#             return flag
#         except Exception as e:
#             print(f"Error logging feedback: {e}")
#             return flag

#     # A zero‑arg function for value that calls a greeting generator:
#     def initial_value_general():
#         return [{"role":"assistant", "content": generate_initial_greeting_general(system_prompt)}]

#     # Instantiate a Chatbot with additional components.
#     chatbot_comp = gr.Chatbot(
#         value=initial_value_general,
#         type="messages",
#         show_copy_button=True,
#         avatar_images=("images/user-icon1.png", "images/chatbot-icon.png"),
#         sanitize_html=True,
#         allow_tags=["thinking"],
#         height=600,
#         group_consecutive_messages=False
#     )

#     # Create the chat interface with a custom chatbot component
#     with gr.Blocks(elem_id="general-chat-interface", elem_classes="chat-interface-container") as interface:
#         # Create the chat interface
#         chat_interface = gr.ChatInterface(
#             fn=general_chat,
#             chatbot=chatbot_comp,
#             editable=True,
#             save_history=True,
#             title="General Enquiries",
#             description="<div style='display:flex; justify-content:center;'>Hi there! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance.</div>",
#             type="messages",
#             cache_mode="eager",
#             flagging_mode="manual",
#             flagging_options=("Like","Dislike","Neutral"),
#             flagging_dir="user_feedback_enquiry"
#         )
        
#         # Set up feedback handling after the interface is created
#         # If your Gradio version supports setting this up manually:
#         try:
#             if hasattr(chat_interface, "flagging_callback"):
#                 chat_interface.flagging_callback = log_feedback
#         except Exception as e:
#             print(f"Could not attach feedback handler: {e}")
    
#     # Return the blocks interface instead of launching it
#     return interface.queue(default_concurrency_limit=2000)

def general_chat_ui(system_prompt: str, model: str):
    """Creates a Gradio ChatInterface for general academic chat with RAG and Weights & Biases (W&B) tracking."""

    def general_chat(message: str, chat_history) -> str:
        start_time = time.time()
        
        # Get a session ID (either from headers or generate a new one)
        session_id = None
        user_id = "anonymous"
        
        # Try to extract session ID from chat history
        if chat_history and isinstance(chat_history[0], dict) and "session_id" in chat_history[0]:
            session_id = chat_history[0]["session_id"]
            user_id = chat_history[0].get("user_id", "anonymous")
        else:
            # Create a fallback session ID
            session_id = f"general_{int(time.time())}"
        
        # Ensure chat_history is a list and filter out any None items.
        if chat_history is None:
            chat_history = []
        else:
            chat_history = [msg for msg in chat_history if msg is not None]

        # If this is a new conversation, insert a conversation header with session info.
        if not chat_history:
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            conv_header = {
                "role": "header",
                "content": (
                    f"<div style='text-align: center; font-weight: bold; font-size: 16px; color: #000;'>"
                    f"Conversation started on {date_str}"
                    f"</div>"
                ),
                "session_id": session_id,
                "user_id": user_id
            }
            chat_history.insert(0, conv_header)  # Insert at the beginning

        # Build the messages array for Claude
        msgs = []
        for entry in chat_history:
            if isinstance(entry, dict) and entry.get("role") != "header":
                msgs.append({"role": entry["role"], "content": entry["content"]})
            elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                human, assistant = entry
                msgs.extend(
                    [
                        {"role": "user", "content": human},
                        {"role": "assistant", "content": assistant},
                    ]
                )

        # Append the user's current message
        msgs.append({"role": "user", "content": message})
        chat_history.append({"role": "user", "content": message, "session_id": session_id})

        # Try to get the W&B tracker service
        wandb_tracker = get_service("wandb_tracker")
        
        # Optimized RAG Retrieval and Summarization Implementation:
        retrieved_docs = []

        if GLOBAL_RETRIEVER is not None:
            try:
                # Retrieve relevant documents
                docs = GLOBAL_RETRIEVER.invoke(message)
                
                # Convert to list immediately to avoid generator issues
                if docs is not None:
                    if hasattr(docs, '__iter__') and not isinstance(docs, (list, tuple, str)):
                        docs = list(docs)
                    elif not isinstance(docs, list):
                        docs = [docs] if docs else []
                else:
                    docs = []
                
                if docs:
                    # Store document content for W&B logging
                    retrieved_docs = []
                    for doc in docs:
                        if hasattr(doc, 'page_content'):
                            retrieved_docs.append(doc.page_content[:200] + "...")
                    
                    # Only proceed if we have documents with content
                    if retrieved_docs:
                        # Limit the number of documents to process
                        docs_to_process = docs[:5]  # Process maximum 5 documents
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(docs_to_process), 5)) as executor:
                            futures = []
                            for doc in docs_to_process:
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
                        else:
                            print("No valid summaries were generated.")
                            
            except Exception as e:
                print(f"RAG retrieval failed: {e}")
                if wandb_tracker:
                    wandb_tracker.log_error("rag_retrieval", str(e), session_id, message)

        # Stream from Claude with retry mechanism
        final_response = ""
        
        # Initialize retry parameters
        attempts, delay, max_retry = 0, 3, 8
        
        while attempts < max_retry:
            try:
                # Create a streaming response from Claude
                stream = claude_client.messages.stream(
                    model=model,
                    system=system_prompt,
                    messages=msgs,
                    max_tokens=500,
                    temperature=0.7,
                )
                
                # Stream responses
                with stream as s:
                    for chunk in s.text_stream:
                        final_response += chunk
                        yield final_response
                        
                # Log to W&B after response is complete
                end_time = time.time()
                response_time = end_time - start_time
                
                if wandb_tracker:
                    # Estimate token count (rough estimate)
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
                        feedback=None  # Will be updated if user provides feedback
                    )
                
                # If we get here, the request was successful, so break the retry loop
                break
                    
            except Exception as e:
                # Check if the error is due to API overload
                if "overloaded" in str(e).lower():
                    attempts += 1
                    # Let the user know we're retrying
                    retry_message = f"(Service busy – retrying in {delay}s, {attempts}/{max_retry})"
                    yield retry_message
                    time.sleep(delay)
                    # Clear the retry message from the output for the next attempt
                    final_response = ""
                else:
                    # For other errors, log and return the error message
                    error_msg = f"Error: {str(e)}"
                    print(f"Claude generation error: {e}")
                    if wandb_tracker:
                        wandb_tracker.log_error("claude_generation", str(e), session_id, message)
                    print(error_msg)
                    break

    # Define feedback logging function
    def log_feedback(message, response, flag):
        """Log user feedback to Weights & Biases (W&B)"""
        try:
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                # Try to extract session ID from chat history or use a fallback
                session_id = f"feedback_{int(time.time())}"
                user_id = "anonymous"
                
                # Convert flag value to feedback type
                feedback = "neutral"
                if flag == "Like":
                    feedback = "positive"
                elif flag == "Dislike":
                    feedback = "negative"
                
                # Log the feedback
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

    # A zero‑arg function for value that calls a greeting generator:
    def initial_value_general():
        try:
            return [{"role":"assistant", "content": generate_initial_greeting_general(system_prompt, model)}]
        except Exception as e:
            print(f"[Warning] could not generate dynamic greeting with Claude: {e}")
            # Fallback static greeting
            fallback_greeting = "Hello! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance."
            return [{"role":"assistant", "content": fallback_greeting}]

    # Instantiate a Chatbot with additional components.
    chatbot_comp = gr.Chatbot(
        value=initial_value_general,
        type="messages",
        show_copy_button=True,
        avatar_images=("images/user-icon1.png", "images/chatbot-icon.png"),
        sanitize_html=True,
        allow_tags=["thinking"],
        height=600,
        group_consecutive_messages=False
    )

    # Create the chat interface with a custom chatbot component
    with gr.Blocks(elem_id="general-chat-interface", elem_classes="chat-interface-container") as interface:
        # Create the chat interface
        chat_interface = gr.ChatInterface(
            fn=general_chat,
            chatbot=chatbot_comp,
            editable=True,
            save_history=True,
            title="General Enquiries",
            description="<div style='display:flex; justify-content:center;'>Hi there! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance.</div>",
            type="messages",
            cache_mode="eager",
            flagging_mode="manual",
            flagging_options=("Like","Dislike","Neutral"),
            flagging_dir="user_feedback_enquiry"
        )
        
        # Set up feedback handling after the interface is created
        try:
            if hasattr(chat_interface, "flagging_callback"):
                chat_interface.flagging_callback = log_feedback
        except Exception as e:
            print(f"Could not attach feedback handler: {e}")
    
    # Return the blocks interface with concurrency limit for multiple simultaneous users
    return interface.queue(default_concurrency_limit=1000)

# --------------  STUDY SUPPORT CHAT UI  ------------------------------------------

# Define global variables at the module level
current_file_path = None
auto_clear_files_state = True

def study_support_ui(system_prompt: str, model: str):
    """
    Returns a queued gr.Blocks object that hosts the Study‑Support chat with W&B tracking.
    The file‑upload accordion sits *under* the chat input.
    """
    # Explicitly declare globals inside the function
    global current_file_path
    global auto_clear_files_state

    # Original streaming function that Gradio will call directly
    def study_support_chat(message: str, chat_history: list, session_id: str):
        """Streams a reply from Claude; embeds the uploaded file if present."""
        global current_file_path
        global auto_clear_files_state
        
        start_time = time.time()
        
        # Debug log
        print(f"Starting chat with file: {current_file_path}")
        
        # Get W&B tracker
        wandb_tracker = get_service("wandb_tracker")

        # ---- Session alive? --------------------------------------------------
        if session_id:
            update_session_activity(session_id)
            sess = get_session(session_id)
            if not sess or not sess.get("logged_in", False):
                return "Your session has expired. Please log in again."
            user_id = sess.get("user_id", "anonymous")
        else:
            user_id = "anonymous"
            session_id = f"study_{int(time.time())}"

        chat_history = chat_history or []

        # ---- Header on first exchange ---------------------------------------
        if not chat_history:
            chat_history.insert(
                0,
                {
                    "role": "header",
                    "content": f"<div style='text-align:center;font-weight:bold;'>"
                    f"Conversation started on {time.strftime('%Y-%m-%d %H:%M')}</div>",
                    "session_id": session_id,
                    "user_id": user_id
                },
            )

        # ---- Rebuild prompt for Claude --------------------------------------
        msgs = []
        for entry in chat_history:
            if isinstance(entry, dict) and entry.get("role") != "header":
                msgs.append({"role": entry["role"], "content": entry["content"]})
            elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                human, assistant = entry
                msgs.extend(
                    [
                        {"role": "user", "content": human},
                        {"role": "assistant", "content": assistant},
                    ]
                )

        msgs.append({"role": "user", "content": message})

        # ---- If a file was supplied, process and log it ----------------------
        file_processing_start = None
        file_size = None
        file_type = None
        file_text = None
        context_used = []
        
        if current_file_path:
            try:
                file_to_process = current_file_path
                file_processing_start = time.time()
                print(f"Processing file: {file_to_process}")
                file_text = FileProcessor.read_file(file_to_process)
                meta = FileProcessor.get_file_metadata(file_to_process)
                file_size = meta.get("size", 0)
                file_type = meta.get("extension", "unknown")
                compact_meta = ", ".join(
                    f"{k}: {v}"
                    for k, v in meta.items()
                    if k in ("filename", "extension", "size_formatted", "pages", "rows", "columns", "dimensions")
                )
                
                # Add file info to context used for W&B tracking
                context_used = [f"Uploaded file ({compact_meta})"]
                
                file_msg = (
                    f"I've uploaded a file ({compact_meta}) with the following content:\n\n"
                    f"{file_text[:50000]}{'…[truncated]' if len(file_text) > 50000 else ''}"
                )
                msgs.append({"role": "user", "content": file_msg})
                
                # Log file upload to W&B
                if wandb_tracker and file_processing_start:
                    file_processing_time = time.time() - file_processing_start
                    wandb_tracker.log_file_upload(
                        session_id=session_id,
                        file_type=file_type,
                        file_size=file_size,
                        processing_time=file_processing_time
                    )
                
                # Clear the file if auto-clear is enabled
                if auto_clear_files_state:
                    current_file_path = None
                    
            except Exception as e:
                error_msg = f"[Error processing file: {e}]"
                print(f"File processing error: {e}")
                msgs.append({"role": "user", "content": error_msg})
                if wandb_tracker:
                    wandb_tracker.log_error("file_processing", str(e), session_id, message)

        # ---- Stream from Claude with retry mechanism ---------------------------------------
        final_response = ""
        
        # Initialize retry parameters
        attempts, delay, max_retry = 0, 3, 8
        
        while attempts < max_retry:
            try:
                # Create a streaming response from Claude
                stream = claude_client.messages.stream(
                    model=model,
                    system=system_prompt,
                    messages=msgs,
                    max_tokens=63_800,
                    extra_query={"extended_thinking": True},
                )
                
                # Use a string-based approach instead of a generator
                with stream as s:
                    for chunk in s.text_stream:
                        final_response += chunk
                        yield final_response
                        
                # Log to W&B after response is complete
                end_time = time.time()
                response_time = end_time - start_time
                
                if wandb_tracker:
                    # Estimate token count (rough estimate)
                    token_estimate = len(message.split()) + len(final_response.split()) * 1.3
                    if file_text:
                        token_estimate += len(file_text.split()) * 0.8  # Approximate file tokens
                    
                    wandb_tracker.log_conversation(
                        session_id=session_id,
                        user_id=user_id,
                        chat_type="study_support",
                        query=message,
                        response=final_response,
                        context_used=context_used,
                        tokens=int(token_estimate),
                        response_time=response_time,
                        feedback=None  # Will be updated if user provides feedback
                    )
                
                # If we get here, the request was successful, so break the retry loop
                break
                    
            except Exception as e:
                # Check if the error is due to API overload
                if "overloaded" in str(e).lower():
                    attempts += 1
                    # Let the user know we're retrying
                    retry_message = f"Service busy – retrying in {delay}s, {attempts}/{max_retry}..."
                    yield retry_message
                    time.sleep(delay)
                    # Clear the retry message from the output for the next attempt
                    final_response = ""
                else:
                    # For other errors, log and return the error message
                    error_msg = f"Error: {str(e)}"
                    print(f"Claude generation error: {e}")
                    if wandb_tracker:
                        wandb_tracker.log_error("claude_generation", str(e), session_id, message)
                    print(error_msg)
                    break

    # ===================== INITIAL GREETING ================================= #
    def initial_value_study():
        return [
            {
                "role": "assistant",
                "content": generate_initial_greeting_study(system_prompt, model),
            }
        ]

    # Define feedback logging function for study support
    def log_study_feedback(message, response, flag):
        """Log user feedback to W&B"""
        try:
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                # Try to extract session ID or use a fallback
                session_id = f"feedback_study_{int(time.time())}"
                user_id = "anonymous"
                
                # Convert flag value to feedback type
                feedback = "neutral"
                if flag == "Like":
                    feedback = "positive"
                elif flag == "Dislike":
                    feedback = "negative"
                
                # Log the feedback
                wandb_tracker.log_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    chat_type="study_support",
                    query=message,
                    response=response,
                    feedback=feedback
                )
            return flag
        except Exception as e:
            print(f"Error logging feedback: {e}")
            return flag

    # ===================== BUILD THE UI ===================================== #
    with gr.Blocks(elem_id="study-chat-interface") as interface:
        # Store the session ID as a state variable
        session_id_box = gr.Textbox(visible=False)
        
        # Create chatbot component
        chatbot = gr.Chatbot(
            value=initial_value_study,
            type="messages",
            show_copy_button=True,
            avatar_images=("images/user-icon1.png", "images/chatbot-icon.png"),
            sanitize_html=True,
            allow_tags=["thinking"],
            height=600,
            group_consecutive_messages=False,
        )

        # Create the chat interface with the streaming function directly
        chat_interface = gr.ChatInterface(
            fn=study_support_chat,  # Use the generator function directly
            chatbot=chatbot,
            editable=True,
            save_history=True,
            title="Study Bud",
            description=(
                "<div style='display:flex; justify-content:center;'>"
                "Hi there! I'm your AI study bud, here to assist you with your study journey. "
                "You can upload files using the File Upload section below."
                "</div>"
            ),
            type="messages",
            cache_mode="eager",
            flagging_mode="manual",
            flagging_options=("Like", "Dislike", "Neutral"),
            flagging_dir="user_feedback_study",
        )
        
        # Try to set up feedback handler after interface creation
        try:
            if hasattr(chat_interface, "flagging_callback"):
                chat_interface.flagging_callback = log_study_feedback
        except Exception as e:
            print(f"Could not attach study feedback handler: {e}")

        # Now add the file upload accordion AFTER the chat interface
        with gr.Accordion("File Upload & Settings", open=False, elem_classes="additional-inputs-accordion"):
            with gr.Row():
                with gr.Column(scale=3):
                    file_input = gr.File(
                        label="Upload a file (PDF, Word, Excel, CSV, TXT, etc.)",
                        file_types=[".txt", ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", 
                                    ".pptx", ".ppt", ".png", ".jpg", ".jpeg", ".gif"],
                        type="filepath",
                    )
                with gr.Column(scale=2):
                    file_status = gr.Textbox(
                        label="File Status", value="No file uploaded", interactive=False
                    )

            with gr.Row():
                auto_clear_files = gr.Checkbox(
                    label="Auto‑clear files after processing", value=True
                )
                test_button = gr.Button("Test File Processing")
                clear_button = gr.Button("Clear File")

            test_output = gr.Textbox(
                label="File Test Results",
                visible=True,
                interactive=False,
                max_lines=10,
            )

        # ---------- helper fns for status + test ---------------------------
        def update_file_status(f):
            global current_file_path
            current_file_path = f
            
            if not f:
                return "No file uploaded"
            if isinstance(f, (str, os.PathLike)):
                try:
                    size = os.path.getsize(f)
                    return f"{os.path.basename(f)} • {FileProcessor._format_file_size(size)}"
                except Exception as e:
                    return f"File received but size unknown ({e})"
            # fallback for BytesIO etc.
            name = getattr(f, "name", "unknown")
            return f"{name} ready"

        def test_file_processing(f):
            if not f:
                return "No file selected. Please upload a file first."
            try:
                content_preview = FileProcessor.read_file(f)[:1000]
                meta = FileProcessor.get_file_metadata(f)
                meta_str = "\n".join(f"- {k}: {v}" for k, v in meta.items())
                return f"✅ **Metadata:**\n{meta_str}\n\n📄 **Preview:**\n{content_preview}"
            except Exception as e:
                return f"❌ Error testing file: {e}"
                
        def clear_file():
            global current_file_path
            current_file_path = None
            return None, "File cleared"
            
        def toggle_auto_clear(value):
            global auto_clear_files_state
            auto_clear_files_state = value

        # Connect the events
        file_input.change(update_file_status, file_input, file_status)
        test_button.click(test_file_processing, file_input, test_output)
        clear_button.click(clear_file, None, [file_input, file_status])
        auto_clear_files.change(toggle_auto_clear, auto_clear_files, None)

    return interface.queue(default_concurrency_limit=1000)

# ---------- Dashboard UI with W&B Integration ----------

# Theme toggle JavaScript
theme_toggle_js = """
<script>
// Theme handling functionality
document.addEventListener('DOMContentLoaded', function() {
    // Theme detection and initialization
    function initTheme() {
        // Check for saved theme preference or use system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        } else {
            // Check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const theme = prefersDark ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            updateThemeIcon(theme);
        }
    }

    // Update the theme toggle icon based on current theme
    function updateThemeIcon(theme) {
        const themeToggles = document.querySelectorAll('.theme-toggle');
        themeToggles.forEach(toggle => {
            if (theme === 'dark') {
                toggle.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06z" />
                    </svg>
                    <span class="tooltip">Switch to Light Mode</span>
                `;
            } else {
                toggle.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z" />
                    </svg>
                    <span class="tooltip">Switch to Dark Mode</span>
                `;
            }
        });
    }

    // Toggle between light and dark theme
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    }

    // Initialize theme when page loads
    initTheme();

    // Set up listeners for theme toggle buttons that may be dynamically added
    document.addEventListener('click', function(e) {
        if (e.target.closest('.theme-toggle')) {
            toggleTheme();
        }
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // Only apply if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            const theme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            updateThemeIcon(theme);
        }
    });
});
</script>
"""

def dashboard_ui(general_chat_prompt: str, general_model: str, 
                 study_prompt: str, study_model: str, retriever=None):
    """
    Creates a dashboard with professional styling, two main menus (General Chat and Study Support),
    and smooth transitions between views. For Study Support, a login form (with authentication)
    is shown before revealing the chat interface.
    
    Args:
        general_chat_prompt: System prompt for general enquiries
        general_model: Model ID for general chat (e.g., GPT4O_MODEL)
        study_prompt: System prompt for study support
        study_model: Model ID for study support (e.g., CLAUDE_MODEL)
        retriever: The retriever to use for RAG in general chat
    """
    global GLOBAL_RETRIEVER
    GLOBAL_RETRIEVER = retriever
    
    # Retrieve the existing chat interfaces.
    general_chat_component = general_chat_ui(general_chat_prompt, general_model)
    study_support_component = study_support_ui(study_prompt, study_model)
    # Retrieve the login form.
    (login_form_component, user_id_input, user_id_error, password_input, password_error,
     login_btn, login_msg, proceed_btn, login_back_btn, session_id) = login_form_ui()
    
    # Create the inactivity warning modal HTML
    inactivity_warning_html = """
    <div class="overlay" id="inactivity-overlay"></div>
    <div class="inactive-warning" id="inactivity-warning">
        <h3>Session Timeout Warning</h3>
        <p>Your session will expire due to inactivity in <span id="countdown">0</span> seconds.</p>
        <p>Would you like to continue your session?</p>
        <button id="stay-active-btn">Stay Active</button>
    </div>
    """
    
    # Default values for W&B dashboard
    default_entity = "daboramidu93-united-states-international-university-africa"
    default_project = "usiu-chatbot"
    
    # Try to get the entity and project from wandb tracker
    entity = default_entity
    project = default_project
    
    # Try to get wandb tracker service
    try:
        wandb_tracker = get_service("wandb_tracker")
        if wandb_tracker:
            if hasattr(wandb_tracker, 'entity') and wandb_tracker.entity:
                entity = wandb_tracker.entity
            if hasattr(wandb_tracker, 'project_name') and wandb_tracker.project_name:
                project = wandb_tracker.project_name
    except Exception as e:
        print(f"Error getting W&B tracker: {e}")
    
    # Create dashboard URL with validated entity and project
    dashboard_url = f"https://wandb.ai/{entity}/{project}"
    
    # Create the W&B dashboard HTML directly
    wandb_dashboard_html = f"""
    <div style="display: flex; flex-direction: column; height: 66vh; padding: 20px; text-align: center;">
        <h2 style="margin-bottom: 20px;">Chatbot Analytics</h2>
        <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 14px; color: #666;">
            <p>
                Full analytics and visualizations are available in the Weights & Biases dashboard.
                Click the button below to open the dashboard in a new tab.
            </p>
        </div>
        
        <div style="margin: 0 auto;">
            <a href="{dashboard_url}" target="_blank" 
               style="background-color: #FFBE00; color: black; text-decoration: none; 
                      padding: 15px 30px; border-radius: 5px; font-weight: bold; 
                      display: inline-block; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                      transition: all 0.3s ease;">
                Open W&B Dashboard
            </a>
        </div>
        <div style="margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
            <h3>What's tracked in the dashboard?</h3>
            <ul style="text-align: left; margin: 20px auto; max-width: 600px;">
                <li><strong>Conversation metrics</strong>: Number of conversations, response times, token usage</li>
                <li><strong>User feedback</strong>: Likes, dislikes, and neutral ratings</li>
                <li><strong>File uploads</strong>: Types, sizes, and processing times</li>
                <li><strong>System performance</strong>: CPU, memory, and API usage</li>
                <li><strong>Error tracking</strong>: Occurred errors and their frequency</li>
            </ul>
        </div>
    </div>
    """
    
    with gr.Blocks(css=custom_css()) as dashboard:
        # Header component with theme toggle
        header_component = gr.HTML('''
        <div class="app-header">
            <!-- USIU Logo on the left -->
            <img src="/Users/apple/Desktop/chatbot_prototype/images/usiu-logo.png" alt="Logo" class="logo-dashboard" />
            
            <!-- Theme toggle button -->
            <div class="header-controls">
                <button class="theme-toggle" aria-label="Toggle theme">
                    <!-- Icon will be set by JavaScript -->
                </button>
            </div>
        </div>
        <div class="content-area"></div>
        ''', elem_id="header-container"
        )

        # Define containers for different views with initial animation state
        # Add content-area class to ensure proper spacing below fixed header
        dashboard_container = gr.Column(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInUp content-area")
        general_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
        login_container = gr.Column(visible=False, elem_classes="container floating-card login-form-container pre-animation content-area")
        study_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
        analytics_container = gr.Column(visible=False, elem_classes="container floating-card dashboard-card pre-animation content-area")
        
        # Add the inactivity warning modal to the UI
        gr.HTML(inactivity_warning_html)
        
        # Logout Button Component (hidden by default, will be shown after login)
        with gr.Row(visible=False, elem_id="logout-row") as logout_component:
            # Hidden email for user info
            current_user = gr.Textbox(visible=False, elem_id="user-email")
            
            # Actual logout button - will be triggered via the icon in the header
            logout_btn = gr.Button("Logout", elem_id="logout-btn", visible=False)
        
        # ------------- Dashboard View -------------
        with dashboard_container:
            gr.Markdown("<h1 class='with-logo'>Academic AI Assistant</h1>")
            with gr.Column(elem_classes="dashboard-menu"):
                gen_button = gr.Button("General Enquiries", elem_classes="menu-button")
                study_button = gr.Button("Study with AI", elem_classes="menu-button")
                analytics_button = gr.Button("Analytics Dashboard", elem_classes="menu-button")
        
        # ------------- General Academic Chat View -------------
        with general_container:
            back_gen = gr.Button("Back to Dashboard")
            # Render the general chat component directly in the container
            general_chat_component.render()
        
        # ------------- Login Form (for Study Support) View -------------
        with login_container:
            login_form_component.render()
        
        # ------------- Study Support Chat View -------------
        with study_container:
            back_study = gr.Button("Back to Dashboard")
            # Render the study support component directly in the container
            study_support_component.render()
            
            # Set session ID for the study chat interface
            # This ensures the session is refreshed on user interaction
            session_id_for_study = gr.Textbox(visible=False)
            
        # ------------- Analytics Dashboard View -------------
        with analytics_container:
            back_analytics = gr.Button("Back to Dashboard")
            # Add W&B dashboard content directly using HTML instead of rendering a component
            gr.Markdown("## Weights & Biases Analytics Dashboard")
            gr.HTML(wandb_dashboard_html)
        
        # Hidden components for session management
        with gr.Row(visible=False):
            check_session_fn = gr.Button("check_session", elem_id="check_session_status")
            keep_alive_fn = gr.Button("keep_alive", elem_id="keep_session_alive")
            session_status_output = gr.JSON(elem_id="session_status_output")
            keep_alive_output = gr.JSON(elem_id="keep_alive_output")
        
        # Function calls for session management
        check_session_fn.click(
            check_session_status,
            inputs=[session_id_for_study],
            outputs=[session_status_output]
        )
        
        keep_alive_fn.click(
            keep_session_alive,
            inputs=[session_id_for_study],
            outputs=[keep_alive_output]
        )
        
        # Add the theme toggle JavaScript and the session management JavaScript
        gr.HTML(theme_toggle_js + """
        <script>
        // Session management with server synchronization
        let sessionId = "";
        let sessionCheckInterval;
        let warningDisplayed = false;
        
        // Function to start session monitoring
        function startSessionMonitoring(sid) {
            sessionId = sid;
            console.log("Starting session monitoring for session ID:", sid);
            
            // Clear any existing interval
            if (sessionCheckInterval) {
                clearInterval(sessionCheckInterval);
            }
            
            // Check session status every 5 seconds
            sessionCheckInterval = setInterval(checkSessionStatus, 5000);
            
            // Setup activity tracking
            setupActivityTracking();
        }
        
        // Function to check session status with the server
        function checkSessionStatus() {
            if (!sessionId) return;
            
            // Find the check session status button and click it
            const buttons = document.querySelectorAll('button');
            for (const button of buttons) {
                if (button.textContent === 'check_session') {
                    button.click();
                    break;
                }
            }
        }
        
        // Function to handle session status updates
        function handleSessionStatus(status) {
            if (!status) return;
            
            if (!status.valid) {
                // Session expired - force logout
                performLogout();
                return;
            }
            
            // Handle warning display
            if (status.show_warning && !warningDisplayed) {
                showSessionWarning(status.remaining);
                warningDisplayed = true;
            } else if (!status.show_warning && warningDisplayed) {
                hideSessionWarning();
                warningDisplayed = false;
            }
            
            // Update countdown if warning is displayed
            if (warningDisplayed) {
                updateCountdown(status.remaining);
            }
        }
        
        // Function to keep session alive
        function keepSessionAlive() {
            if (!sessionId) return;
            
            // Find the keep session alive button and click it
            const buttons = document.querySelectorAll('button');
            for (const button of buttons) {
                if (button.textContent === 'keep_alive') {
                    button.click();
                    break;
                }
            }
            
            // Hide warning if displayed
            hideSessionWarning();
            warningDisplayed = false;
        }
        
        // Function to show session warning
        function showSessionWarning(remaining) {
            const overlay = document.getElementById('inactivity-overlay');
            const warning = document.getElementById('inactivity-warning');
            
            if (overlay && warning) {
                updateCountdown(remaining);
                overlay.style.display = "block";
                warning.style.display = "block";
            }
        }
        
        // Function to hide session warning
        function hideSessionWarning() {
            const overlay = document.getElementById('inactivity-overlay');
            const warning = document.getElementById('inactivity-warning');
            
            if (overlay && warning) {
                overlay.style.display = "none";
                warning.style.display = "none";
            }
        }
        
        // Function to update countdown display
        function updateCountdown(seconds) {
            const countdownEl = document.getElementById('countdown');
            if (countdownEl) {
                countdownEl.textContent = Math.max(0, seconds);
            }
        }
        
        // Function to perform logout
        function performLogout() {
            // Find and click logout button
            const logoutBtn = document.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.click();
            } else {
                // Fallback: redirect to dashboard
                window.location.href = window.location.pathname;
            }
        }
        
        // Function to setup activity tracking
        function setupActivityTracking() {
            // Track user activity events that should reset timer
            ["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(function(event) {
                document.addEventListener(event, function() {
                    // Only reset if warning is not displayed
                    if (!warningDisplayed) {
                        keepSessionAlive();
                    }
                });
            });
            
            // Setup the stay active button
            const stayActiveBtn = document.getElementById('stay-active-btn');
            if (stayActiveBtn) {
                stayActiveBtn.addEventListener('click', keepSessionAlive);
            }
        }
        
        // Function to fix chat interface heights
        function adjustChatInterfaceHeights() {
            // Wait for DOM to be fully rendered
            setTimeout(function() {
                // Target the chat interfaces specifically
                const chatInterfaces = document.querySelectorAll('.chat-interface-container');
                
                chatInterfaces.forEach(function(chatInterface) {
                    // Set minimum height
                    chatInterface.style.minHeight = '600px';
                    chatInterface.style.height = '75vh';
                    
                    // Find the chat element inside
                    const chatElement = chatInterface.querySelector('.chat');
                    if (chatElement) {
                        chatElement.style.minHeight = '600px';
                        chatElement.style.height = '75vh';
                        
                        // Find the chat window inside
                        const chatWindow = chatElement.querySelector('.chat-window');
                        if (chatWindow) {
                            chatWindow.style.minHeight = '450px';
                            chatWindow.style.height = 'calc(75vh - 150px)';
                            chatWindow.style.overflowY = 'auto';
                            
                            // Also target the content container
                            const chatContent = chatWindow.querySelector('.chat-window-content');
                            if (chatContent) {
                                chatContent.style.minHeight = '450px';
                                chatContent.style.height = 'calc(75vh - 150px)';
                                chatContent.style.overflowY = 'auto';
                            }
                        }
                    }
                });
            }, 500);
        }
        
        // Watch for session status updates
        document.addEventListener('DOMContentLoaded', function() {
            // Run height adjustment when page loads
            adjustChatInterfaceHeights();
            
            // Monitor for view changes and adjust heights again
            const observer = new MutationObserver(function(mutations) {
                adjustChatInterfaceHeights();
                
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList') {
                        // Look for the session status output element
                        const statusElements = document.querySelectorAll('[id$="session_status_output"]');
                        for (const element of statusElements) {
                            if (element.textContent.trim()) {
                                try {
                                    const status = JSON.parse(element.textContent);
                                    handleSessionStatus(status);
                                } catch (e) {
                                    console.error("Error parsing session status:", e);
                                }
                            }
                        }
                    }
                });
            });
            
            // Observe the entire document for changes
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Run height adjustment periodically to ensure it's applied
            setInterval(adjustChatInterfaceHeights, 2000);
        });
        
        // Add event listeners for the menu buttons to adjust heights when views change
        window.addEventListener('load', function() {
            // Find button elements
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(function(button) {
                button.addEventListener('click', function() {
                    // Delay to allow DOM updates
                    setTimeout(adjustChatInterfaceHeights, 300);
                });
            });
        });
        </script>
        """
        )
        
        # ------------- Navigation Callbacks -------------
        # When "General Academic Chat" is selected from the dashboard.
        gen_button.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        # When "Study Support Chat" is selected from the dashboard, show the login view with animation.
        study_button.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=True, elem_classes="container floating-card login-form-container animate-fadeInRight"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        # When "Analytics Dashboard" is selected
        analytics_button.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInRight")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        # "Back to Dashboard" buttons with animation.
        back_gen.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        # Add the header_component to the outputs
        back_study.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
                "", # Clear the current user
                gr.update(visible=False), # Hide logout component
                '''
                <div class="app-header">
                    <!-- USIU Logo on the left -->
                    <img src="/Users/apple/Desktop/chatbot_prototype/images/usiu-logo.png" alt="Logo" class="logo-dashboard" />
                    
                    <!-- Theme toggle button -->
                    <div class="header-controls">
                        <button class="theme-toggle" aria-label="Toggle theme">
                            <!-- Icon will be set by JavaScript -->
                        </button>
                    </div>
                </div>
                <div class="content-area"></div>
                '''  # Reset header to original state with theme toggle
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container, current_user, logout_component, header_component]
        )
        
        # Back from analytics to dashboard
        back_analytics.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        login_back_btn.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
        )
        
        # ------------- Authentication Logic -------------
        login_btn.click(
            handle_login,
            inputs=[user_id_input, password_input],
            outputs=[login_msg, user_id_error, password_error, proceed_btn, login_btn, session_id]
        )
        
        # When "Proceed" is clicked after successful authentication
        def proceed_to_study(session_id_value):
            # Get user info from the session
            session = get_session(session_id_value)
            user_email = session["user_id"] if session and "user_id" in session else "Guest"
            
            # Create HTML that includes the logout icon and theme toggle directly in the header
            updated_header_html = f'''
            <div class="app-header">
                <!-- USIU Logo on the left -->
                <img src="images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
                
                <!-- Controls on the right (theme toggle and logout) -->
                <div class="header-controls">
                    <!-- Theme toggle button -->
                    <button class="theme-toggle" aria-label="Toggle theme">
                        <!-- Icon will be set by JavaScript -->
                    </button>
                    
                    <!-- Logout icon directly embedded -->
                    <div class="logout-icon-container">
                        <span class="user-email">{user_email}</span>
                        <div class="logout-icon" onclick="document.getElementById('logout-btn').click();">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                                <path d="M5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5zm16 7l-4-4v3H9v2h8v3l4-4z" fill="white"/>
                            </svg>
                            <span class="tooltip">Logout</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="content-area"></div>

            <script>
                // Initialize session monitoring with the current session ID
                setTimeout(function() {{
                    if (typeof startSessionMonitoring === 'function') {{
                        startSessionMonitoring('{session_id_value}');
                    }}
                    
                    // Adjust chat heights after view change
                    if (typeof adjustChatInterfaceHeights === 'function') {{
                        adjustChatInterfaceHeights();
                    }}
                }}, 1000);
            </script>
            '''
            
            # Start tracking activity for this session
            update_session_activity(session_id_value)
            
            # Log login event in W&B
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                try:
                    wandb_tracker.log_system_metrics({
                        "login/success": 1,
                        "login/user": user_email
                    })
                except Exception as e:
                    print(f"Failed to log login event to W&B: {e}")
            
            return [
                gr.update(visible=False),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
                user_email,              # Set current user
                session_id_value,        # Pass session ID to study interface
                gr.update(visible=True), # Show logout component
                updated_header_html      # Replace entire header HTML
            ]
        
        proceed_btn.click(
            proceed_to_study,
            inputs=[session_id],
            outputs=[
                dashboard_container, 
                general_container, 
                login_container, 
                study_container,
                analytics_container,
                current_user,
                session_id_for_study,
                logout_component,
                header_component
            ]
        )
        
        def enhanced_logout(session_id_value):
            # End the session in the backend
            end_session(session_id_value)
            
            # Log logout event in W&B
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                try:
                    # Get user from session if possible
                    session = get_session(session_id_value)
                    user_email = session.get("user_id", "anonymous") if session else "anonymous"
                    
                    wandb_tracker.log_system_metrics({
                        "logout/event": 1,
                        "logout/user": user_email
                    })
                except Exception as e:
                    print(f"Failed to log logout event to W&B: {e}")
            
            # Reset the header to the original state with theme toggle but without logout icon
            original_header_html = '''
            <div class="app-header">
                <!-- USIU Logo on the left -->
                <img src="images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
                
                <!-- Theme toggle button -->
                <div class="header-controls">
                    <button class="theme-toggle" aria-label="Toggle theme">
                        <!-- Icon will be set by JavaScript -->
                    </button>
                </div>
            </div>
            <div class="content-area"></div>
            '''
            
            # Return updates for UI components
            return [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
                "",  # Clear user_id_input
                "",  # Clear password_input
                "",  # Clear any login errors
                "",  # Clear any field errors
                "",  # Clear any field errors
                gr.update(visible=True),  # Show login button
                gr.update(visible=False),  # Hide proceed button
                gr.update(visible=False),  # Hide logout component
                original_header_html  # Reset header to original state
            ]
        
        logout_btn.click(
            enhanced_logout,
            inputs=[session_id_for_study],
            outputs=[
                dashboard_container, 
                general_container, 
                login_container, 
                study_container,
                analytics_container,
                user_id_input,
                password_input,
                login_msg,
                user_id_error,
                password_error,
                login_btn,
                proceed_btn,
                logout_component,
                header_component
            ]
        )
        
    # Add the theme toggle script to the dashboard before returning
    dashboard = dashboard.queue()
    return dashboard