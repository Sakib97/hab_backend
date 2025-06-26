from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String,DateTime, func, Text

class CreateArticleReactionRequest(BaseModel):
    article_id: int
    reaction: str  # e.g., "like", "dislike", "love", "laugh", etc.
    react_place: str  # e.g., "article" or "comment"