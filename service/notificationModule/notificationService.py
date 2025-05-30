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
            # if not all_notif:
            #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            #                     detail="No Notifications Found !")

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
            # if not all_notif:
            #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            #                     detail="No Notifications Found !")

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

def get_unread_notis_count(request: Request, user_type: str, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        
        if user_type == "editor":
            total_unread_notis_count = db.query(EditorNotificationModel).filter(
            EditorNotificationModel.editor_email == user_email,
            EditorNotificationModel.is_read == False
                ).count()
            
        elif user_type == "general":
            total_unread_notis_count = db.query(UserAuthorNotificationModel).filter(
            UserAuthorNotificationModel.user_email == user_email,
            UserAuthorNotificationModel.is_read == False
                ).count()
        else: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user type !")
        
        # if not total_unread_notis_count:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        #                     detail=f"No data found !{total_unread_notis_count}")

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

def get_total_unread_unclicked_notis_count(request: Request,  db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        
        # get user roles
        user_role, user_role_list = get_role_list(user_email, db)


        combined_notis_count = 0
        latest_notis = {}
        if 1260 in user_role_list:
            # user_type = "editor"
            total_editor_notis_count = db.query(EditorNotificationModel).filter(
                EditorNotificationModel.editor_email == user_email,
                EditorNotificationModel.is_read == False,
                EditorNotificationModel.is_clicked == False
            ).count()
            combined_notis_count += total_editor_notis_count
            latest_notis["editorNotisCount"] = total_editor_notis_count


            # get latest notification for editor
            latest_editor_notis = db.query(EditorNotificationModel).filter(
                EditorNotificationModel.editor_email == user_email,
                EditorNotificationModel.is_read == False,
                EditorNotificationModel.is_clicked == False
            ).order_by(desc(EditorNotificationModel.notification_time)).first()
            if latest_editor_notis:
                latest_notis['editorLatestNotis'] = {
                    "notification_title": latest_editor_notis.notification_title,
                    "notification_time": latest_editor_notis.notification_time,
                    "notification_link": latest_editor_notis.notification_link,
                    "notification_type": latest_editor_notis.notification_type
                }
            else:
                latest_notis['editorLatestNotis'] = {}
        
        if 1203 in user_role_list or 2024 in user_role_list:
            # user_type = "author(1203)" or "general(2024)"
            total_user_author_notis_count = db.query(UserAuthorNotificationModel).filter(
                UserAuthorNotificationModel.user_email == user_email,
                UserAuthorNotificationModel.is_read == False,
                UserAuthorNotificationModel.is_clicked == False
            ).count()
            combined_notis_count += total_user_author_notis_count
            latest_notis["userAuthorNotisCount"] = total_user_author_notis_count

            # get latest notification for author/general
            latest_author_notis = db.query(UserAuthorNotificationModel).filter(
                UserAuthorNotificationModel.user_email == user_email,
                UserAuthorNotificationModel.is_read == False,
                UserAuthorNotificationModel.is_clicked == False
            ).order_by(desc(UserAuthorNotificationModel.notification_time)).first()
            if latest_author_notis:
                latest_notis['userAuthorLatestNotis'] = {
                    "notification_title": latest_author_notis.notification_title,
                    "notification_time": latest_author_notis.notification_time,
                    "notification_link": latest_author_notis.notification_link,
                    "notification_type": latest_author_notis.notification_type
                }
            else:
                latest_notis['userAuthorLatestNotis'] = {}
        # else: 
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        #                     detail="Invalid user type !")
        
        latest_notis["combinedNotisCount"] = combined_notis_count
        return latest_notis

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )