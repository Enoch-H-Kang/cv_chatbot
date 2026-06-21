# 04 · How the RAG works

This guide explains, in plain language, what happens between a visitor typing a
question and the answer appearing. You don't need this to run the bot, but it
helps when you want to tune or extend it. Everything described here lives in
[`src/streamlit_app.py`](../src/streamlit_app.py).

## The big idea: Retrieval-Augmented Generation

A language model on its own answers from its training data — it has never seen
your specific papers, and if you ask anyway it may make things up. **RAG** fixes
this by doing two things for every question:

1. **Retrieve** the most relevant passages from *your* documents.
2. **Generate** an answer that is instructed to use *only* those passages.

The result: answers grounded in your real work, with the model saying "I don't
know" when your papers don't cover something.

```
question ──> [ retrieve relevant chunks from your papers ] ──> [ LLM answers using only those chunks ] ──> answer
```

## Step 1 — Loading and chunking your papers

When the Space boots, it reads every `.txt` file in `src/data/` plus your
`CV.txt`. Long documents can't be fed to a model whole, so they're split into
**chunks**.

Naive chunking cuts every N characters, which often slices a sentence — or a
definition — in half. This project uses **semantic chunking**
(`SemanticSplitterNodeParser`): it measures where the *meaning* shifts between
sentences and splits there. Each chunk ends up being a coherent unit (a full
idea, a complete method description), which makes retrieval far more accurate.

> This runs on the Space's CPU, which is why the first load takes 30–60 seconds.
> It's cached (`@st.cache_resource`), so it only happens once per boot.

## Step 2 — Building two search indexes

Each chunk is stored so it can be searched two complementary ways:

- **Vector (semantic) search.** Every chunk is converted into an embedding — a
  list of numbers capturing its meaning — using a small model
  (`BAAI/bge-small-en-v1.5`) that runs on the Space CPU. At query time, your
  question is embedded too, and the chunks with the closest meaning are
  retrieved. This understands *synonyms and paraphrase*: a question about
  "self-attention" can match a passage about "the attention mechanism."

- **BM25 (keyword) search.** A classic algorithm that ranks chunks by exact word
  overlap. This is precise where embeddings get fuzzy: exact dataset names,
  mathematical symbols, specific algorithm names, rare jargon. If someone asks
  about "the CIFAR-10 results," BM25 finds the literal string.

## Step 3 — Hybrid retrieval (fusion)

Why choose? The `QueryFusionRetriever` runs **both** retrievers and merges their
ranked lists using **Reciprocal Rank Fusion (RRF)**. RRF rewards chunks that
rank highly in *either* list, so you get semantic recall and keyword precision at
once. In practice this is the single biggest quality win for technical Q&A,
where questions mix conceptual language with exact terminology.

The top 5 fused chunks become the context for the answer.

## Step 4 — Conversational memory

Research conversations are rarely one-shot. Someone asks about a method, then
follows up with *"what's its accuracy?"* — which is meaningless without the
previous turn.

The `CondensePlusContextChatEngine` handles this. Before retrieving, it
**condenses** the chat history plus the new question into a single standalone
query (e.g. *"what is the accuracy of [the method discussed above]?"*), retrieves
against *that*, and then answers. A `ChatMemoryBuffer` keeps the recent history
within a token budget so it never overflows.

## Step 5 — Generating the answer

The retrieved chunks, the chat history, and a **system prompt** are sent to your
local LLM through the tunnel. The system prompt sets the rules:

> *"You are [your name]. Answer based ONLY on the provided context. If the answer
> is not in the context, say you don't know. Here is your CV for biographical
> context: …"*

A low **temperature** (0.3 by default) keeps answers factual rather than
creative. The model's response streams back to the browser and is shown in the
chat.

## Putting it together

```
                        ┌─────────────── Space (CPU) ───────────────┐
 question ─────────────>│ condense w/ history → standalone query    │
                        │           │                               │
                        │   ┌───────┴────────┐                       │
                        │   ▼                ▼                       │
                        │ vector search   BM25 search               │
                        │   └───────┬────────┘                       │
                        │           ▼                               │
                        │   reciprocal rank fusion → top 5 chunks    │
                        │           │                               │
                        └───────────┼───────────────────────────────┘
                                    ▼ (chunks + history + system prompt)
                        ┌──────── tunnel ────────┐
                        ▼                        │
                  your local LLM (GPU) ──────────┘──> answer ──> browser
```

## Where to tweak

- More/fewer retrieved chunks: `similarity_top_k` in `get_chat_engine()`.
- Stricter or chattier persona: the `system_prompt` string.
- Different embedding model: `EMBED_MODEL_NAME` env var.
- Chunk sensitivity: `breakpoint_percentile_threshold` in the splitter.

See [docs/07](07-customization.md) for a tour of the safe knobs.

---

**Next:** [05 · Operations runbook](05-operations-runbook.md)
