from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from service.notificationModule.notificationService import \
get_all_editor_notification, get_unread_editor_notis_count

notification_router = APIRouter(
    prefix="/notification", 
    tags=["Notification"])

@notification_router.get("/editor_notifcation_list", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_all_editor_notif(request: Request, 
                               page: int = 1,
                               limit: int = 3,
                               db: Session = Depends(get_db)):
    total_notis_count, all_notifs = get_all_editor_notification(request=request, 
                                             page=page, 
                                             limit=limit,
                                             db=db)
    return {"totalCount": total_notis_count, "all_notis": all_notifs}

@notification_router.get("/unread_editor_notis_count", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)

async def get_unread_editor_notif_count(request: Request, 
                                        db: Session = Depends(get_db)):
    total_unread = get_unread_editor_notis_count(request=request, db=db)
    return {"totalUnread": total_unread}