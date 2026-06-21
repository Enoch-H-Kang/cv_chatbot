"""
Personalized Research Chatbot — Streamlit front-end.

Architecture (see docs/ARCHITECTURE.md for the full picture):

    Browser ──> Hugging Face Space (this Streamlit app, the "Face")
                      │
                      │  embeddings + retrieval run here on CPU
                      │
                      └──> zrok tunnel ──> your laptop/workstation (the "Brain")
                                                 └──> Ollama serving a local LLM

The Space is CPU-only and free. The heavy LLM runs on *your* GPU at home and is
exposed to the Space through a secure named tunnel. The Space embeds your papers,
retrieves the most relevant chunks for each question, and asks your local model to
answer using only those chunks (Retrieval-Augmented Generation).

Every file in this project is configured from environment variables so you never
have to hard-code your own name, URL, or model into the source. Copy `.env.example`
to `.env` for local runs, or set the same keys as "Variables" in your Space settings.
"""

import os
import json
import uuid
import datetime
from pathlib import Path

import httpx
import streamlit as st

from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from huggingface_hub import CommitScheduler


# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
# Everything here is read from the environment so the same code runs locally
# and on Hugging Face without edits. See .env.example for the full list.

RESEARCHER_NAME = os.environ.get("RESEARCHER_NAME", "Your Name")

# The public URL of your zrok tunnel that points at your local Ollama server.
# Example: https://researchbot.share.zrok.io
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# The Ollama model tag you pulled on your machine, e.g. "qwen3:8b" or "llama3.1:8b".
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")

# Embedding model. Runs locally on the Space CPU — keep it small and fast.
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "BAAI/bge-small-en-v1.5")

# Lower temperature => more factual, less creative. Good for research Q&A.
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.3"))

# How many tokens of context the model should consider per request.
CONTEXT_WINDOW = int(os.environ.get("CONTEXT_WINDOW", "8192"))

# Seconds to wait for the local GPU to answer before giving up.
REQUEST_TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", "120.0"))

# Optional: a header some tunnels (like zrok) require to skip an interstitial page.
# Leave blank if you are not using zrok.
TUNNEL_SKIP_HEADER = os.environ.get("TUNNEL_SKIP_HEADER", "skip_zrok_interstitial")


# ---------------------------------------------------------------------------
# 2. LOGGING SETUP (optional — logs to a private Hugging Face Dataset)
# ---------------------------------------------------------------------------
# This lets you review every question visitors ask so you can improve the bot.
# To enable: create a PRIVATE dataset on HF (e.g. "yourname/researchbot-logs"),
# add a write-scoped HF_TOKEN secret to your Space, and set LOG_DATASET below.
# If LOG_DATASET is empty, logging is silently disabled.

LOG_DATASET = os.environ.get("LOG_DATASET", "")  # "" disables logging
LOG_FILE = "qna_logs.jsonl"

scheduler = None
if LOG_DATASET:
    try:
        # CommitScheduler batches new log lines and pushes them to the dataset
        # repo every few minutes (and once more on shutdown), so we never block
        # the chat UI on a network call.
        scheduler = CommitScheduler(
            repo_id=LOG_DATASET,
            repo_type="dataset",
            folder_path="logs",
            path_in_repo="data",
            every=10,  # minutes
        )
    except Exception as e:  # noqa: BLE001 — never let logging break the app
        st.warning(f"Logging disabled (could not start scheduler): {e}")
        scheduler = None


def log_interaction(question: str, answer: str) -> None:
    """Append one Q&A pair to the local log file; the scheduler uploads it."""
    if scheduler is None:
        return
    log_path = Path("logs") / LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": st.session_state.get("session_id"),
        "question": question,
        "answer": str(answer),
    }
    # The scheduler's lock prevents a race between our write and its upload.
    with scheduler.lock:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# 3. CUSTOM OLLAMA CLIENT
# ---------------------------------------------------------------------------
# zrok puts an "interstitial" warning page in front of new tunnels. Sending the
# skip header on every request bypasses it so the API responds with raw JSON.
# If you are not using zrok, this subclass is harmless.

class CustomOllama(Ollama):
    def _get_client(self):
        headers = {}
        if TUNNEL_SKIP_HEADER:
            headers[TUNNEL_SKIP_HEADER] = "true"
        return httpx.Client(
            base_url=self.base_url,
            timeout=REQUEST_TIMEOUT,
            headers=headers,
        )


