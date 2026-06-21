# 06 · Logging and analytics (optional)

Want to see what people ask your chatbot? You can log every question and answer
to a **private Hugging Face Dataset**, then review or analyze it later. This is
entirely optional — leave `LOG_DATASET` empty and the app skips it.

This is useful for spotting questions your papers *don't* answer well (a cue to
add more material) and for understanding what visitors care about.

---

## How it works

The app uses a `CommitScheduler` from `huggingface_hub`. Each Q&A pair is written
to a local `.jsonl` file and the scheduler **batches uploads** to your dataset
every ~10 minutes (and once on shutdown), so logging never slows down the chat.

Each log line looks like:

```json
{"timestamp": "2025-06-21T10:30:00", "session_id": "a1b2...", "question": "What is your main result?", "answer": "..."}
```

The `session_id` groups messages from the same browser session, so you can
reconstruct whole conversations.

---

## Setup

### Step 1 — Create a private dataset

1. Go to <https://huggingface.co/new-dataset>.
2. Name it, e.g. `yourname/researchbot-logs`.
3. Set visibility to **Private** (important — it will hold visitor questions).
4. Create it.

### Step 2 — Create a write token

1. Go to <https://huggingface.co/settings/tokens>.
2. **New token** → type **Write** → name it `researchbot-logging`.
3. Copy the token (you won't see it again).

### Step 3 — Add the token and dataset to your Space

In your Space → **Settings → Variables and secrets**:

- Add a **Secret** named `HF_TOKEN` with the write token as its value.
- Add a **Variable** named `LOG_DATASET` set to `yourname/researchbot-logs`.

Restart the Space. From now on, interactions accumulate in the dataset.

> The app reads `HF_TOKEN` automatically via `huggingface_hub`; you don't need to
> reference it in code. Keep it a **Secret**, never a Variable, and never commit
> it.

---

## Reviewing the logs

- **In the browser:** open your dataset on Hugging Face and use the Dataset
  Viewer, or browse the files under `data/`.
- **In Python:**
  ```python
  from huggingface_hub import hf_hub_download
  import json

  path = hf_hub_download(
      repo_id="yourname/researchbot-logs",
      filename="data/qna_logs.jsonl",
      repo_type="dataset",
      token="hf_...",  # your read/write token
  )
  with open(path) as f:
      rows = [json.loads(line) for line in f]

  print(f"{len(rows)} interactions logged")
  for r in rows[-5:]:
      print(r["question"])
  ```

From there it's ordinary data analysis — count common questions, find ones where
the bot said "I don't know," and decide which papers or CV sections to expand.

---

## Privacy & ethics

- Visitor questions may contain personal or sensitive text. Keep the dataset
  **private**, and tell users on the chat page if you log conversations.
- Don't log more than you need. The default schema is intentionally minimal
  (timestamp, session id, question, answer) — no IP addresses or identifiers.
- Follow your institution's guidance and any applicable privacy law for the
  jurisdictions your visitors come from.

---

**Next:** [07 · Customization](07-customization.md)
