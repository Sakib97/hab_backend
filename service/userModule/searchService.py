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
from model.userModel import UserModel, UserRoleModel, RefreshTokenModel
from core.jwtHandler import get_password_hash, create_access_token

from core.jwtHandler import JWT_SECRET, JWT_ALGORITHM
from service.userModule.userService import get_current_user_profile

def search_user_by_query(
    request: Request, 
    query: str, 
    db
):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Invalid user!")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required.")
        # Search for users by email or username
        query_lower = f"%{query.lower()}%"
        users = db.query(UserModel).filter(
            (UserModel.email.ilike(query_lower)) | 
            (UserModel.first_name.ilike(query_lower)) |
            (UserModel.last_name.ilike(query_lower)) 
        ).limit(10).all()

        # exclude the current user from the search results
        users = [user for user in users if user.email != user_email]
        
        # if not users:
        #     raise HTTPException(status_code=404, detail="No users found matching the query.")
        
        return [
            {
                "user_id": user.user_id,
                "full_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )
   