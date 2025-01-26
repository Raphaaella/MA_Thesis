# -*- coding: utf-8 -*-
import asyncio
import logging
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import re
from tqdm.asyncio import tqdm

# Configuration
INPUT_CSV = "../02_data/text_messages.csv"  # Path to your input CSV containing text data
OUTPUT_TXT = "../02_data/messages_embeddings.txt"  # Output TXT to save embeddings
LOG_FILE = "../02_data/embedding_creation.log"  # Log file
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model
BATCH_SIZE = 64  # Batch size for processing

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Function to preprocess text
def preprocess_text(text):
    """
    Preprocess text by:
    - Converting to lowercase
    - Removing special characters
    - Replacing multiple spaces with a single space
    """
    if not isinstance(text, str):  # Handle non-string entries gracefully
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\sáéíóúñüäößàèìòùç]", " ", text)  # Allow common accented characters
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Function to preprocess a DataFrame
def preprocess_dataframe(df):
    """
    Apply text preprocessing to the DataFrame.
    """
    if "top_1_fwds_text" not in df or "url" not in df:
        raise ValueError("Input DataFrame must have 'top_1_fwds_text' and 'url' columns")
    logging.info("Preprocessing text data...")
    df["top_1_fwds_text"] = df["top_1_fwds_text"].apply(preprocess_text)
    return df

# Function to load model
def load_model():
    logging.info("Loading Sentence Transformer model...")
    return SentenceTransformer(MODEL_NAME, device="cuda" if torch.cuda.is_available() else "cpu")

# Function to generate embeddings asynchronously
async def generate_embeddings(texts, model, batch_size=BATCH_SIZE):
    loop = asyncio.get_event_loop()
    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    # Batch processing for efficiency with tqdm progress bar
    async for i, batch in tqdm(
        enumerate((texts[i: i + batch_size] for i in range(0, len(texts), batch_size))),
        total=total_batches,
        desc="Generating Embeddings",
        unit="batch"
    ):
        # Process embedding in a thread-safe manner
        embedding_batch = await loop.run_in_executor(
            None, lambda: model.encode(batch, show_progress_bar=False)
        )
        embeddings.extend(embedding_batch)
    return embeddings

# Save embeddings to a .txt file
def save_to_txt(output_file, urls, texts, embeddings):
    logging.info(f"Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for url, text, embedding in zip(urls, texts, embeddings):
            f.write(f"URL: {url}\n")
            f.write(f"Text: {text}\n")
            f.write(f"Embedding: {embedding.tolist()}\n")
            f.write("\n" + "-" * 80 + "\n")  # Separator for readability
    logging.info("Results successfully saved.")

# Main function
async def main():
    # Load text data
    logging.info("Loading text data...")
    df = pd.read_csv(INPUT_CSV)

    if "top_1_fwds_text" not in df or "url" not in df:
        raise ValueError("Input CSV must have 'top_1_fwds_text' and 'url' columns")

    # Preprocess text data
    df = preprocess_dataframe(df)

    # Extract relevant columns for embedding
    texts = df["top_1_fwds_text"].tolist()
    urls = df["url"].tolist()

    # Load model
    model = load_model()

    # Generate embeddings
    embeddings = await generate_embeddings(texts, model)

    # Save results to a .txt file
    save_to_txt(OUTPUT_TXT, urls, texts, embeddings)

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