# ---------------------------------------------------------------------------
# 4. PAGE + MODEL SETUP
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{RESEARCHER_NAME}'s Research Assistant",
    layout="centered",
)

# A stable id per browser session, used to group log entries by conversation.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

try:
    # Embedding model runs on the Space CPU — lightweight and fast to load.
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    Settings.embed_model = embed_model

    # The LLM itself runs on YOUR machine, reached through the tunnel URL.
    Settings.llm = CustomOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        request_timeout=REQUEST_TIMEOUT,
        context_window=CONTEXT_WINDOW,
        temperature=LLM_TEMPERATURE,
    )
except Exception as e:  # noqa: BLE001
    st.error(f"Configuration error while initializing models: {e}")
    st.stop()


# ---------------------------------------------------------------------------
# 5. INDEXING — semantic chunking + vector index (cached across reruns)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Indexing your research (first load can take ~30–60s)...")
def load_resources():
    """Read the CV + papers, chunk them semantically, and build a vector index.

    @st.cache_resource ensures this expensive work runs once per Space boot,
    not on every user keystroke. Returns (cv_text, vector_index, nodes).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # A. Load the CV (used as biographical context in the system prompt).
    cv_text = ""
    cv_path = os.path.join(script_dir, "CV.txt")
    if os.path.exists(cv_path):
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()

    # B. Load every .txt file under src/data/ as a document.
    data_dir = os.path.join(script_dir, "data")
    if not os.path.exists(data_dir):
        return cv_text, None, None

    documents = SimpleDirectoryReader(
        data_dir, required_exts=[".txt"], recursive=True
    ).load_data()
    if not documents:
        return cv_text, None, None

    # Semantic chunking splits text where the *meaning* shifts, instead of at a
    # fixed number of characters. This keeps related sentences together so each
    # retrieved chunk is self-contained. It runs on CPU, hence the boot delay.
    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=embed_model,
    )
    nodes = splitter.get_nodes_from_documents(documents)

    vector_index = VectorStoreIndex(nodes)
    return cv_text, vector_index, nodes


cv_content, vector_index, all_nodes = load_resources()


# ---------------------------------------------------------------------------
# 6. HYBRID RETRIEVER + CHAT ENGINE
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_chat_engine():
    """Build a chat engine backed by hybrid (vector + keyword) retrieval."""
    if vector_index is None:
        return None

    # Vector search captures meaning ("transformer attention" ~ "self-attention").
    vector_retriever = vector_index.as_retriever(similarity_top_k=5)

    # BM25 is classic keyword search. It nails exact terms — dataset names,
    # algorithm names, equation symbols — that embeddings sometimes blur.
    bm25_retriever = BM25Retriever.from_defaults(nodes=all_nodes, similarity_top_k=5)

    # Reciprocal Rank Fusion merges both ranked lists into one, giving you the
    # best of semantic recall and keyword precision.
    retriever = QueryFusionRetriever(
        [vector_retriever, bm25_retriever],
        similarity_top_k=5,
        num_queries=1,  # do not rewrite the query; keep it deterministic
        mode=FUSION_MODES.RECIPROCAL_RANK,
        use_async=False,
    )

    # Memory lets the bot resolve follow-ups like "what is ITS accuracy?" by
    # condensing chat history into a standalone question before retrieving.
    memory = ChatMemoryBuffer.from_defaults(token_limit=4000)

    system_prompt = (
        f"You are {RESEARCHER_NAME}. Answer questions about your research based "
        f"ONLY on the provided context. If the answer is not in the context, say "
        f"you don't know rather than guessing. Here is your CV for biographical "
        f"context:\n{cv_content}"
    )

    return CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=Settings.llm,
        memory=memory,
        system_prompt=system_prompt,
        verbose=True,
    )


chat_engine = get_chat_engine()


# ---------------------------------------------------------------------------
# 7. CHAT UI
# ---------------------------------------------------------------------------
st.title(f"💬 Chat with {RESEARCHER_NAME}'s Research")
st.caption(
    "Ask about my papers, methods, and findings. Answers are grounded in my "
    "publications — if it's not in my work, I'll say so."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me anything about my research."}
    ]

# Replay the conversation so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle a new question.
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if chat_engine is None:
        st.error(
            "No research index is loaded. Add .txt files to src/data/ and restart."
        )
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_engine.chat(prompt)
                st.write(str(response))
        st.session_state.messages.append(
            {"role": "assistant", "content": str(response)}
        )
        log_interaction(prompt, response)
