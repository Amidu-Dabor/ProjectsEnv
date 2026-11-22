---
title: chatbot_prototype
app_file: app.py
sdk: gradio
sdk_version: 5.12.0
---

# AI Assistant for Academic Support (USIU-Africa)

A modular Python RAG assistant that answers students' questions about USIU-Africa and helps with their studies. It is built on Claude and GPT-4o, with a metrics dashboard and an automated evaluation script.

*Built as my MSc research project in Information Systems & Technology (Software Engineering), USIU-Africa, 2023–2025.*

---

## The problem

Answers to everyday student questions (admissions, fees, financial aid, the academic calendar, campus services) are spread across many pages of the university website. Students also need study help grounded in their own course material, which a general chatbot cannot give. The aim was one assistant that answers quickly from university sources and can be measured.

## What it does

- **General Enquiries chat:** answers university questions using retrieval (RAG) over a vector database built from the USIU-Africa website.
- **Study Support chat:** helps with coursework, including questions about uploaded PDF, Word, PowerPoint and text files. Requires login.
- **Voice chat:** speech in and out through the Hume AI voice API.
- **Sessions:** login, an inactivity warning and automatic expiry of idle sessions.
- **Feedback and flagging:** users can rate or flag answers; flags and feedback are saved to CSV files for review.
- **Metrics:** response times, gateway metrics and a performance summary at `/metrics-dashboard` and `/api/performance-summary`, with optional tracking in Weights & Biases.

**Models:** Claude 3.7 Sonnet writes the answers in both chats, GPT-4o summarises retrieved passages, and OpenAI embeddings power the search. Model names live in `configs/config.py`.

## Architecture

```
                    Gradio UI  (services/ui_service.py)
                             │
                      API gateway  (api_gateway/gateway.py)
        service registry · request routing · timing and error metrics
                             │
   ┌───────────────┬─────────┴──────┬───────────────┬──────────────┐
General chat     Study support     Voice chat      Auth/sessions    Files
(RAG)            (file Q&A)        (Hume AI)       (auth_service)   (file_service)
   │
Retriever ◄── Chroma vector DB ◄── DataCurator (load, split, embed)
                                         ▲
                       Scraper (crawls the USIU-Africa website into categories)
```

Each capability is a separate service registered with the gateway, so one can be changed without touching the others. The gateway buffers metrics and reports them in batches, keeping logging out of the request path.

| Path | Purpose |
|---|---|
| `app.py` | Entry point: loads the vector store, registers services, starts the UI and metrics endpoints |
| `api_gateway/` | Service registry, routing, metrics and performance summary |
| `services/` | UI, chat, study support, voice, auth, file processing, W&B tracking |
| `vector_services/` | Website scraper, document curation and embedding, vector store visualiser |
| `system_prompts/` | Prompt management for each assistant |
| `configs/config.py` | Model names and settings; API keys come from environment variables |
| `evaluate_llm_responses.py` | Automated evaluation script |
| `evaluation_results/` | Test queries, saved results, charts and an HTML report |

## Getting started

### Requirements

- Python 3.11
- API keys: OpenAI and Anthropic (required); Hume AI and Weights & Biases (optional)

### 1. Install

```bash
git clone https://github.com/Amidu-Dabor/ProjectsEnv.git
cd "ProjectsEnv/Conversational AI - NVIDIA Workshop & More/AI Assistant for Academic Support"
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your keys

Create a `.env` file in this folder (it is git-ignored):

```
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
HUMEAI_API_KEY=your-key          # optional, for voice chat
HUMEAI_CONFIG_ID=your-config-id  # optional
WANDB_API_KEY=your-key           # optional, for experiment tracking
```

### 3. Build the knowledge base (first run only)

The repository does not include the scraped website content, so build it once. Run both commands from this folder:

```bash
python vector_services/scraper.py        # crawls usiu.ac.ke into usiu-knowledge-base/
python vector_services/data_curator.py   # splits and embeds it into usiu_vector_db/
```

### 4. Run

```bash
python app.py
```

Then open http://localhost:7860. The metrics dashboard is at http://localhost:7860/metrics-dashboard.

## Evaluation

`evaluate_llm_responses.py` sends test queries from `evaluation_results/*_test_queries.json` to each assistant, repeating each one several times. It records response time, token use and an accuracy score based on the key points each answer should contain, and compares the General chat **with and without RAG**. It then writes CSV and JSON results, charts and an HTML report.

```bash
python evaluate_llm_responses.py --iterations 5 --output-dir evaluation_results
python evaluate_llm_responses.py --disable-rag        # run without retrieval, for comparison
python evaluate_llm_responses.py --disable-wandb      # run without W&B logging
```

The saved run in `evaluation_results/` covers 150 responses: 100 from the General chat (50 with RAG, 50 without) and 50 from Study Support.

## Engineering notes

- **Modular services behind one gateway:** each capability is its own class, registered and called through a routing layer that also measures it.
- **Retries on rate limits:** embedding calls use a retry decorator, so a temporary API limit does not stop the build.
- **No secrets in code:** keys come from `.env`.
- **Optional local model:** `services/quantized_model_loader.py` can load an open model in 4-bit (bitsandbytes) to cut memory use.

## Limitations and next steps

- Expand the test set beyond the current handful of questions, and grade answers against labelled reference answers.
- Add unit tests for the gateway, auth and file services.
- Containerise with Docker for a one-command, reproducible setup.
- Improve retrieval quality with better chunking and re-ranking.

## Tech stack

Python · Gradio · FastAPI · LangChain · Chroma · Anthropic Claude · OpenAI GPT-4o and embeddings · Hume AI · Weights & Biases · BeautifulSoup · pandas · Matplotlib and Plotly

## Author

**Amidu Dabor** · [LinkedIn](https://linkedin.com/in/adabor) · [GitHub](https://github.com/Amidu-Dabor)
