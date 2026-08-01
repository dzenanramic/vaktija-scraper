#!/bin/bash
# ============================================
# Cron setup za vaktija sync
#
# Dodaj u crontab:
#   0 0 * * * /home/dzenan/vaktija-scraper/scripts/cron-sync.sh >> /home/dzenan/vaktija-scraper/logs/cron.log 2>&1
#
# Za setup:
#   chmod +x scripts/cron-sync.sh
#   crontab -e
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

# Load env vars (POSIX-compatible, works with dash and bash)
if [ -f "$PROJECT_DIR/.env" ]; then
    while IFS= read -r line; do
        case "$line" in
            \#*|"") continue ;;
            *=*) export "$line" ;;
        esac
    done < "$PROJECT_DIR/.env"
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') Starting vaktija sync ==="

"$VENV_PYTHON" "$SCRIPT_DIR/sync-to-supabase.py" "$@"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') Done ==="
