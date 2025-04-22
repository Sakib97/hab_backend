from model.articleModel import TagModel, CategoryModel, SubcategoryModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from request.categoryRequest import CreateTagRequest, CreateCategoryRequest, CreateSubCategoryRequest
from service.userModule.userService import get_current_user_profile
from model.userModel import UserRoleModel
import ast
from service.common.roleFinder import get_role_list
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List, Optional

# this create can only be done by Super Admin
# so we need to check if the request is coming from him
# async def create_category(request: Request, addCatReq: CreateCategoryRequest, db: Session = Depends(get_db)):
async def create_category(request: Request,
                      addCatReq: CreateCategoryRequest,
                      db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        
        user_role, role_list = get_role_list(user_email, db)

        # checking if user is sadmin
        sadmin_role = 1453
        if sadmin_role not in role_list:
            raise HTTPException(status_code=409, detail="User not authorized to make this change !") 

        category = db.query(CategoryModel).filter(CategoryModel.category_name == addCatReq.category_name).first()
        if category:
            raise HTTPException(status_code=409, detail="Category already exists !")

        new_category = CategoryModel(
             category_name=addCatReq.category_name,
             category_slug=addCatReq.category_slug,
             category_order=addCatReq.category_order,
             is_enabled=True
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return {"msg": "new category created"}


    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

# also can only be created by sadmin
async def create_subcategory(request: Request, addSubCatReq: CreateSubCategoryRequest, db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role, role_list = get_role_list(user_email, db)

        sadmin_role = 1453
        if sadmin_role not in role_list:
            raise HTTPException(status_code=409, detail="User not authorized to make this change !") 
        
        # check if category (id and name) specified in addSubCatReq is in Category table or not
        # subcat name have to be unique
        category = db.query(CategoryModel).filter(CategoryModel.category_id == addSubCatReq.category_id).first()
        if not category or category.category_name != addSubCatReq.category_name:
            raise HTTPException(status_code=409, detail="Category doesn't exist !")
        
        subcategory = db.query(SubcategoryModel).filter(SubcategoryModel.subcategory_name == addSubCatReq.subcategory_name).first()
        if subcategory:
            raise HTTPException(status_code=409, detail="SubCategory already exists !")
        
        new_subcategory = SubcategoryModel(
             subcategory_name=addSubCatReq.subcategory_name,
             category_id=addSubCatReq.category_id,
             category_name=addSubCatReq.category_name,
             subcategory_slug=addSubCatReq.subcategory_slug,
             subcategory_order=addSubCatReq.subcategory_order,
             is_enabled=True
        )

        db.add(new_subcategory)
        db.commit()
        db.refresh(new_subcategory)

        return {"msg": "new subcategory created"}

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )
    
async def create_tag(request: Request,
                      addTagReq: CreateTagRequest,
                      db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role, user_role_list = get_role_list(user_email, db)

        # sadmin, editor, sub-editor can create tags
        authorized_role_list = [1453,1260,1444]
        
        # Convert to sets and check for intersection
        # If the intersection is non-empty, it evaluates to True; 
        # otherwise, False.
        if set(user_role_list) & set(authorized_role_list):
            tag = db.query(TagModel).filter(TagModel.tag_name == addTagReq.tag_name).first()
            if tag:
                raise HTTPException(status_code=409, detail="Tag already exists !")

            new_tag = TagModel(
                tag_name=addTagReq.tag_name,
                tag_slug=addTagReq.tag_slug
            )
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)     

            return {"msg": "new tag created"}       
        else:
            raise HTTPException(status_code=409, detail="User not authorized to make this change !") 

    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )

async def fetch_subcategory_by_cat_id_or_slug(db, 
                                            category_slug:  Optional[str]  = None,
                                            category_id:  Optional[int] = None, 
                                            slug_or_id:  Optional[str] = None,
                                              ) -> List[SubcategoryModel]:
    try:
        target_category_id: Optional[int] = None
        if slug_or_id == "slug":
            if not category_slug:
                raise HTTPException(status_code=400, detail="category_slug is required")  
            # check if category slug is valid
            category = db.query(CategoryModel).filter(CategoryModel.category_slug == category_slug).first()
            if not category:
                raise HTTPException(status_code=409, detail="Category doesn't exist !")
            
            target_category_id = category.category_id

        elif slug_or_id == "id":
            if category_id is None: # Check specifically for None, as 0 is a valid ID but falsy
                raise HTTPException(status_code=400, detail="category_id is required")
            
            # check if category id is valid
            category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
            if not category:
                raise HTTPException(status_code=409, detail="Category doesn't exist !")
            
            target_category_id = category_id
            
        else:
            raise HTTPException(status_code=409, detail="Invalid value for slug_or_id. Must be 'slug' or 'id'!")

        # Fetch subcategories using the determined category ID
        # Ensure target_category_id was set (should always be if no exception raised above)
        if target_category_id is None:
             # This case should technically be unreachable if logic above is correct
             raise HTTPException(status_code=500, detail="Internal error: Failed to determine category ID.")

        subcategories = db.query(SubcategoryModel).filter(SubcategoryModel.category_id == target_category_id).all()

        if not subcategories:
            raise HTTPException(status_code=404, detail="No subcategories found for this category.")
        
        # list of subcategories with their names, orders and slugs
        # also is_enabled = True
        subcategories = [
            {
                "subcategory_name": subcategory.subcategory_name,
                "subcategory_order": subcategory.subcategory_order,
                "subcategory_slug": subcategory.subcategory_slug
            }
            for subcategory in subcategories if subcategory.is_enabled
        ]

        return subcategories


    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )