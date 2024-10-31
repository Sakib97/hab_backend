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
from sqlalchemy import desc
from core.database import get_db
import random
from datetime import datetime

def get_all_editor_notification(request: Request, page: int, limit:int, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)

        # step 1: get all the notifications
        offset = (page - 1) * limit
        all_notif = db.query(EditorNotificationModel).filter(
            EditorNotificationModel.editor_email == user_email
        ).order_by(desc(EditorNotificationModel.notification_time)).offset(offset).limit(limit).all()
        
        total_notis_count = db.query(EditorNotificationModel).filter(
            EditorNotificationModel.editor_email == user_email
        ).count()

        # step 2: make all is_read == true, as all the notifs have been seen
        for notification in all_notif:
            if not notification.is_read:  # Only update if it hasn't been marked as read
                notification.is_read = True
                db.commit()
                db.refresh(notification)

        # Step 3: Commit the changes to update the database
        # db.commit()


        return total_notis_count, all_notif
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )

def get_unread_editor_notis_count(request: Request,db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        total_unread_notis_count = db.query(EditorNotificationModel).filter(
            EditorNotificationModel.editor_email == user_email,
            EditorNotificationModel.is_read == False
        ).count()

        return total_unread_notis_count

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )