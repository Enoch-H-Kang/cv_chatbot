# 01 · Prerequisites

Before you start, make sure you have the following. None of it costs money.

## Accounts

- **A Hugging Face account** — free. Sign up at <https://huggingface.co/join>.
  This hosts the public chat page (the "Face").
- **A zrok account** — free. Sign up at <https://zrok.io>. This creates the
  secure tunnel from the Space to your computer. (Alternatives like Cloudflare
  Tunnel or ngrok also work; see [docs/03](03-local-gpu-and-tunnel.md).)
- **A GitHub account** (optional but recommended) — for version control and
  optional auto-deploy to your Space.

## Hardware

- **A computer with a GPU** that stays on while people use the chatbot. This
  runs the language model. A consumer GPU with **8 GB of VRAM** comfortably runs
  an 8-billion-parameter model like `qwen3:8b` or `llama3.1:8b`.
  - No GPU? It still works on CPU, just slower. Pick a smaller model such as
    `qwen2.5:3b` or `phi3:mini`.
  - Apple Silicon (M1/M2/M3) works well with Ollama out of the box.

> The Hugging Face Space itself is **CPU-only and free**. You do *not* need to
> pay for a GPU Space — that's the whole point of running the model at home.

## Software (on your local GPU machine)

You'll install these in [docs/03](03-local-gpu-and-tunnel.md), but here's what's
coming:

- **[Ollama](https://ollama.com/download)** — runs the language model locally
  with a simple API.
- **[zrok](https://docs.zrok.io/docs/getting-started/)** — the tunnel client.
- **Git** — to clone this repository.
- **Python 3.10+** — only needed if you want to run the app locally or use the
  PDF conversion script.

## Knowledge

You don't need to be an ML engineer. You should be comfortable with:

- Running commands in a terminal.
- Editing a text file.
- Basic Git (`clone`, `add`, `commit`, `push`) — or willingness to learn the
  three commands as you go.

## Your research material

Gather what the chatbot will talk about:

- **Your CV** as plain text (a short biographical sketch is enough).
- **Your papers** as text. PDFs are fine to start with — the helper script
  `scripts/pdf_to_text.py` converts them. Aim for the versions you have the
  right to share publicly (preprints, accepted manuscripts).

---

**Next:** [02 · Deploy the Space](02-deploy-the-space.md)
