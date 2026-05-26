#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  HotelAIExtractor — tmux Live Demo Launcher
#
#  Usage:
#    bash scripts/run_demo.sh
#    bash scripts/run_demo.sh Singapore 2026-06-01 2026-06-04 150 7.5 rating
#    bash scripts/run_demo.sh Bangkok   2026-06-01 2026-06-04 150 7.5 rating
#
#  Layout:
#  ┌────────────────────────────────────────────────────────────────────────┐
#  │  pane 0  ·  ORCHESTRATOR  (top 40%)                                    │
#  ├──────────────┬───────────────┬───────────────┬──────────────────────────┤
#  │  pane 1      │  pane 2       │  pane 3       │  pane 4                  │
#  │  SEARCHER    │  EXTRACTOR    │  PROCESSOR    │  EXPORTER                │
#  └──────────────┴───────────────┴───────────────┴──────────────────────────┘
# ─────────────────────────────────────────────────────────────────────────────
set -e

command -v tmux >/dev/null 2>&1 || { echo "tmux not found — run: brew install tmux"; exit 1; }

SESSION="hotel-demo"
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOGS="$BASE_DIR/data/logs"
SCRIPTS="$BASE_DIR/scripts"

DESTINATION="${1:-Singapore}"
CHECKIN="${2:-2026-06-01}"
CHECKOUT="${3:-2026-06-04}"
MAX_PRICE="${4:-150}"
MIN_RATING="${5:-7.5}"
SORT_BY="${6:-rating}"

echo ""
echo "  HotelAIExtractor — tmux Demo"
echo "  Destination : $DESTINATION"
echo "  Check-in    : $CHECKIN"
echo "  Check-out   : $CHECKOUT"
echo "  Max price   : \$$MAX_PRICE/night"
echo "  Min rating  : $MIN_RATING"
echo "  Sort by     : $SORT_BY"
echo ""

# ── Reset ──────────────────────────────────────────────────────────────────────
tmux kill-session -t "$SESSION" 2>/dev/null || true
mkdir -p "$LOGS"
: > "$LOGS/searcher.log"
: > "$LOGS/extractor.log"
: > "$LOGS/processor.log"
: > "$LOGS/exporter.log"
chmod +x "$SCRIPTS/start_agent_pane.sh"

# ── Create session ─────────────────────────────────────────────────────────────
tmux new-session -d -s "$SESSION" -x 220 -y 55

# ── Split: top 40% = orchestrator, bottom 60% = 4 agent panes ─────────────────
tmux split-window -t "$SESSION:0.0" -v -p 60         # pane 0 (top) / pane 1 (bottom)
tmux split-window -t "$SESSION:0.1" -h -p 75         # pane 2 (right 75% of bottom)
tmux split-window -t "$SESSION:0.2" -h -p 67         # pane 3 (right 67%)
tmux split-window -t "$SESSION:0.3" -h -p 50         # pane 4 (right 50%)

# ── Agent panes — each shows header then tails its log ────────────────────────
tmux send-keys -t "$SESSION:0.1" \
  "bash '$SCRIPTS/start_agent_pane.sh' searcher  '$LOGS/searcher.log'"  Enter
tmux send-keys -t "$SESSION:0.2" \
  "bash '$SCRIPTS/start_agent_pane.sh' extractor '$LOGS/extractor.log'" Enter
tmux send-keys -t "$SESSION:0.3" \
  "bash '$SCRIPTS/start_agent_pane.sh' processor '$LOGS/processor.log'" Enter
tmux send-keys -t "$SESSION:0.4" \
  "bash '$SCRIPTS/start_agent_pane.sh' exporter  '$LOGS/exporter.log'"  Enter

# Give agent panes a moment to render headers
sleep 1

# ── Orchestrator — top pane runs the pipeline ─────────────────────────────────
tmux send-keys -t "$SESSION:0.0" \
  "cd '$BASE_DIR' && python3 scripts/pipeline.py --tmux \
   --destination '$DESTINATION' \
   --checkin '$CHECKIN' \
   --checkout '$CHECKOUT' \
   --max-price '$MAX_PRICE' \
   --min-rating '$MIN_RATING' \
   --sort-by '$SORT_BY'" Enter

# ── Attach ────────────────────────────────────────────────────────────────────
tmux attach-session -t "$SESSION"
