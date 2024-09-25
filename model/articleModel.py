from core.database import Base
from sqlalchemy import Boolean, Column, Integer, String,DateTime, func, Text

class CategoryModel(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255))
    category_slug = Column(String(255))
    category_order = Column(Integer)
    is_enabled = Column(Boolean)

class SubcategoryModel(Base):
    __tablename__ = "subcategory"
    subcategory_id = Column(Integer, primary_key=True, index=True)
    subcategory_name = Column(String(255))
    category_id = Column(Integer)
    category_name = Column(String(100))
    subcategory_slug = Column(String(255))
    subcategory_order = Column(Integer)
    is_enabled = Column(Boolean)

class TagModel(Base):
    __tablename__ = "tag"
    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(100)) # will be unique
    tag_slug = Column(String(100))

class ArticleModel(Base):
    __tablename__ = "article"
    article_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    email = Column(String(255))
    category_id = Column(Integer)
    subcategory_id = Column(Integer)
    title_en = Column(Text)
    title_bn = Column(Text)
    subtitle_en = Column(Text)
    subtitle_bn = Column(Text)
    content_en = Column(Text)
    content_bn = Column(Text)
    article_status = Column(String(100)) # under_review_new / under_review_resubmit / rejected / published / hidden
    # submitted_at = Column(DateTime, nullable=True)
    # updated_at = Column(DateTime, nullable=True)
    article_slug = Column(String(255))
    tags = Column(String)

class ArticleTagModel(Base):
    __tablename__ = "article_tag"
    article_tag_id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer)
    tag_name = Column(String)
    article_id_list = Column(String) # List of article ids = "[1,2,3]"
    # Example Query: "Select article_id_list from article_tag where tag_name == "tag_name" "

class ArticleSubmissionModel(Base):
    __tablename__ = "article_submission"
    submission_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer)
    author_id = Column(Integer)
    author_email = Column(String(255))
    editor_id = Column(Integer)
    editor_email = Column(String(255))
    article_status = Column(String(100)) # under_review /  under_review_resubmit / rejected / published / hidden
    submitted_at = Column(DateTime, nullable=True)
    
    decision_comment = Column(String)
    decision_comment_at = Column(DateTime, nullable=True)
    sent_for_edit_at = Column(DateTime, nullable=True) # editor sent for edits to author
    resubmitted_at = Column(DateTime, nullable=True) # author resubmit with edits

    published_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    hidden_at = Column(DateTime, nullable=True)












