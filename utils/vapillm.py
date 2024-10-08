from fastapi.responses import JSONResponse
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


async def vapi_chat_completion(request):
    """vapi response"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are an helpful assistant",
                },
                {"role": "user", "content": request}
            ]
        )

        res = completion.choices[0].message.content
        return res

    except Exception as e:
        return {"error": str(e)}
    