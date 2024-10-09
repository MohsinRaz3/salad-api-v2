import os
import json
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
from typing import Generator
from fastapi.responses import StreamingResponse, JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Pydantic model for request data
class ChatRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False
    # Include other necessary fields as per the OpenAI API

# Function to generate streaming responses
def generate_streaming_response(data) -> Generator:
    for message in data:
        json_data = message.model_dump_json()
        logger.info(f"JSON data: {json.dumps(json_data, indent=2)}")
        yield f"data: {json_data}\n\n"


@app.post("/chat/completions")
async def openai_advanced_custom_llm_route(request_data: ChatRequest):
    # Convert Pydantic model to dictionary
    request_dict = request_data.dict()

    # Log the request data
    logger.info(f"Request data: {json.dumps(request_dict, indent=2)}")
    
    # Get the 'stream' flag from the request, default to False if not provided
    streaming = request_dict.get('stream', False)
    
    # Remove fields 'call' and 'metadata' from the request (if present)
    request_dict.pop('call', None)
    request_dict.pop('metadata', None)
    
    try:
        if streaming:
            # Call OpenAI API with streaming enabled
            chat_completion_stream = client.chat.completions.create(**request_dict)

            return StreamingResponse(
                generate_streaming_response(chat_completion_stream),
                media_type='text/event-stream'
            )
        else:
            # Non-streaming API call
            chat_completion = client.chat.completions.create(**request_dict)
            return JSONResponse(content=chat_completion.model_dump_json())

    except Exception as e:
        logger.error(f"Error in OpenAI API call: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

