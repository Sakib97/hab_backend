from core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

class NoteSubject(Base):
    __tablename__ = "note_subject"
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String)
    subject_slug = Column(String)
    created_at = Column(DateTime, nullable=True)
    # user1 and user2 are the participants in the conversation.
    sender_email = Column(String(255), nullable=True)  
    receiver_email = Column(String(255), nullable=True)  

class NoteMessage(Base):
    __tablename__ = "note_message"
    message_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer)  # Foreign key to NoteSubject
    message_text = Column(Text)
    sender_email = Column(String(255))  # Email of the sender
    receiver_email = Column(String(255))  # Email of the receiver
    created_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)  
    is_read_at = Column(DateTime, nullable=True)  # Timestamp when the message was read