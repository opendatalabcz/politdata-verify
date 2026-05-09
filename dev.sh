#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${BLUE}[dev]${NC} $1"; }
ok()   { echo -e "${GREEN}[ok]${NC}  $1"; }
warn() { echo -e "${YELLOW}[!]${NC}   $1"; }

PIDS=()
cleanup() {
  echo ""
  log "Zastavuji backend a frontend..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  ok "Hotovo. Milvus stále běží (docker compose stop standalone zastaví)."
  exit 0
}
trap cleanup SIGINT SIGTERM

log "Spouštím Milvus stack (etcd, minio, standalone)..."
cd "$ROOT"
docker compose up -d etcd minio standalone 2>/dev/null
ok "Milvus stack běží."

if [ ! -f "$ROOT/venv/bin/activate" ]; then
  warn "Venv nenalezen na $ROOT/venv — spouštím uvicorn ze systémového Pythonu."
else
  source "$ROOT/venv/bin/activate"
  ok "Venv aktivován."
fi

log "Spouštím backend na http://localhost:8000 ..."
cd "$ROOT"
MILVUS_URI="http://localhost:19530" uvicorn app.src.api.server:app --reload --reload-dir app --port 8000 &
BACKEND_PID=$!
PIDS+=($BACKEND_PID)
ok "Backend PID=$BACKEND_PID"

if [ ! -d "$ROOT/fe/node_modules" ]; then
  log "node_modules nenalezeny — spouštím npm install..."
  cd "$ROOT/fe" && npm install
fi

log "Spouštím frontend na http://localhost:5173 ..."
cd "$ROOT/fe"
npm run dev &
FRONTEND_PID=$!
PIDS+=($FRONTEND_PID)
ok "Frontend PID=$FRONTEND_PID"

echo ""
echo -e "  ${GREEN}Backend:${NC}   http://localhost:8000"
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:5173"
echo -e "  ${GREEN}API docs:${NC}  http://localhost:8000/docs"
echo ""
echo -e "  Ctrl+C zastaví backend a frontend (Milvus zůstane)."
echo ""

# Ctrl+C
wait
