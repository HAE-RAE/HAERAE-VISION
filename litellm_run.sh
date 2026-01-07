#!/usr/bin/env bash
# set -euo pipefail

# -------- Config --------
ENGINE="litellm"
MAX_TOKENS=4096
TEMPERATURE=1.0
# TOP_P=0.95
RUNS=1   # how many times to run each model

export OPENAI_API_KEY=

export GEMINI_API_KEY=

export OPENROUTER_API_KEY=

# Add or remove model IDs here
MODELS=(
    # "gpt-5"
    # "gpt-5-mini"
    # "gpt-5-nano"
    # "gemini/gemini-2.5-pro"
    # "gemini/gemini-2.5-flash"
    # "gemini/gemini-2.5-flash-lite"
    
    # "openrouter/x-ai/grok-4"
    
    # "openrouter/perplexity/sonar-pro"
    
    # "openrouter/mistralai/pixtral-large-2411"
    # "openrouter/mistralai/mistral-medium-3.1"
    # "openrouter/mistralai/pixtral-12b"
    # "openrouter/mistralai/mistral-small-3.2-24b-instruct"
    
    # "openrouter/z-ai/glm-4.5v"
    
    # "openrouter/baidu/ernie-4.5-vl-424b-a47b"
    # "openrouter/baidu/ernie-4.5-vl-28b-a3b"

    # "openrouter/meta-llama/llama-3.2-90b-vision-instruct"
    # "openrouter/meta-llama/llama-4-maverick"
    # "openrouter/meta-llama/llama-4-scout"
    # "openrouter/qwen/qwen2.5-vl-72b-instruct:online"
    "openrouter/perplexity/sonar-deep-research"
)

OUT_DIR="./outputs"
mkdir -p "$OUT_DIR"

# Convert model id to a filename-safe slug
slugify() {
  local s="$1"
  s="${s//\//_}"
  s="${s// /_}"
  s="${s//:/_}"
  printf '%s' "$(echo "$s" | sed 's/[^A-Za-z0-9._-]/_/g')"
}

for MODEL in "${MODELS[@]}"; do
  SLUG="$(slugify "$MODEL")"
  for i in $(seq 1 "$RUNS"); do
    OUT_FILE="${OUT_DIR}/${ENGINE}_${SLUG}_${i}.csv"
    echo ">>> Running ${MODEL} [${i}/${RUNS}] -> ${OUT_FILE}"

    python main.py \
      --engine "${ENGINE}" \
      --model "${MODEL}" \
      --output "${OUT_FILE}" \
      --max_tokens "${MAX_TOKENS}" \
      --temperature "${TEMPERATURE}"
  done
done

echo "All runs complete. Outputs in: ${OUT_DIR}"
