from pydantic import BaseModel

class ReactionRequest(BaseModel):
    content_id: int
    reaction_type: str