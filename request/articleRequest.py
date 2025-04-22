from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String,DateTime, func, Text

class CreateArticleRequest(BaseModel):
    category_id: int
    subcategory_id: int
    title_en: str
    title_bn: str
    subtitle_en: str
    subtitle_bn: str
    content_en: str
    content_bn: str
    cover_img_link: str
    cover_img_cap_en: str
    cover_img_cap_bn: str
    tags: str # ex: "['tag1', 'tag2']"
    new_tag: str # ex: "['new_tag1', 'new_tag2']"

class AddTagToArticleRequest(BaseModel):
    article_id: int
    tag_name: str # ex: "['new_tag']"

class ApproveArticleRequest(BaseModel):
    article_id: int
    decision_comment: str
