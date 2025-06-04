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
from core.jwtHandler import refresh_exp_sec
from service.userModule.searchService import search_user_by_query


search_router = APIRouter(
    prefix="/search", 
    tags=["Search"])

# search user by query (query of username / mail)
@search_router.get("/search_uname_mail", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_search_user(request: Request, 
                                 query: str = Query(..., min_length=1, max_length=50),
                               db: Session = Depends(get_db)):
    users = search_user_by_query(request=request,
                                              query=query,
                                              db=db)
    return users 