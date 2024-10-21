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
webhook_url = "https://webhook.site/e0486713-535e-4976-96a8-efe58fb3ba30"

async def get_vapi_data(call_id: str):
    async with httpx.AsyncClient() as client:
        await asyncio.sleep(60)  
        
        response = await client.get(f"{url}/{call_id}", headers=headers)
        text = response.json()
        print("call id output-----",text)
        structured_vapi_data = text['analysis']['structuredData']
        send_data = await client.post(url=webhook_url,json=structured_vapi_data)
        print("send data-----",send_data)
