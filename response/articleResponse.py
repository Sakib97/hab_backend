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
    def __init__(self, article_id: int, author_email: str, editor_email: str, article_status: str,
                 submitted_at: str, decision_comment: str, decision_comment_at: str,
                 sent_for_edit_at: str, resubmitted_at: str, category_id: int, subcategory_id: int,
                 title_en: str, title_bn: str, subtitle_en: str, subtitle_bn: str, 
                 content_en: str, content_bn: str, tags: str, cover_img_link: str, 
                 cover_img_cap_en: str, cover_img_cap_bn: str):
        self.article_id = article_id
        self.author_email = author_email
        self.editor_email = editor_email
        self.article_status = article_status
        self.submitted_at = submitted_at
        self.decision_comment = decision_comment
        self.decision_comment_at = decision_comment_at
        self.sent_for_edit_at = sent_for_edit_at
        self.resubmitted_at = resubmitted_at
        self.category_id = category_id
        self.subcategory_id = subcategory_id
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

    def __repr__(self):
        return f"UnrevArticleResponse(article_id={self.article_id}, title_en={self.title_en}, author_email={self.author_email})"