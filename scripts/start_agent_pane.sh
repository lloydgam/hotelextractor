#!/usr/bin/env bash
# Usage: start_agent_pane.sh <agent_name> <log_file>
AGENT="$1"
LOG_FILE="$2"

clear

case "$AGENT" in
  searcher)
    COLOR="\033[1;96m"    # bright cyan
    LABEL=" SEARCHER  AGENT"
    ;;
  extractor)
    COLOR="\033[1;93m"    # bright yellow
    LABEL=" EXTRACTOR AGENT"
    ;;
  processor)
    COLOR="\033[1;92m"    # bright green
    LABEL=" PROCESSOR AGENT"
    ;;
  exporter)
    COLOR="\033[1;95m"    # bright magenta
    LABEL=" EXPORTER  AGENT"
    ;;
  *)
    COLOR="\033[1;37m"
    LABEL=" ${AGENT^^} AGENT"
    ;;
esac

RESET="\033[0m"
BAR="═══════════════════════════════"

printf "${COLOR}"
printf "\n  ${BAR}\n"
printf "  ${LABEL}\n"
printf "  ${BAR}\n"
printf "${RESET}\n\n"

# Wait for log file to exist then follow it
while [ ! -f "$LOG_FILE" ]; do sleep 0.05; done
tail -f "$LOG_FILE"
