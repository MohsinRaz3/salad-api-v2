from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
load_dotenv()

async def serp_keyword(text_keywords:str)->str:
  keywords = [text_keywords]

  for keyword in keywords:
      params = {
          "engine": "google",
          "q": keyword,
          "hl": "en",
          "google_domain": "google.com",
          "num": "5",
          "start": "10",
          "safe": "active",
          "api_key": os.getenv("SERP_API_KEY")
      }

      search = GoogleSearch(params)
      results = search.get_dict()
      organic_results = results.get("organic_results", [])

      for result in organic_results:
          title = result.get("title", "No title available")
          print(title)
          return {"seo_output": title}