from fastapi import APIRouter, HTTPException, Depends, status, \
Request, Response, Header, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.jwtHandler import JWTBearer
from service.userModule.noteService import get_user_notes_by_email, send_new_note_to_user, get_note_by_subject_id, \
send_note_by_subject_id
from request.noteRequest import NewNoteRequest, NewNoteToSubjectRequest

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

# send note api
@note_router.post("/send_new_note/{target_user_email}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_201_CREATED)
async def send_new_note(request: Request,
                    target_user_email: str,
                    newNoteRequest: NewNoteRequest,
                    db: Session = Depends(get_db)):
    message = send_new_note_to_user(request=request,
                                          target_user_email=target_user_email,
                                          newNoteRequest=newNoteRequest,
                                          db=db)
    return message

# get note by note_id 
@note_router.get("/get_note_by_sub_id/{note_id}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_note_by_id(request: Request, 
                         note_id: int,
                         db: Session = Depends(get_db)):
    notes = get_note_by_subject_id(request=request,
                                    subject_id=note_id,
                                    db=db)
    return notes

# send note to existing subject
@note_router.post("/send_note_to_subject/{subject_id}/{target_user_email}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_201_CREATED)
async def send_note_to_subject(request: Request,
                                subject_id: int,
                                target_user_email: str,
                                newNoteRequest: NewNoteToSubjectRequest,
                                db: Session = Depends(get_db)):
    message = send_note_by_subject_id(request=request,
                                      subject_id=subject_id,
                                      target_user_email=target_user_email,
                                      newNoteRequest=newNoteRequest,
                                      db=db)
    return message