from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from request.articleRequest import CreateArticleRequest
from service.articleModule.articleService import get_unreviewed_article_list_by_editor, get_editor_by_category_id, create_article

article_router = APIRouter(
    prefix="/article", 
    tags=["Article"])


# get article by category ID
@article_router.get("/editor_list/{cat_id}", 
                      status_code=status.HTTP_200_OK)
async def get_cat_editor(cat_id, db: Session = Depends(get_db)):
    editors = get_editor_by_category_id(category_id=cat_id, db=db)
    return {"editors": editors}
    # return editors


# create article
@article_router.post("/create_article", 
                     dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_201_CREATED)
async def post_article(request: Request,
                       createArticleRequest:CreateArticleRequest,
                       db: Session = Depends(get_db)):
    response = await create_article(request,createArticleRequest,db)
    return response

# get unreviewed article by editor_email
@article_router.get("/unrev_article_by_editor_mail/{editor_email}", 
                      status_code=status.HTTP_200_OK)
async def get_list(request: Request,
                   editor_email, 
                   db: Session = Depends(get_db)):
    article_list = get_unreviewed_article_list_by_editor(request, 
                                                         editor_email=editor_email, 
                                                         db=db)
    # return {"unreviewed_list": article_list}
    return article_list
    # pass
