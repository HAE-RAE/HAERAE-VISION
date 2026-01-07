# HAERAE-VISION

Evaluation code for HAERAE-Vision benchmark - a Korean visual QA dataset with real-world, under-specified questions.

- **Dataset**: [HAERAE-HUB/HAERAE-VISION](https://huggingface.co/datasets/HAERAE-HUB/HAERAE-VISION)
- **Leaderboard**: [https://board.haerae.world/](https://board.haerae.world/)

## Installation

**Requirements**: Python >= 3.9

```bash
pip install -r requirements.txt
cp env.example .env  # Add your API keys (see env.example for details)
```

> **Note**: `OPENAI_API_KEY` is required for the judge model.

## Dataset

The dataset includes **two question types**:
- **`original`**: Under-specified, authentic user queries 
- **`explicit`**: Clarified queries with full context 

Both share the same images and reference answers, allowing controlled evaluation of query under-specification.

> **Note**: This public dataset contains **25% of the full benchmark** (165 items) for development and testing. 

## Usage

The evaluation process consists of **two stages**:
1. **Inference** (`main.py`): Generate model responses
2. **Scoring** (`score.py`): Evaluate responses with a judge model (GPT-5-mini)

> **Note**: Stage 2 always requires `OPENAI_API_KEY` for the judge model. Stage 1 requires API keys only for cloud models (GPT, Claude, Gemini, etc.); local vLLM models do not need API keys.

### Stage 1: Generate Model Responses

```bash
# Evaluate with ORIGINAL questions (under-specified)
python main.py \
  --engine litellm \
  --model gpt-4o \
  --question-type original \
  --output results/gpt4o_original.csv

# Evaluate with EXPLICIT questions (clarified)
python main.py \
  --engine litellm \
  --model gpt-4o \
  --question-type explicit \
  --output results/gpt4o_explicit.csv

# Using OpenRouter (access multiple models with one API key)
python main.py \
  --engine litellm \
  --model openrouter/anthropic/claude-3.5-sonnet \
  --question-type original \
  --output results/claude_original.csv

# Using vLLM for local models (requires GPU)
CUDA_VISIBLE_DEVICES=0,1 python main.py \
  --engine vllm \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --question-type original \
  --output results/qwen_original.csv
```

**Arguments**:
- `--engine`: `vllm` or `litellm`
- `--model`: Model name (examples below, but supports any litellm/vLLM compatible model)
  - GPT models: `gpt-4o`, `gpt-4o-mini`, `gpt-5-mini`
  - Gemini: `gemini/gemini-2.5-pro`, `gemini/gemini-2.5-flash`
  - Claude: `claude-3.5-sonnet`, `claude-3-opus`
  - Via OpenRouter: `openrouter/{provider}/{model}`
  - Local vLLM: `Qwen/Qwen2.5-VL-3B-Instruct`, `OpenGVLab/InternVL3-8B`, etc.
- `--question-type`: `original` or `explicit` (default: `original`)
- `--output`: Output CSV path (the `results/` directory will be created automatically)
- `--max_tokens`: Max generation tokens (default: 512)
- `--temperature`: Sampling temperature (default: 0.2)

### Stage 2: Score with Judge Model

After generating responses, evaluate them using a judge model (default: GPT-5-mini):

> **Required**: `OPENAI_API_KEY` must be set for the judge model.

```bash
python score.py \
  --input results/gpt4o_original.csv \
  --output results/gpt4o_original_scored.csv \
  --model gpt-5-mini
```

**Arguments**:
- `--input`: CSV from step 1
- `--output`: Output CSV with scores
- `--model`: Judge model (default: `gpt-5-mini`)
- `--question-col`: Question column name (default: `question_used`)
- `--answer-col`: Response column name (default: `response`)

## Output Format

**After Stage 1** (`main.py`):
- All dataset fields (question_original, question_explicit, images, etc.)
- `response`: Model's generated answer
- `question_type`: Which question type was used
- `question_used`: Actual question text used

**After Stage 2** (`score.py`):
- All Stage 1 fields plus:
- `judge_response`: Judge model's detailed evaluation
- `score`: Final score (0.0 to 1.0)

## Citation


```bibtex

```


## Contact

For access to the full test set / leaderboard submission:

- Dasol Choi (dasolchoi@yonsei.ac.kr)  
- Guijin Son (spthsrbwls123@yonsei.ac.kr)
