from fastapi import HTTPException, Request, status, Response, BackgroundTasks
from datetime import datetime
from model.userModel import UserModel, UserRoleModel
from model.noteModel import NoteSubject, NoteMessage
from service.userModule.userService import get_current_user_profile
from service.common.roleFinder import get_role_list
from util.slugMaker import slugify
from request.noteRequest import NewNoteRequest

def get_user_notes_by_email(
    request: Request, 
    target_user_email: str, 
    requester_user_email: str,
    db
):
    try:
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
            (NoteSubject.sender_email == requester_user_email and 
            NoteSubject.receiver_email == target_user_email) or
            (NoteSubject.sender_email == requester_user_email and
            NoteSubject.receiver_email == target_user_email)
        ).all()
        
        return {
            "target_user": {
                "user_id": target_user.user_id,
                "full_name": f"{target_user.first_name} {target_user.last_name}",
                "email": target_user.email,
                 "image_url": target_user.image_url if target_user.image_url else None,
                 "roles": target_user_role_list if target_user_role_list else [2024]  # Default role if none found
            },
            "notes": [
                {
                    "note_id": note.subject_id,
                    "title": note.subject_name,
                    "sender_email": note.sender_email,
                    "receiver_email": note.receiver_email,
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
        
        return "Note sent successfully to the user."
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )