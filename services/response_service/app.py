# services/response_service/app.py
from flask import Flask, request, Response
from typing import Generator, Tuple, List
import time
import json
import requests
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import base64

app = Flask(__name__)

def get_system_prompt(mode: str) -> str:
    """Retrieve system prompt from the System Prompt Service."""
    resp = requests.get(f"http://localhost:5006/get_prompt?mode={mode}")
    if resp.status_code == 200:
        return resp.json().get("prompt", "")
    return ""

def load_llama_model() -> HuggingFacePipeline:
    """Load a Llama-based model for general enquiries (simulation)."""
    model_id = "huggyllama/llama-7b"  # Placeholder; adjust to a suitable model
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
    gen_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=256, do_sample=True, temperature=0.7)
    return HuggingFacePipeline(pipeline=gen_pipe)

def load_claude_model() -> HuggingFacePipeline:
    """Load a model simulating Claude 3.5 Sonnet for study support (simulation)."""
    model_id = "tiiuae/falcon-7b"  # Placeholder; adjust as needed
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
    gen_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=256, do_sample=True, temperature=0.7)
    return HuggingFacePipeline(pipeline=gen_pipe)

# Initialize LLMs (simulate loading)
GENERAL_LLM = load_llama_model()
STUDY_LLM = load_claude_model()

def synthesize_tts(text: str) -> str:
    """
    Dummy TTS function that simulates text-to-speech.
    In production, integrate an actual TTS pipeline (e.g., TensorFlowTTS) to stream audio.
    Returns base64-encoded audio data.
    """
    dummy_audio = b"DummyAudioData"  # Replace with actual TTS output
    return base64.b64encode(dummy_audio).decode('utf-8')

def generate_streaming_response(mode: str, query: str, chat_history: List[str]) -> Generator[Tuple[str, str], None, None]:
    """
    Generator that yields streaming text and voice outputs.
    Combines system prompt, chat history, and user query.
    """
    system_prompt = get_system_prompt(mode)
    prompt = f"{system_prompt}\nUser: {query}\nAssistant:"
    llm = GENERAL_LLM if mode == "general" else STUDY_LLM
    full_response = llm(prompt)
    tokens = full_response.split()
    accumulated_text = ""
    for token in tokens:
        accumulated_text += token + " "
        audio_chunk = synthesize_tts(accumulated_text)
        yield accumulated_text.strip(), audio_chunk
        time.sleep(0.2)  # Simulated delay for streaming

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.json
    query = data.get("query", "")
    mode = data.get("mode", "general")
    chat_history = data.get("chat_history", [])
    
    def generate():
        for text_chunk, audio_chunk in generate_streaming_response(mode, query, chat_history):
            yield json.dumps({"response": text_chunk, "audio": audio_chunk}) + "\n"
    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(port=5005, debug=True)
