from typing import Dict, Any

from pipeline.data_runner import load_processed_df, run_pandas_code
from pipeline.code_generator import generate_pandas_code
from pipeline.insight_generator import generate_insights


def answer_question(question: str) -> Dict[str, Any]:
    df = load_processed_df()

    # 1) Generate pandas code
    code = generate_pandas_code(question)

    # 2) Run the code
    result_df, summary_stats = run_pandas_code(df, code)

    # 3) Generate narrative insights
    narrative = generate_insights(question, result_df, summary_stats)

    return {
        "code": code,
        "result_df": result_df,
        "summary_stats": summary_stats,
        "narrative": narrative,
    }
