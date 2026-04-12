#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# CASA LOS — Cloudflare Tunnel Deployment
# Landing page at /  ·  Streamlit app at /app
# Free public https://*.trycloudflare.com — no account needed.
# ─────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

VENV="$(pwd)/.venv"
BACKEND_PORT=8000
STREAMLIT_PORT=8501
GATEWAY_PORT=8080
CF_LOG=/tmp/casa_cf.log

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; RESET='\033[0m'

echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════╗"
echo -e "║     CASA LOS — Cloudflare Deployment     ║"
echo -e "╚══════════════════════════════════════════╝${RESET}\n"

# ── 1. Install cloudflared if missing ─────────────────────────
if ! command -v cloudflared &>/dev/null; then
  echo -e "${YELLOW}▸ cloudflared not found — installing...${RESET}"
  if command -v brew &>/dev/null; then
    brew install cloudflared
  else
    ARCH=$(uname -m)
    [ "$ARCH" = "arm64" ] \
      && CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz" \
      || CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
    TMP=$(mktemp -d)
    curl -sL "$CF_URL" | tar -xz -C "$TMP"
    sudo mv "$TMP/cloudflared" /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
  fi
  echo -e "${GREEN}✓ cloudflared installed${RESET}"
fi
echo -e "${GREEN}✓ cloudflared $(cloudflared --version 2>&1 | head -1)${RESET}"

# ── 2. Free ports ─────────────────────────────────────────────
for PORT in $BACKEND_PORT $STREAMLIT_PORT $GATEWAY_PORT; do
  PID=$(lsof -ti tcp:$PORT 2>/dev/null || true)
  if [ -n "$PID" ]; then
    echo -e "${YELLOW}▸ Freeing port $PORT${RESET}"
    kill -9 $PID 2>/dev/null || true
    sleep 0.5
  fi
done

# ── 3. Activate venv ──────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo -e "${RED}✗ Virtual environment not found. Run:${RESET}"
  echo "  python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi
source "$VENV/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${RESET}"

# ── 4. Cleanup trap ───────────────────────────────────────────
cleanup() {
  echo -e "\n${YELLOW}▸ Shutting down...${RESET}"
  [ -n "${BACKEND_PID:-}"  ] && kill $BACKEND_PID  2>/dev/null || true
  [ -n "${STREAM_PID:-}"   ] && kill $STREAM_PID   2>/dev/null || true
  [ -n "${GATEWAY_PID:-}"  ] && kill $GATEWAY_PID  2>/dev/null || true
  [ -n "${CF_PID:-}"       ] && kill $CF_PID       2>/dev/null || true
  echo -e "${GREEN}✓ Done${RESET}"
}
trap cleanup EXIT INT TERM

# ── 5. FastAPI backend ────────────────────────────────────────
echo -e "${CYAN}▸ Starting API backend on port $BACKEND_PORT...${RESET}"
python -m uvicorn backend.main:app --port $BACKEND_PORT \
  --log-level warning > /tmp/casa_backend.log 2>&1 &
BACKEND_PID=$!

for i in {1..15}; do
  curl -sf http://localhost:$BACKEND_PORT/health &>/dev/null && \
    { echo -e "${GREEN}✓ Backend ready${RESET}"; break; }
  sleep 1
done

# ── 6. Streamlit (internal only — gateway exposes it at /app) ─
echo -e "${CYAN}▸ Starting Streamlit on port $STREAMLIT_PORT (internal)...${RESET}"
python -m streamlit run frontend/app.py \
  --server.port $STREAMLIT_PORT \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --server.baseUrlPath /app \
  > /tmp/casa_streamlit.log 2>&1 &
STREAM_PID=$!

for i in {1..20}; do
  curl -sf http://localhost:$STREAMLIT_PORT &>/dev/null && \
    { echo -e "${GREEN}✓ Streamlit ready${RESET}"; break; }
  sleep 1
done

# ── 7. Gateway (landing + /app proxy) ────────────────────────
echo -e "${CYAN}▸ Starting gateway on port $GATEWAY_PORT...${RESET}"
STREAMLIT_PORT=$STREAMLIT_PORT GATEWAY_PORT=$GATEWAY_PORT \
  python gateway.py > /tmp/casa_gateway.log 2>&1 &
GATEWAY_PID=$!
sleep 2
echo -e "${GREEN}✓ Gateway ready${RESET}"
echo -e "  Landing page : ${CYAN}http://localhost:$GATEWAY_PORT/${RESET}"
echo -e "  App          : ${CYAN}http://localhost:$GATEWAY_PORT/app${RESET}"

# ── 8. Cloudflare Tunnel → gateway ───────────────────────────
echo ""
echo -e "${BOLD}${CYAN}▸ Opening Cloudflare Tunnel...${RESET}"
cloudflared tunnel --url http://localhost:$GATEWAY_PORT \
  --no-autoupdate > "$CF_LOG" 2>&1 &
CF_PID=$!

URL=""
for i in {1..30}; do
  URL=$(grep -o 'https://[^ ]*trycloudflare\.com' "$CF_LOG" 2>/dev/null | head -1 || true)
  [ -n "$URL" ] && break
  sleep 1
done

if [ -n "$URL" ]; then
  echo ""
  echo -e "${BOLD}${GREEN}  🚀  CASA LOS is live${RESET}"
  echo -e "${GREEN}  ─────────────────────────────────────────${RESET}"
  echo -e "  Landing : ${BOLD}${CYAN}${URL}/${RESET}"
  echo -e "  App     : ${BOLD}${CYAN}${URL}/app${RESET}"
  echo -e "${GREEN}  ─────────────────────────────────────────${RESET}"
  echo -e "${YELLOW}  Valid until Ctrl+C${RESET}"
  echo ""
else
  echo -e "${RED}✗ Tunnel URL not found. Check $CF_LOG${RESET}"
fi

echo -e "${YELLOW}Press Ctrl+C to stop all services.${RESET}\n"
wait $CF_PID
