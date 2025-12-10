import json
from pathlib import Path
import random

BASE_DIR = Path(__file__).resolve().parents[1]  # project root
OUT_PATH = BASE_DIR / "synthetic" / "qa_supplychain.json"


METRICS = [
    "on_time_delivery rate",
    "late_delivery_risk percentage",
    "average shipping_delay_days",
    "average benefit_per_order",
    "total sales",
    "average order_item_quantity",
]

SEGMENTS = [
    "customer_segment",
    "order_region",
    "market",
    "category_name",
    "payment_type",
    "shipping_mode",
]

BUSINESS_FOCUS = [
    "identify high-risk regions for delays",
    "find the most profitable customer groups",
    "understand where operational bottlenecks exist",
    "optimize shipping strategy",
    "prioritize customers for retention programs",
]


def generate_question(metric: str, segment: str) -> str:
    templates = [
        f"What is the {metric} by {segment}?",
        f"Compare {metric} across different {segment}.",
        f"Which {segment} has the highest {metric}?",
        f"How does {metric} vary across {segment} groups?",
    ]
    return random.choice(templates)


def generate_answer(metric: str, segment: str) -> str:
    # Synthetic, qualitative answers – not tied to real numbers
    patterns = [
        f"The {segment} groups show clear differences in {metric}. "
        f"A few segments stand out with significantly higher values, "
        f"indicating where operations or pricing strategies are working better.",

        f"In general, {metric} is highest for a small subset of {segment}, "
        f"while most segments cluster around the average. These outliers "
        f"are good candidates for deeper investigation.",

        f"The analysis reveals that {metric} is unevenly distributed across {segment}. "
        f"Some segments perform well, while others lag behind, suggesting "
        f"targeted interventions could improve overall performance.",
    ]
    return random.choice(patterns)


def generate_dataset(n: int = 80):
    examples = []

    for _ in range(n):
        metric = random.choice(METRICS)
        segment = random.choice(SEGMENTS)
        focus = random.choice(BUSINESS_FOCUS)

        q = generate_question(metric, segment) + f" I want to {focus}."
        a = generate_answer(metric, segment)

        examples.append(
            {
                "question": q,
                "answer": a,
                "metric": metric,
                "segment": segment,
                "focus": focus,
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(examples)} synthetic Q&A pairs at {OUT_PATH}")


if __name__ == "__main__":
    generate_dataset()
