from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import CreateArticleRequest, AddTagToArticleRequest, ApproveArticleRequest
from response.articleResponse import UnrevArticleResponse
from service.userModule.userService import get_current_user_profile
from model.userModel import EditorModel, UserModel
from model.articleModel import ArticleModel, ArticleSubmissionModel
from model.notificationModel import EditorNotificationModel, UserAuthorNotificationModel
import ast
from service.common.roleFinder import get_role_list
from sqlalchemy.orm import Session
from sqlalchemy import desc
from core.database import get_db
import random
from datetime import datetime
from util.slugMaker import slugify
from util.encryptionUtil import xor_encode, xor_decode
from util.getUserNameFromMail import get_user_name_from_mail
from sqlalchemy.exc import SQLAlchemyError
from util.reactionUtil import ReactionType, is_valid_reaction
from model.commentModel import ArticleReactionModel

# article reaction submission
def article_react(request: Request, 
                  reactPlace: str, 
                  article_id: int,
                  reaction_type: str,
                  db: Session = Depends(get_db), 
                  
                  ):
    """
    React to an article or comment.
    """
    try:
        if reactPlace not in ["article", "comment"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid react place")
        current_user, user_email, exp = get_current_user_profile(request, db)
        if not is_valid_reaction(reaction_type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reaction type")
        
        article = db.query(ArticleModel).filter(ArticleModel.article_id == article_id).first()
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        # Check if the user has already reacted to the article
        existing_reaction = db.query(ArticleReactionModel).filter(
            ArticleReactionModel.article_id == article_id,
            ArticleReactionModel.user_email == user_email,
            ArticleReactionModel.reaction_type == reaction_type
        ).first()
        if existing_reaction:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reacted to this article")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# def bfs:
#     xys = 1