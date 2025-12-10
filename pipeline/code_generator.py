from typing import List
from textwrap import dedent

from openai import OpenAI

from config import LLM_MODEL_NAME
from rag.retriever import retrieve_context

# Single global client instance (new OpenAI SDK)
client = OpenAI()

SYSTEM_PROMPT = """
You are a supply chain data analytics assistant.

You generate Python pandas code to answer questions about a DataFrame called df.
The DataFrame contains supply chain order line data with columns such as:

- order_id, order_date, shipping_date
- order_region, order_country, order_city, order_state
- customer_segment, market, category_name, department_name, product_name
- days_for_shipment_scheduled, days_for_shipping_real, shipping_delay_days, on_time_delivery
- sales, benefit_per_order, order_profit_per_order
- order_item_quantity, order_item_total, order_item_discount, order_item_discount_rate

Rules:
- Use only columns that exist in the schema context.
- Use df for all operations.
- The final result MUST be stored in a variable named result_df.
- Do NOT print anything.
- Do NOT include backticks.
"""


def build_prompt(user_question: str, kb_context_docs: List[dict]) -> str:
    context_texts = "\n\n".join([d["text"] for d in kb_context_docs])
    prompt = f"""
Context (schema and metrics):
{context_texts}

User question:
{user_question}

Instructions:
- Write pandas code using df (the orders table).
- Use groupby/aggregation if the question suggests comparison across segments.
- Make sure the final table or series that answers the question
  is assigned to a variable called result_df.

Write ONLY the Python code. No explanation.
"""
    return dedent(prompt)


def generate_pandas_code(user_question: str) -> str:
    kb_docs = retrieve_context(user_question, top_k=4)
    prompt = build_prompt(user_question, kb_docs)

    resp = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    code = resp.choices[0].message.content.strip()
    return code
