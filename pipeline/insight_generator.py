from typing import List, Dict
from textwrap import dedent

import pandas as pd
from openai import OpenAI

from config import LLM_MODEL_NAME,USE_TINYLLAMA_LOCAL
from rag.retriever import retrieve_context
# TinyLlama narrative generator
from finetuning.tinyllama_narrative import generate_narrative_tinyllama

client = OpenAI()

INSIGHT_SYSTEM_PROMPT = """
You are a senior supply chain and business analyst.

Given:
- A business question
- A preview of tabular results (grouped metrics)
- Simple summary statistics
- Domain context (schema, metric definitions, business playbook)

You must produce:
1. 2–3 bullet points executive summary (clear, non-technical).
2. A short technical explanation (1–2 paragraphs) describing how the metric was calculated and segmented.
3. 1–2 recommended next actions for operations, logistics, or business stakeholders.

Be concise.
Do NOT invent metrics that are not supported by the results.
"""


def build_insight_prompt(
    user_question: str,
    results_preview: str,
    summary_stats: Dict,
    kb_docs: List[Dict],
) -> str:
    context_texts = "\n\n".join([d["text"] for d in kb_docs])
    prompt = f"""
Business question:
{user_question}

Results preview (first rows or aggregates):
{results_preview}

Summary stats (JSON-like):
{summary_stats}

Domain context:
{context_texts}

Now respond with:
1. Executive summary (2–3 bullet points).
2. Technical explanation.
3. Recommended next actions.
"""
    return dedent(prompt), context_texts


def generate_insights(
    user_question: str,
    result_df: pd.DataFrame,
    summary_stats: Dict,
) -> str:
    kb_docs = retrieve_context(user_question, top_k=5)
    results_preview = result_df.head(10).to_markdown()
    prompt, context_texts = build_insight_prompt(
        user_question=user_question,
        results_preview=results_preview,
        summary_stats=summary_stats,
        kb_docs=kb_docs,
    )

    # ---- Path 1: TinyLlama local (preferred for project) ----
    if USE_TINYLLAMA_LOCAL:
        return generate_narrative_tinyllama(
            question=user_question,
            results_preview_md=results_preview,
            summary_stats=summary_stats,
            kb_context_text=context_texts,
        )

    # ---- Path 2: Fallback to OpenAI ----
    resp = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    text = resp.choices[0].message.content.strip()
    return text
