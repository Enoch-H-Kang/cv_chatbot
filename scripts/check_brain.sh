#!/usr/bin/env bash
#
# check_brain.sh — verify each link in the chain when the chatbot won't answer.
#
# Run on the GPU box. Tests, in order:
#   A) Is Ollama running locally?
#   B) Is the tunnel pointing at the right port?
#   C) Can the public internet reach your GPU through the tunnel?
#
set -uo pipefail

OLLAMA_PORT="${OLLAMA_PORT:-11435}"
TUNNEL_NAME="${TUNNEL_NAME:-researchbot}"
PUBLIC_URL="${PUBLIC_URL:-https://${TUNNEL_NAME}.share.zrok.io}"

echo "===== Test A: Ollama running locally on port ${OLLAMA_PORT}? ====="
if curl -fsS "http://127.0.0.1:${OLLAMA_PORT}" | grep -qi "ollama is running"; then
    echo "  ✅ PASS — Ollama is up."
else
    echo "  ❌ FAIL — connection refused. Re-run ./scripts/start_brain.sh"
fi
echo ""

echo "===== Test B: Tunnel target port ====="
TARGET=$(grep "sharing target" zrok.log 2>/dev/null | tail -n1 || true)
echo "  ${TARGET:-'(no zrok.log found)'}"
if echo "$TARGET" | grep -q "${OLLAMA_PORT}"; then
    echo "  ✅ PASS — tunnel points at ${OLLAMA_PORT}."
else
    echo "  ⚠️  Tunnel may point at the wrong port. Expected ${OLLAMA_PORT}."
    echo "     Fix: killall zrok && zrok release ${TUNNEL_NAME} && \\"
    echo "          zrok reserve public http://localhost:${OLLAMA_PORT} \\"
    echo "          --backend-mode proxy --unique-name ${TUNNEL_NAME}"
fi
echo ""

echo "===== Test C: Public reachability via ${PUBLIC_URL} ====="
if curl -fsS -H "skip_zrok_interstitial: true" "${PUBLIC_URL}" | grep -qi "ollama is running"; then
    echo "  ✅ PASS — the outside world can reach your GPU."
else
    echo "  ❌ FAIL."
    echo "     403 Forbidden  -> you forgot OLLAMA_HOST=0.0.0.0 when starting Ollama."
    echo "     404 Not Found  -> the tunnel is down; re-run ./scripts/start_brain.sh."
fi
