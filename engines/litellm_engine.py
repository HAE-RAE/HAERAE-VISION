from litellm import completion
from utils.prompts import build_messages_litellm, strip_reasoning
from utils.retry import with_backoff
import time
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Any, Dict, Optional

def _safe_parse(result):
    try:
        content = result.choices[0].message.content.strip()
    except Exception:
        content = ""
    return content

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from tqdm.auto import tqdm  # auto picks notebook/terminal
import os

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from tqdm.auto import tqdm
import os

def run(
    model: str,
    rows: List[Dict[str, Any]],
    max_tokens: int = 1024,
    temperature: float = 0.0,
    top_p: float = 1.0,
    *,
    use_threads: bool = True,
    progress_desc: str = "Generating",
) -> List[str]:
    """
    Execute generations over `rows` concurrently and return ONLY the outputs,
    aligned with input order. Failed items return an empty string.
    """
    if not isinstance(rows, list):
        raise TypeError("rows must be a list")

    n_workers = min(os.cpu_count() or 2, 32)
    Executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    outputs: List[Optional[str]] = [None] * len(rows)

    with Executor(max_workers=n_workers) as ex:
        future_to_idx = {
            ex.submit(
                generate_with_retry,
                model,
                row,  # build messages before if your generate expects them
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            ): i
            for i, row in enumerate(rows)
        }

        ok = 0
        fail = 0
        with tqdm(total=len(future_to_idx), desc=progress_desc, unit="task", dynamic_ncols=True) as pbar:
            for fut in as_completed(future_to_idx):
                i = future_to_idx[fut]
                try:
                    resp = fut.result()
                    outputs[i] = (strip_reasoning(resp) if resp else "").strip()
                    ok += 1
                except Exception:
                    outputs[i] = ""  # leave blank on error to preserve order
                    fail += 1
                finally:
                    pbar.update(1)
                    pbar.set_postfix(ok=ok, fail=fail)

    # Replace any None with empty string and return
    return [o if o is not None else "" for o in outputs]



def generate_with_retry(
    model: str,
    messages: List[Dict[str, str]],
    *,
    max_tokens: int,
    temperature: float,
    top_p: float,
    max_total_retries: int = 20,
    short_wait_s: int = 5 * 60,   # 5 minutes
    long_wait_s: int = 60 * 60    # 60 minutes
) -> str:
    """
    Call the model with controlled back-off:
      • 1st or 2nd consecutive failure -> wait 5 min
      • 3+ consecutive failures        -> wait 60 min
      • after a success                -> failure counter resets
    """
    consecutive_failures = 0
    attempts = 0

    while attempts < max_total_retries:
        attempts += 1
        try:
            result = completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            resp = _safe_parse(result)
            return resp
        except Exception as e:
            consecutive_failures += 1
            wait_seconds = short_wait_s if consecutive_failures < 3 else long_wait_s
            print(
                f"[WARN] Generation failed ({e}). "
                f"{consecutive_failures} consecutive error(s). "
                f"Sleeping {wait_seconds // 60} min and retrying..."
            )
            time.sleep(wait_seconds)

    raise RuntimeError(f"Exceeded {max_total_retries} retries; aborting.")