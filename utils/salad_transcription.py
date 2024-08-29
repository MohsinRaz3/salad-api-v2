import os
from dotenv import load_dotenv
import requests
import time
import json
from fastapi import HTTPException
load_dotenv()



async def pabbly_whook(output_data):
     ap_webhook_url = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY0MDYzZTA0Mzc1MjZhNTUzMjUxM2Ii_pc"
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
            res_json = response.json()
            
            if res_json["status"] == "succeeded":
                return res_json
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
        #list_of_audio_files = [audio_link]

        list_of_job_ids = []
        headers = {
            "Salad-Api-Key": salad_key,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        # for audio_file in list_of_audio_files:
        #     print("audio file", audio_file)
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
        
        #response.raise_for_status()
        job_id = response.json()["id"]
        #print("here is job id",job_id)

        list_of_job_ids.append(job_id)
        get_transcription = await get_job(job_id)
        if get_transcription:                
            output_data = {"transcript" : get_transcription['output']['text']}
            await pabbly_whook(output_data)
            #print("data sent to pabbly")
            return output_data     
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

