from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import CreateArticleRequest, AddTagToArticleRequest, ApproveArticleRequest
from response.articleResponse import ApprovedArticleResponse
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

def fetch_approved_article_by_id(article_id,db):
    try:
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == article_id
            ).first()
        if not article_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        # check if article is approved
        if article_obj.article_status != "approved":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article is not approved !")

        
        # category and subcategory name
        category = db.query(CategoryModel).filter(
            CategoryModel.category_id ==article_obj.category_id).first()
        category_name = category.category_name

        subcategory = db.query(SubcategoryModel).filter(
            SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
        subcategory_name = subcategory.subcategory_name

        # Author info
        article_author = db.query(UserModel).filter(
            UserModel.email == article_obj.email
        ).first()

        # published time info
        article_submission = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.article_id == article_obj.article_id
        ).first()

        published_time = article_submission.published_at if article_submission else None
        if not published_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Published time not found !")
         
        
        article = ApprovedArticleResponse(
            author_email=article_obj.email,
            author_firstname=article_author.first_name,
            author_lastname=article_author.last_name,
            author_image_url=article_author.image_url,

            published_at=str(published_time),
            category_name=category_name,
            subcategory_name=subcategory_name,

            title_en=article_obj.title_en,
            title_bn=article_obj.title_bn,
            subtitle_en=article_obj.subtitle_en,
            subtitle_bn=article_obj.subtitle_bn,
            content_en=article_obj.content_en,
            content_bn=article_obj.content_bn,
            tags=article_obj.tags,
                
            cover_img_link=article_obj.cover_img_link,
            cover_img_cap_en=article_obj.cover_img_cap_en,
            cover_img_cap_bn=article_obj.cover_img_cap_bn,
        )

        return article

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )