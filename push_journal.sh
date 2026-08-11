#!/bin/bash
# Journal Bionumérique PSCVIC — auto-push toutes les 5 minutes
# Le journal se réveille avec Ugo · se repose avec Luna

JOURNAL_DIR="/Users/pscv/JOURNAL_VIVANT"
LOG="/Users/pscv/JOURNAL_VIVANT/push_log.txt"

cd "$JOURNAL_DIR"

# Générer le journal depuis les données vivantes
python3 generate_journal.py >> "$LOG" 2>&1

# Pousser vers GitHub
git add index.html journal.json
git commit -m "journal vivant · $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG" 2>&1
git push origin main >> "$LOG" 2>&1

echo "[$(date '+%H:%M:%S')] journal poussé" >> "$LOG"
