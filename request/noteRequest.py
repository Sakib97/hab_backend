from pydantic import BaseModel

class NewNoteRequest(BaseModel):
    subject_name: str 
    message_text: str

class NewNoteToSubjectRequest(BaseModel):
    message_text: str