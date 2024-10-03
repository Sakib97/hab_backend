from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated
import ast

from core.database import get_db
from core.jwtHandler import verify_password, verify_user_access, create_access_token, create_refreshed_access_token
# from core.jwtHandler import get_current_user
from request.userRequest import CreateEditorRequest, CreateUserRequest, UserLoginRequest, EditUserRequest, PasswordResetEmailRequest, PasswordResetTokenRequest
from service.userModule.userService import reset_pass, get_reset_token_link, send_email_background, profile_edit, user_logout, create_user_account, get_current_user_profile, add_or_update_refresh_token
from service.sadminModule.sadminService import create_editor_or_author
from model.userModel import UserModel, UserRoleModel, RefreshTokenModel
from core.jwtHandler import JWTBearer
from core.jwtHandler import refresh_exp_sec




user_router = APIRouter(
    prefix="/user", 
    tags=["User"])


# create User
@user_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest,
                      db: Session = Depends(get_db)):
    response = await create_user_account(data, db)
    return response


# user login and access token generation
@user_router.post("/token", status_code=status.HTTP_200_OK)
async def login_with_access_token(data: UserLoginRequest,
                                  response: Response,
                                  db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid Login Credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # verify_user_access(user)
    user_role = db.query(UserRoleModel).filter(UserRoleModel.email == user.email).first()
    
    if user_role.role_code_list:
        role_code_as_list = ast.literal_eval(user_role.role_code_list)
    else: 
        role_code_as_list = [2024]

    # create_access_token() is in jwtHandler.py, as it is related to creating a new token
    # access_token = create_access_token({"user_id": user.user_id , 
    #                                     "email": user.email})
    access_token, acc_exp = create_access_token({"email": user.email}, token_type="access")
    refresh_token, ref_exp = create_access_token({"email": user.email}, token_type="refresh")
    
    # attaching the refresh token with http-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=(21600+ refresh_exp_sec), # adding GMT +6hrs (6 hrs = 21600 sec)
        secure=True,
        samesite='strict' 
    )

    entry = add_or_update_refresh_token(db, user, refresh_token, ref_exp)

    return { "email":user.email,
            "first_name": user.first_name,
            "last_name": user.last_name, 
            "image_url": user.image_url,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role": role_code_as_list,
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"}


@user_router.get("/profile",dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_user_profile(request: Request,
                           db: Session = Depends(get_db)):
    current_user, user_email, exp = get_current_user_profile(request, db)
    return {"first_name":current_user.first_name,
            "last_name":current_user.last_name,
            "user_email": user_email, 
            "image_url": current_user.image_url,
            "delete_image_url": current_user.delete_image_url,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "exp": exp}


@user_router.post("/refresh_token", status_code=status.HTTP_200_OK)
async def refresh_access_token(request: Request,
                                # authorization: str = Header(),
                               db: Session = Depends(get_db)):
    
    # create_refreshed_access_token() is in jwtHandler as it is related to tokens
    # new_access_token = create_refreshed_access_token(authorization, db)

    # cookie usage expl
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    new_access_token = create_refreshed_access_token(refresh_token, db)
    return {"new_access_token": new_access_token}

######################## Reset Password ##############################
# Can be used to send direct password in mails
# @user_router.post("/reset_password", status_code=status.HTTP_200_OK)
# async def reset_password(background_tasks: BackgroundTasks):
#     name = "sakib"

#     background_tasks.add_task(send_email_background, 
#                               "Reset Password: History and Beyond", 
#                               "ashekseum86@gmail.com", 
#                               f"hello {name}, This is a new message")
#     # demo_mail()
#     return {"message": "Email sent in the background"}

@user_router.post("/reset_pass_email", status_code=status.HTTP_200_OK)
async def reset_password_email(background_tasks: BackgroundTasks,
                               resetEmail: PasswordResetEmailRequest,
                               db: Session = Depends(get_db)):
    email = resetEmail.email
    reset_token, reset_link = get_reset_token_link(email, db)

    background_tasks.add_task(send_email_background, 
                              "Reset Password: History and Beyond", 
                              f"{email}", 
                              f"Hello {email},\n\nPlease click the link below to reset a new password:\n\n {reset_link} \n\nValidity of the link is 05 minutes.")

    return {"reset_link": reset_link,
            "reset_token": reset_token,
        "message": "Reset Email sent Successfully"}
    # return {"reset_link": reset_link} 

@user_router.post("/reset_pass_token", status_code=status.HTTP_200_OK)
async def reset_password_token( tokenRequest: PasswordResetTokenRequest, 
                                db: Session = Depends(get_db)):
    token = tokenRequest.reset_token
    new_pass = tokenRequest.new_password
    reset_pass(token, new_pass, db)
    return {"message": "password reset successful"} 

############################## Reset Password ##############################

@user_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request,
                 response: Response, 
                 db: Session = Depends(get_db)):

    msg = user_logout(request, response, db)
    return msg

@user_router.put("/edit_profile", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED)
async def edit_profile(request: Request,
                       editRequest: EditUserRequest,
                       db: Session = Depends(get_db)):
    msg = profile_edit(request, editRequest, db) 
    return {"message": msg}

####### Editor and Author related (can only be done by SAdmin)  #########
########### in SAdminService.py ############
# create editor
@user_router.post("/create_editor", 
                  dependencies=[Depends(JWTBearer())],
                  status_code=status.HTTP_201_CREATED)
async def editor_create(request: Request,
                        createReq: CreateEditorRequest,
                        db: Session = Depends(get_db)):
    response = await create_editor_or_author(request, createReq, 
                                             db, role="editor", mode="create")
    return response 
    

# create editor
@user_router.post("/create_author", 
                  dependencies=[Depends(JWTBearer())],
                  status_code=status.HTTP_201_CREATED)
async def author_create(request: Request,
                        createReq: CreateEditorRequest,
                        db: Session = Depends(get_db)):
    response = await create_editor_or_author(request, createReq, 
                                             db, role="author", mode="create")
    return response 

# edit editor (change assgned cat list)
@user_router.post("/edit_editor", 
                  dependencies=[Depends(JWTBearer())],
                  status_code=status.HTTP_201_CREATED)
async def editor_edit(request: Request,
                        createReq: CreateEditorRequest,
                        db: Session = Depends(get_db)):
    response = await create_editor_or_author(request, createReq, 
                                             db, role="editor", mode="edit")
    return response 


# edit author (change assgned cat list)
@user_router.post("/edit_author", 
                  dependencies=[Depends(JWTBearer())],
                  status_code=status.HTTP_201_CREATED)
async def author_edit(request: Request,
                        createReq: CreateEditorRequest,
                        db: Session = Depends(get_db)):
    response = await create_editor_or_author(request, createReq, 
                                             db, role="author", mode="edit")
    return response 


