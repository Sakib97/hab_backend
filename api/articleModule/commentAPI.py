from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from core.jwtHandler import JWTBearer
from core.database import get_db
from sqlalchemy.orm import Session
from service.articleModule.commentService import article_or_comment_react, get_reaction_counts
from request.commentRequest import ReactionRequest

comment_router = APIRouter( 
    prefix="/comment", 
    tags=["Comment"])


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