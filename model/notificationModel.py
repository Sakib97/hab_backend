from core.database import Base
from sqlalchemy import Boolean, Column, Integer, String,DateTime, func, Text

class EditorNotificationModel(Base):
    __tablename__ = "editor_notification"
    notification_id = Column(Integer, primary_key=True, index=True)
    editor_email = Column(String(255))
    notification_title = Column(String(255))
    notification_title_color = Column(String(100))
    notification_text = Column(String)
    notification_type = Column(String(100))
    notification_icon = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False)
    notification_time = Column(DateTime, nullable=True)
    notification_link = Column(String(100))

class UserAuthorNotificationModel(Base):
    __tablename__ = "userAuthor_notification"
    notification_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255))
    notification_title = Column(String(255))
    notification_title_color = Column(String(100))
    notification_text = Column(String)
    notification_type = Column(String(100))
    notification_icon = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False)
    notification_time = Column(DateTime, nullable=True)
    notification_link = Column(String(100))

    