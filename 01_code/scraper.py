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
CONCURRENT_REQUESTS = 10  # Adjust based on your system's capabilities
TIMEOUT = aiohttp.ClientTimeout(total=30)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    # Add more user-agent strings as needed
]

async def fetch(session, url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                logging.info(f'Successfully fetched URL: {url}')
                return await response.text()
            else:
                a = 1
                # logging.warning(f'Non-200 status code {response.status} for URL: {url}')
    except Exception as e:
        pass
        # logging.error(f'Exception for URL {url}: {e}')

async def parse(html, url):
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title = soup.title.string.strip() if soup.title else 'No Title Found'

        # Extract main text
        # This may vary depending on the website's structure
        # Common tags include <article>, <div id="content">, etc.
        article_tags = soup.find_all(['p', 'h1', 'h2', 'h3'])
        text = ' '.join(tag.get_text(strip=True) for tag in article_tags)
        text = text[:1000]  # Limit to first 1000 characters for brevity

        return {'url': url, 'title': title, 'text': text}
    except Exception as e:
        pass
        # logging.error(f'Error parsing HTML from {url}: {e}')

async def save(data, f):
    # Save or process the data as needed
    # Here, we're just printing it to the console
    f.write(f"URL: {data['url']}\nTitle: {data['title']}\nText: {data['text']}\n")
    print(f"URL: {data['url']}\nTitle: {data['title']}\nText: {data['text']}\n{'-'*80}")

async def worker(sem, session, url, f):
    async with sem:
        html = await fetch(session, url)
        if html:
            data = await parse(html, url)
            if data:
                await save(data, f)

async def run(urls, f):
    tasks = []
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    connector = TCPConnector(limit=CONCURRENT_REQUESTS)
    async with ClientSession(connector=connector, timeout=TIMEOUT) as session:
        for url in urls:
            task = asyncio.create_task(worker(sem, session, url, f))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

def load_urls(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == '__main__':
    start_time = time.time()
    f = open("output.txt", "a")
    url_list = load_urls('urls.txt')[:1000]  # Replace with your file path
    logging.info(f'Starting scrape of {len(url_list)} URLs.')
    asyncio.run(run(url_list, f))
    elapsed = time.time() - start_time
    logging.info(f'Scraping completed in {elapsed:.2f} seconds.')
