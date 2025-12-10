from pathlib import Path
from typing import Dict

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from config import TINYLLAMA_BASE, TINYLLAMA_ADAPTER_PATH

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None
_tokenizer = None

def _load_model():
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    base = AutoModelForCausalLM.from_pretrained(
        TINYLLAMA_BASE,
        torch_dtype=torch.float16 if _device == "cuda" else torch.float32,
        device_map="auto" if _device == "cuda" else None,
    )
    model = PeftModel.from_pretrained(base, str(TINYLLAMA_ADAPTER_PATH))
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(TINYLLAMA_BASE)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    _model, _tokenizer = model, tokenizer
    return _model, _tokenizer


def generate_narrative_tinyllama(
    question: str,
    results_preview_md: str,
    summary_stats: Dict,
    kb_context_text: str,
    max_new_tokens: int = 220,
) -> str:
    model, tokenizer = _load_model()

    system = (
        "You are a senior supply chain analytics expert. "
        "You receive a business question, a preview of computed metrics, "
        "and some domain knowledge. You explain the results clearly and concisely "
        "in 3–6 sentences, focusing on the main patterns and practical actions."
    )

    prompt = (
        f"{system}\n\n"
        f"Question:\n{question}\n\n"
        f"Results (markdown table snippet):\n{results_preview_md}\n\n"
        f"Summary stats (JSON-like):\n{summary_stats}\n\n"
        f"Domain context:\n{kb_context_text}\n\n"
        "Write a concise explanation of what the data shows, "
        "including 1–2 recommended actions for operations or business teams.\n\n"
        "Answer:"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    ).to(_device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            eos_token_id=tokenizer.eos_token_id,
        )

    full = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # Return text *after* the "Answer:" marker if present
    if "Answer:" in full:
        return full.split("Answer:", 1)[1].strip()
    return full.strip()
