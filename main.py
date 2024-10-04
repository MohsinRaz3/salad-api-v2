import os
import time
import requests, json
import fal_client
from fastapi import Body, FastAPI, File, Query, UploadFile, HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv
from models import AudioLink, PodcastData, PodcastTextData
from utils.mpodcast import call_bucket
from utils.mpodcast_v2 import call_bucket_text_v2, call_bucket_v2
from utils.salad_transcription import salad_transcription_api
from utils.search import scrape_website
import httpx

load_dotenv()
app = FastAPI(
    title="RocketTools",
    description="RocketTools' AI",
    docs_url="/docs",
    version="v1",
)

# origins = [
    
#     "https://typebot.co/mohsinraz",
#     "https://salad-api-v2-zrui.onrender.com",
#     "https://salad-api-v2-zrui.onrender.com/",
#     "https://salad-api-v2-zrui.onrender.com/transcribe"
#     "https://rocket-tools.netlify.app/",
#     "https://rocket-tools.netlify.app",
#     "https://api.scrapeowl.com/v1/scrape",
#     "https://api.scrapeowl.com/",
#     "https://cloud.activepieces.com/api/v1/webhooks/VKcq0ji9g6BItj59d9h1l",
#     "https://cloud.activepieces.com/"
#     "https://salad-api.vercel.app/",
#     "https://salad-api.vercel.app/transcribe",
#     "https://salad-api.vercel.app",
#     "http://localhost:3000/",
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://127.0.0.1:8000/",
#     "http://localhost:3001/",
#     "http://localhost",
#     "http://localhost:8000/",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     "http://127.0.0.1:3000/",
#     "http://localhost",
#     "http://localhost:8000",
#     "http://localhost:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
FAL_API_KEY = os.getenv('FAL_API')

async def img_webhook_ap(output_data):
     ap_webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/7SjaMFw5xjjRFJsHYi90S"
     res = requests.post(ap_webhook_url, data=json.dumps(output_data),headers={'Content-Type': 'application/json'})
     return 

async def webhook_ap(output_data):
     ap_webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/v1paRjoAYx8qek5kFJjuj"
     res = requests.post(ap_webhook_url, data=json.dumps(output_data),headers={'Content-Type': 'application/json'})
     return

async def submit(user_prompt: str):
    try:
        handler = await fal_client.submit_async(
            "fal-ai/flux-pro/v1.1",
            arguments={"prompt": user_prompt},
        )

        log_index = 0
        async for event in handler.iter_events(with_logs=True):
            if isinstance(event, fal_client.InProgress):
                new_logs = event.logs[log_index:]
                for log in new_logs:
                    print(log["message"])
                log_index = len(event.logs)

        result = await handler.get()
        if 'images' not in result or not result['images']:
            raise HTTPException(status_code=500, detail="No images returned from the API")

        return {"image_url": result['images'][0]['url']}
    
    except fal_client.FalClientError:
        raise HTTPException(status_code=500, detail="Failed to communicate with the image generation service")
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

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
    return {"message": "RocketTools Home!"}

@app.post("/scrapeowl", tags=["Scrapping"])
async def serpapi_keyword( background_tasks:BackgroundTasks, query: str = Body(..., embed=True)):
    """Turns query into keywords, searches and create blogs"""
    try:  
        print("User query:", query)
        background_tasks.add_task(scrape_website, query)
        return {"message": "scraping has begun."}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post("/prompt/{user_prompt}", tags=["Fluxai"])
async def image_prompt(user_prompt:str):
    """Turn text into Fluxai Image, sends to APs"""
    try:
        img_url = await submit(user_prompt) 
        await img_webhook_ap(img_url)
        return {"image_url": img_url}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post("/flux_prompt/{user_prompt}", tags=["Fluxai"])
async def flux_typebot(user_prompt:str):
    """Turn text into Fluxai Image only"""

    try:
        img_url = await submit(user_prompt) 
        return {"image_url": img_url}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@app.post("/salad_transcription/", tags=["Salad Trasncription API"])
async def salad_transcript(audio_link: AudioLink = Body(...)):
    """Turns audio file into text only"""
    #print(" Audio link", audio_link.audio_link)
    try:
        transcript = await salad_transcription_api(audio_link=audio_link.audio_link)
        #print("Transcript", transcript)
        return transcript
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@app.post("/micro_podcast/", tags=["Podcast"])
async def create_micro_podcast(background_tasks:BackgroundTasks, audio_link: AudioLink = Body(...)):
    """Takes audio file and creates audio podcast with shownotes, sends to AP"""

    try:
        background_tasks.add_task(call_bucket,audio_link.audio_link)
        return {"message": "success"}
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

  
@app.post("/micro_podcast_v2/", tags=["Podcast"])
async def create_micro_podcast_v2(podcast_data: PodcastData = Body(...))->dict:
    """Takes audio file and creates audio podcast with shownotes"""
    try: 
        result = await call_bucket_v2(
            podcast_data.user_name,
            podcast_data.podcast_email,
            podcast_data.voice_name,
            podcast_data.audio_link, 
            podcast_data.show_notes_prompt, 
            podcast_data.podcast_script_prompt
        )        
        return {"message": "success", "result": result}
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.post("/micro_podcast_text_v2/")
async def create_micro_podcast_text_v2(podcast_data: PodcastTextData = Body(...))->dict:
    """Takes Text and creates audio podcast with shownotes. sends AP"""

    try:
        result = await call_bucket_text_v2(
            podcast_data.user_name,
            podcast_data.podcast_email,
            podcast_data.voice_name,
            podcast_data.podcast_text, 
            podcast_data.show_notes_prompt, 
            podcast_data.podcast_script_prompt
        )    
        return {"message": "success", "result": result}
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/transcribe", tags=["Salad Trasncription API"])
async def transcribe_voice(file: UploadFile = File(...)):
    """Takes audio file and creates transcription, sends to AP"""

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
                await webhook_ap(output_data)
                return output_data     
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)