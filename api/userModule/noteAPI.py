from fastapi import APIRouter, HTTPException, Depends, status, \
Request, Response, Header, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated
import ast

from core.database import get_db
from core.jwtHandler import verify_password, verify_user_access, create_access_token, create_refreshed_access_token
# from core.jwtHandler import get_current_user
from request.userRequest import CreateEditorRequest, CreateUserRequest, UserLoginRequest, EditUserRequest, PasswordResetEmailRequest, PasswordResetTokenRequest
from model.userModel import UserModel, UserRoleModel, RefreshTokenModel
from core.jwtHandler import JWTBearer
from service.userModule.noteService import get_user_notes_by_email

note_router = APIRouter(
    prefix="/notes", 
    tags=["Note"])

# this api fetches basic user info and also 
# the notes shared between the users , if any

# requester_user_email is the email of the user who is 
# requesting the info (the one sending API req)

# target_user_email is the email of the user whose info is being requested

@note_router.get("/get_user_note_by_mail/{target_user_email}/{requester_user_email}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_user_note_by_mail(request: Request, 
                                target_user_email: str,
                                requester_user_email: str,
                                db: Session = Depends(get_db)):
    notes = get_user_notes_by_email(request=request,
                                    target_user_email=target_user_email,
                                    requester_user_email=requester_user_email,
                                    db=db)
    return notes 