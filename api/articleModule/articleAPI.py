from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from request.articleRequest import CreateArticleRequest, AddTagToArticleRequest, ApproveArticleRequest, EditArticleRequest
from service.articleModule.articleService import get_unreviewed_article_list_by_editor, \
get_editor_by_category_id, create_article, add_tag_to_article, approve_reject_resend_article, \
get_article_by_article_id
from service.articleModule.articleService_part2 import fetch_approved_article_by_id, get_article_by_email, \
get_any_article_by_id, get_sent_for_edit_article_by_id, edit_article_by_id


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
# (those which sent to this editor)
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

# get unreviewed article by article_id
@article_router.get("/unreviewed_article/{article_id}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_unreviewed_article_by_id(request: Request,
                             article_id: int, 
                             db: Session = Depends(get_db)):
    article = get_article_by_article_id(request, article_id=article_id, article_status="under_review_new", db=db)
    return { "article": article}

@article_router.post("/add_tag_to_article", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def add_tag_article(request: Request,
                          addTagReq: AddTagToArticleRequest,
                        db: Session = Depends(get_db)):
    tags = add_tag_to_article(request=request, addTagReq=addTagReq, db=db)
    return tags


# article actions by id ("approved", "rejected", "sent_for_edit")	
@article_router.post("/article_actions/{action}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def article_actions(request: Request, action,
                     approveArticleRequest: ApproveArticleRequest,                 
                   db: Session = Depends(get_db)):
    response = approve_reject_resend_article(request, action, approveArticleRequest, db)
    return response



# All the below API functions will be in ::
# :: articleService_part2.py
# =============================================

# get Approved article by article_id
@article_router.get("/approved_article/{article_id}", 
                    # dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_approved_article_by_id(
                             article_id: int, 
                             db: Session = Depends(get_db)):
    article = fetch_approved_article_by_id(article_id=article_id, db=db)
    return { "article": article}


# get all article by author / editor email 
# (Review History for editor) / (My Articles for Author)
@article_router.get("/all_article_by_email/{user_type}/{email}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)

async def get_all_article_by_email(request: Request,
                                   user_type: str,
                                   email: str, 
                                   page: int = 1,
                                   limit: int = 3,
                                   db: Session = Depends(get_db)):
    total_article_count, article_list = get_article_by_email(request, 
                                                             user_type=user_type, 
                                                             email=email, 
                                                             page=page, 
                                                             limit=limit, 
                                                             db=db)
    return { "totalCount": total_article_count, "articles": article_list}

# get_any_article_by_article_id 
# (for author/editor History purpose)
@article_router.get("/any_article/{article_id}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_any_article_by_article_id(request: Request,
                             article_id: int, 
                             db: Session = Depends(get_db)):
    article = get_any_article_by_id(request=request, article_id=article_id, db=db)
    return article


# This api is for get articles that Editor sent for edit 
# and Author wants to edit
# Accessible by Author
@article_router.get("/sent_for_edit_article/{article_id}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
async def get_sent_for_edit_article_by_article_id(request: Request,
                             article_id: int, 
                             db: Session = Depends(get_db)):
    article, category_name, subcategory_name, editor_email, editor_firstname, editor_lastname = get_sent_for_edit_article_by_id(request=request, article_id=article_id, db=db)
    return {"article": article, "category_name": category_name, 
            "subcategory_name": subcategory_name, "editor_email": editor_email,
            "editor_firstname": editor_firstname, "editor_lastname": editor_lastname}
    
  
# This API is for when author submits his edits, 
# as requested by editor
@article_router.post("/edit_article/{article_id}", 
                    dependencies=[Depends(JWTBearer())], 
                    status_code=status.HTTP_202_ACCEPTED)
async def edit_article(request: Request,
                       editRequest: EditArticleRequest,
                       article_id: int,
                       db: Session = Depends(get_db)):
    msg = edit_article_by_id(request=request, 
                       editArticleRequest=editRequest,
                       article_id=article_id,
                       db=db) 
    return {"message": msg}

# ['Hello', 'newTagRequested']

