from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import CreateArticleRequest
from response.articleResponse import UnrevArticleResponse
from service.userModule.userService import get_current_user_profile
from model.userModel import EditorModel, UserModel
from model.articleModel import ArticleModel, ArticleSubmissionModel
from model.notificationModel import EditorNotificationModel, UserAuthorNotificationModel
import ast
from service.common.roleFinder import get_role_list
from sqlalchemy import desc
from core.database import get_db
import random
from datetime import datetime

def get_all_notification(request: Request, 
                        user_type: str,
                         page: int, 
                         limit:int, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        if user_type not in ["editor", "author", "general"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user type !")
        
        offset = (page - 1) * limit
        if user_type == "editor":
            # step 1: get all the notifications
            all_notif = db.query(EditorNotificationModel).filter(
                EditorNotificationModel.editor_email == user_email
            ).order_by(desc(EditorNotificationModel.notification_time)).offset(offset).limit(limit).all()
            
            # check if notifications exist
            if not all_notif:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="No Notifications Found !")

            total_notis_count = db.query(EditorNotificationModel).filter(
                EditorNotificationModel.editor_email == user_email
            ).count()

            # step 2: make all is_read == true, as all the notifs have been seen
            for notification in all_notif:
                if not notification.is_read:  # Only update if it hasn't been marked as read
                    notification.is_read = True
                    db.commit()
                    db.refresh(notification)

            return total_notis_count, all_notif
        
        elif user_type == "general":
            # step 1: get all the notifications
            all_notif = db.query(UserAuthorNotificationModel).filter(
                UserAuthorNotificationModel.user_email == user_email
            ).order_by(desc(UserAuthorNotificationModel.notification_time)).offset(offset).limit(limit).all()
            
            # check if notifications exist
            if not all_notif:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="No Notifications Found !")

            total_notis_count = db.query(UserAuthorNotificationModel).filter(
                UserAuthorNotificationModel.user_email == user_email
            ).count()

            # step 2: make all is_read == true, as all the notifs have been seen
            for notification in all_notif:
                if not notification.is_read:  # Only update if it hasn't been marked as read
                    notification.is_read = True
                    db.commit()
                    db.refresh(notification)
            return total_notis_count, all_notif
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
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
                status_code=e.status_code,
                detail=e.detail
                )

def mark_notis_as_clicked(request: Request, user_type: str, notis_id: int, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        # print("user_email", user_email)
        # print("user_type", user_type)
        if user_type not in ["editor", "author", "general"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user type !")
        if user_type == "editor":
            # get notification by notis_id
            notification = db.query(EditorNotificationModel).filter(
                EditorNotificationModel.notification_id == notis_id
            ).first()
            # check if notification exists
            if not notification:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Notification Not Found !")
            # check if editor email is same as the user
            if notification.editor_email != user_email:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to access this notification !")
            # mark notification as clicked
            if notification.is_clicked == True:
                return {"msg": "Notification already marked as clicked",
                        "type": notification.notification_type}
            notification.is_clicked = True
            db.commit()
            return {"msg": "Notification marked as clicked",
                        "type": notification.notification_type}
        
        elif user_type == "general":
            # get notification by notis_id
            notification = db.query(UserAuthorNotificationModel).filter(
                UserAuthorNotificationModel.notification_id == notis_id
            ).first()
            # check if notification exists
            if not notification:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Notification Not Found !")
            # check if user email is same as the user
            if notification.user_email != user_email:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to access this notification !")
            # mark notification as clicked
            if notification.is_clicked == True:
                return {"msg": "Notification already marked as clicked",
                        "type": notification.notification_type}
            notification.is_clicked = True
            db.commit()
            return {"msg": "Notification marked as clicked",
                        "type": notification.notification_type}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user type !")
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )