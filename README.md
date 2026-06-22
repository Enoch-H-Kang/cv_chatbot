# 🧑‍🔬 Build a Personalized CV Chatbot

<p align="center">
  <img src="https://raw.githubusercontent.com/Enoch-H-Kang/cv_chatbot/main/docs/example_bot.png" alt="Research chatbot demo" width="700"/>
</p>
<p align="center">
  <a href="https://sites.google.com/view/hyunwookkang/ask-the-chatbot">🤖 Try the live chatbot here</a>
</p>

<br>

A complete, free-to-host chatbot that answers questions about **your** research
papers — grounded in your actual publications, speaking in your voice, and
powered by a large language model running on **your own GPU** instead of a paid
API.

> Visitors chat on a public web page. Behind the scenes, their questions are
> answered by a model running on the computer under your desk.

This repository is a **step-by-step tutorial**. Follow the numbered guides in
[`docs/`](docs/) and you'll have a live chatbot in about an hour.

---

## What you'll build

```
   ┌──────────────┐        ┌─────────────────────────┐        ┌──────────────────┐
   │   Visitor's  │  HTTPS │  Hugging Face Space      │  tunnel │  Your computer   │
   │   browser    │ ─────> │  (the "Face")            │ ──────> │  (the "Brain")   │
   │              │ <───── │  • Streamlit chat UI     │ <────── │  • Ollama        │
   └──────────────┘        │  • Embeds your papers    │         │  • Local LLM     │
                           │  • Hybrid retrieval (CPU)│         │    (your GPU)    │
                           └─────────────────────────┘         └──────────────────┘
```

- **The Face** — a free Hugging Face Space. It hosts the chat interface, embeds
  your papers, and retrieves the most relevant passages for each question. CPU
  only, so it costs nothing to run.
- **The Brain** — your own machine running [Ollama](https://ollama.com). It runs
  the large language model that actually writes the answers, using your GPU. A
  secure named tunnel ([zrok](https://zrok.io)) connects the two without
  exposing your whole computer to the internet.
- **The Knowledge** — your papers and CV, converted to plain text. The chatbot
  answers *only* from this material and admits when something isn't covered.

### Why split it this way?

| Concern | This architecture's answer |
| --- | --- |
| **Cost** | The Space is free; the model runs on hardware you already own. No per-token API bills. |
| **Privacy** | Your model and unpublished notes never leave your machine. |
| **Control** | Swap models, tune prompts, and update papers whenever you like. |
| **Grounding** | Retrieval-Augmented Generation keeps answers tied to your real work. |

---

## Key techniques (and why they matter for research Q&A)

This isn't a naive "stuff everything into the prompt" bot. It uses three ideas
that meaningfully improve answer quality on technical documents:

1. **Semantic chunking** — papers are split where the *meaning* changes, not at
   arbitrary character counts, so each retrieved passage stays self-contained.
2. **Hybrid retrieval** — combines dense vector search (understands *meaning*,
   e.g. "attention" ≈ "self-attention") with BM25 keyword search (nails *exact*
   terms like dataset names, symbols, and algorithm names), merged via
   reciprocal rank fusion.
3. **Conversational memory** — follow-ups like *"what's its accuracy?"* are
   automatically rewritten into standalone questions before retrieval, so
   context carries across turns.

Each is explained in plain language in
[`docs/04-how-the-rag-works.md`](docs/04-how-the-rag-works.md).

---

## Repository layout

```
researcher-chatbot/
├── README.md                  ← you are here
├── Dockerfile                 ← builds the Space container
├── requirements.txt           ← Python dependencies
├── .env.example               ← every config option, documented
├── .gitignore
├── src/
│   ├── streamlit_app.py       ← the whole application (well commented)
│   ├── README_SPACE.md        ← becomes the Space's home page (rename to README.md on HF)
│   ├── CV.txt                 ← your biographical sketch (replace me)
│   └── data/
│       └── sample_paper.txt   ← your papers go here, one .txt each (replace me)
├── scripts/
│   ├── start_brain.sh         ← one command to boot Ollama + the tunnel
│   ├── check_brain.sh         ← diagnoses a broken connection
│   └── pdf_to_text.py         ← converts your PDFs to indexable .txt
├── docs/
│   ├── 01-prerequisites.md
│   ├── 02-deploy-the-space.md
│   ├── 03-local-gpu-and-tunnel.md
│   ├── 04-how-the-rag-works.md
│   ├── 05-operations-runbook.md
│   ├── 06-logging-and-analytics.md
│   ├── 07-customization.md
│   └── 08-troubleshooting.md
└── .github/workflows/
    └── sync-to-hf.yml         ← optional: auto-push commits to your Space
```

---

## Quick start

If you just want the shape of it, here's the whole flow. The
[`docs/`](docs/) guides expand every step.

### 1. Get the code
```bash
git clone https://github.com/<you>/researcher-chatbot.git
cd researcher-chatbot
```

### 2. Add your research
Replace `src/CV.txt` with your CV and drop your papers into `src/data/` as
`.txt` files (use `scripts/pdf_to_text.py` to convert PDFs).

### 3. Start the Brain (on your GPU machine)
Install Ollama and zrok (see [`docs/03`](docs/03-local-gpu-and-tunnel.md)), then:
```bash
./scripts/start_brain.sh
```
Copy the printed tunnel URL — you'll need it in the next step.

### 4. Deploy the Face (Hugging Face Space)
Create a **Docker** Space, push this repo to it, and set these **Variables** in
the Space settings (see [`docs/02`](docs/02-deploy-the-space.md)):

| Key | Value |
| --- | --- |
| `RESEARCHER_NAME` | `Your Name` |
| `OLLAMA_BASE_URL` | the tunnel URL from step 3 |
| `OLLAMA_MODEL` | `qwen3:8b` (or whatever you pulled) |

### 5. Chat
Open your Space URL. Keep the Brain running on your machine while people use it.

> **Try it locally first.** You can run the whole thing on one machine before
> touching Hugging Face — see [`docs/02`](docs/02-deploy-the-space.md#run-it-locally-first).

---

## The one thing to remember

**The chatbot only works while your local machine is on and running
`start_brain.sh`.** If you close your laptop, the Face stays up but has no Brain
to talk to, and answers will time out. The
[operations runbook](docs/05-operations-runbook.md) covers keeping it alive and
restarting after a reboot.

---

## License

Code in this tutorial is provided under the MIT License (see [`LICENSE`](LICENSE)).
The example Hugging Face Space metadata uses `openrail`. Your papers and CV
remain yours — check your publisher agreements before posting full paper text
publicly, and prefer preprint/accepted versions you have the right to share.

## Acknowledgements

The architecture in this tutorial is adapted from a real researcher's chatbot
built on Hugging Face Spaces with Streamlit, LlamaIndex, Ollama, and zrok.
