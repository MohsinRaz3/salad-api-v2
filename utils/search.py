import asyncio
import time
import random
from typing import Any
import httpx
import os
from bs4 import BeautifulSoup
from googlesearch import search
from dotenv import load_dotenv
load_dotenv()

SCRAPEOWL_API_KEY =  os.getenv('SCRAPEOWL_API_KEY')
SCRAPEOWL_URL = 'https://api.scrapeowl.com/v1/scrape'
MAX_RETRIES = 5 
FIXED_DELAY = 10 

async def search_query(query: Any):
    urls = []

    for url in search(query, lang="en", sleep_interval=3, num_results=7):
        urls.append(url)
        time.sleep(random.uniform(3, 7)) 
    return urls


async def scrape_website(query: Any):
    urls = await search_query(query)
    
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
                "json_response": False,
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
                    break 

                except httpx.HTTPStatusError as http_err:
                    #print(f"HTTP error occurred for {url}: {http_err}")
                    if attempt < MAX_RETRIES - 1:
                        #print(f"Retrying in {FIXED_DELAY} seconds...")
                        await asyncio.sleep(FIXED_DELAY)  
                    else:
                        #print(f"Failed to scrape {url} after {MAX_RETRIES} attempts.")
                        break
                except Exception as err:
                    #print(f"An error occurred for {url}: {err}")
                    break

        if result:    
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": result} 
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                return "success"
                #print("Data successfully sent to the webhook.")
            else:
                return response.status_code
                #print(f"Failed to send data to the webhook. Status code: {response.status_code}")
        else:
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": ""} 
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})

    return  

