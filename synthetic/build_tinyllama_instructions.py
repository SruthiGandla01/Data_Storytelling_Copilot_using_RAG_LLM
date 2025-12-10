import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
QA_PATH = BASE_DIR / "synthetic" / "qa_supplychain.json"
OUT_PATH = BASE_DIR / "synthetic" / "tinyllama_instructions.jsonl"

SYSTEM_PROMPT = (
    "You are a senior supply chain analytics assistant. "
    "Given a business question and context, you explain the key insights clearly, "
    "in 3–6 sentences, focusing on deliveries, delays, customer segments, and profitability."
)

def main():
    with QA_PATH.open("r", encoding="utf-8") as f:
        qa_data = json.load(f)

    with OUT_PATH.open("w", encoding="utf-8") as out_f:
        for item in qa_data:
            q = item["question"]
            a = item["answer"]

            # This is the full prompt TinyLlama sees
            instruction = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Question: {q}\n\n"
                "Write a concise explanation of what the data likely shows, "
                "highlighting the most important differences and what they imply."
            )

            record = {
                "instruction": instruction,
                "output": a,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote TinyLlama instructions to {OUT_PATH}")

if __name__ == "__main__":
    main()
