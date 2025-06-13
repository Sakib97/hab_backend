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


# async def create_article(request: Request,
#                          data: CreateArticleRequest,
#                          db):
#     try:
#         current_user, user_email, exp = get_current_user_profile(request, db)
        
#         # check if category_id, subcategory_id and tag_ids are valid
#         # category is mandatory field
#         category = db.query(CategoryModel).filter(CategoryModel.category_id == data.category_id).first()
#         if not category:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                         detail="Category Not Found")
        
#         # sub-category is mandatory field
#         subcategory = db.query(SubcategoryModel).filter(
#             SubcategoryModel.subcategory_id == data.subcategory_id
#             ).filter(
#               SubcategoryModel.category_id == data.category_id  
#             ).first()
#         if not subcategory:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                         detail="Sub Category Not Found")
        
#         # tag is not mandatory field
#         existing_tag_name_list = ast.literal_eval(data.tags)
#         if(len(existing_tag_name_list) > 0):
#             for tag_name in existing_tag_name_list:
#                 tag = db.query(TagModel).filter(TagModel.tag_name == tag_name).first()
#                 if not tag:
#                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                         detail="Tag Not Found")
#             final_tag_name_list = existing_tag_name_list.copy()
                
#         new_tag_name_list = ast.literal_eval(data.new_tag)
#         if(len(new_tag_name_list) > 0):
#             new_tag_name_list.append('newTagRequested')
#             final_tag_name_list = new_tag_name_list.copy()
        
#         # new_article_slug = data.title_en.lower().replace(" ", "-")
#         new_article_slug = slugify(data.title_en)
        
#         new_article = ArticleModel(
#             user_id=current_user.user_id,
#             email=user_email, 
#             category_id=data.category_id,
#             subcategory_id=data.subcategory_id,
#             title_en=data.title_en,
#             title_bn=data.title_bn,
#             subtitle_en=data.subtitle_en,
#             subtitle_bn=data.subtitle_bn,
#             content_en=data.content_en,
#             content_bn=data.content_bn,
#             cover_img_link=data.cover_img_link,
#             cover_img_cap_en=data.cover_img_cap_en,
#             cover_img_cap_bn=data.cover_img_cap_bn,
#             article_status="under_review_new",
#             article_slug=new_article_slug,
#             tags=str(final_tag_name_list)
#         )
#         db.add(new_article)
#         db.commit()
#         db.refresh(new_article)

#         # entry also will go to ArticleSubmissionModel
#         # we will assign the articles to the editors RANDOMLY
#         editors, category_editors_ids = get_editor_by_category_id(data.category_id, db)
#         random_editor = random.choice(editors)

#         new_article_submission = ArticleSubmissionModel(
#             article_id = new_article.article_id,
#             author_id = current_user.user_id,
#             author_email = user_email,
#             editor_id = random_editor.editor_id,
#             editor_email = random_editor.user_email,
#             article_status = "under_review_new",
#             submitted_at = datetime.now(),
#         )
#         db.add(new_article_submission)
#         db.commit()
#         db.refresh(new_article_submission)

#         # entry will also go to Author and Editor Notification Model
#         notif_text = f"""You have a new article review request from 
#         <b> {current_user.first_name} {current_user.last_name} </b> 
#         on category: <b> {category.category_name} </b> 
#         and subcategory: <b> {subcategory.subcategory_name} </b> <br> 
#         Article Title: <b> {new_article.title_en} </b>"""
        
#         new_editor_notification = EditorNotificationModel(
#             editor_email=random_editor.user_email,
#             notification_title="New Article Review Request !",
#             notification_title_color="blue",
#             notification_text=notif_text,
#             notification_type=f"new_article_review_request_article_id_{new_article.article_id}",
#             notification_icon="""<i class="fa-solid fa-file-circle-exclamation"></i>""",
#             # <i className="fa-solid fa-file-circle-exclamation"></i>
#             is_read=False,
#             notification_time=datetime.now(),
#             notification_link=f"/editor_dashboard/review/article-review/{new_article.article_id}"
#         )

#         db.add(new_editor_notification)
#         db.commit()
#         db.refresh(new_editor_notification)

#         return {"msg": f"new article sent for review to: {get_user_name_from_mail(random_editor.user_email, db)}_{xor_encode(random_editor.user_email)}"}

#     except Exception as e:
#         raise HTTPException(
#                 status_code=e.status_code,
#                 detail=e.detail
#                 )


