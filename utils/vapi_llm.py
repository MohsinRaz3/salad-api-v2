from dotenv import load_dotenv
import httpx
import os

load_dotenv()
bearer_token = os.getenv('VAPI_BEARER_TOKEN')
headers = {
    "Authorization": f"Bearer {bearer_token}"
}
url = "https://api.vapi.ai/call"

def get_vapi_data(call_id:str):
    with httpx.Client() as client:
        response = client.get(f"{url}/{call_id}", headers=headers)
        text = response.text
        print(text)

