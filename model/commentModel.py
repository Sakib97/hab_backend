from core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

class ArticleReactionModel(Base):
    __tablename__ = "article_reaction"
    reaction_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer)  # Foreign key to ArticleModel
    user_email = Column(String(255))  # Email of the user who reacted
    user_slug = Column(String)  # Slug of the user who reacted
    reaction_type = Column(String)  # Type of reaction (like, dislike, etc.)
    created_at = Column(DateTime, nullable=True)

class CommentModel(Base):
    __tablename__ = "comment"
    comment_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer)  # Foreign key to ArticleModel 
    user_email = Column(String(255))  # Email of the user who commented
    user_slug = Column(String)  # Slug of the user who commented
    parent_comment_id = Column(Integer, nullable=True)  # ID of the parent comment if it's a reply
    comment_text = Column(Text)  # The text of the comment
    created_at = Column(DateTime, nullable=True)
    is_hidden = Column(Boolean, default=False)  # Whether the comment is hidden or not

class CommentReactionModel(Base):
    __tablename__ = "comment_reaction"
    reaction_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer)  # Foreign key to CommentModel
    user_email = Column(String(255))  # Email of the user who reacted
    user_slug = Column(String)  # Slug of the user who reacted
    reaction_type = Column(String)  # Type of reaction (like, dislike, etc.)
    created_at = Column(DateTime, nullable=True)

class CommentReportModel(Base):
    __tablename__ = "comment_report"
    report_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer)  # Foreign key to CommentModel
    user_email = Column(String(255))  # Email of the user who reported
    user_slug = Column(String)  # Slug of the user who reported
    created_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")  # Status of the report (pending, reviewed, etc.)
