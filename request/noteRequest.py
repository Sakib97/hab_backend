from pydantic import BaseModel

class NewNoteRequest(BaseModel):
    subject_name: str 
    message_text: str