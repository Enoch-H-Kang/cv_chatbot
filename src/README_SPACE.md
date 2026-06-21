---
title: Research Assistant
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 8501
tags:
  - streamlit
  - rag
  - llama-index
pinned: false
short_description: A personalized RAG chatbot for a researcher's publications.
license: openrail
---

# 🚀 Research Assistant

A personalized chatbot that answers questions about a researcher's publications.
It runs as a Hugging Face Space (the lightweight "Face") and forwards each
question to a large language model running on the researcher's own GPU at home
(the "Brain"), reached through a secure named tunnel.

**This file is the Space's home page.** The YAML block at the top is required by
Hugging Face — `sdk: docker` and `app_port: 8501` must stay as they are. For the
full setup walkthrough, see the project repository's `README.md` and the `docs/`
folder.

## How it works

1. The Space embeds your papers and stores them in a vector index (CPU only).
2. For each question it runs **hybrid retrieval** (semantic + keyword) to find
   the most relevant passages.
3. It sends those passages, plus your question, to your local LLM via the tunnel.
4. The model answers using only your research, and the answer streams back.

## Operating the local "Brain"

The GPU box needs Ollama and the tunnel running before the chat will work.
See `docs/03-local-gpu-and-tunnel.md` and `docs/05-operations-runbook.md` in the
repository for the start/stop commands and troubleshooting steps.
