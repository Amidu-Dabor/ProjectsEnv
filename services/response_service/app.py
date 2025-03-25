import os
from flask import Flask, request, Response
from typing import Generator, Tuple, List
import time
import json
import base64
import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Model names (can be overridden by env vars)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")

app = Flask(__name__)

def get_system_prompt(mode: str) -> str:
    system_prompt_url = os.environ.get("SYSTEM_PROMPT_SERVICE_URL", "http://localhost:5006")
    try:
        resp = __import__("requests").get(f"{system_prompt_url}/get_prompt?mode={mode}")
        if resp.status_code == 200:
            return resp.json().get("prompt", "")
    except Exception as e:
        print(f"Error retrieving system prompt: {e}")
    return ""

def synthesize_tts(text: str) -> str:
    dummy_audio = b"DummyAudioData"
    return base64.b64encode(dummy_audio).decode('utf-8')

def generate_response_openai(prompt: str) -> Generator[Tuple[str, str], None, None]:
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    accumulated = ""
    for chunk in response:
        if 'choices' in chunk:
            delta = chunk['choices'][0].get('delta', {})
            content = delta.get('content', "")
            accumulated += content
            yield accumulated, synthesize_tts(accumulated)
            time.sleep(0.2)

def generate_response_claude(prompt: str) -> Generator[Tuple[str, str], None, None]:
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    full_prompt = f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"
    response = client.completion_create(
        model=CLAUDE_MODEL,
        prompt=full_prompt,
        stream=True,
        max_tokens_to_sample=256,
        stop_sequences=["\n\nHuman:"]
    )
    accumulated = ""
    for chunk in response:
        text = chunk.get("completion", "")
        accumulated += text
        yield accumulated, synthesize_tts(accumulated)
        time.sleep(0.2)

def generate_streaming_response(mode: str, query: str, chat_history: List[str]) -> Generator[Tuple[str, str], None, None]:
    system_prompt = get_system_prompt(mode)
    prompt = f"{system_prompt}\nUser: {query}\nAssistant:"
    if mode == "general":
        return generate_response_openai(prompt)
    else:
        return generate_response_claude(prompt)

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
    port = int(os.environ.get("PORT", 5005))
    app.run(port=port, debug=True)
