"""
Data runner utilities:
- load_processed_df: load cleaned parquet file
- run_pandas_code: safely execute LLM-generated pandas code
"""

import re
import pandas as pd

from config import DATA_PROCESSED_PATH


def load_processed_df() -> pd.DataFrame:
    """Load the cleaned orders dataframe from parquet."""
    return pd.read_parquet(DATA_PROCESSED_PATH)


def clean_code(raw_code: str) -> str:
    """
    Remove markdown formatting such as ```python, ``` and stray backticks.
    Ensures the code passed to exec() is valid Python.
    """
    code = raw_code.strip()

    # Remove fenced code blocks like ```python ... ```
    code = re.sub(r"```python", "", code, flags=re.IGNORECASE)
    code = code.replace("```", "")

    # Remove any remaining stray backticks
    code = code.replace("`", "")

    return code.strip()


def run_pandas_code(df: pd.DataFrame, raw_code: str):
    """
    Execute generated pandas code safely.

    - `df` is injected into local_vars
    - Generated code MUST create a variable named `result_df`
    """
    cleaned = clean_code(raw_code)

    local_vars = {"df": df}

    try:
        exec(cleaned, {}, local_vars)
    except Exception as e:
        raise RuntimeError(
            f"Error executing generated code: {e}\n\nCleaned Code:\n{cleaned}"
        ) from e

    if "result_df" not in local_vars:
        raise RuntimeError(
            "Generated code did not create `result_df`. "
            "Make sure the model assigns the final table to result_df."
        )

    result_df = local_vars["result_df"]

    if not isinstance(result_df, pd.DataFrame):
        # Try to coerce Series/list/dict into a DataFrame
        result_df = pd.DataFrame(result_df)

    summary_stats = {
        "rows": len(result_df),
        "columns": list(result_df.columns),
        "dtypes": {col: str(result_df[col].dtype) for col in result_df.columns},
    }

    return result_df, summary_stats
