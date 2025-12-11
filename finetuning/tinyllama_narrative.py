from pathlib import Path
from typing import Dict
import re

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


def clean_tinyllama_output(raw_output: str, question: str) -> str:
    """
    Clean TinyLlama output by removing prompt echoes and irrelevant content.
    """
    
    # Remove the question if it's being repeated
    cleaned = raw_output.replace(question, "").strip()
    
    # Remove common prompt artifacts that TinyLlama echoes
    patterns_to_remove = [
        r"You are a senior.*?(?=\n\n|\Z)",  # System prompt
        r"Question:.*?\n",  # Question label
        r"Results.*?:\s*\n",  # Results header
        r"Summary stats.*?:\s*\n",  # Summary stats header
        r"Domain context:.*?(?=\n\n|\Z)",  # Domain context section
        r"Main analytical table:.*?(?=\n\n|\Z)",  # Schema descriptions
        r"Key fields:.*?(?=\n\n|\Z)",  # Field lists
        r"Customer fields:.*?(?=\n\n|\Z)",  # Customer field lists
        r"Product fields:.*?(?=\n\n|\Z)",  # Product field lists
        r"\* `order_[^`]+`[^\n]*\n",  # Field definitions with backticks
        r"order_[a-z_]+\s*:.*?(?=\n|\.)",  # Field explanations
        r"`[^`]+`:.*?(?=\n|\.|$)",  # Any backtick definitions
        r"average order [a-z_]+.*?per order\.",  # Generic field descriptions
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove markdown table artifacts
    cleaned = re.sub(r'\|[^\n]+\|', "", cleaned)  # Table rows
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)  # Multiple newlines
    
    # Split into sentences and filter
    sentences = []
    for sentence in re.split(r'[.!?]+', cleaned):
        sentence = sentence.strip()
        
        # Skip if too short
        if len(sentence) < 20:
            continue
        
        # Skip if contains technical field names or schema references
        if any(x in sentence.lower() for x in [
            'order_', 'customer_', 'product_', 'main analytical', 
            'key fields', 'identifier', '`', 'table:', 'schema'
        ]):
            continue
        
        # Keep if it looks like a proper insight sentence
        if sentence and sentence[0].isupper():
            sentences.append(sentence)
    
    # Reconstruct cleaned output
    if sentences:
        result = '. '.join(sentences)
        if not result.endswith('.'):
            result += '.'
        return result
    
    # If no valid sentences found, return empty (will trigger fallback)
    return ""


def generate_narrative_tinyllama(
    question: str,
    results_preview_md: str,
    summary_stats: Dict,
    kb_context_text: str,
    max_new_tokens: int = 150,  # Reduced from 220 for more focused output
) -> str:
    """
    Generate narrative using fine-tuned TinyLlama with improved prompting.
    """
    model, tokenizer = _load_model()

    # Simplified prompt that reduces schema echoing
    system = (
        "You are a business analyst. Analyze supply chain data and provide "
        "a brief 2-3 sentence insight focusing on key findings and recommendations."
    )

    # More focused prompt without excessive context
    prompt = (
        f"{system}\n\n"
        f"Question: {question}\n\n"
        f"Data Results:\n{results_preview_md}\n\n"
        "Provide a concise business insight with specific numbers and one actionable recommendation.\n\n"
        "Insight:"
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
            temperature=0.6,  # Slightly lower for more focused output
            repetition_penalty=1.2,  # Prevent repeating prompt
            eos_token_id=tokenizer.eos_token_id,
        )

    full = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    # Extract answer after the marker
    if "Insight:" in full:
        raw_answer = full.split("Insight:", 1)[1].strip()
    elif "Answer:" in full:
        raw_answer = full.split("Answer:", 1)[1].strip()
    else:
        raw_answer = full.strip()
    
    # Clean the output
    cleaned_answer = clean_tinyllama_output(raw_answer, question)
    
    # Return cleaned output (empty string will trigger fallback in insight_generator)
    return cleaned_answer