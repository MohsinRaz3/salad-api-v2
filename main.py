import os
import time
from typing import Any, Optional
import requests, json
import fal_client
from fastapi import Body, FastAPI, File, Form, Query, UploadFile, HTTPException,BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv
from models import AudioLink, PodcastData, PodcastTextData, ProseRequest, TextData
from utils.mpodcast import call_bucket
from utils.mpodcast_v2 import call_bucket_text_v2, call_bucket_v2, call_elevenlabs
from utils.openaiapi import transcription_prose
from utils.salad_transcription import salad_transcription_api
from utils.search import scrape_website
import httpx
from openai import OpenAI
from fastapi.responses import StreamingResponse, JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


load_dotenv()
app = FastAPI(
    title="RocketTools",
    description="RocketTools' AI",
    docs_url="/docs",
    version="v1",
)

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "OPTIONS":  # Allow OPTIONS requests to bypass rate limiting
        return await call_next(request)
    try:
        response = await call_next(request)
        return response
    except RateLimitExceeded as exc:
        return JSONResponse(
            status_code=429, content={"detail": str(exc.detail)}
        )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


origins = [
    "https://typebot.co",                      
    "https://api.scrapeowl.com",               
    "https://cloud.activepieces.com",          
    "https://www.rocketfusionsuite.io",        
    "https://rocketprose.vercel.app",          
    "https://rocketfomo.vercel.app",           
    "http://127.0.0.1:8000",                  
    "http://127.0.0.1:3000",                  
    "http://localhost:5173",
    "https://coolrocket.cc",
    "https://rocketfomo.coolrocket.cc",
    "https://rocketprose.coolrocket.cc"                  
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],             
)


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    """Uploads a file to Backblaze B2 storage"""
    APPLICATION_KEY_ID = os.getenv('APPLICATION_KEY_ID')
    APPLICATION_KEY = os.getenv('APPLICATION_KEY')
    

    if not APPLICATION_KEY_ID or not APPLICATION_KEY:
        raise HTTPException(status_code=500, detail="Internal server error: Missing credentials")
    
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account('production', APPLICATION_KEY_ID, APPLICATION_KEY)

        bucket_name = os.getenv('BUCKET_NAME')
        if not bucket_name:
            raise HTTPException(status_code=500, detail="Internal server error: Missing bucket name")

        bucket = b2_api.get_bucket_by_name(bucket_name)
        content = await file.read()
        file_name = file.filename

        bucket.upload_bytes(
            content,
            file_name,
            content_type=file.content_type
        )

        salad_url = os.getenv('SALAD_URL')
        if not salad_url:
            raise HTTPException(status_code=500, detail="Internal server error: Missing salad URL")

        file_url = f"{salad_url}/{file.filename}"
        return file_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

@app.get("/")
@limiter.limit("5/minute") 
async def home_notes(request: Request):
    return {"message": "RocketTools Home!"}

@app.post("/scrapeowl", tags=["Scrapping"])
@limiter.limit("5/minute")
async def serpapi_keyword(request: Request, background_tasks:BackgroundTasks, query: str = Body(..., embed=True)):
    """Turns query into keywords, searches and create blogs, sends to AP"""
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
@limiter.limit("5/minute")
async def image_prompt(request:Request, user_prompt:str):
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
@limiter.limit("5/minute") 
async def flux_typebot(request: Request,user_prompt:str):
    """Turn text into Fluxai Image only"""

    try:
        img_url = await submit(user_prompt) 
        return {"image_url": img_url}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@app.post("/salad_transcription/", tags=["Salad Trasncription API"])
@limiter.limit("5/minute") 
async def salad_transcript(request: Request,audio_link: AudioLink = Body(...)):
    """Turns audio file into text only"""
    try:
        transcript = await salad_transcription_api(audio_link=audio_link.audio_link)
        return transcript
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@app.post("/micro_podcast/", tags=["Podcast"])
@limiter.limit("5/minute") 
async def create_micro_podcast(request: Request,background_tasks:BackgroundTasks, audio_link: AudioLink = Body(...)):
    """Takes audio file and creates audio podcast with shownotes, sends to AP"""

    try:
        background_tasks.add_task(call_bucket,audio_link.audio_link)
        return {"message": "success"}
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

  
@app.post("/micro_podcast_v2/", tags=["Podcast"])
@limiter.limit("5/minute") 
async def create_micro_podcast_v2(request: Request,podcast_data: PodcastData = Body(...))->dict:
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


@app.post("/micro_podcast_text_v2/", tags=["Podcast"])
@limiter.limit("5/minute") 
async def create_micro_podcast_text_v2(request: Request,podcast_data: PodcastTextData = Body(...))->dict:
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

@app.post("/text_to_elevenlabs_voice/", tags=["Elevenlabs"])
@limiter.limit("5/minute") 
async def create_text_to_elevenlabs_voice(request: Request,text_data: TextData = Body(...))->dict:
    """Takes Text and creates audio """
    try:
        result = await call_elevenlabs(
            text_data.text_data
        )    
        return {"message": "success", "result": result}
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error during request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


