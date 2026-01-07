import time

def with_backoff(call, max_total_retries: int = 20, wait_short_sec: int = 60, wait_long_sec: int = 300):
    consecutive_failures = 0
    total_attempts = 0
    last_exc = None
    while total_attempts < max_total_retries:
        total_attempts += 1
        try:
            out = call()
            consecutive_failures = 0
            return out
        except Exception as e:
            last_exc = e
            consecutive_failures += 1
            wait = wait_short_sec if consecutive_failures < 3 else wait_long_sec
            print(f"[WARN] Call failed ({e}). {consecutive_failures} consecutive error(s). Sleeping {wait//60} min...")
            time.sleep(wait)
    raise RuntimeError(f"Exceeded {max_total_retries} retries. Last error: {last_exc}")