async def create_article(request: Request, data: CreateArticleRequest, db):
    try:
        # Pre-declare variables to use later
        response_msg = None

        with db.begin():  # Entire block is transactional
            current_user, user_email, exp = get_current_user_profile(request, db)

            # Validate Category and Subcategory
            category = db.query(CategoryModel).filter(CategoryModel.category_id == data.category_id).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category Not Found")

            subcategory = db.query(SubcategoryModel).filter(
                SubcategoryModel.subcategory_id == data.subcategory_id,
                SubcategoryModel.category_id == data.category_id
            ).first()
            if not subcategory:
                raise HTTPException(status_code=400, detail="Sub Category Not Found")

            # Process Tags
            final_tag_name_list = []
            existing_tag_name_list = ast.literal_eval(data.tags)
            if existing_tag_name_list:
                for tag_name in existing_tag_name_list:
                    tag = db.query(TagModel).filter(TagModel.tag_name == tag_name).first()
                    if not tag:
                        raise HTTPException(status_code=400, detail="Tag Not Found")
                final_tag_name_list = existing_tag_name_list.copy()

            new_tag_name_list = ast.literal_eval(data.new_tag)
            if new_tag_name_list:
                new_tag_name_list.append('newTagRequested')
                final_tag_name_list = new_tag_name_list.copy()

            # Create Article
            new_article_slug = slugify(data.title_en)
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
                tags=str(final_tag_name_list)
            )
            db.add(new_article)
            db.flush()  # Get article_id without committing

            # Assign Editor
            editors, category_editors_ids = get_editor_by_category_id(data.category_id, db)
            random_editor = random.choice(editors)

            new_article_submission = ArticleSubmissionModel(
                article_id=new_article.article_id,
                author_id=current_user.user_id,
                author_email=user_email,
                editor_id=random_editor.editor_id,
                editor_email=random_editor.user_email,
                article_status="under_review_new",
                submitted_at=datetime.now(),
            )
            db.add(new_article_submission)

            # Notify Editor
            notif_text = f"""You have a new article review request from 
            <b> {current_user.first_name} {current_user.last_name} </b> 
            on category: <b> {category.category_name} </b> 
            and subcategory: <b> {subcategory.subcategory_name} </b> <br> 
            Article Title: <b> {new_article.title_en} </b>"""

            new_editor_notification = EditorNotificationModel(
                editor_email=random_editor.user_email,
                notification_title="New Article Review Request !",
                notification_title_color="blue",
                notification_text=notif_text,
                notification_type=f"new_article_review_request_article_id_{new_article.article_id}",
                notification_icon="""<i class="fa-solid fa-file-circle-exclamation"></i>""",
                is_read=False,
                notification_time=datetime.now(),
                notification_link=f"/editor_dashboard/review/article-review/{new_article.article_id}"
            )
            db.add(new_editor_notification)

            # Prepare response message INSIDE the transaction
            response_msg = {
                "msg": f"new article sent for review to: {get_user_name_from_mail(random_editor.user_email, db)}_{xor_encode(random_editor.user_email)}"
            }

        # Return AFTER successful commit
        return response_msg

    except HTTPException as e:
        # Context manager auto-rolls back; no need for db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        
        offset = (page - 1) * limit
        unRevArticleSub = db.query(ArticleSubmissionModel).filter(
        ArticleSubmissionModel.editor_email == editor_email,
        # ArticleSubmissionModel.article_status == "under_review_new"
        ArticleSubmissionModel.article_status.startswith("under_review")
        ).order_by(desc(ArticleSubmissionModel.submitted_at)).offset(offset).limit(limit).all()
        # Sort by date in descending order

        total_article_count = db.query(ArticleSubmissionModel).filter(
            ArticleSubmissionModel.editor_email == editor_email,
            # ArticleSubmissionModel.article_status == "under_review_new"
            ArticleSubmissionModel.article_status.startswith("under_review")

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

        return total_article_count, unRev_article_obj_list
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

def add_tag_to_article(request: Request,
                       addTagReq: AddTagToArticleRequest, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db) 
        
        allowed_roles = [1260, 1453] # editor_role = 1260, sadmin_role = 1453

        if not any(item in user_role_list for item in allowed_roles):
            raise HTTPException(status_code=403, detail="User not authorized to see this information !") 
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == addTagReq.article_id
            ).first()
        if not article_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        existing_tags =  ast.literal_eval(article_obj.tags)
        if existing_tags[-1] == "newTagRequested":
            existing_tags = []

        new_tags = ast.literal_eval(addTagReq.tag_name)
        for tag in new_tags:
            if tag != "newTagRequested":
                existing_tags.append(tag)

        article_obj.tags = str(existing_tags)
        db.commit()
        db.refresh(article_obj)

        return {"msg": "tag added to article"}
        
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# this function is for getting article by 
# article_id (either unreviewed or rejected or sent_for_edit)
# this is for editor and sadmin
def get_article_by_article_id(request: Request,
                              article_id: int,
                              article_status: str,
                                db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        allowed_roles = [1260, 1453] # editor_role = 1260, sadmin_role = 1453
        
        if not any(item in user_role_list for item in allowed_roles):
            raise HTTPException(status_code=403, detail="User not authorized to see this information !")
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == article_id
            ).first()
        if not article_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Not Found !")
        
        # check if article status is valid
        if article_status != article_obj.article_status:
            if article_obj.article_status in ["approved", "rejected"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Article Already Reviewed !")
            if str(article_obj.article_status).startswith("sent_for_edit"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Article sent for edit !")
        
        # check is right editor is accessing the article 
        article_submission_obj = db.query(ArticleSubmissionModel).filter(
                ArticleSubmissionModel.article_id == article_id,
            ).first()
        if not article_submission_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Submission Not Found !")
        
        if article_submission_obj.editor_email != user_email:
            raise HTTPException(status_code=403, detail="User not authorized to see this information !")
        
        # get author details
        article_author = db.query(UserModel).filter(
            UserModel.email == article_obj.email
        ).first()

        # get category and subcategory name
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

                editor_email=article_submission_obj.editor_email,
                article_status=article_submission_obj.article_status,
                
                submitted_at=article_submission_obj.submitted_at,
                decision_comment=article_submission_obj.decision_comment,
                decision_comment_at=article_submission_obj.decision_comment_at,
                sent_for_edit_at=article_submission_obj.sent_for_edit_at,
                resubmitted_at=article_submission_obj.resubmitted_at,
                
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
        
        return article
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )


def approve_reject_resend_article(request: Request, action: str,  
                    approveArticleRequest: ApproveArticleRequest,db):

    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)
        allowed_roles = [1260, 1453] # editor_role = 1260, sadmin_role = 1453

        if not any(item in user_role_list for item in allowed_roles):
            raise HTTPException(status_code=403, detail="User not authorized to see this information !") 
        
        # get article by article id
        article_obj = db.query(ArticleModel).filter(
                ArticleModel.article_id == approveArticleRequest.article_id
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

        # article submission object
        article_submission_obj = db.query(ArticleSubmissionModel).filter(
                ArticleSubmissionModel.article_id == approveArticleRequest.article_id
            ).first()
        if not article_submission_obj:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article Submission Not Found !") 
        
        # if action is not in ["approved", "rejected", "sent_for_edit"]
        if action not in ["approved", "rejected", "sent_for_edit"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid action !")
        
        # see if correct editor accessing correct article
        if user_email != article_submission_obj.editor_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You don't have access to this information !")
        
        # only approve / reject / resend article if 
        # article is in "under_review_new" or "sent_for_edit"  status
        valid_status =  ["under_review", "sent_for_edit"]
        if not str(article_obj.article_status).startswith(valid_status[0]) :
            if not str(article_obj.article_status).startswith(valid_status[1]) :
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Article not in under review status !")
        
        # can reject or resend only if decision comment is given 
        # ("" or " " is not allowed)
        if action == "rejected" or action == "sent_for_edit":
            if  len(approveArticleRequest.decision_comment) == 0 or approveArticleRequest.decision_comment.isspace():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Decision comment is required !")
            
        # update article status in ARTICLE table
        if action == "rejected" or action == "approved":
            article_obj.article_status = action

        if action == "sent_for_edit":
            # check the no. of times the editor sent for edit:
            # first check current status
            curent_article_status = article_obj.article_status
            # if the current_status == "under_review_new", 
            # it's the 1st edit request, so new status = "sent_for_edit_1"
            if curent_article_status == "under_review_new":
                article_obj.article_status = "sent_for_edit_1"

            # if current_status contains "under_review_edit" part, 
            # sepetate the number associated with it, increment by 1,
            # and reappeand with "sent_for_edit" (ex. "sent_for_edit_2")
            # Signifies 2nd edit request
            elif "under_review_edit" in curent_article_status:
                split_string = curent_article_status.split('_')
                if len(split_string) > 1:
                    edit_request_number = int(split_string[-1])
                    edit_request_number += 1
                    final_status = "sent_for_edit" + "_" + str(edit_request_number)
                    article_obj.article_status = final_status
            
             
        db.commit()
        db.refresh(article_obj)
        
        if action == "approved":
            article_submission_obj.article_status = action
            article_submission_obj.published_at = datetime.now()
        else:
            if action == "rejected":
                article_submission_obj.rejected_at = datetime.now()
                article_submission_obj.article_status = action
                article_submission_obj.decision_comment = approveArticleRequest.decision_comment
                article_submission_obj.decision_comment_at = datetime.now()

            if action == "sent_for_edit":
                curent_article_sub_status = article_submission_obj.article_status
                
                if curent_article_sub_status == "under_review_new":
                    article_submission_obj.article_status = "sent_for_edit_1"
                    # time as list
                    article_submission_obj.sent_for_edit_at = str([ str(datetime.now()) ]) 
                    article_submission_obj.decision_comment =str([approveArticleRequest.decision_comment]) 
                
                elif "under_review_edit" in curent_article_sub_status:
                    split_string_sub = curent_article_sub_status.split('_')
                    if len(split_string_sub) > 1:
                        edit_request_number_sub = int(split_string_sub[-1])
                        edit_request_number_sub += 1
                        final_status_sub = "sent_for_edit" + "_" + str(edit_request_number_sub)
                        article_submission_obj.article_status = final_status_sub

                        # add sent for edit time, 
                        # sent_for_edit_at format : ["time1", "time2"..]
                        # first get current sent for edit time list
                        current_sent_for_edit_time_list = ast.literal_eval(article_submission_obj.sent_for_edit_at)
                        if isinstance(current_sent_for_edit_time_list, list):
                            # append this edit request's time
                            current_sent_for_edit_time_list.append(  str(datetime.now()) )
                            # update DB
                            article_submission_obj.sent_for_edit_at = str(current_sent_for_edit_time_list)
                        
                        # same for decision comment
                        currnet_decision_cmnt_list = ast.literal_eval(article_submission_obj.decision_comment)
                        if isinstance(currnet_decision_cmnt_list, list):
                            currnet_decision_cmnt_list.append(approveArticleRequest.decision_comment)
                            article_submission_obj.decision_comment = str(currnet_decision_cmnt_list)
                

        db.commit()
        db.refresh(article_submission_obj)

        # entry will also go to Author and Editor Notification Model
        notis_text = f"""Your article has been {action} by
        <b> {current_user.first_name} {current_user.last_name} </b> 
        ({current_user.email}) <br>
        on category: <b> {category_name} </b>
        and subcategory: <b> {subcategory_name} </b> <br>
        Article Title: <b> {article_obj.title_en} </b>"""
        notis_color = "green" if action == "approved" else "red" if action == "rejected" else "darkred" if action == "sent_for_edit" else "blue"
        notis_icon = """<i class="fa-solid fa-file-circle-check"></i>""" if action == "approved" \
        else """<i class="fa-solid fa-file-circle-xmark"></i>""" if action == "rejected" \
            else """<i class="fa-solid fa-file-circle-question"></i>""" if action == "sent_for_edit"\
                else """<i class="fa-solid fa-file-circle-exclamation"></i>"""
        
        if action == "approved":
            notif_link = f"/{slugify(category_name)}/{slugify(subcategory_name)}/article/{article_obj.article_id}/{article_obj.article_slug}"
        else: # else action == "rejected" or "sent_for_edit"
            notif_link = f"/profile/my_articles/details?a_id={article_obj.article_id}"

        new_author_notification = UserAuthorNotificationModel(
            user_email=article_obj.email,
            notification_title=f"Article Review Result - {action} !",
            notification_title_color=notis_color,
            notification_text=notis_text,
            notification_type=f"article_review_result_article_id_{article_obj.article_id}",
            notification_icon=notis_icon,
            is_read=False,
            notification_time=datetime.now(),
            notification_link=notif_link,
        )
        db.add(new_author_notification)
        db.commit()
        db.refresh(new_author_notification)

        return {"msg": f"Article {action} !"}
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )