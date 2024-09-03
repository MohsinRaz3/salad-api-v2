import os
import uuid
import io
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from b2sdk.v2 import InMemoryAccountInfo, B2Api
import asyncio
from fastapi import HTTPException

from utils.openaiapi import create_podcast_script, show_notes
from utils.salad_transcription import salad_transcription_api

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

async def text_to_speech_file(text: str) -> io.BytesIO:
    response = client.text_to_speech.convert(
        voice_id=os.getenv("VOICE_ID"),  # Dan's voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",  # Use the turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=False,
        ),
    )

    audio_data = io.BytesIO()
    for chunk in response:
        if chunk:
            audio_data.write(chunk)
    audio_data.seek(0)  # Rewind the file pointer to the beginning of the BytesIO object
    return audio_data

async def upload_b2_storage(audio_data: io.BytesIO, file_name: str, content_type: str):
    APPLICATION_KEY_ID = os.getenv('APPLICATION_KEY_ID')
    APPLICATION_KEY = os.getenv('APPLICATION_KEY')
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account('production', APPLICATION_KEY_ID, APPLICATION_KEY)

        bucket_name = os.getenv('BUCKET_NAME')
        bucket = b2_api.get_bucket_by_name(bucket_name)

        # Upload file content to B2 storage
        bucket.upload_bytes(
            audio_data.getvalue(),
            file_name,
            content_type=content_type
        )

        salad_url = os.getenv('SALAD_URL')
        file_url = f"{salad_url}/{file_name}"
        return file_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
    


async def call_bucket(audio_link):
    """ Takes Typebot audio link; returns Show Notes and Dan's cloned voice Podcast .mp3 Link"""
    transcript = await salad_transcription_api(audio_link=audio_link)
    #### Show_Notes ####
    podcast_show_notes = await show_notes(transcript=transcript)
    
    #### Posdcast_Script_text #####
    created_posdcast_script = await create_podcast_script(transcript=transcript)

    audio_data = await text_to_speech_file(created_posdcast_script)
    file_name = f"RT{uuid.uuid4()}.mp3"
    file_url = await upload_b2_storage(audio_data, file_name, content_type="audio/mpeg")
    print(f"File uploaded to: {file_url}")

    return {"audio_link":file_url, "show_notes":podcast_show_notes}
# asyncio.run(call_bucket())