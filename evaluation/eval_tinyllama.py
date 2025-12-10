from pathlib import Path
import json

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "synthetic" / "tinyllama_instructions.jsonl"
ADAPTER_PATH = BASE_DIR / "finetuning" / "tinyllama_lora"
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

MAX_EXAMPLES = 5
MAX_NEW_TOKENS = 120

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    model = PeftModel.from_pretrained(base, str(ADAPTER_PATH))
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return model, tokenizer, device

def main():
    model, tokenizer, device = load_model()
    print("Loaded TinyLlama + LoRA for evaluation.")

    examples = []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= MAX_EXAMPLES:
                break
            examples.append(json.loads(line))

    for i, ex in enumerate(examples):
        instr = ex["instruction"]
        target = ex["output"]
        prompt = instr + "\n\nAnswer:"

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                top_p=0.9,
                temperature=0.7,
                eos_token_id=tokenizer.eos_token_id,
            )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        pred = text.split("Answer:", 1)[-1].strip()

        print("=" * 80)
        print(f"Example {i+1}")
        print("PROMPT:\n", instr)
        print("\nTARGET:\n", target)
        print("\nPREDICTION:\n", pred)

if __name__ == "__main__":
    main()
