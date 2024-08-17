import asyncio
import pprint
import time
import random
import httpx
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import json

# #============================ Google-search ==================================#

# def search_query(query: str):
#     result = search(query, num_results=1)
#     print(result)
#     return result
#     # url_res = []

#     # for url in result:
#     #     url_res.append(url)
#     #     time.sleep(random.uniform(3, 7))  # Introduce a delay between requests 
#     #     print(url_res)
#     # return url_res
# search_query("mental health issue")
# #============================= ScrapeOwl ========================================#

# # def scrapeowl_website(query:str): 
# #     url_data = search_query(query)

# #     scrapeowl_url = "https://api.scrapeowl.com/v1/scrape"
# #     object_of_data = {
# #         "api_key": "cc06829ee3d999aeef99bbd82fdf65",  
# #         "url": url_data,
# #         "elements": [
# #             {
# #                 "type": "css",
# #                 "selector": "title"
# #             },
# #             {
# #                 "type": "css",
# #                 "selector": "h1"
# #             },
# #             {
# #                 "type": "css",
# #                 "selector": "p"
# #             }
# #         ],
# #         "json_response": False 
# #     }

# #     headers = {
# #         "Content-Type": "application/json"
# #     }
# #     response = requests.post(scrapeowl_url, json=object_of_data, headers=headers)

# #     if response.status_code == 200:
# #         raw_html = response.text
# #         soup = BeautifulSoup(raw_html, 'html.parser')

# #         title = soup.title.string if soup.title else "No title found"
# #         h1_tags = [h1.get_text() for h1 in soup.find_all('h1')]
# #         blog_content = [p.get_text() for p in soup.find_all('p')]

# #         print("Title of the page:\n", title)
# #         print("\nFirst <h1> tag(s):\n", h1_tags if h1_tags else "No <h1> tags found")
# #         print("\nParagraphs:\n", blog_content if blog_content else "No <p> tags found")
# #         return {"title" : f"{title} {h1_tags}", "blog_data" : {blog_content}}
    
# #     else:
# #         print(f"Failed to scrape the website. Status code: {response.status_code}")
# #         return response.status_code

# # scrapeowl_website("mental health issue")

#========================================= VERSION 2 ================================#

# from googlesearch import search
# import time
# import random
# import requests
# from bs4 import BeautifulSoup

# SCRAPEOWL_API_KEY = 'cc06829ee3d999aeef99bbd82fdf65'  
# SCRAPEOWL_URL = 'https://api.scrapeowl.com/v1/scrape'

# def search_query(query: str):
#     urls = []

#     for url in search(query,sleep_interval=3, num_results=2):
#         urls.append(url)
#         time.sleep(random.uniform(3, 7)) 
#         print(f"Found URL: {url}")
    
#     return urls

# def scrape_website(urls):
#     for url in urls:
#         payload = {
#             'api_key': SCRAPEOWL_API_KEY,
#             'url': url,
#             'elements': [
#                 {
#                     "type": "css",
#                     "selector": "title"
#                 },
#                 {
#                     "type": "css",
#                     "selector": "h1"
#                 },
#                 {
#                     "type": "css",
#                     "selector": "p"
#                 }
#             ],
#             "premium_proxies": True,
# 	        "country": "us",
#             'json_response': False  
#         }
#         headers = {
#   "Content-Type": "application/json"
# }
        
#         response = requests.post(SCRAPEOWL_URL, json=payload,headers=headers )
        
#         if response.status_code == 200:
#             raw_html = response.text
            
#             soup = BeautifulSoup(raw_html, 'html.parser')
            
#             title = soup.title.string if soup.title else "No title found"
            
#             h1_tags = [h1.get_text() for h1 in soup.find_all('h1')]
            
#             blog_content = [p.get_text() for p in soup.find_all('p')]
            
#             print(f"\nTitle from {url}: {title}")
#             print(f"H1 tags from {url}: {h1_tags}")
#             print(f"Paragraphs from {url}: {blog_content}")
#         else:
#             print(f"Failed to scrape {url}. Status code: {response.status_code}")
        
#         scrape_delay = random.uniform(3, 7) 
#         time.sleep(scrape_delay)

# # Run the functions
# urls = search_query("medical health issue")
# scrape_website(urls)
#================================= above code is almost correct ====================================#
import time
import random
import httpx  # Replaced requests with httpx for async support
from bs4 import BeautifulSoup
from googlesearch import search
import json

SCRAPEOWL_API_KEY = '6c47a592eedd52d14eb58158c5cdde'  
SCRAPEOWL_URL = 'https://api.scrapeowl.com/v1/scrape'
MAX_RETRIES = 5  # Number of retries
FIXED_DELAY = 10 

async def search_query(query: str):
    urls = []

    # Perform the Google search
    for url in search(query, lang="en", sleep_interval=3, num_results=7):
        urls.append(url)
        time.sleep(random.uniform(3, 7)) 
        print(f"Found URL: {url}")
    
    return urls


async def scrape_website(query: str):
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
                    response.raise_for_status()  # Raises an error for bad status codes
                    
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

                    break  # Exit retry loop on success

                except httpx.HTTPStatusError as http_err:
                    print(f"HTTP error occurred for {url}: {http_err}")
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {FIXED_DELAY} seconds...")
                        await asyncio.sleep(FIXED_DELAY)  # Fixed delay before retrying
                    else:
                        print(f"Failed to scrape {url} after {MAX_RETRIES} attempts.")
                        break
                except Exception as err:
                    print(f"An error occurred for {url}: {err}")
                    break

        if result:    
            # Sending the data to a webhook
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": result}  # Wrap the list in a dictionary
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                print("Data successfully sent to the webhook.")
            else:
                print(f"Failed to send data to the webhook. Status code: {response.status_code}")
        else:
            print("No data to send!")
            wh_url = "https://cloud.activepieces.com/api/v1/webhooks/0AbBBSdtEkxdADBfR1hdO"
            data = {"blog_data": ""}  # Wrap the list in a dictionary
            response = await client.post(wh_url, json=data, headers={"Content-Type": "application/json"})

    return result 


# Run the functions
# asyncio.run(scrape_website("how to create custom gpts"))
#===============================================================================#
