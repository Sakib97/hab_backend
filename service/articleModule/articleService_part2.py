from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.articleRequest import EditArticleRequest
from response.articleResponse import ApprovedArticleResponse, HistoryArticleForListResponse, \
HistoryArticleDetailsResponse
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
        if str(article_obj.article_status).startswith("hidden"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article is currently unavailable !")

        
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

def get_article_by_email(request: Request,user_type: str,
                         email: str, page: int, limit:int, db: Session):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db) 
        
        # check if user is valid
        if user_email != email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user email !")
        
        # editor= 1260, sadmin = 1453, author = 1203
        allowed_roles = [1260, 1453, 1203] 
        if not any(role in user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        # check if user_type is valid
        if user_type not in ["editor", "author", "sadmin"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user type !")
        
        offset = (page - 1) * limit

        if user_type == "author":
            all_articles = db.query(ArticleModel).filter(
                ArticleModel.email == user_email
            ).order_by(desc(ArticleModel.article_id)).offset(offset).limit(limit).all()

            total_articles_count = db.query(ArticleModel).filter(
                ArticleModel.email == user_email
            ).count()

            historyArticleList = []
            for article_obj in all_articles:
                # published time info
                article_submission = db.query(ArticleSubmissionModel).filter(
                    ArticleSubmissionModel.article_id == article_obj.article_id
                        ).first()
                # category and subcategory name
                category = db.query(CategoryModel).filter(
                    CategoryModel.category_id ==article_obj.category_id).first()
                category_name = category.category_name
                subcategory = db.query(SubcategoryModel).filter(
                    SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
                subcategory_name = subcategory.subcategory_name

                submission_time = article_submission.submitted_at if article_submission else None
                if not submission_time:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Submission time not found !")

                processedArtricle =  HistoryArticleForListResponse(
                    article_id=article_obj.article_id,
                    title_en=article_obj.title_en,
                    subtitle_en=article_obj.subtitle_en,
                    cover_img_link=article_obj.cover_img_link,
                    article_status=article_obj.article_status,
                    submitted_at=str(submission_time),
                    category_name=category_name,
                    subcategory_name=subcategory_name
                )
                historyArticleList.append(processedArtricle)
            return total_articles_count, historyArticleList

        if user_type == "editor":
            all_article_submissions = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.editor_email == user_email
        ).order_by(desc(ArticleSubmissionModel.article_id)).offset(offset).limit(limit).all()
        
            total_articles_count = db.query(ArticleSubmissionModel).filter(
                ArticleSubmissionModel.editor_email == user_email
            ).count()

            historyArticleList = []
            for article_submission_obj in all_article_submissions:
                article_obj = db.query(ArticleModel).filter(
                    ArticleModel.article_id == article_submission_obj.article_id
                ).first()
                if not article_obj:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
                # category and subcategory name
                category = db.query(CategoryModel).filter(
                    CategoryModel.category_id ==article_obj.category_id).first()
                category_name = category.category_name
                subcategory = db.query(SubcategoryModel).filter(
                    SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
                subcategory_name = subcategory.subcategory_name

                # published time info
                submission_time = article_submission_obj.submitted_at if article_submission_obj else None
                if not submission_time:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Submission time not found !")

                processedArtricle =  HistoryArticleForListResponse(
                    article_id=article_obj.article_id,
                    title_en=article_obj.title_en,
                    subtitle_en=article_obj.subtitle_en,
                    cover_img_link=article_obj.cover_img_link,
                    article_status=article_obj.article_status,
                    submitted_at=str(submission_time),
                    category_name=category_name,
                    subcategory_name=subcategory_name
                )
                historyArticleList.append(processedArtricle)

            return total_articles_count, historyArticleList
        
        return 0, []

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# this is for Article History Purpose
def get_any_article_by_id(request: Request,article_id: int,
                        db: Session):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        # check if user is valid
        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user!")
        
        # editor= 1260, sadmin = 1453, author = 1203
        allowed_roles = [1260, 1453, 1203]
        if not any(role in user_role_list for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == article_id
            ).first()
        if not article_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        # check is valid user is accessing this api
        if user_email != article_obj.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User not authorized to access this endpoint !")
        
        # category and subcategory name
        category = db.query(CategoryModel).filter(
            CategoryModel.category_id ==article_obj.category_id).first()
        category_name = category.category_name
        subcategory = db.query(SubcategoryModel).filter(
            SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
        subcategory_name = subcategory.subcategory_name
        
        # article_editor = db.query(UserModel).filter(
        #     UserModel.email == article_obj.email
        # ).first()
        
        # article submission
        article_submission = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.article_id == article_obj.article_id
        ).first()
        if not article_submission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Submission not found !")

        # editor info
        article_editor = db.query(UserModel).filter(
            UserModel.email == article_submission.editor_email
        ).first()
        editor_firstname = article_editor.first_name
        editor_lastname = article_editor.last_name

        submitted_at = str(article_submission.submitted_at)
        published_at = str(article_submission.published_at)
        rejected_at = str(article_submission.rejected_at)
        decision_comment = article_submission.decision_comment if article_submission.decision_comment else ""

        sent_for_edit_at = str(article_submission.sent_for_edit_at)
        resubmitted_at = str(article_submission.resubmitted_at)

        
        article = HistoryArticleDetailsResponse(
            article_id=article_obj.article_id,
            title_en=article_obj.title_en,
            subtitle_en=article_obj.subtitle_en,
            category_name=category_name,
            subcategory_name=subcategory_name,
            article_status=article_obj.article_status,

            editor_email=article_submission.editor_email,
            editor_firstname=editor_firstname,
            editor_lastname=editor_lastname,

            submitted_at=submitted_at,
            published_at=published_at,
            rejected_at=rejected_at,
            decision_comment=decision_comment,
            
            sent_for_edit_at=sent_for_edit_at,
            resubmitted_at=resubmitted_at
             
        )
        return article
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )


def get_sent_for_edit_article_by_id(request: Request,
                                    article_id: int,
                                    # article_status: str,
                                    db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        allowed_roles = [1203, 1453] # author_role = 1260, sadmin_role = 1453
        
        if not any(item in user_role_list for item in allowed_roles):
            raise HTTPException(status_code=403, detail="User not authorized to see this information !")
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == article_id
            ).first()
        if not article_obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        # see if correct author is accessing his/her article
        if user_email != article_obj.email:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You do not have access to see this information !")

        if not str(article_obj.article_status).startswith("sent_for_edit"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Article is not editable !")

        # get category and subcategory name
        category = db.query(CategoryModel).filter(
            CategoryModel.category_id ==article_obj.category_id).first()
        category_name = category.category_name

        subcategory = db.query(SubcategoryModel).filter(
            SubcategoryModel.subcategory_id ==article_obj.subcategory_id).first()
        subcategory_name = subcategory.subcategory_name

        # article submission to get the editor email, cause we 
        # will send the article back to the editor who requested edit
        article_submission = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.article_id == article_obj.article_id
        ).first()
        if not article_submission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Submission not found !")

        # editor info
        article_editor = db.query(UserModel).filter(
            UserModel.email == article_submission.editor_email
        ).first()
        editor_firstname = article_editor.first_name
        editor_lastname = article_editor.last_name

        return article_obj, category_name, subcategory_name, article_submission.editor_email, editor_firstname, editor_lastname
    
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )


# This is for when author submits his edits, 
# as requested by editor
def edit_article_by_id(request: Request, 
                 editArticleRequest: EditArticleRequest,
                article_id: int,db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == article_id
            ).first()
        if not article_obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        # see if correct author is accessing his/her article
        if user_email != article_obj.email:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You do not have access to see this information !")

        if not str(article_obj.article_status).startswith("sent_for_edit"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Article is not editable !")
        
        # actual updates
        message = []
        # edit title
        if editArticleRequest.title_en:
            article_obj.title_en = editArticleRequest.title_en
            article_obj.article_slug = slugify(editArticleRequest.title_en)
            message.append("Edit has title_en")            
        else:
            message.append("Edit doesn't have title_en")
        
        if editArticleRequest.title_bn:
            article_obj.title_bn = editArticleRequest.title_bn
            message.append("Edit has title_bn")            
        else:
            message.append("Edit doesn't have title_bn")

        # edit subtitle
        if editArticleRequest.subtitle_en:
            article_obj.subtitle_en = editArticleRequest.subtitle_en
            message.append("Edit has subtitle_en")            
        else:
            message.append("Edit doesn't have subtitle_en")
        
        if editArticleRequest.subtitle_bn:
            article_obj.subtitle_bn = editArticleRequest.subtitle_bn
            message.append("Edit has subtitle_bn")            
        else:
            message.append("Edit doesn't have subtitle_bn")
        
        # edit content
        if editArticleRequest.content_en:
            article_obj.content_en = editArticleRequest.content_en
            message.append("Edit has content_en")            
        else:
            message.append("Edit doesn't have content_en")
        
        if editArticleRequest.content_bn:
            article_obj.content_bn = editArticleRequest.content_bn
            message.append("Edit has content_bn")
        else:
            message.append("Edit doesn't have content_bn")
        
        # edit cover img cap
        if editArticleRequest.cover_img_cap_en:
            article_obj.cover_img_cap_en = editArticleRequest.cover_img_cap_en
            message.append("Edit has cover_img_cap_en")            
        else:
            message.append("Edit doesn't have cover_img_cap_en")
        
        if editArticleRequest.cover_img_cap_bn:
            article_obj.cover_img_cap_bn = editArticleRequest.cover_img_cap_bn
            message.append("Edit has cover_img_cap_bn")
        else:
            message.append("Edit doesn't have cover_img_cap_bn")

        # edit cover img link
        if editArticleRequest.cover_img_link:
            article_obj.cover_img_link = editArticleRequest.cover_img_link
            message.append("Edit has cover_img_link")
        else:
            message.append("Edit doesn't have cover_img_link")
        
        # tags and new_tag
        if editArticleRequest.tags:
            existing_tag_name_list = ast.literal_eval(editArticleRequest.tags)
            if(len(existing_tag_name_list) > 0):
                for tag_name in existing_tag_name_list:
                    tag = db.query(TagModel).filter(TagModel.tag_name == tag_name).first()
                    if not tag:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Tag Not Found")
                final_tag_name_list = existing_tag_name_list.copy()
                article_obj.tags = str(final_tag_name_list)
                message.append("Edit has tags")
        else:
            message.append("Edit doesn't have tags")
        
        if editArticleRequest.new_tag:
            new_tag_name_list = ast.literal_eval(editArticleRequest.new_tag)
            if(len(new_tag_name_list) > 0):
                new_tag_name_list.append('newTagRequested')
                final_tag_name_list = new_tag_name_list.copy()
                article_obj.tags = str(final_tag_name_list)
                message.append("Edit has new_tags")
        else:
            message.append("Edit doesn't have new_tags")
        
        # Update article status
        # current article_status is like sent_for_edit_1 / sent_for_edit_2 etc.
        # first seperate number, then add to new status
        edit_number = str(article_obj.article_status).split('_')[-1]
        article_obj.article_status = f"under_review_edit_{edit_number}"

        # Commit changes and refresh the article
        db.commit()
        db.refresh(article_obj)

        # edit in article submission table
        article_submission = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.article_id == article_obj.article_id
        ).first()
        if not article_submission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Submission not found !")
        
        # see if DB editor matches with editor sent with requ
        if editArticleRequest.editor_email != article_submission.editor_email:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="DB editor & request editor Mismatch!")
        # check status
        if not str(article_submission.article_status).startswith("sent_for_edit"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Article submission is not editable !")
        
        article_submission.article_status = f"under_review_edit_{edit_number}"
        current_resubmitted_at_time_list = ast.literal_eval(article_submission.resubmitted_at)
        if isinstance(current_resubmitted_at_time_list, list):
            # append this edit request's time
            current_resubmitted_at_time_list.append(  str(datetime.now()) )
            # update DB
            article_submission.resubmitted_at = str(current_resubmitted_at_time_list)
        else:
            article_submission.resubmitted_at = str([ str(datetime.now()) ]) 
        
        db.commit()
        db.refresh(article_submission)

        # new entry in editor notification model
        notif_text = f"""You have a <b> Edited </b> article review request from 
        <b> {current_user.first_name} {current_user.last_name} </b> 
        on category: <b> {editArticleRequest.category_name} </b> 
        and subcategory: <b> {editArticleRequest.subcategory_name} </b> <br> 
        Article Title: <b> {article_obj.title_en} </b>"""

        new_editor_notification = EditorNotificationModel(
            editor_email=editArticleRequest.editor_email,
            notification_title="Edited Article Review Request !",
            notification_title_color="blue",
            notification_text=notif_text,
            notification_type=f"edit_{edit_number}_article_review_request_article_id_{article_obj.article_id}",
            notification_icon="""<i class="fa-solid fa-file-circle-exclamation"></i>""",
            # <i className="fa-solid fa-file-circle-exclamation"></i>
            is_read=False,
            notification_time=datetime.now(),
            notification_link=f"/editor_dashboard/review/article-review/{article_obj.article_id}"
        )

        db.add(new_editor_notification)
        db.commit()
        db.refresh(new_editor_notification)

        return message

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )