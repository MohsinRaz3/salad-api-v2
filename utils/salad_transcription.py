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
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                res_json = response.json()

            if res_json["status"] == "succeeded":
                return res_json
            else:
                await asyncio.sleep(3)  # Non-blocking sleep

        except httpx.RequestError as e:
            print(f"Error during request: {e}")
            break

async def salad_transcription_api(audio_link):
    try:
        organization_name = os.getenv('ORGANIZATION_NAME')
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
                "word_level_timestamps": False,
                "diarization": False,
                "srt": False,
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            job_id = response.json()["id"]

        get_transcription = await get_job(job_id)
        if get_transcription:
            #print("Word level Transcript timestamps", get_transcription)
            user_transcript = get_transcription.get('output', {}).get('text', '')
            output_data = {"transcript": user_transcript}
            #print("Transcript ", output_data)
            # await pabbly_whook(output_data)  # Uncomment if needed
            return output_data

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