PROMPT_INDEX_FILE = 'prompt_indices.json'
PATHWAYS_MESSAGES_FILE = 'pathways.json'

# Ensure the JSON file exists
if not os.path.exists(PROMPT_INDEX_FILE):
    with open(PROMPT_INDEX_FILE, 'w') as f:
        json.dump({}, f)

# Load the prompt messages
with open(PATHWAYS_MESSAGES_FILE, 'r') as f:
    prompt_messages = json.load(f)


def get_prompt_index(call_id, increment=True):
    with open(PROMPT_INDEX_FILE, 'r') as f:
        indices = json.load(f)

    index = indices.get(call_id, 0)

    if increment:
        indices[call_id] = index + 1 if index + 1 < len(prompt_messages) else 0

    with open(PROMPT_INDEX_FILE, 'w') as f:
        json.dump(indices, f)

    return index


def generate_streaming_response(data):
    """
    Generator function to simulate streaming data.
    """
    for message in data:
        json_data = message.model_dump_json()
        yield f"data: {json_data}\n\n"

@app.post("/chat/completions")
async def openai_advanced_custom_llm_route(request: Request):
    request_data = await request.json()

    next_prompt = ''
    call_id = request_data['call']['id']
    prompt_index = get_prompt_index(call_id, False)

    last_assistant_message = ''
    if 'messages' in request_data and len(request_data['messages']) >= 2:
        last_assistant_message = request_data['messages'][-2]

    last_message = request_data['messages'][-1]
    pathway_prompt = prompt_messages[prompt_index]

    # Check if there are specific conditions for classification
    if 'check' in pathway_prompt and pathway_prompt['check']:
        prompt = f"""
        You're an AI classifier. Your goal is to classify the following condition/instructions based on the last user message. 
        If the condition is met, you only answer with a lowercase 'yes', and if it was not met, you answer with a lowercase 'no' (No Markdown or punctuation).
        ----------
        Conditions/Instructions: {pathway_prompt['check']}"""

        if last_assistant_message:
            prompt_completion_messages = [
                {"role": "system", "content": prompt},
                {"role": "assistant", "content": last_assistant_message['content']},
                {"role": "user", "content": last_message['content']}
            ]
        else:
            prompt_completion_messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": last_message['content']}
            ]

        # OpenAI chat completion request
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=prompt_completion_messages,
            max_tokens=10,
            temperature=0.7
        )

        # Classify based on response
        if completion.choices[0].message.content == 'yes':
            prompt_index = get_prompt_index(call_id)
            next_prompt = pathway_prompt['next']
           
        else:
            next_prompt = pathway_prompt['error']
    else:
        # No conditions, proceed to the next state
        prompt_index = get_prompt_index(call_id)
        next_prompt = pathway_prompt['next']

    # Modify the request with new prompt
    modified_messages = [
        {"role": "system", "content": next_prompt},
        {"role": "user", "content": last_message['content']}
    ]

    request_data['messages'] = modified_messages

    # Clean up unnecessary fields from the request
    request_data.pop('call', None)
    request_data.pop('metadata', None)
    request_data.pop('phoneNumber', None)
    request_data.pop('customer', None)

    try:
        streaming = request_data.get('stream', False)

        # If streaming, handle response generation via streaming
        if streaming:
            chat_completion_stream = client.chat.completions.create(**request_data)
            print("chat_completion result", chat_completion_stream)

            return StreamingResponse(
                generate_streaming_response(chat_completion_stream),
                media_type='text/event-stream'
            )
        else:
            # Handle non-streaming response
            chat_completion = client.chat.completions.create(**request_data)
            print("chat_completion result", chat_completion.choices[0].message.content)
            return JSONResponse(content=chat_completion.model_dump_json())

    except Exception as e:
        # Handle errors
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    
@app.post("/rocketprose_openaiapi", tags=["Salad Trasncription API"])
@limiter.limit("5/minute") 
async def transcription_response(request: Request, proseData: ProseRequest = Body(..., embed=True)):
    try:
        print(f"transcribe value is '{proseData.transcribed_value}' and get text value '{proseData.text}'" )
        result = await transcription_prose(transcribed_value=proseData.transcribed_value,text=proseData.text)
        return result
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}

@app.post("/transcribe", tags=["Salad Trasncription API"])
@limiter.limit("5/minute") 
async def transcribe_voice(request: Request,file: UploadFile = File(...)):
    """Takes audio blob file and creates transcription, sends to AP"""

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


@app.post("/rocketprose_transcribe", tags=["Salad Trasncription API"])
@limiter.limit("5/minute") 
async def transcribe_rocketprose_voice(request: Request, file: UploadFile = File(...)):
    """Takes audio blob file and creates transcription only"""

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

