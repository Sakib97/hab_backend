from pydantic import BaseModel

# class UnrevArticleResponse():
#     article_id: int 
#     author_email: str 
#     editor_email: str 
#     article_status: str 
#     submitted_at: str 
#     decision_comment: str 
#     decision_comment_at: str 
#     sent_for_edit_at: str 
#     resubmitted_at: str 

#     category_id: int
#     subcategory_id: int
#     title_en: str
#     title_bn: str
#     subtitle_en: str
#     subtitle_bn: str
#     content_en: str
#     content_bn: str
#     tags: str 
#     cover_img_link: str 
#     cover_img_cap_en: str 
#     cover_img_cap_bn: str 

#     # class Config():
#     #     orm_mode = True

class UnrevArticleResponse:
    def __init__(self, article_id: int, author_email: str, author_firstname:str, author_lastname:str,
                 author_image_url: str, editor_email: str, article_status: str,
                 submitted_at: str, decision_comment: str, decision_comment_at: str,
                 sent_for_edit_at: str, resubmitted_at: str, 
                 category_id: int, subcategory_id: int, category_name: str, subcategory_name: str,
                 title_en: str, title_bn: str, subtitle_en: str, subtitle_bn: str, 
                 content_en: str, content_bn: str, tags: str, cover_img_link: str, 
                 cover_img_cap_en: str, cover_img_cap_bn: str, status: str):
        self.article_id = article_id
        self.author_email = author_email
        self.author_firstname = author_firstname
        self.author_lastname = author_lastname 
        self.author_image_url = author_image_url

        self.editor_email = editor_email
        self.article_status = article_status
        self.submitted_at = submitted_at
        self.decision_comment = decision_comment
        self.decision_comment_at = decision_comment_at
        self.sent_for_edit_at = sent_for_edit_at
        self.resubmitted_at = resubmitted_at

        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.category_name = category_name,
        self.subcategory_name = subcategory_name,

        self.title_en = title_en
        self.title_bn = title_bn
        self.subtitle_en = subtitle_en
        self.subtitle_bn = subtitle_bn
        self.content_en = content_en
        self.content_bn = content_bn
        self.tags = tags
        self.cover_img_link = cover_img_link
        self.cover_img_cap_en = cover_img_cap_en
        self.cover_img_cap_bn = cover_img_cap_bn

        self.status = status
    def __repr__(self):
        return f"UnrevArticleResponse(article_id={self.article_id}, title_en={self.title_en}, author_email={self.author_email})"
    
class ApprovedArticleResponse(BaseModel):
    # author_email: str 
    author_slug: str 
    author_firstname: str
    author_lastname: str
    author_image_url: str
    published_at: str 

    category_name: str
    subcategory_name: str
    title_en: str
    title_bn: str
    subtitle_en: str
    subtitle_bn: str
    content_en: str
    content_bn: str

    tags: str 
    cover_img_link: str 
    cover_img_cap_en: str 
    cover_img_cap_bn: str

    class Config():
        from_attributes = True
    
class HistoryArticleForListResponse(BaseModel):
    article_id: int 
    submitted_at: str
    title_en: str
    subtitle_en: str
    cover_img_link: str 
    article_status: str

    category_name: str
    subcategory_name: str

    class Config():
        from_attributes = True

class HistoryArticleDetailsResponse(BaseModel):
    article_id: int 
    title_en: str
    subtitle_en: str
    category_name: str
    subcategory_name: str
    article_status: str

    # editor_email: str
    editor_slug: str
    editor_firstname: str
    editor_lastname: str
    
    submitted_at: str
    published_at: str
    rejected_at: str
    decision_comment: str

    sent_for_edit_at: str
    resubmitted_at: str
    
    class Config():
        from_attributes = True