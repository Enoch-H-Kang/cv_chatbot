# 02 · Deploy the Space (the "Face")

The Space is the public web page people visit. It's a **Docker** Space running
Streamlit. This guide gets it online.

> You can do this before or after setting up the local GPU. The Space will load
> fine on its own; it just won't be able to answer questions until the Brain
> ([docs/03](03-local-gpu-and-tunnel.md)) is running and `OLLAMA_BASE_URL` points
> at it.

---

## Run it locally first

Before deploying, it's worth confirming everything works on one machine.

```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set RESEARCHER_NAME, and OLLAMA_BASE_URL=http://localhost:11434,
# and OLLAMA_MODEL to a model you've pulled (see docs/03 for Ollama setup)

streamlit run src/streamlit_app.py
```

Open <http://localhost:8501>. If you've already got Ollama running locally
(docs/03), you can chat with the sample paper right away. Once that works,
deploying is mostly copying files to Hugging Face.

> **Loading the `.env` file:** Streamlit doesn't read `.env` automatically. For
> local runs, either export the variables in your shell first, or install
> `python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` at the
> top of `streamlit_app.py`. On Hugging Face you set the variables in the UI
> (below), so this only matters locally.

---

## Step 1 — Create the Space

1. Go to <https://huggingface.co/new-space>.
2. **Owner:** you. **Space name:** e.g. `researchbot`.
3. **License:** `openrail` (or your choice).
4. **Select the Space SDK:** choose **Docker** → **Blank**.
5. **Hardware:** leave it on the free **CPU basic**. (No GPU needed.)
6. **Visibility:** Public (so people can use it) or Private (for testing).
7. Click **Create Space**.

## Step 2 — Push the code to the Space

A Space is just a Git repository. You have two options.

### Option A — push directly with Git

```bash
# Add your Space as a remote (URL shown on the Space's "Files" tab)
git remote add space https://huggingface.co/spaces/<you>/researchbot

# Hugging Face needs your README.md to carry the Space metadata header.
# Use the Space-specific one from src/:
cp src/README_SPACE.md README.md   # overwrites the tutorial README for HF

git add .
git commit -m "Deploy research chatbot"
git push space main
```

> ⚠️ **Two READMEs, on purpose.** The repo's top-level `README.md` is the
> tutorial (great for GitHub). Hugging Face instead needs the YAML metadata
> header from `src/README_SPACE.md`. When pushing to the Space, that file must
> become the top-level `README.md`. If you keep the project on GitHub *and*
> mirror to HF, the optional workflow in
> [`.github/workflows/sync-to-hf.yml`](../.github/workflows/sync-to-hf.yml)
> handles this swap automatically.

### Option B — upload through the website

On the Space's **Files** tab, click **Add file → Upload files** and upload the
`Dockerfile`, `requirements.txt`, the `src/` folder, and a `README.md`
containing the metadata header from `src/README_SPACE.md`.

## Step 3 — Set configuration variables

Go to your Space → **Settings** → **Variables and secrets**.

Add these as **Variables** (they're not secret):

| Name | Example value | What it does |
| --- | --- | --- |
| `RESEARCHER_NAME` | `Jane Q. Researcher` | Page title + bot persona |
| `OLLAMA_BASE_URL` | `https://researchbot.share.zrok.io` | The tunnel URL from [docs/03](03-local-gpu-and-tunnel.md) |
| `OLLAMA_MODEL` | `qwen3:8b` | The model you pulled locally |

Optional tuning variables (defaults are sensible — see
[docs/07](07-customization.md)): `LLM_TEMPERATURE`, `CONTEXT_WINDOW`,
`EMBED_MODEL_NAME`, `REQUEST_TIMEOUT`, `TUNNEL_SKIP_HEADER`.

If you want Q&A logging, add `LOG_DATASET` and an `HF_TOKEN` **Secret** — see
[docs/06](06-logging-and-analytics.md).

## Step 4 — Watch it build

The Space rebuilds the Docker image on every push. Click the **Logs** tab to
watch. First build takes a few minutes (installing dependencies). When it says
the app is running, open the **App** tab.

> On first load the app indexes your papers, which can take **30–60 seconds**
> because semantic chunking runs on CPU. This happens once per boot.

---

## What "working" looks like

- The chat page loads with your name in the title. ✅ The Face is deployed.
- You type a question and get a grounded answer. ✅ The Brain is connected.
- You type a question and it spins then errors/times out. ➡️ The Face is fine,
  but the Brain isn't reachable. Go to [docs/03](03-local-gpu-and-tunnel.md) and
  [docs/08](08-troubleshooting.md).

---

**Next:** [03 · Local GPU and tunnel](03-local-gpu-and-tunnel.md)
