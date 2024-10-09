import os
import json
import logging
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from openai import OpenAI
from typing import Generator
from fastapi.responses import StreamingResponse, JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False

def generate_streaming_response(data) -> Generator:
    for message in data:
        json_data = message.model_dump_json()
        logger.info(f"JSON data: {json.dumps(json_data, indent=2)}")
        yield f"data: {json_data}\n\n"


async def openai_advanced_custom_llm_route(request: Request):
    request_data = await request.json()

    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")

    streaming = request_data.get('stream', False)

    request_data.pop('call', None)
    request_data.pop('metadata', None)

    try:
        if streaming:
            chat_completion_stream = client.chat.completions.create(**request_data)

            return StreamingResponse(
                generate_streaming_response(chat_completion_stream),
                media_type='text/event-stream'
            )
        else:
            chat_completion = client.chat.completions.create(**request_data)
            return JSONResponse(content=chat_completion.model_dump_json())

    except Exception as e:
        logger.error(f"Error in OpenAI API call: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

