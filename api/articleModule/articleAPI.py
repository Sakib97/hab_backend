from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from request.articleRequest import CreateArticleRequest, AddTagToArticleRequest
from service.articleModule.articleService import get_unreviewed_article_list_by_editor, \
get_editor_by_category_id, create_article, add_tag_to_article

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
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_list(request: Request,
                   editor_email, 
                   page: int = 1,
                   limit: int = 3,
                   db: Session = Depends(get_db)):
    total_article_count, article_list = get_unreviewed_article_list_by_editor(request, 
                                                         editor_email=editor_email, 
                                                         page=page,
                                                         limit=limit,
                                                         db=db)
    
    return { "totalCount": total_article_count, "articles": article_list}
    # return article_list

@article_router.post("/add_tag_to_article", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def add_tag_article(request: Request,
                          addTagReq: AddTagToArticleRequest,
                        db: Session = Depends(get_db)):
    tags = add_tag_to_article(request=request, addTagReq=addTagReq, db=db)
    return tags

# approve article by id
@article_router.post("/approve_article", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def approve_art(request: Request,
                   db: Session = Depends(get_db)):
    pass

# ['Hello', 'newTagRequested']

