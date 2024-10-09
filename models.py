from typing import Any, Tuple, Optional
from pydantic import BaseModel, validator, Field

class FileWrapper(BaseModel):
    file: Tuple[str, bytes, str] = Field(..., description="A tuple containing filename, file content, and MIME type")

    @validator('file')
    def check_file_tuple(cls, value):
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError('file must be a tuple with exactly three elements')
        
        filename, file_content, mime_type = value
        
        if not isinstance(filename, str):
            raise ValueError('filename must be a string')
        
        if not isinstance(file_content, bytes):
            raise ValueError('file_content must be bytes')
        
        if not isinstance(mime_type, str):
            raise ValueError('mime_type must be a string')
        
        return value


class AudioLink(BaseModel):
    audio_link: str
    

class PodcastData(BaseModel):
    user_name: Optional[str] = None
    podcast_email: Optional[str] = None
    voice_name: str
    audio_link: str
    show_notes_prompt: str
    podcast_script_prompt: str    
    
    
class PodcastTextData(BaseModel):
    user_name: Optional[str] = None
    podcast_email: Optional[str] = None
    voice_name: str
    podcast_text: str
    show_notes_prompt: str
    podcast_script_prompt: str 

class TextData(BaseModel):
    text_data: str
    
class ChatRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False
    