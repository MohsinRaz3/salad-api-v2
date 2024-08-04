import os
import time
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="RocketTools",
    description="RocketTools' voice rec",
    docs_url="/docs",
    version="v1",
)

origins = [
    "https://rocket-tools.netlify.app/",
    "https://rocket-tools.netlify.app",
    "https://salad-api.vercel.app/",
    "https://salad-api.vercel.app/transcribe",
    "https://salad-api.vercel.app",
    "http://localhost:3000/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000/",
    "http://localhost:3001/",
    "http://localhost",
    "http://localhost:8000/",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000/",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


async def upload_b2_storage(file: UploadFile):
    APPLICATION_KEY_ID = os.getenv('APPLICATION_KEY_ID')
    APPLICATION_KEY = os.getenv('APPLICATION_KEY')
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account('production', APPLICATION_KEY_ID, APPLICATION_KEY)

        bucket_name = os.getenv('BUCKET_NAME')
        bucket = b2_api.get_bucket_by_name(bucket_name)

        # Read file content into memory
        content = await file.read()
        file_name = file.filename

        # Upload file content to B2 storage
        bucket.upload_bytes(
            content,
            file_name,
            content_type=file.content_type
        )

        salad_url = os.getenv('SALAD_URL')
        file_url = f"{salad_url}/{file.filename}"
        return file_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")


@app.get("/")
async def home_notes():
    return {"message": "RocketTools root!"}

@app.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
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
            response.raise_for_status()
            job_id = response.json()["id"]

            list_of_job_ids.append(job_id)
            get_transcription = await get_job(job_id)
            if get_transcription:
                return get_transcription['output']['text']
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)