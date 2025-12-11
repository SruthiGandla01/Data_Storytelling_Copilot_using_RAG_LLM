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

CRITICAL RULES:
1. ALWAYS aggregate data - NEVER return raw rows
2. Use groupby() for comparison questions
3. The final result MUST be stored in a variable named result_df
4. result_df should have 1-20 rows max (aggregated summary)
5. For correlation questions, use groupby to show average metrics by category
6. Sort results by the metric (descending) to show top performers first
7. Do NOT print anything
8. Do NOT include backticks or markdown
9. Do NOT return more than 100 rows

Examples:
- "Which category has most orders?" → df.groupby('category_name')['order_id'].count().sort_values(ascending=False).head(10).reset_index()
- "What factors correlate with high profit?" → df.groupby('category_name')['order_profit_per_order'].mean().sort_values(ascending=False).head(10).reset_index()
- "Average sales by region" → df.groupby('order_region')['sales'].mean().sort_values(ascending=False).reset_index()
"""


def build_prompt(user_question: str, kb_context_docs: List[dict]) -> str:
    context_texts = "\n\n".join([d["text"] for d in kb_context_docs])
    
    # Detect query type and provide specific guidance
    question_lower = user_question.lower()
    
    guidance = ""
    if 'correlate' in question_lower or 'factors' in question_lower:
        guidance = """
IMPORTANT: This is a correlation/factors question.
- Use groupby to aggregate metrics by categorical dimension
- Calculate AVERAGE/MEAN for numeric metrics
- Sort descending to show highest values first
- Limit to top 10-15 results
- Example: df.groupby('category_name')['order_profit_per_order'].mean().sort_values(ascending=False).head(10).reset_index()
"""
    elif any(word in question_lower for word in ['most', 'highest', 'top', 'which']):
        guidance = """
IMPORTANT: This is a ranking/comparison question.
- Use groupby + count() or sum() or mean()
- Sort descending
- Limit to top 10 results
- Always use reset_index() to get a clean DataFrame
"""
    elif 'rate' in question_lower or 'percentage' in question_lower:
        guidance = """
IMPORTANT: This is a rate/percentage calculation.
- Calculate the percentage or rate using appropriate formula
- Group by the dimension asked (region, category, etc.)
- Sort to show best/worst performers
"""
    
    prompt = f"""
Context (schema and metrics):
{context_texts}

User question:
{user_question}

{guidance}

Instructions:
- Write pandas code using df (the orders DataFrame)
- MUST use groupby + aggregation (count, sum, mean, etc.)
- MUST sort results to show top performers first
- MUST limit to 10-20 rows maximum
- The final result MUST be assigned to result_df
- result_df should be a clean DataFrame with 2-3 columns
- Use .reset_index() to convert Series to DataFrame
- Use .head(10) or .head(15) to limit rows

Write ONLY the Python code. No explanation. No markdown. No backticks.
"""
    return dedent(prompt)


def generate_pandas_code(user_question: str) -> str:
    """Generate pandas code with better guidance for aggregation queries."""
    kb_docs = retrieve_context(user_question, top_k=4)
    prompt = build_prompt(user_question, kb_docs)

    resp = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    code = resp.choices[0].message.content.strip()
    
    # Clean up code if it has markdown
    code = code.replace('```python', '').replace('```', '').strip()
    
    return code