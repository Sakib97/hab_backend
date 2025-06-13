from fastapi import HTTPException, Request, status, Response, BackgroundTasks
from datetime import datetime
from model.userModel import UserModel, UserRoleModel
from model.noteModel import NoteSubject, NoteMessage
from service.userModule.userService import get_current_user_profile
from service.common.roleFinder import get_role_list
from util.slugMaker import slugify
from request.noteRequest import NewNoteRequest, NewNoteToSubjectRequest
from model.notificationModel import UserAuthorNotificationModel
from sqlalchemy import or_, and_
from sqlalchemy import desc
from util.getUserNameFromMail import get_user_name_from_mail
import base64
from util.encryptionUtil import xor_decode, xor_encode

def get_user_notes_by_email(
    request: Request, 
    target_user_email: str, 
    requester_user_email: str,
    db
):
    try:
        # target_user_email = base64.b64decode(target_user_email+ "===").decode('utf-8')
        # requester_user_email = base64.b64decode(requester_user_email+ "===").decode('utf-8')

        target_user_email = xor_decode(target_user_email)
        requester_user_email = xor_decode(requester_user_email)
        
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        # check if user is valid
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user!")
        
        # editor= 1260, sadmin = 1453, author = 1203
        allowed_roles = [1260, 1453, 1203]
        if not any(role in user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        if not target_user_email or not requester_user_email:
            raise HTTPException(status_code=400, detail="Both target and requester emails are required.")
        
        if target_user_email == requester_user_email:
            raise HTTPException(status_code=400, detail="Target user cannot be the same as requester user.")
        
        if user_email != requester_user_email:
            raise HTTPException(status_code=403, detail="Requester user is not authorized to access this information.")
        
        # Fetch the target user by email
        target_user = db.query(UserModel).filter(UserModel.email == target_user_email).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found.")
        _ , target_user_role_list = get_role_list(target_user.email, db)
        
        if not any(role in target_user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Unauthorized Target User !")
         
        
        # Fetch notes shared with the requester user
        notes = db.query(NoteSubject).filter(
            or_(
                and_(
                    NoteSubject.sender_email == requester_user_email,
                    NoteSubject.receiver_email == target_user_email
                ),
                and_(
                    NoteSubject.sender_email == target_user_email,
                    NoteSubject.receiver_email == requester_user_email
                )
            )
        ).order_by(desc(NoteSubject.created_at)) \
        .all()
        
        return {
            "target_user": {
                # "user_id": target_user.user_id,
                "full_name": f"{target_user.first_name} {target_user.last_name}",
                # "email": target_user.email,
                "user_slug": target_user.user_slug,
                 "image_url": target_user.image_url if target_user.image_url else None,
                 "roles": target_user_role_list if target_user_role_list else [2024]  # Default role if none found
            },
            "notes": [
                {
                    "note_id": note.subject_id,
                    "title": note.subject_name,
                    "title_slug": note.subject_slug,
                    "sender_slug": xor_encode(note.sender_email),
                    "receiver_slug": xor_encode(note.receiver_email),
                    "created_at": note.created_at,
                }
                for note in notes
            ]
        }
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )

# send note to user
def send_new_note_to_user(
    request: Request, 
    target_user_email: str, 
    newNoteRequest: NewNoteRequest,
    db
):
    try:
        target_user_email = xor_decode(target_user_email)
        note_subject = newNoteRequest.subject_name if newNoteRequest.subject_name else ""
        note_content = newNoteRequest.message_text if newNoteRequest.message_text else ""
        
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user!")
        # editor= 1260, sadmin = 1453, author = 1203
        allowed_roles = [1260, 1453, 1203]
        if not any(role in user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        if not target_user_email or not note_subject or not note_content:
            raise HTTPException(status_code=400, detail="Target email, subject and content are required.")
        
        # Fetch the target user by email
        target_user = db.query(UserModel).filter(UserModel.email == target_user_email).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found.")
        _ , target_user_role_list = get_role_list(target_user.email, db)
        
        if not any(role in target_user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Unauthorized Target User !")
        # Create a new note entry
        new_note = NoteSubject(
            subject_name=note_subject,
            subject_slug=slugify(note_subject),
            sender_email=user_email,
            receiver_email=target_user_email,
            created_at=datetime.now()
        )
        db.add(new_note)
        db.commit()

        # Add the note content in NoteMessage Model
        note_message = NoteMessage(
            subject_id=new_note.subject_id,  # Assuming subject_id is auto-generated
            message_text=note_content,
            sender_email=user_email,
            receiver_email=target_user_email,
            created_at=datetime.now()
        )

        
        # db.add(new_note)
        # db.commit()
        db.add(note_message)
        db.commit()

        # notification to the target user
        notif_text = f"""You have a <b> New Note </b> from 
        <b> {target_user.first_name} {target_user.last_name} </b> 
        Subject: <b> {note_subject} </b>"""
        notis_color = "#038b0a"  
        notis_icon = """<i class="fa-solid fa-envelope"></i>"""
        notis_link = f"/profile/note/details?n_id={new_note.subject_id}" 
        notification = UserAuthorNotificationModel(
            user_email=target_user_email,
            notification_title=f"New Note from {current_user.first_name} {current_user.last_name} !",
            notification_title_color=notis_color,
            notification_text=notif_text,
            notification_type=f"new_note_subject_id_{new_note.subject_id}_sender_{xor_encode(user_email)}",
            # notification_type=f"new_note_subject_id_{note_subject.subject_id}_sender_{user_email}",
            
            notification_icon=notis_icon,
            notification_time=datetime.now(),
            is_read=False,
            is_clicked=False,
            notification_link=notis_link,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return "Note & notification sent successfully to the user."
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )

# get note by subject id
def get_note_by_subject_id(
    request: Request, 
    subject_id: int, 
    db
):
    try:

        current_user, user_email, exp = get_current_user_profile(request, db)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user!")
        
        
        # Fetch the note subject by subject_id
        note_subject = db.query(NoteSubject).filter(NoteSubject.subject_id == subject_id).first()
        if not note_subject:
            raise HTTPException(status_code=404, detail="Note subject not found.")
    
        # Check if the current user is either the sender or receiver of the note
        if note_subject.sender_email != user_email and note_subject.receiver_email != user_email:
            raise HTTPException(status_code=403, detail="You are not authorized to access this note.")
        
        # Fetch all messages for this note subject
        note_messages = db.query(NoteMessage).filter(NoteMessage.subject_id == subject_id).order_by(NoteMessage.created_at).all()
        
        return {
            "note_subject": {
                "subject_id": note_subject.subject_id,
                "subject_name": note_subject.subject_name,
                "subject_slug": note_subject.subject_slug,
                "sender_slug": xor_encode(note_subject.sender_email),
                "sender_name": get_user_name_from_mail(note_subject.sender_email, db),
                "receiver_slug": xor_encode(note_subject.receiver_email),
                "receiver_name": get_user_name_from_mail(note_subject.receiver_email, db),
                "created_at": note_subject.created_at,
            },
            "messages": [
                {
                    "message_id": message.message_id,
                    "message_text": message.message_text,
                    "sender_slug": xor_encode(message.sender_email),
                    "sender_name": get_user_name_from_mail(message.sender_email, db),
                    "receiver_slug": xor_encode(message.receiver_email),
                    "receiver_name": get_user_name_from_mail(message.receiver_email, db),
                    "created_at": message.created_at,
                    "is_read": message.is_read,
                    "is_read_at": message.is_read_at
                }
                for message in note_messages
            ]
        }
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )

# send note to existing subject
def send_note_by_subject_id(
    request: Request, 
    subject_id: int, 
    target_user_email: str, 
    newNoteRequest: NewNoteToSubjectRequest,
    db
):
    try:
        target_user_email = xor_decode(target_user_email)
        note_content = newNoteRequest.message_text if newNoteRequest.message_text else ""
        
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user!")
        
        if target_user_email == user_email: 
            raise HTTPException(status_code=400, detail="Target user cannot be the same as sender user.")
        # editor= 1260, sadmin = 1453, author = 1203
        allowed_roles = [1260, 1453, 1203]
        if not any(role in user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        if not target_user_email or not note_content:
            raise HTTPException(status_code=400, detail="Target email and content are required.")
        
        # Fetch the target user by email
        target_user = db.query(UserModel).filter(UserModel.email == target_user_email).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found.")
        _ , target_user_role_list = get_role_list(target_user.email, db)
        
        if not any(role in target_user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Unauthorized Target User !")
        
        # Fetch the note subject by subject_id
        note_subject = db.query(NoteSubject).filter(NoteSubject.subject_id == subject_id).first()
        if not note_subject:
            raise HTTPException(status_code=404, detail="Note subject not found.")
        
        # sender_receiver email list
        sender_receiver_emails = [note_subject.sender_email, note_subject.receiver_email]
        if user_email not in sender_receiver_emails:
            raise HTTPException(status_code=403, detail="You are not authorized to send notes to this subject.")
        if target_user_email not in sender_receiver_emails:
            raise HTTPException(status_code=403, detail="Target user is not authorized to receive notes for this subject.")
        
        # Add the new message to the existing note subject
        new_message = NoteMessage(
            subject_id=note_subject.subject_id,
            message_text=note_content,
            sender_email=user_email,
            receiver_email=target_user_email,
            created_at=datetime.now(),
            is_read=False,
            is_read_at=None
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        # notification to the target user
        notif_text = f"""You have a <b> New Note </b> from
        <b> {current_user.first_name} {current_user.last_name} </b> <br> 
        Subject: <b> {note_subject.subject_name} </b>"""
        notis_color = "#038b0a"
        notis_icon = """<i class="fa-solid fa-envelope"></i>"""
        notis_link = f"/profile/note/details?n_id={note_subject.subject_id}"
        notification = UserAuthorNotificationModel(
            user_email=target_user_email,
            notification_title=f"New Note from {current_user.first_name} {current_user.last_name} !",
            notification_title_color=notis_color,
            notification_text=notif_text,
            notification_type=f"new_note_subject_id_{note_subject.subject_id}_sender_{user_email}",
            notification_icon=notis_icon,
            notification_time=datetime.now(),
            is_read=False,
            is_clicked=False,
            notification_link=notis_link,
        )   
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return "Note and notification sent successfully to the user."
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )

        