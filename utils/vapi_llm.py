from dotenv import load_dotenv
import asyncio 
import httpx
import os

load_dotenv()

bearer_token = os.getenv('VAPI_BEARER_TOKEN')
headers = {
    "Authorization": f"Bearer {bearer_token}"
}
url = "https://api.vapi.ai/call"

async def get_vapi_data(call_id: str):
    async with httpx.AsyncClient() as client:
        await asyncio.sleep(60)  
        
        response = await client.get(f"{url}/{call_id}", headers=headers)
        
        text = response.json()
        print(text)
