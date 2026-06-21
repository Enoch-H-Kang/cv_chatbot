# 05 · Operations runbook

Day-to-day operation of the running chatbot. Keep this handy — it's the page
you'll return to after a reboot or when something stops working.

> **The golden rule:** the chatbot answers only while your local machine is on
> **and** `start_brain.sh` is running. The Hugging Face Space stays up on its
> own, but with no Brain it can only time out.

---

## Starting everything (e.g. after a reboot)

On your GPU machine, from the repo root:

```bash
./scripts/start_brain.sh
```

Then confirm:

```bash
./scripts/check_brain.sh
```

If all three tests pass, open your Space and it's live.

### The raw commands (what the script does)

If you ever need to run it by hand:

```bash
# 1. Clear old processes
pkill -f "ollama serve" ; killall zrok

# 2. Start Ollama on the custom port, publicly bound
OLLAMA_HOST=0.0.0.0:11435 OLLAMA_ORIGINS="*" \
    nohup ollama serve > my_ollama.log 2>&1 &

sleep 5

# 3. Start the reserved tunnel
nohup zrok share reserved researchbot --headless > zrok.log 2>&1 &

# 4. Get the public URL
grep "access your zrok share" zrok.log
```

---

## Checking status

| Question | Command |
| --- | --- |
| Is Ollama up locally? | `curl http://127.0.0.1:11435` → "Ollama is running" |
| What's the tunnel doing? | `cat zrok.log` |
| What port is the tunnel on? | `grep "sharing target" zrok.log | tail -n1` |
| Can the world reach it? | `curl -H "skip_zrok_interstitial: true" https://researchbot.share.zrok.io` |
| What models are installed? | `OLLAMA_HOST=127.0.0.1:11435 ollama list` |

Or just run `./scripts/check_brain.sh` which bundles these.

---

## Stopping everything

```bash
pkill -f "ollama serve"
killall zrok
```

The Space will then show "thinking" and time out for visitors — stop the Brain
only when you intend the bot to be offline.

---

## Updating your research content

Your papers and CV live on the **Space**, not the local machine.

1. Open your Space → **Files** tab.
2. **Update your CV:** click `src/CV.txt` → **Edit** → paste new text → **Commit**.
3. **Add a paper:** **Add file → Upload** a new `.txt` into `src/data/`.
   (Convert PDFs first with `scripts/pdf_to_text.py`.)
4. **Restart to reindex:** **Settings → Restart this Space**. On reboot it
   re-chunks and re-embeds everything, so new papers become searchable.

> If you keep the project in Git, edit locally and `git push` instead — same
> effect, with version history.

---

## Changing the model

On the GPU machine:

```bash
# See what you have
OLLAMA_HOST=127.0.0.1:11435 ollama list

# Pull a different model
OLLAMA_HOST=127.0.0.1:11435 ollama pull llama3.1:8b
```

Then update `OLLAMA_MODEL` in your Space's **Variables** to match the new tag and
restart the Space. (The model name must match exactly, or requests will fail.)

---

## Keeping it running unattended

`nohup ... &` survives you closing the terminal, but **not** a logout, sleep, or
reboot. For something more permanent:

- **Linux:** wrap the commands in a `systemd` service or a `tmux`/`screen`
  session.
- **macOS:** disable sleep (`caffeinate`), or use a `launchd` agent.
- **Always-on box:** a spare desktop or mini-PC that you never close is the
  simplest reliable host.

Whatever you choose, the chatbot is only as available as the machine running the
Brain.

---

**Next:** [06 · Logging and analytics](06-logging-and-analytics.md)
