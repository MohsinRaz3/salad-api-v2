


import os
from fastapi import HTTPException
import requests

from main import get_job, upload_b2_storage


async def rocket_prose(file):
    try:
        # Upload file to B2 storage
        b2_file_url = await upload_b2_storage(file)

        organization_name =  os.getenv('ORGANIZATION_NAME')
        url = f"https://api.salad.com/api/public/organizations/{organization_name}/inference-endpoints/transcribe/jobs"
        salad_key = os.getenv('SALAD_KEY')
        language_code = "en"
        list_of_audio_files = [b2_file_url]

        list_of_job_ids = []
        headers = {
            "Salad-Api-Key": salad_key,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        for audio_file in list_of_audio_files:
            data = {
                "input": {
                    "url": audio_file,
                    "language_code": language_code,
                    "word_level_timestamps": True,
                    "diarization": True,
                    "srt": True,
                }
            }
            response = requests.post(url, headers=headers, json=data)
            
            #response.raise_for_status()
            job_id = response.json()["id"]

            list_of_job_ids.append(job_id)
            get_transcription = await get_job(job_id)
            if get_transcription:                
                output_data = {"transcript" : get_transcription['output']['text']}
                return output_data     
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
