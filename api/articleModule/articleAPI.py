from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer


article_router = APIRouter(
    prefix="/article", 
    tags=["Article"])

# create article
@article_router.post("/create_article", 
                     dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_201_CREATED)
async def post_article():
    pass

