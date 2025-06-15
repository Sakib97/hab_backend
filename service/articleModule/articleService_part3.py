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
from sqlalchemy import or_

def get_article_count_by_status(request: Request,
                                status: str,
                                user_type: str,
                                email: str, 
                                db: Session):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role_obj, user_role_list = get_role_list(user_email, db)

        # check if user is valid
        if user_email != email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid user email !")
        
        if user_type == "editor":
            user = db.query(EditorModel).filter(EditorModel.user_email == email).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid editor email !")
            # get all articles by this editor from ArticleSubmissionModel
            if status in ["under_review"]:
                articles = db.query(ArticleSubmissionModel).filter(
                    ArticleSubmissionModel.editor_email == email,
                    ArticleSubmissionModel.article_status.startswith(status)
                ).all()
                return len(articles)
            elif status == "reviewed": # approved or rejected
                articles_approved = db.query(ArticleSubmissionModel).filter(
                    ArticleSubmissionModel.editor_email == email,
                    ArticleSubmissionModel.article_status == "approved"
                ).all()
                articles_rejected = db.query(ArticleSubmissionModel).filter(
                    ArticleSubmissionModel.editor_email == email,
                    ArticleSubmissionModel.article_status == "rejected"
                ).all()
                return len(articles_approved) + len(articles_rejected)
        
        return 0

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

def get_published_art_list_by_cat_subcat(page: int,
                                        limit: int,
                                        catSlug: str,
                                        db: Session,
                                        subcatSlug: str = None):
    try:
        # Get category by slug
        category = db.query(CategoryModel).filter(
            CategoryModel.category_slug == catSlug
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        cat_id = category.category_id

        # Base query with joins
        query = db.query(
            ArticleModel.article_id,
            ArticleModel.title_en,
            ArticleModel.subtitle_en,
            ArticleModel.cover_img_link,
            CategoryModel.category_name,
            SubcategoryModel.subcategory_name
        ).join(
            CategoryModel, ArticleModel.category_id == CategoryModel.category_id
        ).outerjoin(
            SubcategoryModel, ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
        ).join(
            ArticleSubmissionModel, ArticleModel.article_id == ArticleSubmissionModel.article_id
        ).filter(
            ArticleModel.category_id == cat_id,
            ArticleModel.article_status == "approved"
        )

        # Filter by subcategory if provided
        if subcatSlug:
            subcategory = db.query(SubcategoryModel).filter(
                SubcategoryModel.subcategory_slug == subcatSlug
            ).first()
            if not subcategory:
                raise HTTPException(status_code=404, detail="Subcategory not found")
            subcat_id = subcategory.subcategory_id
            query = query.filter(ArticleModel.subcategory_id == subcat_id)

        # Always order by latest published
        query = query.order_by(ArticleSubmissionModel.published_at.desc())

        # Get total count before pagination
        all_articles_count = query.count()

        # Apply pagination
        articles = query.offset((page - 1) * limit).limit(limit).all()

        # Build article list with author info
        all_articles = []
        for article in articles:
            article_submission = db.query(ArticleSubmissionModel).filter(
                ArticleSubmissionModel.article_id == article.article_id
            ).first()
            if not article_submission:
                raise HTTPException(status_code=404, detail="Article submission not found")

            author = db.query(UserModel).filter(
                UserModel.email == article_submission.author_email
            ).first()
            if not author:
                raise HTTPException(status_code=404, detail="Author not found")

            all_articles.append({
                "article_id": article.article_id,
                "title_en": article.title_en,
                "subtitle_en": article.subtitle_en,
                "cover_img_link": article.cover_img_link,
                "author_firstname": author.first_name,
                "author_lastname": author.last_name,
                "published_at": article_submission.published_at,
                "category_name": article.category_name,
                "subcategory_name": article.subcategory_name
            })

        return all_articles, all_articles_count

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )
    
