# services/study_support_service.py

import os
import time
import anthropic
import gradio as gr
from typing import List, Dict, Any, Generator, Optional

from services.auth_service import update_session_activity, get_session
from services.file_service import FileProcessor
from api_gateway.gateway import get_service

class StudySupportService:
    """Service for handling study support with file upload capabilities."""
    
    def __init__(self, system_prompt: str, model: str):
        self.system_prompt = system_prompt
        self.model = model
        self.claude_client = anthropic.Anthropic()
        self.current_file_path = None
        self.auto_clear_files_state = True
        
    def generate_initial_greeting(self) -> str:
        """Generate a dynamic greeting using Claude."""
        try:
            response = self.claude_client.messages.create(
                model=self.model,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"[Warning] could not generate dynamic greeting with Claude: {e}")
            return "Hello and welcome! I'm your AI study assistant, here to help you with your academic journey."
    
    def chat(self, message: str, chat_history: list, session_id: str) -> Generator[str, None, None]:
        """Handle study support chat with file processing and metrics tracking."""
        start_time = time.time()
        
        # Debug log
        print(f"Starting chat with file: {self.current_file_path}")
        
        # Get W&B tracker
        wandb_tracker = get_service("wandb_tracker")
        
        # Session validation
        if session_id:
            update_session_activity(session_id)
            sess = get_session(session_id)
            if not sess or not sess.get("logged_in", False):
                yield "Your session has expired. Please log in again."
                return
            user_id = sess.get("user_id", "anonymous")
        else:
            user_id = "anonymous"
            session_id = f"study_{int(time.time())}"
        
        chat_history = chat_history or []
        
        # Add header for new conversations
        if not chat_history:
            chat_history.insert(
                0,
                {
                    "role": "header",
                    "content": f"<div style='text-align:center;font-weight:bold;'>Conversation started on {time.strftime('%Y-%m-%d %H:%M')}</div>",
                    "session_id": session_id,
                    "user_id": user_id
                },
            )
        
        # Build messages for Claude
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
        
        # File processing
        file_processing_start = None
        file_size = None
        file_type = None
        file_text = None
        context_used = []
        
        if self.current_file_path:
            try:
                file_to_process = self.current_file_path
                file_processing_start = time.time()
                print(f"Processing file: {file_to_process}")
                
                file_text = FileProcessor.read_file(file_to_process)
                meta = FileProcessor.get_file_metadata(file_to_process)
                file_size = meta.get("size_bytes", 0)
                file_type = meta.get("extension", "unknown")
                
                compact_meta = ", ".join(
                    f"{k}: {v}"
                    for k, v in meta.items()
                    if k in ("filename", "extension", "size_formatted", "pages", "rows", "columns", "dimensions")
                )
                
                context_used = [f"Uploaded file ({compact_meta})"]
                
                file_msg = (
                    f"I've uploaded a file ({compact_meta}) with the following content:\n\n"
                    f"{file_text[:60000]}{'…[truncated]' if len(file_text) > 60000 else ''}"
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
                
                # Clear file if auto-clear is enabled
                if self.auto_clear_files_state:
                    self.current_file_path = None
                    
            except Exception as e:
                error_msg = f"[Error processing file: {e}]"
                print(f"File processing error: {e}")
                msgs.append({"role": "user", "content": error_msg})
                if wandb_tracker:
                    wandb_tracker.log_error("file_processing", str(e), session_id, message)
        
        # Generate response with Claude
        final_response = ""
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                stream = self.claude_client.messages.stream(
                    model=self.model,
                    system=self.system_prompt,
                    messages=msgs,
                    max_tokens=63_800,
                    temperature=0.7,
                )
                
                with stream as s:
                    for chunk in s.text_stream:
                        final_response += chunk
                        yield final_response
                
                # Success - log metrics
                end_time = time.time()
                response_time = end_time - start_time
                
                if wandb_tracker:
                    # Estimate token count
                    token_estimate = len(message.split()) + len(final_response.split()) * 1.3
                    if file_text:
                        token_estimate += len(file_text.split()) * 0.8
                    
                    wandb_tracker.log_conversation(
                        session_id=session_id,
                        user_id=user_id,
                        chat_type="study_support",
                        query=message,
                        response=final_response,
                        context_used=context_used,
                        tokens=int(token_estimate),
                        response_time=response_time,
                        feedback=None
                    )
                
                break
                
            except anthropic.APIStatusError as e:
                if e.status_code == 529 and attempt < max_retries - 1:
                    final_response = ""
                    time.sleep(retry_delay)
                    retry_delay *= 1.5
                    continue
                else:
                    error_msg = "I apologize, but the service is currently busy. Please try again in a few moments."
                    if wandb_tracker:
                        wandb_tracker.log_error("claude_overload", str(e), session_id, message)
                    yield error_msg
                    break
                    
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error. Please try again."
                print(f"Claude generation error: {e}")
                if wandb_tracker:
                    wandb_tracker.log_error("claude_generation", str(e), session_id, message)
                yield error_msg
                break
    
    def log_feedback(self, message: str, response: str, flag: str) -> str:
        """Log user feedback to W&B."""
        try:
            wandb_tracker = get_service("wandb_tracker")
            if wandb_tracker:
                session_id = f"feedback_study_{int(time.time())}"
                user_id = "anonymous"
                
                feedback = "neutral"
                if flag == "Like":
                    feedback = "positive"
                elif flag == "Dislike":
                    feedback = "negative"
                
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
    
    def update_file_status(self, f):
        """Update file status when a file is uploaded."""
        self.current_file_path = f
        
        if not f:
            return "No file uploaded"
        if isinstance(f, (str, os.PathLike)):
            try:
                size = os.path.getsize(f)
                return f"{os.path.basename(f)} • {FileProcessor._human_size(size)}"
            except Exception as e:
                return f"File received but size unknown ({e})"
        name = getattr(f, "name", "unknown")
        return f"{name} ready"
    
    def test_file_processing(self, f):
        """Test file processing functionality."""
        if not f:
            return "No file selected. Please upload a file first."
        try:
            content_preview = FileProcessor.read_file(f)[:1000]
            meta = FileProcessor.get_file_metadata(f)
            meta_str = "\n".join(f"- {k}: {v}" for k, v in meta.items())
            return f"✅ **Metadata:**\n{meta_str}\n\n📄 **Preview:**\n{content_preview}"
        except Exception as e:
            return f"❌ Error testing file: {e}"
    
    def clear_file(self):
        """Clear the uploaded file."""
        self.current_file_path = None
        return None, "File cleared"
    
    def toggle_auto_clear(self, value):
        """Toggle auto-clear setting for files."""
        self.auto_clear_files_state = value
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for study support."""
        initial_greeting = self.generate_initial_greeting()
        initial_messages = [{"role": "assistant", "content": initial_greeting}]
        
        with gr.Blocks(elem_id="study-chat-interface") as interface:
            session_id_box = gr.Textbox(visible=False)
            
            chatbot = gr.Chatbot(
                value=initial_messages,
                type="messages",
                show_copy_button=True,
                avatar_images=("images/user-icon1.png", "images/chatbot-icon.png"),
                sanitize_html=True,
                allow_tags=["thinking"],
                height=600,
            )
            
            chat_interface = gr.ChatInterface(
                fn=self.chat,
                chatbot=chatbot,
                editable=True,
                type="messages",
                save_history=True,
                title="Study Support",
                description=(
                    "<div style='display:flex; justify-content:center;'>"
                    "Hi there! I'm your AI study assistant, here to help you with your academic journey. "
                    "You can upload files using the File Upload section below."
                    "</div>"
                ),
                examples=[
                    ["Help me understand recursion in programming"],
                    ["Can you explain the Pythagorean theorem?"],
                    ["I need help writing an essay introduction"],
                    ["Debug this Python code for me"]
                ],
                cache_examples=False,
                additional_inputs=[session_id_box],
                cache_mode="eager",
                flagging_mode="manual",
                flagging_options=("Like", "Dislike", "Neutral"),
                flagging_dir="user_feedback_study",
            )
            
            # Set up feedback handler
            try:
                if hasattr(chat_interface, "flagging_callback"):
                    chat_interface.flagging_callback = self.log_feedback
            except Exception as e:
                print(f"Could not attach study feedback handler: {e}")
            
            # File upload section
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
            
            # Connect events
            file_input.change(self.update_file_status, file_input, file_status)
            test_button.click(self.test_file_processing, file_input, test_output)
            clear_button.click(self.clear_file, None, [file_input, file_status])
            auto_clear_files.change(self.toggle_auto_clear, auto_clear_files, None)
        
        return interface.queue(default_concurrency_limit=1000)