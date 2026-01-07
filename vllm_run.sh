#!/usr/bin/env bash
# set -euo pipefail

# -------- Config --------
ENGINE="vllm"
MAX_TOKENS=4096
TEMPERATURE=0.6
TOP_P=0.95
RUNS=3   # how many times to run each model

# Add or remove model IDs here
MODELS=(
  # "Qwen/Qwen2.5-VL-3B-Instruct"
  # "Qwen/Qwen2.5-VL-7B-Instruct"
  # "Qwen/Qwen2.5-VL-72B-Instruct" # memory issue on H100x2
  # "OpenGVLab/InternVL3-1B"
  # "OpenGVLab/InternVL3-2B"
  # "OpenGVLab/InternVL3-8B"
  # "OpenGVLab/InternVL3-9B"
  # "OpenGVLab/InternVL3-14B"
  # "OpenGVLab/InternVL3-38B"
  # "OpenGVLab/InternVL3-78B" # memory issue on H100x2
  # "mistralai/Pixtral-12B-2409"
  # "google/gemma-3-1b-it" # no image model
  # "google/gemma-3-4b-it"
  # "google/gemma-3-12b-it"
  # "google/gemma-3-27b-it"
  # "naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B" # pip install timm
  # "kakaocorp/kanana-1.5-v-3b-instruct" # vllm not supporter
  # "NCSOFT/VARCO-VISION-2.0-1.7B"
  # "NCSOFT/VARCO-VISION-2.0-14B"
  # "OpenGVLab/InternVL3_5-1B"
  # "OpenGVLab/InternVL3_5-2B"
  # "OpenGVLab/InternVL3_5-4B"
  # "OpenGVLab/InternVL3_5-8B"
  # "OpenGVLab/InternVL3_5-14B"
  # "OpenGVLab/InternVL3_5-38B"
  # "OpenGVLab/InternVL3_5-30B-A3B"
  # "AIDC-AI/Ovis2.5-2B"
  # "AIDC-AI/Ovis2.5-9B" # vllm error for both . for vllm inference see https://github.com/AIDC-AI/Ovis

  # "AIDC-AI/Ovis2-1B"
  # "AIDC-AI/Ovis2-2B"
  "AIDC-AI/Ovis2-4B"
  # "AIDC-AI/Ovis2-8B"
  # "AIDC-AI/Ovis2-16B"
  # "AIDC-AI/Ovis2-34B"
  # "moonshotai/Kimi-VL-A3B-Instruct"
  # "moonshotai/Kimi-VL-A3B-Thinking-2506"
  # "Skywork/Skywork-R1V3-38B"
  # "Qwen/QVQ-72B-Preview"
  # "meta-llama/Llama-3.2-11B-Vision-Instruct"
  # "meta-llama/Llama-3.2-90B-Vision-Instruct"
  # "baidu/ERNIE-4.5-VL-28B-A3B-PT"
  
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
      --temperature "${TEMPERATURE}" \
      --top_p "${TOP_P}"
  done
done

echo "All runs complete. Outputs in: ${OUT_DIR}"