# get featured article list by category slug
'''
Requirements
    1. Return 5 articles.
    2. If any have is_featured=True:
        3. Sort by featured_priority (if available); 
            else by published_at desc.
        4. Fill remaining slots with latest non-featured articles.
    5. Ensure no duplicates.
    6. If none are featured, return 5 latest articles.
'''
def get_featured_article_list_by_cat(catSlug: str, 
                                     db, 
                                     limit: int = 5):
    try:
        # get category and subcategory by slug
        category = db.query(CategoryModel).filter(
            CategoryModel.category_slug == catSlug
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        cat_id = category.category_id

        # Step 1: Get featured articles
        featured_articles_query = db.query(
                ArticleModel.article_id,
                ArticleModel.title_en,
                ArticleModel.subtitle_en,
                ArticleModel.cover_img_link,
                CategoryModel.category_name,
                SubcategoryModel.subcategory_name,
                UserModel.first_name,
                UserModel.last_name,
                ArticleSubmissionModel.published_at
            ).select_from(ArticleModel).join(
                ArticleSubmissionModel,
                ArticleModel.article_id == ArticleSubmissionModel.article_id
            ).join(
                UserModel,
                UserModel.email == ArticleModel.email
            ).join(
                CategoryModel,
                ArticleModel.category_id == CategoryModel.category_id
            ).outerjoin(
                SubcategoryModel,
                ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
            ).filter(
                ArticleModel.category_id == cat_id,
                ArticleModel.is_featured == True,
                ArticleModel.article_status == "approved"
        )

        # Split based on whether priority is set or not
        featured_with_priority = featured_articles_query.filter(ArticleModel.featured_priority != None)\
            .order_by(ArticleModel.featured_priority.asc()).all()

        featured_without_priority = featured_articles_query.filter(ArticleModel.featured_priority == None)\
            .order_by(ArticleSubmissionModel.published_at.desc()).all()

        # Combine both lists
        final_featured = featured_with_priority + featured_without_priority
        final_featured = final_featured[:limit]  # take at most 5

        # If is_featured == true is fewer than `limit`, 
        # fetch latest non-featured articles to fill in
        if len(final_featured) < limit:
            # Get IDs of already selected articles to exclude
            featured_ids = [a.article_id for a in final_featured]

            remaining_needed = limit - len(final_featured)
            filler_articles = db.query(
                    ArticleModel.article_id,
                    ArticleModel.title_en,
                    ArticleModel.subtitle_en,
                    ArticleModel.cover_img_link,
                    CategoryModel.category_name,
                    SubcategoryModel.subcategory_name,
                    UserModel.first_name,
                    UserModel.last_name,
                    ArticleSubmissionModel.published_at
                ).select_from(ArticleModel).join(
                    ArticleSubmissionModel,
                    ArticleModel.article_id == ArticleSubmissionModel.article_id
                ).join(
                    UserModel,
                    UserModel.email == ArticleModel.email
                ).join(
                    CategoryModel,
                    ArticleModel.category_id == CategoryModel.category_id
                ).outerjoin(
                    SubcategoryModel,
                    ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
                ).filter(
                    ArticleModel.category_id == cat_id,
                    ArticleModel.article_status == "approved",
                    or_(ArticleModel.is_featured == False, 
                        ArticleModel.is_featured == None),
                    ~ArticleModel.article_id.in_(featured_ids) # Ensures no duplicates via exclusion with ~
            ).order_by(ArticleSubmissionModel.published_at.desc()).limit(remaining_needed).all()

            final_featured.extend(filler_articles)

        # If there were no featured articles at all
        if len(final_featured) == 0:
            final_featured = db.query(
                    ArticleModel.article_id,
                    ArticleModel.title_en,
                    ArticleModel.subtitle_en,
                    ArticleModel.cover_img_link,
                    CategoryModel.category_name,
                    SubcategoryModel.subcategory_name,
                    UserModel.first_name,
                    UserModel.last_name,
                    ArticleSubmissionModel.published_at
                ).select_from(ArticleModel).join(
                    ArticleSubmissionModel,
                    ArticleModel.article_id == ArticleSubmissionModel.article_id
                ).join(
                    UserModel,
                    UserModel.email == ArticleModel.email
                ).join(
                    CategoryModel,
                    ArticleModel.category_id == CategoryModel.category_id
                ).outerjoin(
                    SubcategoryModel,
                    ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
                ).filter(
                    ArticleModel.category_id == cat_id,
                    ArticleModel.article_status == "approved"
            ).order_by(ArticleSubmissionModel.published_at.desc()).limit(limit).all()
        
        return [
                {
                    "article_id": a.article_id,
                    "title_en": a.title_en,
                    "subtitle_en": a.subtitle_en,
                    "cover_img_link": a.cover_img_link,
                    "author_firstname": a.first_name,
                    "author_lastname": a.last_name,
                    "published_at": a.published_at,
                    "category_name": a.category_name,
                    "subcategory_name": a.subcategory_name
                }
                for a in final_featured
            ]
    
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# get articles by userSlug
def get_articles_by_userSlug(
    userSlug: str, 
    db: Session, 
    page: int, 
    limit: int
):
    try:
        # get user by slug
        user = db.query(UserModel).filter(
            UserModel.user_slug == userSlug
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # get articles by user email
        articles = db.query(
            ArticleModel.article_id,
            ArticleModel.title_en,
            ArticleModel.subtitle_en,
            ArticleModel.cover_img_link,
            ArticleSubmissionModel.published_at,
            CategoryModel.category_name,
            SubcategoryModel.subcategory_name
        ).join(
            ArticleSubmissionModel, 
            ArticleModel.article_id == ArticleSubmissionModel.article_id
        ).filter(
            ArticleSubmissionModel.author_email == user.email,
            ArticleModel.article_status == "approved"
        ).join(
                CategoryModel,
                ArticleModel.category_id == CategoryModel.category_id
        ).outerjoin(
                SubcategoryModel,
                ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
        ).order_by(
            desc(ArticleSubmissionModel.published_at)
        ).offset((page - 1) * limit).limit(limit).all()

        # article count
        article_count = db.query(
            ArticleModel.article_id
        ).join(
            ArticleSubmissionModel, 
            ArticleModel.article_id == ArticleSubmissionModel.article_id
        ).filter(
            ArticleSubmissionModel.author_email == user.email,
            ArticleModel.article_status == "approved"
        ).count()

        return {
            "articles": [
                {
                    "article_id": article.article_id,
                    "title": article.title_en,
                    "subtitle": article.subtitle_en,
                    "cover_img_link": article.cover_img_link,
                    "published_at": article.published_at,
                    "category_name": article.category_name,
                    "subcategory_name": article.subcategory_name
                }
                for article in articles
            ],
            "article_count": article_count
        }

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# get latest approved articles (top 4)
def get_latest_approved_articles(db: Session, 
                                 limit: int,
                                 catSlug: str = None):
    try:
        if catSlug is not None:        
            # get category and subcategory by slug
            category = db.query(CategoryModel).filter(
                CategoryModel.category_slug == catSlug
            ).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            cat_id = category.category_id
        
        articles = db.query(
            ArticleModel.article_id,
            ArticleModel.title_en,
            ArticleModel.subtitle_en,
            ArticleModel.cover_img_link,
            ArticleSubmissionModel.published_at,
            CategoryModel.category_name,
            SubcategoryModel.subcategory_name
        ).join(
            ArticleSubmissionModel, 
            ArticleModel.article_id == ArticleSubmissionModel.article_id
        ).join(
                CategoryModel,
                ArticleModel.category_id == CategoryModel.category_id
        ).outerjoin(
                SubcategoryModel,
                ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
        ).filter(
            ArticleModel.article_status == "approved",
            # If category slug is provided, filter by category
            (ArticleModel.category_id == cat_id) if catSlug else True
        ).order_by(
            desc(ArticleSubmissionModel.published_at)
        ).limit(limit).all()

        return [
            {
                "article_id": article.article_id,
                "title": article.title_en,
                "subtitle": article.subtitle_en,
                "cover_img_link": article.cover_img_link,
                "published_at": article.published_at,
                "category_name": article.category_name,
                "subcategory_name": article.subcategory_name
            }
            for article in articles
        ]

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# get featured articles (top 4)
def get_featured_articles(db: Session, limit: int = 4):
    try:
        # Step 1: Get featured articles
        featured_articles_query = db.query(
                ArticleModel.article_id,
                ArticleModel.title_en,
                ArticleModel.subtitle_en,
                ArticleModel.cover_img_link,
                CategoryModel.category_name,
                SubcategoryModel.subcategory_name,
                ArticleSubmissionModel.published_at
            ).select_from(ArticleModel).join(
                ArticleSubmissionModel,
                ArticleModel.article_id == ArticleSubmissionModel.article_id
            ).join(
                UserModel,
                UserModel.email == ArticleModel.email
            ).join(
                CategoryModel,
                ArticleModel.category_id == CategoryModel.category_id
            ).outerjoin(
                SubcategoryModel,
                ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
            ).filter(
                ArticleModel.is_featured == True,
                ArticleModel.article_status == "approved"
        )

        # Split based on whether priority is set or not
        featured_with_priority = featured_articles_query.filter(ArticleModel.featured_priority != None)\
            .order_by(ArticleModel.featured_priority.asc()).all()

        featured_without_priority = featured_articles_query.filter(ArticleModel.featured_priority == None)\
            .order_by(ArticleSubmissionModel.published_at.desc()).all()

        # Combine both lists
        final_featured = featured_with_priority + featured_without_priority
        final_featured = final_featured[:limit]  # take at most 5

        # If is_featured == true is fewer than `limit`, 
        # fetch latest non-featured articles to fill in
        if len(final_featured) < limit:
            # Get IDs of already selected articles to exclude
            featured_ids = [a.article_id for a in final_featured]

            remaining_needed = limit - len(final_featured)
            filler_articles = db.query(
                    ArticleModel.article_id,
                    ArticleModel.title_en,
                    ArticleModel.subtitle_en,
                    ArticleModel.cover_img_link,
                    CategoryModel.category_name,
                    SubcategoryModel.subcategory_name,
                    ArticleSubmissionModel.published_at
                ).select_from(ArticleModel).join(
                    ArticleSubmissionModel,
                    ArticleModel.article_id == ArticleSubmissionModel.article_id
                ).join(
                    UserModel,
                    UserModel.email == ArticleModel.email
                ).join(
                    CategoryModel,
                    ArticleModel.category_id == CategoryModel.category_id
                ).outerjoin(
                    SubcategoryModel,
                    ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
                ).filter(
                    ArticleModel.article_status == "approved",
                    or_(ArticleModel.is_featured == False, 
                        ArticleModel.is_featured == None),
                    ~ArticleModel.article_id.in_(featured_ids) # Ensures no duplicates via exclusion with ~
            ).order_by(ArticleSubmissionModel.published_at.desc()).limit(remaining_needed).all()

            final_featured.extend(filler_articles)

        # If there were no featured articles at all
        if len(final_featured) == 0:
            final_featured = db.query(
                    ArticleModel.article_id,
                    ArticleModel.title_en,
                    ArticleModel.subtitle_en,
                    ArticleModel.cover_img_link,
                    CategoryModel.category_name,
                    SubcategoryModel.subcategory_name,
                    ArticleSubmissionModel.published_at
                ).select_from(ArticleModel).join(
                    ArticleSubmissionModel,
                    ArticleModel.article_id == ArticleSubmissionModel.article_id
                ).join(
                    UserModel,
                    UserModel.email == ArticleModel.email
                ).join(
                    CategoryModel,
                    ArticleModel.category_id == CategoryModel.category_id
                ).outerjoin(
                    SubcategoryModel,
                    ArticleModel.subcategory_id == SubcategoryModel.subcategory_id
                ).filter(
                    ArticleModel.article_status == "approved"
            ).order_by(ArticleSubmissionModel.published_at.desc()).limit(limit).all()
        
        return [
                {
                    "article_id": a.article_id,
                    "title_en": a.title_en,
                    "subtitle_en": a.subtitle_en,
                    "cover_img_link": a.cover_img_link,
                    "published_at": a.published_at,
                    "category_name": a.category_name,
                    "subcategory_name": a.subcategory_name
                }
                for a in final_featured
            ]
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

        