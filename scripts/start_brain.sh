#!/usr/bin/env bash
#
# start_brain.sh — boot the local "Brain": Ollama + a zrok tunnel.
#
# Run this on the machine with the GPU (your laptop/workstation), NOT on
# Hugging Face. It starts Ollama on a custom port and exposes it through a
# reserved zrok tunnel so your Space can reach it.
#
# Prerequisites (see docs/03-local-gpu-and-tunnel.md):
#   - Ollama installed and a model pulled, e.g.  ollama pull qwen3:8b
#   - zrok installed, enabled with your account, and a reserved share created:
#       zrok reserve public http://localhost:11435 \
#            --backend-mode proxy --unique-name researchbot
#
# Usage:
#   ./scripts/start_brain.sh
#
set -euo pipefail

# ---- Configuration (edit to match your setup) ----------------------------
OLLAMA_PORT="${OLLAMA_PORT:-11435}"     # custom port avoids clashing with a system Ollama
TUNNEL_NAME="${TUNNEL_NAME:-researchbot}"
MODEL="${MODEL:-qwen3:8b}"

echo "==> Stopping any old Ollama / zrok processes..."
pkill -f "ollama serve" 2>/dev/null || true
killall zrok 2>/dev/null || true
sleep 2

echo "==> Starting Ollama on 0.0.0.0:${OLLAMA_PORT} (public bind, CORS open)..."
# 0.0.0.0 is required so the tunnel can reach it (fixes '403 Forbidden').
# OLLAMA_ORIGINS='*' allows cross-origin requests from the Space.
OLLAMA_HOST="0.0.0.0:${OLLAMA_PORT}" OLLAMA_ORIGINS="*" \
    nohup ollama serve > my_ollama.log 2>&1 &

echo "==> Waiting for Ollama to wake up..."
sleep 5

echo "==> Verifying the model '${MODEL}' is available..."
if ! OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}" ollama list | grep -q "${MODEL%%:*}"; then
    echo "    Model not found locally. Pulling it now (one-time)..."
    OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}" ollama pull "${MODEL}"
fi

echo "==> Starting zrok tunnel '${TUNNEL_NAME}'..."
nohup zrok share reserved "${TUNNEL_NAME}" --headless > zrok.log 2>&1 &
sleep 3

echo ""
echo "================== STATUS =================="
echo "Ollama log:  my_ollama.log"
echo "Tunnel log:  zrok.log"
echo ""
echo "Your public tunnel URL (paste into OLLAMA_BASE_URL):"
grep -m1 "access your zrok share" zrok.log || \
    echo "  (URL not printed yet — run: cat zrok.log)"
echo "============================================"
