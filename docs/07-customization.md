# 07 · Customization

Once the basics work, here's how to make the chatbot your own. Most changes are
just environment variables; a few involve editing
[`src/streamlit_app.py`](../src/streamlit_app.py).

---

## Quick wins (environment variables only)

Set these in your Space → **Settings → Variables**. No code change, just restart.

| Variable | Default | Effect |
| --- | --- | --- |
| `RESEARCHER_NAME` | `Your Name` | Title and the persona the bot adopts |
| `OLLAMA_MODEL` | `qwen3:8b` | Which local model writes answers |
| `LLM_TEMPERATURE` | `0.3` | Lower = more factual; higher = more creative |
| `CONTEXT_WINDOW` | `8192` | Tokens the model considers per request |
| `EMBED_MODEL_NAME` | `BAAI/bge-small-en-v1.5` | Embedding model (keep it small for CPU) |
| `REQUEST_TIMEOUT` | `120.0` | Seconds before giving up on the GPU |

### Choosing a model

- **Faster, lighter:** `qwen2.5:3b`, `phi3:mini` — good for weak GPUs/CPU.
- **Balanced:** `qwen3:8b`, `llama3.1:8b`, `mistral:7b`.
- **Higher quality (needs more VRAM):** `qwen2.5:14b`, `llama3.1:70b`.

Pull the model on your GPU machine first
(`OLLAMA_HOST=127.0.0.1:11435 ollama pull <model>`), then set `OLLAMA_MODEL`.

### Choosing an embedding model

`bge-small-en-v1.5` is fast and runs comfortably on the Space CPU. For better
retrieval on dense technical text, `BAAI/bge-base-en-v1.5` is more accurate but
slower to load. Larger models will make the 30–60s boot longer.

---

## Editing the persona / behavior

The bot's instructions live in the `system_prompt` inside `get_chat_engine()`.
The default is strict ("answer ONLY from context, else say you don't know"),
which is right for research credibility. You might:

- **Add tone guidance:** *"Explain at the level of a first-year graduate
  student."*
- **Add formatting rules:** *"When citing a result, mention which paper it comes
  from."*
- **Loosen grounding** (use with care): allow general background knowledge in
  addition to the papers. This raises the risk of confident-but-wrong answers,
  so most researchers keep it strict.

Keep the line that injects the CV (`{cv_content}`) so biographical questions
still work.

---

## Tuning retrieval quality

In `get_chat_engine()`:

- **`similarity_top_k`** (default 5 in each retriever and the fusion): how many
  chunks feed the answer. More context can help thoroughness but costs tokens and
  can dilute focus. Try 3–8.

In `load_resources()`:

- **`breakpoint_percentile_threshold`** (default 95): how aggressively semantic
  chunking splits. Lower → more, smaller chunks; higher → fewer, larger chunks.

If answers miss obviously relevant passages, raising `top_k` is the first thing
to try. If answers feel unfocused or slow, lower it.

---

## Changing the look of the chat page

The UI is plain Streamlit, easy to extend in `# 7. CHAT UI`:

- **Sidebar with your links:** add `st.sidebar.markdown(...)` with your homepage,
  Google Scholar, etc.
- **Suggested questions:** render a few `st.button(...)`s that prefill common
  queries.
- **A disclaimer:** note that answers are AI-generated and grounded in your
  papers (and that you may log conversations, if you enabled logging).
- **Theme:** add a `.streamlit/config.toml` with `[theme]` colors, or set them in
  the Space.

---

## Supporting more file types

The reader is restricted to `.txt` (`required_exts=[".txt"]`). LlamaIndex's
`SimpleDirectoryReader` can also parse PDFs and more if you install the readers,
but plain text gives you the cleanest, most predictable chunking — which is why
this tutorial standardizes on converting to `.txt` up front via
`scripts/pdf_to_text.py`. Stick with `.txt` unless you have a reason not to.

---

## Going beyond one person

The same architecture works for a **lab** or a **course**: put everyone's papers
(or all the lecture notes) in `data/`, adjust the persona prompt to represent the
group, and you have a shared research assistant. The retrieval layer doesn't care
whose documents they are.

---

**Next:** [08 · Troubleshooting](08-troubleshooting.md)
