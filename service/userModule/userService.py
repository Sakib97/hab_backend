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
from service.common.roleFinder import get_role_list
from model.articleModel import ArticleModel
from util.getCatSubcatName import get_cat_name, get_subcat_name
from util.encryptionUtil import xor_encode, xor_decode

async def create_user_account(data, db):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if user:
        raise HTTPException(status_code=409, detail="Email is already registered with us.")
    
    new_user = UserModel(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password = get_password_hash(data.password),
        image_url = "https://i.ibb.co/YZnHSSd/avatar-2.jpg", # default profile image
        is_active=False, 
        is_verified=False,
        created_at = datetime.now(),
        updated_at = datetime.now(),
        user_slug = xor_encode(data.email)  # Encode the email for user slug
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user_role = UserRoleModel(
        user_id = new_user.user_id,
        email = new_user.email,
        # role_id = 5,
        role_name_list = '["ROLE_GENERAL_USER"]',
        role_code_list = "[2024]"
    )

    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)

    # Combine user and role data for the response
    response_data = CreateUserResponse(
        user_id= new_user.user_id,
        first_name= new_user.first_name,
        last_name= new_user.last_name,
        email= new_user.email,
        is_active= new_user.is_active,
        is_verified= new_user.is_verified,
        created_at= new_user.created_at,
        updated_at= new_user.updated_at,
        role= UserRoleResponse(
            # role_id= new_user_role.role_id,
            role_name_list= new_user_role.role_name_list,
            role_code_list= new_user_role.role_code_list
        )
    )

    return response_data

def add_or_update_refresh_token(db, user, refresh_token, ref_exp):
    try:
        # Step 1: Check if an entry with the given email already exists
        existing_entry = db.query(RefreshTokenModel).filter_by(email=user.email).one_or_none()
        
        if existing_entry:
            # Step 2: If the entry exists, update it
            existing_entry.token = refresh_token
            existing_entry.expires_at = ref_exp
            existing_entry.created_at = datetime.now()
        else:
            # Step 3: If the entry doesn't exist, create a new one
            new_ref_model = RefreshTokenModel(
                user_id=user.user_id,
                email=user.email,
                token=refresh_token,
                expires_at=ref_exp,
                created_at=datetime.now()
            )
            db.add(new_ref_model)

        # Step 4: Commit the transaction to save changes
        db.commit()

        # Refresh the session with the new or updated object
        if existing_entry:
            db.refresh(existing_entry)
        else:
            db.refresh(new_ref_model)

        # Return the new or updated object
        return existing_entry if existing_entry else new_ref_model

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise e  # Re-raise the exception to handle it at a higher level


def get_current_user_profile(request: Request, db):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
            )
        token_type, token = auth_header.split()  # Split "Bearer <token>"
        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header",
            )
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("email")
            exp = payload.get("exp")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload invalid",
                )
            # get other user info
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User Not Found")
            return user, email, exp
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate tokennn",
            )
        
    except Exception as e:
        # logging.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

def user_logout(request: Request, response: Response, db):
    # Invalidate the refresh token in the database
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="No refresh token found in cookies")
    
    # payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    # email = payload.get("email")
    token_in_db =  db.query(RefreshTokenModel).filter(RefreshTokenModel.token == refresh_token).first()
    if not token_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid token in DB")
    db.delete(token_in_db)
    db.commit()

    # Clear the HTTP-only refresh token cookie
    response.delete_cookie("refresh_token")
    
    return {"msg": "Logout successful"}

def profile_edit(request: Request, editUserRequest: EditUserRequest, db):
    try: 
        if (len(editUserRequest.first_name) < 2)  or (len(editUserRequest.last_name) < 2):
            raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Name lenght not acceptable"
        )
        current_user, user_email, exp = get_current_user_profile(request, db)

        message = []
        # Update common fields
        current_user.first_name = editUserRequest.first_name
        current_user.last_name = editUserRequest.last_name
        current_user.updated_at = datetime.now()

        # Update password if provided
        if editUserRequest.password:
            current_user.password = get_password_hash(editUserRequest.password)
            message.append("Update has pwd")
        else:
            message.append("Update does't have pwd")
        
        if editUserRequest.image_url:
            current_user.image_url = editUserRequest.image_url
            message.append("Update has img")
        else:
            message.append("Update does't have img")
        
        if editUserRequest.delete_image_url:
            current_user.delete_image_url = editUserRequest.delete_image_url
            message.append("Update has dlt img")
        else:
            message.append("Update does't have dlt img")

        # Commit changes and refresh the current user
        db.commit()
        db.refresh(current_user)

        return message

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

def send_email_background(subject: str, to: str, body: str):
    # Load environment variables from .env file
    load_dotenv()
    email_user =  str(os.getenv("EMAIL_USER2"))
    email_password = str(os.getenv("EMAIL_PASSWORD4"))

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = to

    # Connect to the SMTP server
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_password)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def get_reset_token_link(email, db):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Email Not Found")
    reset_token, reset_exp = create_access_token({"email": user.email}, token_type="reset_pass")
    reset_link = f"http://127.0.0.1:3000/auth/reset_pass_token?token={reset_token}"
    return reset_token, reset_link


def reset_pass(token, new_pass, db):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("email")
        token_type = payload.get("token_type")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid",
            )
        if token_type != "reset_pass":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type invalid",
            )
        # get other user info
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="User Not Found")
        
        # update password
        user.password = get_password_hash(new_pass)
        user.updated_at = datetime.now()
        # Commit changes and refresh the current user
        db.commit()
        db.refresh(user)

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )
    

# async def demo_mail():
#     load_dotenv()
#     MAIL_USERNAME = "sakib986797@gmail.com"
#     MAIL_PASSWORD = os.getenv('MAIL_PASSWORD1')
#     MAIL_FROM = os.getenv('MAIL_FROM')
#     MAIL_PORT = 587
#     MAIL_SERVER = os.getenv('MAIL_SERVER')
#     MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')

#     conf = ConnectionConfig(
#         MAIL_USERNAME=MAIL_USERNAME,
#         MAIL_PASSWORD=MAIL_PASSWORD,
#         MAIL_FROM=MAIL_FROM,
#         MAIL_PORT=MAIL_PORT,
#         MAIL_SERVER=MAIL_SERVER,
#         MAIL_TLS=True,
#         MAIL_SSL=False
# )
#     message = MessageSchema(
#         subject="Resetting...",
#         recipients=["ashekseum86@gmail.com"],
#         body="THis is body",
#         subtype="html"
#     )

#     fm = FastMail(conf)
#     await fm.send_message(message)
#     print("message:: ", message)

# get user by email
def get_user_by_email(email: str, db):
    try:
        email = xor_decode(email)  # Decode the email if it was encoded
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail="User not found")
        # get user roles
        user_role_obj, user_role_list = get_role_list(user.email, db)

        userDict = {
            # "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "image_url": user.image_url,
            "created_at": user.created_at,
            "roles": user_role_list,
        }
        return userDict
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )