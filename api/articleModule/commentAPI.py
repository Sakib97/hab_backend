from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session

comment_router = APIRouter( 
    prefix="/comment", 
    tags=["Comment"])
 
# react to article
# reactPlace = article or comment
@comment_router.post("/react/{reactPlace}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
def article_react(request: Request, 
                    reactPlace: str, 
                    db: Session = Depends(get_db)): 
        pass
      # generate the function
      
      