import asyncio
import time
import random
from typing import Any
import httpx
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googlesearch import search
from utils.openaiapi import user_response

load_dotenv()

SCRAPEOWL_API_KEY = os.getenv('SCRAPEOWL_API_KEY')
SCRAPEOWL_URL = 'https://api.scrapeowl.com/v1/scrape'
MAX_RETRIES = 5

async def search_query(query: Any, sleep_interval: tuple = (10, 20)):
    user_query = await user_response(query)
    if not user_query:
        raise ValueError("Invalid query")
    
    print("voice file3 : ", query)
    urls = []

    for attempt in range(MAX_RETRIES):
        try:
            for url in search(query, lang="en", num_results=5):
                print("voice file4 : ", query)
                urls.append(url)
                time.sleep(random.uniform(*sleep_interval))  # Adjustable sleep interval
            return urls
        
        except requests.exceptions.ConnectTimeout as e:
            print(f"Connection timed out: {e}. Retrying in {sleep_interval[1]} seconds...")
            if attempt < MAX_RETRIES - 1:
                time.sleep(sleep_interval[1])  # Wait before retrying
            else:
                print("Max retries exceeded. Failing.")
                raise

async def scrape_website(query: Any, fixed_delay: int = 15):
    print("Transacript data :", query, "ending")
    user_transcript = query
    urls = await search_query(query, sleep_interval=(fixed_delay, fixed_delay + 10))  # Adjustable delay for rate limiting
    print("all urls : ", urls)

    async with httpx.AsyncClient() as client:
        result = []
        for url in urls:
            payload = {
                'api_key': SCRAPEOWL_API_KEY,
                'url': url,
                'elements': [
                    {"type": "css", "selector": "title"},
                    {"type": "css", "selector": "h1"},
                    {"type": "css", "selector": "p"}
                ],
            	"premium_proxies": True,
	            "country": "us",
                "json_response": False
            }
            headers = {"Content-Type": "application/json"}

            for attempt in range(MAX_RETRIES):
                try:
                    response = await client.post(SCRAPEOWL_URL, json=payload, headers=headers)
                    response.raise_for_status()

                    raw_html = response.text
                    soup = BeautifulSoup(raw_html, 'html.parser')

                    title = soup.title.string if soup.title else "No title found"
                    h1_tags = [h1.get_text() for h1 in soup.find_all('h1')]
                    blog_content = [p.get_text() for p in soup.find_all('p')]

                    url_data = {
                        'url': url,
                        'title': title,
                        'h1_tags': h1_tags,
                        'blog_content': blog_content
                    }
                    result.append(url_data)
                    break  # Exit the loop if the request is successful

                except httpx.HTTPStatusError as http_err:
                    if response.status_code == 429:
                        print(f"429 Too Many Requests for {url}: Retrying in {fixed_delay} seconds...")
                        await asyncio.sleep(fixed_delay)  # Delay if rate limited
                        fixed_delay += 5  # Increase delay if 429 persists
                    else:
                        print(f"HTTP error occurred for {url}: {http_err}")
                        if attempt < MAX_RETRIES - 1:
                            print(f"Retrying in {fixed_delay} seconds...")
                            await asyncio.sleep(fixed_delay)
                        else:
                            print(f"Failed to scrape {url} after {MAX_RETRIES} attempts.")
                            break
                except Exception as err:
                    print(f"An error occurred for {url}: {err}")
                    break

        if result:
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": result, "user_transcript": user_transcript}
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})

            if response.status_code == 200:
                print("Data successfully sent to the webhook.")
                return "success"
            else:
                return response.status_code
        else:
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": ""}
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})
            print("Empty webhook sent")
    return {"message": "task finished"}
