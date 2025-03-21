# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from sentence_transformers import SentenceTransformer
from tqdm.asyncio import tqdm
import torch
import pandas as pd

# Configuration
INPUT_FILE = "../01_code/output.txt"  # Path to your input .txt file
OUTPUT_FILE = "../02_data/article_embeddings.parquet"  # Output TXT file to save embeddings
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model
BATCH_SIZE = 64  # Batch size for processing

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to load the model
def load_model():
    logging.info("Loading Sentence Transformer model...")
    return SentenceTransformer(MODEL_NAME, device="cuda" if torch.cuda.is_available() else "cpu")

# Function to parse .txt file
def parse_txt_file(file_path):
    """
    Parse the .txt file where each line is a JSON object.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()#[:10]  # Load only the desired lines
    return [json.loads(line.strip()) for line in lines]

# Function to preprocess data
def preprocess_data(data):
    """
    Extract 'title' and 'text' and combine them for embedding.
    """
    combined_texts = [f"{item['title']} {item['text']}" for item in data]
    indices = [item['index'] for item in data]
    urls = [item['url'] for item in data]
    return indices, urls, combined_texts

# Asynchronous function to generate embeddings
async def generate_embeddings(texts, model, batch_size=BATCH_SIZE):
    """
    Generate embeddings asynchronously for a batch of texts.
    """
    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    async for i, batch in tqdm(
        enumerate((texts[i: i + batch_size] for i in range(0, len(texts), batch_size))),
        total=total_batches,
        desc="Generating Embeddings",
        unit="batch"
    ):
        loop = asyncio.get_event_loop()
        # Generate embeddings in a thread-safe manner
        embedding_batch = await loop.run_in_executor(
            None, lambda: model.encode(batch, show_progress_bar=False)
        )
        embeddings.extend(embedding_batch)
    return embeddings

# Save embeddings in Parquet format
def save_to_parquet(output_file, indices, urls, combined_texts, embeddings):
    """
    Save embeddings as a Parquet file.
    """
    logging.info(f"Saving embeddings to {output_file}...")
    df = pd.DataFrame({
        "index": indices,
        "url": urls,
        "article":combined_texts,
        "embedding": embeddings#.tolist()
    })
    df.to_parquet(output_file, index=False)
    logging.info("Results successfully saved as Parquet file.")

# Main function
async def main():
    # Load the text data
    logging.info("Loading text data...")
    data = parse_txt_file(INPUT_FILE)
    indices, urls, combined_texts = preprocess_data(data)

    # Load model
    model = load_model()

    # Generate embeddings
    embeddings = await generate_embeddings(combined_texts, model)

    # Save embeddings to a .txt file
    save_to_parquet(OUTPUT_FILE, indices, urls, combined_texts, embeddings)

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
