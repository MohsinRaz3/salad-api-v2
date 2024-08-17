# from googlesearch import search
# import time
# import random
# import requests

# def search_query(query: str):
#     result = search(query, num_results=1)
#     url_res = []

#     for url in result:
#         url_res.append(url)
#         time.sleep(random.uniform(3, 7))  # Introduce a delay between requests 
#     # print(url_res)
#     return url_res

# # search_query("mental health issue")


# SCRAPEOWL_API_KEY = 'cc06829ee3d999aeef99bbd82fdf65'
# SCRAPEOWL_URL = 'https://api.scrapeowl.com/v1/scrape'

# def scrape_website():
#     query = "mental health problem"
#     urls = search_query(query)
    
#     for url in urls:
#         payload = {
#             'api_key': SCRAPEOWL_API_KEY,
#             'url': url,
#             'elements': ['title'] 
#         }
        
#         response = requests.post(SCRAPEOWL_URL, json=payload)
#         if response.status_code == 200:
#             data = response.json()
#             title = data.get('title', 'No title found')
#             print(f"Title from {url}: {title}")
#         else:
#             print(f"Failed to scrape {url}. Status code: {response.status_code}")
        
#         scrape_delay = random.uniform(3, 7) 
#         time.sleep(scrape_delay)  
        
# scrape_website()
