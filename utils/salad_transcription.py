import os
from dotenv import load_dotenv
import requests
import time
import json
import httpx
from fastapi import HTTPException
import asyncio
load_dotenv()



async def pabbly_whook(output_data):
     ap_webhook_url = ""
     res = requests.post(ap_webhook_url, data=json.dumps(output_data),headers={'Content-Type': 'application/json'})
     return "success"
 
async def get_job(job_id):
    organisation_name = os.getenv('ORGANIZATION_NAME')
    salad_key = os.getenv('SALAD_KEY')    
    headers = {
        "Salad-Api-Key": salad_key
    }
    url = f"https://api.salad.com/api/public/organizations/{organisation_name}/inference-endpoints/transcribe/jobs/{job_id}"
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            res_json = response.json()  # Not await, since it's not an async call
            
            if res_json["status"] == "succeeded":
                if "output" in res_json and "text" in res_json["output"]:
                    return res_json
                else:
                    raise ValueError("Response is missing 'text' in 'output'")
            else:
                time.sleep(3)
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            break


async def salad_transcription_api(audio_link):
    try:
        organization_name =  os.getenv('ORGANIZATION_NAME')
        url = f"https://api.salad.com/api/public/organizations/{organization_name}/inference-endpoints/transcribe/jobs"
        salad_key = os.getenv('SALAD_KEY')
        language_code = "en"

        headers = {
            "Salad-Api-Key": salad_key,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        data = {
            "input": {
                "url": audio_link,
                "language_code": language_code,
                "word_level_timestamps": True,
                "diarization": False,
                "srt": False,
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        job_id = response.json().get("id")
        if not job_id:
            raise ValueError("Job ID not returned by the API.")
        
        get_transcription = await get_job(job_id)
        if get_transcription and "output" in get_transcription and "text" in get_transcription["output"]:
            output_data = {"transcript" : get_transcription['output']['text']}
            return output_data
        else:
            raise ValueError("The transcription output is missing the 'text' field.")
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"ValueError: {ve}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
