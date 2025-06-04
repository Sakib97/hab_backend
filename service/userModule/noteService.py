from fastapi import HTTPException, Request, status, Response, BackgroundTasks
from datetime import datetime
from jose import JWTError, jwt
import smtplib
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv
from email.message import EmailMessage

from request.userRequest import EditUserRequest
from response.userResponse import UserRoleResponse, CreateUserResponse
from model.userModel import UserModel, UserRoleModel
from model.noteModel import NoteSubject
from service.userModule.userService import get_current_user_profile
from service.common.roleFinder import get_role_list

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