#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 22:07:39 2024

@author: giordano
"""

import asyncio
import aiohttp
from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup
import time
import logging
import random
import pandas as pd
import json
import os
from tqdm.asyncio import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Global settings
CONCURRENT_REQUESTS = 10
TIMEOUT = aiohttp.ClientTimeout(total=30)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
]
BACKUP_FILE = 'backup.json'
CHECKPOINT_INTERVAL = 1000

async def fetch(session, url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                logging.info(f'Successfully fetched URL: {url}')
                return await response.text()
    except Exception as e:
        logging.error(f'Exception for URL {url}: {e}')

async def parse(html, url, index):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else 'No Title Found'
        article_tags = soup.find_all(['p', 'h1', 'h2', 'h3'])
        text = ' '.join(tag.get_text(strip=True) for tag in article_tags)[:1000]
        return {'index': index, 'url': url, 'title': title, 'text': text}
    except Exception as e:
        logging.error(f'Error parsing HTML from {url}: {e}')

async def save_to_file(data, output_file):
    output_file.write(json.dumps(data) + "\n")
    output_file.flush()

def load_backup():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'r') as f:
            return json.load(f)
    return {'processed': [], 'results': []}

def save_backup(backup_data):
    with open(BACKUP_FILE, 'w') as f:
        json.dump(backup_data, f)

async def worker(sem, session, url, index, backup_data, output_file):
    async with sem:
        if url in backup_data['processed']:
            logging.info(f"Skipping already processed URL: {url}")
            return
        html = await fetch(session, url)
        if html:
            data = await parse(html, url, index)
            if data:
                backup_data['results'].append(data)
                backup_data['processed'].append(url)
                await save_to_file(data, output_file)

async def run(urls_with_indices, backup_data, output_file):
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    connector = TCPConnector(limit=CONCURRENT_REQUESTS)
    
    async with ClientSession(connector=connector, timeout=TIMEOUT) as session:
        tasks = [
            worker(sem, session, url, index, backup_data, output_file)
            for url, index in urls_with_indices
        ]
        
        # Use tqdm to wrap the asyncio tasks for a progress bar
        for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Progress"):
            await task  # Ensure each task is awaited
    save_backup(backup_data)

def load_urls(file_path):
    try:
        # Determine file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Read the file based on the extension
        if file_extension == '.parquet':
            df = pd.read_parquet(file_path)
        elif file_extension == '.csv':
            df = pd.read_csv(file_path)
        else:
            logging.error("Unsupported file format. Please provide a Parquet or CSV file.")
            return []
        
        # Check if 'url' and 'index' columns exist
        if 'url' in df.columns and 'index' in df.columns:
            return df[['url', 'index']].dropna().values.tolist()
        else:
            logging.error(f"Required columns 'url' and 'index'")
            return []
    
    except Exception as e:
        logging.error(f"Error reading the file: {e}")
        return []

if __name__ == '__main__':
    start_time = time.time()
    url_list_with_indices = load_urls('../02_data/top_100_filtered.csv')
    logging.info(f'Starting scrape of {len(url_list_with_indices)} URLs.')
    
    backup_data = load_backup()
    remaining_urls = [item for item in url_list_with_indices if item[0] not in backup_data['processed']]
    
    with open("output.txt", "a") as output_file:
        asyncio.run(run(remaining_urls, backup_data, output_file))
    
    elapsed = time.time() - start_time
    logging.info(f'Scraping completed in {elapsed:.2f} seconds.')