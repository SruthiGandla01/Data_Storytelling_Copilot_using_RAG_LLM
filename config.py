"""
Global configuration for InsightWeaver – Supply Chain project.

This file defines:
- BASE_DIR: project root folder
- Data paths
- KB / RAG paths
- LLM + embedding configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------------
# 1. BASE DIRECTORY + PYTHON PATH PATCH
# ----------------------------------------------------------

# This is the "Final Project" directory, regardless of spaces in the path.
BASE_DIR = Path(__file__).resolve().parent

# Ensure BASE_DIR is on sys.path so `import config` and other modules work
# even when scripts are run via `python pipeline/data_loader.py`.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load environment variables from .env at the project root
load_dotenv(BASE_DIR / ".env")

# ----------------------------------------------------------
# 2. DATA PATHS
# ----------------------------------------------------------

# Raw Kaggle CSV must be here: data/raw/DataCoSupplyChainDataset.csv
DATA_RAW_PATH = BASE_DIR / "data" / "raw" / "DataCoSupplyChainDataset.csv"

# Cleaned parquet file will be written here by data_loader.py
DATA_PROCESSED_PATH = BASE_DIR / "data" / "processed" / "orders_clean.parquet"

# ----------------------------------------------------------
# 3. KNOWLEDGE BASE / RAG PATHS
# ----------------------------------------------------------

KB_BASE_PATH = BASE_DIR / "kb"
CHROMA_DB_DIR = BASE_DIR / "rag" / "chroma_store"

# ----------------------------------------------------------
# 4. MODEL CONFIGURATION
# ----------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")

# Embedding model name used by sentence-transformers
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

USE_TINYLLAMA_LOCAL = os.getenv("USE_TINYLLAMA_LOCAL", "false").lower() == "true" # toggle
TINYLLAMA_BASE = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
TINYLLAMA_ADAPTER_PATH =  "/Users/sruthigandla/Documents/Northeastern/Prompt engineering/Final Project/finetuning/tinyllama_lora"

# ----------------------------------------------------------
# 5. DEBUG (optional)
# ----------------------------------------------------------

if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("DATA_RAW_PATH:", DATA_RAW_PATH)
    print("DATA_PROCESSED_PATH:", DATA_PROCESSED_PATH)
    print("KB_BASE_PATH:", KB_BASE_PATH)
    print("CHROMA_DB_DIR:", CHROMA_DB_DIR)
    print("OPENAI_API_KEY loaded?", bool(OPENAI_API_KEY))
