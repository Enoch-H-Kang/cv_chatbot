# 03 · Set up the local GPU and tunnel (the "Brain")

This is where the language model actually runs. You'll install Ollama, pull a
model, and expose it to your Space through a secure tunnel. Do all of this on the
machine with the GPU.

---

## Part 1 — Install Ollama and pull a model

1. **Install Ollama:** download from <https://ollama.com/download> and follow the
   installer for your OS. Verify it works:
   ```bash
   ollama --version
   ```

2. **Pull a model.** An 8B model is a good balance of quality and speed:
   ```bash
   ollama pull qwen3:8b
   ```
   Other good choices: `llama3.1:8b`, `mistral:7b`. On a weak machine, try
   `qwen2.5:3b` or `phi3:mini`. Whatever you pick, use that exact tag for
   `OLLAMA_MODEL` in your Space.

3. **Quick local test:**
   ```bash
   ollama run qwen3:8b "Say hello in one sentence."
   ```

### A note on ports

If Ollama is already installed as a system service, it listens on the default
port **11434**. To avoid surprises, this tutorial runs *your* chatbot's Ollama on
a **custom port, 11435**, so it never collides with the system one. The
`start_brain.sh` script does this for you.

---

## Part 2 — Install and enable zrok

zrok creates a stable public URL that forwards to your local Ollama, without
opening your whole machine to the internet.

1. **Install zrok:** follow
   <https://docs.zrok.io/docs/getting-started/>. Verify:
   ```bash
   zrok version
   ```

2. **Enable your environment** with the token from your zrok account dashboard:
   ```bash
   zrok enable <your-account-token>
   ```

3. **Create a *reserved* share.** "Reserved" means the URL stays the same every
   time you restart — so you only set `OLLAMA_BASE_URL` once. Point it at your
   custom Ollama port and give it a memorable name:
   ```bash
   zrok reserve public http://localhost:11435 \
        --backend-mode proxy \
        --unique-name researchbot
   ```
   This prints a permanent URL like `https://researchbot.share.zrok.io`. **That
   is your `OLLAMA_BASE_URL`** — paste it into your Space's variables
   ([docs/02](02-deploy-the-space.md), Step 3).

> You only run the `reserve` command **once**. After that, `start_brain.sh` just
> *shares* the already-reserved tunnel.

---

## Part 3 — Boot everything with one command

From the repo root on your GPU machine:

```bash
chmod +x scripts/start_brain.sh    # first time only
./scripts/start_brain.sh
```

This script (read it — it's short and commented):

1. Kills any stale Ollama/zrok processes.
2. Starts Ollama on `0.0.0.0:11435` with CORS open.
3. Confirms your model is present (pulls it if not).
4. Starts the reserved zrok tunnel.
5. Prints the public URL and the log file locations.

### Why `0.0.0.0` and `OLLAMA_ORIGINS="*"`?

- **`0.0.0.0`** binds Ollama to all network interfaces so the tunnel can reach
  it. Binding only to `127.0.0.1` causes a **403 Forbidden** through the tunnel.
- **`OLLAMA_ORIGINS="*"`** allows requests that originate from your Space's
  domain (cross-origin), rather than only from localhost.

Both are set automatically by the script. They expose only the Ollama API
through the named tunnel — not your filesystem or other services.

---

## Part 4 — Verify the whole chain

```bash
chmod +x scripts/check_brain.sh    # first time only
./scripts/check_brain.sh
```

It runs three tests and tells you exactly which link is broken:

- **Test A** — Ollama answering locally on port 11435?
- **Test B** — tunnel pointing at the right port?
- **Test C** — the public URL reachable from the internet?

A full pass means your Space can now talk to your GPU. Open your Space and chat.

---

## Using a different tunnel (Cloudflare / ngrok)

zrok isn't mandatory. Any tool that gives Ollama a public HTTPS URL works:

- **Cloudflare Tunnel:** `cloudflared tunnel --url http://localhost:11435`
- **ngrok:** `ngrok http 11435`

If you switch, set `TUNNEL_SKIP_HEADER=""` in your Space variables (the skip
header is zrok-specific) and use the URL your chosen tool prints as
`OLLAMA_BASE_URL`. Note that free ngrok URLs change on every restart, which is
why a *reserved* zrok share is convenient.

---

## Security notes

- The tunnel exposes **only the Ollama API**, not your computer.
- Anyone who learns the tunnel URL can send prompts to your model (and use your
  GPU cycles). Treat the URL as semi-secret. zrok also supports **private
  shares** with access tokens if you want to lock it down further — see the zrok
  docs on private sharing.
- Your papers and CV live on the Space; your *model* and anything else on your
  machine stay local.

---

**Next:** [04 · How the RAG works](04-how-the-rag-works.md)
