# configs/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file.
load_dotenv()

# LLM Model Settings
GPT4O_MODEL = "gpt-4o"  
CLAUDE_MODEL = "claude-3-7-sonnet-20250219" 
# CLAUDE_MODEL_V4_OPUS = "claude-opus-4-20250514"
# CLAUDE_MODEL_V4_SONNET = "claude-sonnet-4-20250514"
# LLAMA_MODEL = "meta-llama/Meta-Llama-3-8B"
# MISTRAL_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# API Keys
GPT4O_API_KEY = os.getenv("OPENAI_API_KEY", "")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN")
# Hume Voice API config
# HUMEAI_API_KEY = os.getenv("HUMEAI_API_KEY", "")
# HUMEAI_CONFIG_ID = os.getenv("HUMEAI_CONFIG_ID", "")

# Weights & Biases integration
WANDB_PROJECT_NAME = "usiu-chatbot"
WANDB_ENTITY = "daboramidu93-united-states-international-university-africa"
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "")

# Scraping parameters
SCRAPER_MAX_DEPTH = 3
SCRAPER_MAX_PAGES = 200
MIN_CONTENT_LENGTH = 200
