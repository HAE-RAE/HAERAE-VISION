import os
import pandas as pd

def load_df(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[-1].lower()
    if ext in [".parquet", ".pq"]:
        return pd.read_parquet(path)
    return pd.read_csv(path)

def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
