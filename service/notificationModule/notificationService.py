from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import CreateArticleRequest
from response.articleResponse import UnrevArticleResponse
from service.userModule.userService import get_current_user_profile
from model.userModel import EditorModel, UserModel
from model.articleModel import ArticleModel, ArticleSubmissionModel
from model.notificationModel import EditorNotificationModel
import ast
from service.common.roleFinder import get_role_list
from sqlalchemy.orm import Session
from core.database import get_db
import random
from datetime import datetime

def get_all_editor_notification(request: Request, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        # step 1: get all the notifications
        all_notif = db.query(EditorNotificationModel).filter(
            EditorNotificationModel.editor_email == user_email
        ).all()

        # step 2: make all is_read == true, as all the notifs have been seen

        return all_notif
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )