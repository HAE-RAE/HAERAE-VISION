from __future__ import annotations
import argparse
import os
import sys
from typing import List
from dotenv import load_dotenv

import pandas as pd
from litellm import batch_completion
import litellm

# Load environment variables from .env file
load_dotenv()

# litellm._turn_on_debug()

# Your utilities
from utils.evaluate import prompt_template, parse_single_score


def build_messages(df: pd.DataFrame,
                   question_col: str,
                   answer_col: str,
                   checklist_col: str) -> List[List[dict]]:
    """Build per-row chat messages for batch_completion."""
    required = [question_col, answer_col, checklist_col]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Input CSV missing required column: '{col}'")

    messages = []
    for _, row in df.iterrows():
        qry = (
            f"{prompt_template}"
            f"[INPUT]\n{row[question_col]}\n"
            f"[Response]\n{row[answer_col]}\n"
            f"[Checklist]\n{row[checklist_col]}\n"
        )
        messages.append([{"role": "user", "content": str(qry)}])
    return messages


def main():
    parser = argparse.ArgumentParser(
        description="Run a judge model over a CSV and append response/score."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input CSV."
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Path to output CSV. If omitted, overwrites the input."
    )
    parser.add_argument(
        "--model", "-m", default="gpt-5-mini",
        help="Judge model name (litellm model string)."
    )
    parser.add_argument(
        "--api-key", default=None,
        help="API key to set for this run (optional; otherwise use env var)."
    )
    parser.add_argument(
        "--question-col", default="question_used",
        help="Column name for the source question (default: question_used from main.py output)."
    )
    parser.add_argument(
        "--answer-col", default="response",
        help="Column name for the model's answer to be judged."
    )
    parser.add_argument(
        "--checklist-col", default="checklist",
        help="Column name for the checklist text."
    )
    parser.add_argument(
        "--response-col-name", default="judge_response",
        help="Name of the new column to store judge outputs."
    )
    parser.add_argument(
        "--score-col-name", default="score",
        help="Name of the new column to store parsed scores."
    )

    args = parser.parse_args()

    # API key handling (prefer env var)
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key

    # Sanity check
    if "OPENAI_API_KEY" not in os.environ:
        print(
            "ERROR: OPENAI_API_KEY not set. Export it or pass --api-key.",
            file=sys.stderr
        )
        sys.exit(1)

    # Load CSV
    df = pd.read_csv(args.input)

    # Build messages for batch call
    messages = build_messages(
        df,
        question_col=args.question_col,
        answer_col=args.answer_col,
        checklist_col=args.checklist_col,
    )

    # Call litellm batch completion
    try:
        responses = batch_completion(
            model=args.model,
            messages=messages
        )
    except Exception as e:
        print(f"Batch completion failed: {e}", file=sys.stderr)
        sys.exit(2)

    # Extract outputs (aligned with inputs)
    # litellm returns a list of Response objects compatible with OpenAI schema
    raw_outputs: List[str] = []
    scores: List[float] = []
    for resp in responses:
        try:
            content = resp.choices[0].message.content
        except Exception:
            content = ""
        raw_outputs.append(content)
        try:
            score_dict = parse_single_score(content)
            # Extract the numeric value from the dict
            score_val = score_dict['value'] if score_dict else None
        except Exception:
            score_val = None
        scores.append(score_val)

    # Append new columns
    df[args.response_col_name] = raw_outputs
    df[args.score_col_name] = scores

    # Write out
    out_path = args.output or args.input
    df.to_csv(out_path, index=False)
    print(f"✓ Wrote {len(df)} rows to: {out_path}")


if __name__ == "__main__":
    main()
