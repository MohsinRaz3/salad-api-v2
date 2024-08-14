import httpx
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# Define a Pydantic model for the response
class SEOOutput(BaseModel):
    seo_output: List[str]

@app.get("/search/")
async def serp_keyword(text_keywords: str):
    keywords = [text_keywords]
    titles = []

    for keyword in keywords:
        params = {
            "engine": "google",
            "q": keyword,
            "hl": "en",
            "google_domain": "google.com",
            "num": "10",  # Get top 10 results
            "start": "0",
            "safe": "active",
            "api_key": os.getenv("SERP_API_KEY")
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])

        # Collect up to 5 titles from the top 10 results
        for result in organic_results[:5]:
            title = result.get("title", "No title available")
            titles.append(title)
    
    # Use httpx for asynchronous requests
    async with httpx.AsyncClient() as client:
        url = "https://cloud.activepieces.com/api/v1/webhooks/rGPVtIDZ58aEuf1sVDWuw"
        headers = {"Content-Type": "application/json"}
        data = {"titles": titles}  # Wrap the list in a dictionary
        response = await client.post(url, json=data, headers=headers)
    
    return response.json()
