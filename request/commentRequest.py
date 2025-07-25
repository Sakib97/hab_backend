from pydantic import BaseModel

class ReactionRequest(BaseModel):
    content_id: int
    reaction_type: str

class PostCommentRequest(BaseModel):
    comment_text: str
    parent_comment_id: str = None  # Optional, for nested comments
