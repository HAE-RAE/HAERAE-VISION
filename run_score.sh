#!/usr/bin/env bash
# batch_score_missing.sh
# Scan outputs/*.csv; if scores/<same name>.csv is missing, run judge_csv.py and write there.

# set -euo pipefail
export OPENAI_API_KEY=

export GEMINI_API_KEY=
# Defaults (override via flags below)
OUTPUTS_DIR="outputs"
SCORES_DIR="scores"
JUDGE_SCRIPT="score.py"
PYTHON_BIN="${PYTHON_BIN:-python}"
PATTERN="*.csv"
MODEL="gpt-5-mini"
DRY_RUN=0
JUDGE_ARGS=()  # extra args passed to judge script

usage() {
  cat <<EOF
Usage: $0 [options] [-- extra-judge-args]

Options:
  --outputs-dir DIR     Directory to read raw outputs (default: outputs)
  --scores-dir DIR      Directory to write scored CSVs (default: scores)
  --judge-script PATH   Path to judge_csv.py (default: judge_csv.py)
  --python-bin PATH     Python interpreter (default: \$PYTHON_BIN or 'python')
  --pattern GLOB        File pattern in outputs-dir (default: *.csv)
  --model NAME          Judge model to pass (default: gpt-5-mini)
  --dry-run             Show what would run, don't execute
  -h, --help            Show this help

Anything after '--' is passed through to the judge script, e.g.:
  $0 -- --response-col-name response --score-col-name scores
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --outputs-dir) OUTPUTS_DIR="$2"; shift 2 ;;
    --scores-dir)  SCORES_DIR="$2";  shift 2 ;;
    --judge-script) JUDGE_SCRIPT="$2"; shift 2 ;;
    --python-bin)  PYTHON_BIN="$2";  shift 2 ;;
    --pattern)     PATTERN="$2";     shift 2 ;;
    --model|-m)    MODEL="$2";       shift 2 ;;
    --dry-run)     DRY_RUN=1;        shift ;;
    -h|--help)     usage; exit 0 ;;
    --)            shift; JUDGE_ARGS+=("$@"); break ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

mkdir -p "$SCORES_DIR"

# Collect files safely (null-delimited)
mapfile -d '' FILES < <(find "$OUTPUTS_DIR" -maxdepth 1 -type f -name "$PATTERN" -print0)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files matching '$PATTERN' in '$OUTPUTS_DIR'. Nothing to do."
  exit 0
fi

for SRC in "${FILES[@]}"; do
  BASE="$(basename "$SRC")"
  DST="$SCORES_DIR/$BASE"

  if [[ -e "$DST" ]]; then
    echo "✓ Already scored, skipping: $BASE"
    continue
  fi

  echo "→ Scoring: $BASE"
  CMD=( "$PYTHON_BIN" "$JUDGE_SCRIPT"
        --input "$SRC"
        --output "$DST"
        --model "$MODEL" )

  if [[ ${#JUDGE_ARGS[@]} -gt 0 ]]; then
    CMD+=( "${JUDGE_ARGS[@]}" )
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '+ %q ' "${CMD[@]}"; echo
  else
    "${CMD[@]}"
  fi
done

echo "Done."
