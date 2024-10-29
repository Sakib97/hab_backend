from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from service.notificationModule.notificationService import get_all_editor_notification
notification_router = APIRouter(
    prefix="/notification", 
    tags=["Notification"])

@notification_router.get("/editor_notifcation_list", 
                         dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_all_editor_notif(request: Request, db: Session = Depends(get_db)):
    all_notifs = get_all_editor_notification(request=request,db=db)
    return {"all_notis": all_notifs}