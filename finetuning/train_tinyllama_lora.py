import json
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "synthetic" / "tinyllama_instructions.jsonl"
OUTPUT_DIR = BASE_DIR / "fine_tuning" / "tinyllama_lora"

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # HF hub id

MAX_LEN = 512

def formatting_func(example):
    # We already embedded system + question in 'instruction'
    prompt = example["instruction"].strip()
    target = example["output"].strip()

    # Simple causalLM format: "<prompt>\n\nAnswer: <target>"
    full = prompt + "\n\nAnswer: " + target
    return {"text": full}

def main():
    print("Loading dataset...")
    ds = load_dataset(
        "json",
        data_files=str(DATA_PATH),
        split="train"
    )
    ds = ds.map(formatting_func)

    print("Loading tokenizer and base model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize(example):
        return tokenizer(
            example["text"],
            max_length=MAX_LEN,
            truncation=True,
            padding="max_length",
        )

    tokenized = ds.map(tokenize, batched=True, remove_columns=ds.column_names)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # LoRA config
    config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],  # keep it small
    )

    model = get_peft_model(model, config)
    model.print_trainable_parameters()

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        learning_rate=2e-4,
        num_train_epochs=2,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="no",
        fp16=True,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
    )

    trainer.train()

    print(f"Saving LoRA adapter to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

if __name__ == "__main__":
    main()
