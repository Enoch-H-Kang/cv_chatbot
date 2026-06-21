# 📚 Documentation

Step-by-step guides for building your personalized research chatbot. Read them in
order the first time; afterward, jump straight to the one you need.

| # | Guide | What it covers |
| --- | --- | --- |
| 01 | [Prerequisites](01-prerequisites.md) | Accounts, hardware, and software you need |
| 02 | [Deploy the Space](02-deploy-the-space.md) | Putting the chat page online (and running it locally first) |
| 03 | [Local GPU and tunnel](03-local-gpu-and-tunnel.md) | Running the model on your machine and exposing it securely |
| 04 | [How the RAG works](04-how-the-rag-works.md) | Plain-language tour of retrieval + generation |
| 05 | [Operations runbook](05-operations-runbook.md) | Starting, stopping, updating, restarting after reboot |
| 06 | [Logging and analytics](06-logging-and-analytics.md) | Optionally recording questions to a private dataset |
| 07 | [Customization](07-customization.md) | Models, persona, retrieval tuning, UI tweaks |
| 08 | [Troubleshooting](08-troubleshooting.md) | Fixes organized by symptom |

## The 4 components, mapped to the guides

- **The Face** (public chat page) → guide 02
- **The Brain** (your local model) → guide 03
- **The Knowledge** (your papers/CV) → guides 02 (adding) + 04 (how it's used)
- **The Glue** (retrieval pipeline) → guide 04

## Fastest path to a working bot

1. [01 Prerequisites](01-prerequisites.md) — make sure you're set up.
2. [03 Local GPU and tunnel](03-local-gpu-and-tunnel.md) — get the Brain running,
   copy the tunnel URL.
3. [02 Deploy the Space](02-deploy-the-space.md) — get the Face online, paste the
   URL.
4. Chat. If it doesn't answer → [08 Troubleshooting](08-troubleshooting.md).

Everything else (logging, customization) is optional polish.
