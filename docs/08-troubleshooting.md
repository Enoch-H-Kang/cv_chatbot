# 08 · Troubleshooting

Organized by symptom. Most problems are one of: the Brain isn't running, the
tunnel points at the wrong place, or a config value is mistyped.

> Start here: on the GPU machine, run `./scripts/check_brain.sh`. It pinpoints
> which of the three links (local Ollama → tunnel → public internet) is broken.

---

## The chat spins "Thinking..." then errors or times out

**Meaning:** the Space (Face) is fine, but it can't reach your model (Brain).

Work through it in order:

1. **Is the Brain running?** On the GPU machine:
   ```bash
   curl http://127.0.0.1:11435
   ```
   No "Ollama is running"? → `./scripts/start_brain.sh`.

2. **Is the tunnel up and on the right port?**
   ```bash
   grep "sharing target" zrok.log | tail -n1
   ```
   It must say `11435`. If it says `11434` (the system Ollama) or `8501`
   (Streamlit), fix the reservation:
   ```bash
   killall zrok
   zrok release researchbot
   zrok reserve public http://localhost:11435 \
        --backend-mode proxy --unique-name researchbot
   ./scripts/start_brain.sh
   ```

3. **Can the internet reach it?**
   ```bash
   curl -v -H "skip_zrok_interstitial: true" https://researchbot.share.zrok.io
   ```
   See the error-code table below.

4. **Does the Space have the right URL?** Check `OLLAMA_BASE_URL` in the Space
   Variables exactly matches the tunnel URL (including `https://`, no trailing
   slash).

5. **Does `OLLAMA_MODEL` match an installed model?**
   ```bash
   OLLAMA_HOST=127.0.0.1:11435 ollama list
   ```
   The tag must match the Space variable exactly (e.g. `qwen3:8b`).

6. **Slow GPU?** A big model on modest hardware can exceed the timeout. Raise
   `REQUEST_TIMEOUT`, or switch to a smaller `OLLAMA_MODEL`.

---

## Tunnel error codes

| Code | Meaning | Fix |
| --- | --- | --- |
| **403 Forbidden** | Ollama bound to localhost only | Start with `OLLAMA_HOST=0.0.0.0:11435` (the script does this) |
| **404 Not Found** | Tunnel is down | Re-run `./scripts/start_brain.sh` |
| **502 / connection refused** | Tunnel up, Ollama down | Start Ollama (Test A) |
| **Interstitial HTML page** | zrok warning page not skipped | Ensure `TUNNEL_SKIP_HEADER=skip_zrok_interstitial` in Space vars (default) |

---

## The Space won't build

- **Read the Logs tab** — it names the failing step.
- **Dependency build failures:** usually a missing system package. The provided
  `Dockerfile` installs `build-essential`, `curl`, and `git`, which covers the
  LlamaIndex/BM25 build. Don't remove them.
- **Wrong SDK:** the Space must be a **Docker** Space. The `README.md` on HF must
  contain the metadata header (`sdk: docker`, `app_port: 8501`) from
  `src/README_SPACE.md`.
- **Port mismatch:** `app_port` in the metadata, `EXPOSE`, and the Streamlit
  `--server.port` must all be `8501`.

---

## The Space builds but shows "Index not loaded" / no answers about my papers

- **Are there `.txt` files in `src/data/`?** The reader only picks up `.txt`.
  PDFs are ignored — convert them with `scripts/pdf_to_text.py`.
- **Did you restart after uploading?** New files are only indexed on boot:
  **Settings → Restart this Space**.
- **Empty conversion?** If `pdf_to_text.py` warned that a PDF yielded almost no
  text, it's a scanned image — run OCR first (see the script's header).

---

## First load is very slow (~30–60s)

Expected. Semantic chunking + embedding runs on the Space CPU on every boot. It's
cached for the session afterward. To reduce it: fewer/smaller papers, or a
smaller `EMBED_MODEL_NAME`. This is a one-time-per-boot cost, not per question.

---

## Answers are wrong, vague, or "I don't know" too often

- **Missing content:** the bot only knows what's in `data/` and `CV.txt`. Add the
  relevant paper.
- **Retrieval too narrow:** raise `similarity_top_k` (see
  [docs/07](07-customization.md)).
- **Model too small:** a 3B model may struggle with dense technical reasoning;
  try an 8B+ model if your hardware allows.
- **Chunking too coarse/fine:** adjust `breakpoint_percentile_threshold`.

---

## Logging isn't working

- `LOG_DATASET` set to a real, **existing** dataset you own?
- `HF_TOKEN` added as a **Secret** (not a Variable) with **Write** scope?
- Remember uploads are **batched (~10 min)** — they won't appear instantly. Check
  again later or after the Space restarts.

---

## Everything worked yesterday, now it's dead

Almost always: **your local machine slept, rebooted, or logged out**, killing the
Brain. `nohup` survives a closed terminal but not those. Re-run
`./scripts/start_brain.sh`, and see
[docs/05](05-operations-runbook.md#keeping-it-running-unattended) for making it
persistent.

---

## Still stuck?

Re-run `./scripts/check_brain.sh` and read which test fails — that almost always
names the culprit. Then re-check the matching section above.
