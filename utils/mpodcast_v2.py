import json
import uuid
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils.get_voices_id import get_voice_id_by_name
from utils.mpodcast import text_to_speech_file, upload_b2_storage
from utils.salad_transcription import salad_transcription_api

client = OpenAI()
load_dotenv()

async def mp_whook_v2(output_data):
     ap_webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/LyZ4Jk6xYubFWhBcGPw82"
     res = requests.post(ap_webhook_url, data=json.dumps(output_data),headers={'Content-Type': 'application/json'})
     return "success"
 


async def show_notes_v2(transcript_value, show_notes_prompt):
    """Show notes of Micro Podcast v2"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": show_notes_prompt,
                },
                {"role": "user", "content": transcript_value}
            ]
        )

        res = completion.choices[0].message.content
        return res

    except Exception as e:
        #print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}
    
    
async def create_podcast_script_v2(transcript_value,podcast_script_prompt):
    #"""Create script for Micro Podcast v2"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": podcast_script_prompt
                },
                {"role": "user", "content": transcript_value }
            ]
        )
        res =  completion.choices[0].message.content
        return res
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

  


async def call_bucket_v2(user_name,podcast_email, voice_name,audio_link,show_notes_prompt, podcast_script_prompt):
    """ Takes Typebot audio link; returns Show Notes and Dan's cloned voice Podcast .mp3 Link"""
    transcript_data = await salad_transcription_api(audio_link=audio_link)
    
    transcript_value = transcript_data['transcript']
    
    #### Show_Notes ####
    podcast_show_notes_v2 = await show_notes_v2(transcript_value,show_notes_prompt)
    
    #### Posdcast_Script_text #####
    created_posdcast_script_v2 = await create_podcast_script_v2(transcript_value,podcast_script_prompt)
    
    voice_id =  get_voice_id_by_name(voice_name)
    audio_data = await text_to_speech_file(created_posdcast_script_v2,voice_id=voice_id)
    file_name = f"RT{uuid.uuid4()}.mp3"
    
    file_url = await upload_b2_storage(audio_data, file_name, content_type="audio/mpeg")
    output_data = {"audio_link":file_url, "show_notes":podcast_show_notes_v2, "user_name": user_name, "podcast_email": podcast_email}
    await mp_whook_v2(output_data)
    return output_data

async def call_bucket_text_v2(user_name,podcast_email,voice_name,podcast_text,show_notes_prompt, podcast_script_prompt):
    """ Takes Typebot podcast text; returns Show Notes and Dan's cloned voice Podcast .mp3 Link"""
    transcript_value = podcast_text
    
    #### Show_Notes ####
    podcast_show_notes_v2 = await show_notes_v2(transcript_value,show_notes_prompt)
    
    #### Posdcast_Script_text #####
    created_posdcast_script_v2 = await create_podcast_script_v2(transcript_value,podcast_script_prompt)
    
    voice_id = get_voice_id_by_name(voice_name)

    audio_data = await text_to_speech_file(created_posdcast_script_v2,voice_id=voice_id)
    file_name = f"RT{uuid.uuid4()}.mp3"
    file_url = await upload_b2_storage(audio_data, file_name, content_type="audio/mpeg")

    output_data = {"audio_link":file_url, "show_notes":podcast_show_notes_v2,  "user_name": user_name, "podcast_email": podcast_email}
    await mp_whook_v2(output_data)
    return output_data

