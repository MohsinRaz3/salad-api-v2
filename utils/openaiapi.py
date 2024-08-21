from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

async def user_response(user_input):
    completion = client.chat.completions.create(
    model="gpt-4o-mini-2024-07-18",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Extract the 5 keywords from the user text input that could help search engine to find helpful resource relevant to user input. only provide me text response no numerical values"},
        {"role": "user", "content": user_input}
    ]
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

#user_response("Instagram Is Really Weird Right Now. I Think I've Figured Out Why.")