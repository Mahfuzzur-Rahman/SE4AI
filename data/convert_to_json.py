import json
import os
import sys
from pathlib import Path
from datasets import load_dataset

# --- Dynamic Path Resolution ---
# This ensures 'data/' is found even if run from subdirectories
CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CURRENT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

def download_and_convert():
    print("Downloading FullStack-Bench from Hugging Face...")
    # Load from the specific repository you selected
    ds = load_dataset("luzimu/FullStack-Bench")
    
    tasks = [row for row in ds['train']]
    
    # Define absolute paths dynamically
    dataset_path = DATA_DIR / "dataset.json"
    metadata_path = DATA_DIR / "metadata.json"
    
    # 1. Save the full task list
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)
    
    # 2. Create metadata.json for dataset descriptions
    metadata = {
        "dataset_name": "FullStack-Bench",
        "total_tasks": len(tasks),
        "description": "Comprehensive benchmark for full-stack engineering tasks."
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"Successfully saved to: {dataset_path}")

if __name__ == "__main__":
    download_and_convert()