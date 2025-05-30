from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from service.notificationModule.notificationService import \
get_all_notification, get_unread_notis_count, mark_notis_as_clicked, \
get_total_unread_unclicked_notis_count

notification_router = APIRouter(
    prefix="/notification", 
    tags=["Notification"])

@notification_router.get("/notifcation_list/{user_type}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_all_notif(request: Request, 
                                 user_type: str,
                               page: int = 1,
                               limit: int = 3,
                               db: Session = Depends(get_db)):
    total_notis_count, all_notifs = get_all_notification(request=request, 
                                             user_type=user_type,
                                             page=page, 
                                             limit=limit,
                                             db=db)
    return {"totalCount": total_notis_count, "all_notis": all_notifs}

@notification_router.get("/unread_editor_notis_count", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)

# unread notifications count for editor
async def get_unread_editor_notif_count(request: Request, 
                                        db: Session = Depends(get_db)):
    total_unread = get_unread_notis_count(request=request, 
                                                 user_type = "editor", 
                                                 db=db)
    return {"totalUnread": total_unread}

# unread notifications count for user / author
@notification_router.get("/unread_general_notis_count", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)

async def get_unread_general_notif_count(request: Request, 
                                        db: Session = Depends(get_db)):
    total_unread = get_unread_notis_count(request=request, 
                                          user_type = "general", 
                                          db=db)
    return {"totalUnread": total_unread}


# mark notification as clicked
@notification_router.post("/mark_notis_as_clicked/{user_type}/{notis_id}", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)

async def mark_notification_as_clicked(request: Request,
                                 user_type: str,
                                notis_id: int,
                               db: Session = Depends(get_db)):
    
    response = mark_notis_as_clicked(request=request, 
                                      user_type=user_type,
                                      notis_id=notis_id,
                                      db=db)
    return response

# get all unread and unclicked notification count for a user 
# (editor / author / sadmin combined)
@notification_router.get("/get_all_unread_unclicked_notis_count", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_all_notis_count(request: Request,
                               db: Session = Depends(get_db)):
    latest_unread_unclicked_count = get_total_unread_unclicked_notis_count(request=request,
                                                                             db=db)
    return latest_unread_unclicked_count