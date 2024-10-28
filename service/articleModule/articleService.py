from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import CreateArticleRequest
from response.articleResponse import UnrevArticleResponse
from service.userModule.userService import get_current_user_profile
from model.userModel import EditorModel, UserModel
from model.articleModel import ArticleModel, ArticleSubmissionModel
import ast
from service.common.roleFinder import get_role_list
from sqlalchemy.orm import Session
from core.database import get_db
import random
from datetime import datetime


def get_editor_by_category_id(category_id,db):
    all_editors = db.query(EditorModel).all()
    # find the editors assigned to this category
    category_editors_ids = []
    editors = []
    for editor in all_editors:
        editor_id = editor.editor_id
        assigned_cat_id_list = ast.literal_eval(editor.assigned_cat_id_list)        
        
        if int(category_id) in assigned_cat_id_list:
            category_editors_ids.append(editor_id)
            editors.append(editor)

    # random_editor = random.choice(editors)
    # return random_editor.user_email
    return editors, category_editors_ids


async def create_article(request: Request,
                         data: CreateArticleRequest,
                         db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        
        # check if category_id, subcategory_id and tag_ids are valid
        # category is mandatory field
        category = db.query(CategoryModel).filter(CategoryModel.category_id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Category Not Found")
        
        # sub-category is mandatory field
        subcategory = db.query(SubcategoryModel).filter(
            SubcategoryModel.subcategory_id == data.subcategory_id
            ).filter(
              SubcategoryModel.category_id == data.category_id  
            ).first()
        if not subcategory:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Sub Category Not Found")
        
        # tag is not mandatory field
        existing_tag_name_list = ast.literal_eval(data.tags)
        if(len(existing_tag_name_list) > 0):
            for tag_name in existing_tag_name_list:
                tag = db.query(TagModel).filter(TagModel.tag_name == tag_name).first()
                if not tag:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Tag Not Found")
            final_tag_name_list = existing_tag_name_list.copy()
                
        new_tag_name_list = ast.literal_eval(data.new_tag)
        if(len(new_tag_name_list) > 0):
            new_tag_name_list.append('newTagRequested')
            final_tag_name_list = new_tag_name_list.copy()
        
        new_article_slug = data.title_en.lower().replace(" ", "-")
        
        new_article = ArticleModel(
            user_id=current_user.user_id,
            email=user_email, 
            category_id=data.category_id,
            subcategory_id=data.subcategory_id,
            title_en=data.title_en,
            title_bn=data.title_bn,
            subtitle_en=data.subtitle_en,
            subtitle_bn=data.subtitle_bn,
            content_en=data.content_en,
            content_bn=data.content_bn,
            cover_img_link=data.cover_img_link,
            cover_img_cap_en=data.cover_img_cap_en,
            cover_img_cap_bn=data.cover_img_cap_bn,
            article_status="under_review_new",
            article_slug=new_article_slug,
            tags=final_tag_name_list
        )
        db.add(new_article)
        db.commit()
        db.refresh(new_article)

        # entry also will go to ArticleSubmissionModel
        # we will assign the articles to the editors RANDOMLY
        editors, category_editors_ids = get_editor_by_category_id(data.category_id, db)
        random_editor = random.choice(editors)

        new_article_submission = ArticleSubmissionModel(
            article_id = new_article.article_id,
            author_id = current_user.user_id,
            author_email = user_email,
            editor_id = random_editor.editor_id,
            editor_email = random_editor.user_email,
            article_status = "under_review_new",
            submitted_at = datetime.now(),
        )
        db.add(new_article_submission)
        db.commit()
        db.refresh(new_article_submission)
        # entry will also go to Author and Editor Notification Model

        return {"msg": f"new article sent for review to: {random_editor.user_email}"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )

def get_unreviewed_article_list_by_editor(request: Request, 
                                editor_email: str,
                                page: int,
                                limit: int,
                                db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db) 
        
        allowed_roles = [1260, 1453] # editor_role = 1260, sadmin_role = 1453

        # checking if user is either correct editor or sadmin
        if 1260 in user_role_list:
            isCorrectEditor = editor_email == user_email
            if not isCorrectEditor:
                raise HTTPException(status_code=403, detail="User not authorized to see this information !") 
            
        if not any(item in user_role_list for item in allowed_roles):
            raise HTTPException(status_code=403, detail="User not authorized to see this information !") 
        
        # unRevArticleSub = db.query(ArticleSubmissionModel).filter(
        #     ArticleSubmissionModel.editor_email == editor_email
        # ).filter(
        #     ArticleSubmissionModel.article_status == "under_review_new"
        # ).all()

        offset = (page - 1) * limit
        unRevArticleSub = db.query(ArticleSubmissionModel).filter(
        ArticleSubmissionModel.editor_email == editor_email,
        ArticleSubmissionModel.article_status == "under_review_new"
        ).offset(offset).limit(limit).all()

        total_article_count = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.editor_email == editor_email,
            ArticleSubmissionModel.article_status == "under_review_new"
            ).count()


        unRev_article_id_list = []
        unRev_article_obj_list = []
        for submission in unRevArticleSub:
            unRev_article_id_list.append(submission.article_id)
            
            article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == submission.article_id
            ).first()

            # get author details
            article_author = db.query(UserModel).filter(
                UserModel.email == article_obj.email
            ).first()

            # category and subcategory name
            category = db.query(CategoryModel).filter(
                CategoryModel.category_id ==article_obj.category_id).first()
            category_name = category.category_name

            subcategory = db.query(SubcategoryModel).filter(
                SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
            subcategory_name = subcategory.subcategory_name
            
            article = UnrevArticleResponse(
                article_id=article_obj.article_id,

                author_email=article_obj.email,
                author_firstname=article_author.first_name,
                author_lastname=article_author.last_name,
                author_image_url=article_author.image_url,

                editor_email=submission.editor_email,
                article_status=submission.article_status,
                
                submitted_at=submission.submitted_at,
                decision_comment=submission.decision_comment,
                decision_comment_at=submission.decision_comment_at,
                sent_for_edit_at=submission.sent_for_edit_at,
                resubmitted_at=submission.resubmitted_at,
                
                category_id=article_obj.category_id,
                subcategory_id=article_obj.subcategory_id,
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

                status=article_obj.article_status
            )
            unRev_article_obj_list.append(article)

        # return unRevArticleSub
        # return unRev_article_id_list
        return total_article_count, unRev_article_obj_list
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )