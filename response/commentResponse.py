from pydantic import BaseModel
from typing import Any

class CommentListResponse(BaseModel):
    article_id: int 
    comment_id: int
    user_slug: str
    user_name: str
    user_image_url: str
    parent_comment_id: int | None
    comment_text: str
    created_at: str
    is_hidden: bool
    comment_reaction_count: Any
    # comment_replies: list['CommentListResponse'] | None = None

    class Config():
        from_attributes = True