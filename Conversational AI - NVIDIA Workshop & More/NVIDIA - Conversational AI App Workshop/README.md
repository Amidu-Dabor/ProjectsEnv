# NVIDIA DLI: Building Conversational AI Applications

My completed lab notebooks from the **NVIDIA Deep Learning Institute** course *Building Conversational AI Applications* (July 2025). The course builds a voice assistant from speech recognition through to deployment on Kubernetes. The notebooks are NVIDIA's course material, run and completed on the course's GPU environment.

## What the labs cover

| Notebook | Topic |
|---|---|
| `00. Intro_Overview` | Course overview |
| `01. NVIDIA GPU Cloud Setup - NGC` | Connecting to the NGC registry and downloading Riva |
| `1a. ASR_Pipeline` (zipped), `1b. ASR_Deployment` | **Speech recognition (ASR):** how ASR models work, then deploying an ASR service with NVIDIA Riva |
| `2a. TTS_Pipeline`, `2b. TTS_Deployment` | **Text-to-speech (TTS):** text normalisation, grapheme-to-phoneme conversion and spectrogram synthesis with NeMo (FastPitch, HiFi-GAN), then deployment with Riva |
| `3a. Full_Pipeline` | **End to end:** ASR → NLP (entity recognition, dialogue) → TTS, plus an LLM step with LangChain and NVIDIA AI endpoints |
| `4a–4c. K8s_*` | **Kubernetes:** enabling GPUs in a cluster, monitoring with Prometheus and Grafana, and deploying Riva with Helm |
| `assessment`, `solutions` | Final assessment: a voice-driven question-answering assistant built with Riva |

The PDFs are NVIDIA's course catalogue and learning-path guides.

## Tech

NVIDIA Riva · NeMo · LangChain · Kubernetes · Helm · Prometheus · Grafana · Docker · Python

> These notebooks need NVIDIA's course environment (GPUs, Riva containers and an NGC API key) and won't run as they are on an ordinary machine.
