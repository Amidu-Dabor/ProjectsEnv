# ui/gradio_app.py
import os
import gradio as gr
import requests
import json
from typing import Generator, Tuple

# Use env variable if set; otherwise default to localhost (for local testing)
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://localhost:5008/query")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5001/login")

def authenticate(username: str, password: str) -> Tuple[str, str]:
    resp = requests.post(f"{AUTH_SERVICE_URL}", json={"username": username, "password": password})
    if resp.status_code == 200:
        token = resp.json().get("token")
        return token, "Authentication successful."
    return "", "Authentication failed."

def stream_response(query: str, mode: str, token: str, chat_history: list) -> Generator[Tuple[str, str], None, None]:
    headers = {}
    if mode == "study":
        headers["Authorization"] = token
    payload = {"query": query, "mode": mode, "chat_history": chat_history}
    with requests.post(API_GATEWAY_URL, json=payload, headers=headers, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                yield data.get("response", ""), data.get("audio", "")

css = """
body { background-color: #f7f7f7; font-family: Arial, sans-serif; }
.gradio-container { max-width: 600px; margin: auto; }
.chat-message { border-radius: 10px; padding: 10px; margin: 5px; }
.user { background-color: #e1f5fe; text-align: right; }
.assistant { background-color: #fff9c4; text-align: left; }
.copy-btn { cursor: pointer; color: blue; }
"""

with gr.Blocks(css=css) as demo:
    chat_history_state = gr.State([])
    auth_token_state = gr.State("")
    
    with gr.Tabs():
        with gr.Tab("General Academic Enquiries"):
            chatbot = gr.Chatbot(label="Academic Chatbot")
            query_input = gr.Textbox(label="Your Query", placeholder="Type your question here...", interactive=True)
            send_btn = gr.Button("Send")
            voice_output = gr.Audio(label="Voice Output", type="filepath", interactive=False)
            
            def send_general(query, history):
                history = history + [[query, ""]]
                for text, audio in stream_response(query, "general", "", history):
                    history[-1][1] = text
                    yield history, audio
                return history, None
            
            # Use .click(..., stream=True) with newer versions of Gradio.
            send_btn.click(send_general, inputs=[query_input, chat_history_state],
                           outputs=[chatbot, voice_output], stream=True)
        
        with gr.Tab("Study With Me"):
            auth_username = gr.Textbox(label="Username", placeholder="Enter username")
            auth_password = gr.Textbox(label="Password", placeholder="Enter password", type="password")
            login_btn = gr.Button("Login")
            login_status = gr.Textbox(label="Status", interactive=False)
            study_chatbot = gr.Chatbot(label="Study Support Chatbot")
            study_query_input = gr.Textbox(label="Your Query", placeholder="Type your study query...", interactive=True)
            study_send_btn = gr.Button("Send")
            study_voice_output = gr.Audio(label="Voice Output", type="filepath", interactive=False)
            
            def do_login(username, password):
                token, msg = authenticate(username, password)
                return token, msg
            
            login_btn.click(do_login, inputs=[auth_username, auth_password],
                            outputs=[auth_token_state, login_status])
            
            def send_study(query, history, token):
                history = history + [[query, ""]]
                for text, audio in stream_response(query, "study", token, history):
                    history[-1][1] = text
                    yield history, audio
                return history, None
            
            study_send_btn.click(send_study, inputs=[study_query_input, chat_history_state, auth_token_state],
                                 outputs=[study_chatbot, study_voice_output], stream=True)
    
demo.launch(share=True, server_name="0.0.0.0", server_port=7860, inbrowser=True)
