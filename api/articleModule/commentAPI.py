from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from service.articleModule.commentService import article_or_comment_react, get_reaction_counts, get_comments_by_article_id,\
    post_comment_by_id
from request.commentRequest import ReactionRequest, PostCommentRequest

comment_router = APIRouter( 
    prefix="/comment", 
    tags=["Comment"])


##################################
##### Reaction related APIs ######
##################################

# get reaction counts for an article or comment
@comment_router.get("/reactions/{reactPlace}/{content_id}",
                      status_code=status.HTTP_200_OK)
def get_reactions(request: Request,
                  reactPlace: str,
                  content_id: int,
                  db: Session = Depends(get_db)):
    response = get_reaction_counts(db=db, reactPlace=reactPlace, content_id=content_id, request=request)
    return response

# react to an article or a comment
@comment_router.post("/react/{reactPlace}", 
                    dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_200_OK)
def react_to_content(request: Request, 
                     reactPlace: str, 
                     reaction_req: ReactionRequest,
                     db: Session = Depends(get_db)): 
    response = article_or_comment_react(
        request=request,
        reactPlace=reactPlace,
        content_id=reaction_req.content_id,
        reaction_type=reaction_req.reaction_type,
        db=db)
    return response


##################################
##### comment related APIs #######
##################################
# get comments for an article
# pagination: page=1, limit=3
@comment_router.get("/article/comments/{article_id}",
                    status_code=status.HTTP_200_OK)
def get_comments(
                 request: Request,
                 article_id: int,
                 page: int = 1,
                 limit: int = 3,
                 db: Session = Depends(get_db)):
    parent_comments, total_comments_count = get_comments_by_article_id(
        article_id=article_id,
        page=page,
        limit=limit,
        db=db,
        request=request
    )
    return {"parent_comments": parent_comments, 
            "total_comments_count": total_comments_count}


# post a comment on an article
@comment_router.post("/article/post_comment/{article_id}",
                     dependencies=[Depends(JWTBearer())],
                     status_code=status.HTTP_201_CREATED)
def post_comment(request: Request,
                 article_id: int,
                    comment_request: PostCommentRequest,
                 db: Session = Depends(get_db)):
    response = post_comment_by_id(
        request=request,
        article_id=article_id,
        post_comment_req=comment_request,
        db=db
    )
    return response
