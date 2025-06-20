from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated, List
from core.database import get_db
from service.articleModule.categoryService import create_tag, create_category, create_subcategory, \
fetch_subcategory_by_cat_id_or_slug, get_all_cats_by_mail
from core.jwtHandler import JWTBearer
from request.categoryRequest import CreateTagRequest, CreateCategoryRequest,CreateSubCategoryRequest
from response.categoryResponse import TagResponse, CategoryResponse, SubCategoryResponse
from model.articleModel import TagModel, CategoryModel, SubcategoryModel

category_router = APIRouter(
    prefix="/category", 
    tags=["Category"])

# create category
@category_router.post("/create_category", 
                      dependencies=[Depends(JWTBearer())],
                      status_code=status.HTTP_201_CREATED)
async def create_menu(request: Request,
                      categoryRequest: CreateCategoryRequest,
                      db: Session = Depends(get_db)):
    response = await create_category(request,categoryRequest,db)
    return response

# get all category
@category_router.get("/get_all_cat", 
                     response_model=List[CategoryResponse] ,
                     status_code=status.HTTP_200_OK)
async def get_all_category(db: Session = Depends(get_db)):
    cats = db.query(CategoryModel).all()
    return cats

# create subcategory
@category_router.post("/create_subcategory", dependencies=[Depends(JWTBearer())],status_code=status.HTTP_201_CREATED)
async def create_submenu(request: Request,
                            subcategoryRequest: CreateSubCategoryRequest,
                             db: Session = Depends(get_db)):
    response = await create_subcategory(request,subcategoryRequest,db)
    return response

# get all sub category
@category_router.get("/get_all_subcat", 
                     response_model=List[SubCategoryResponse] ,
                     status_code=status.HTTP_200_OK)
async def get_all_subcategory(db: Session = Depends(get_db)):
    subcats = db.query(SubcategoryModel).all()
    return subcats

# create tag
@category_router.post("/create_tag", dependencies=[Depends(JWTBearer())],status_code=status.HTTP_201_CREATED)
async def tag_creation(request: Request,
                      tagRequest: CreateTagRequest,
                      db: Session = Depends(get_db)):
    response = await create_tag(request,tagRequest,db)
    return response

# get all tags
@category_router.get("/get_all_tag", response_model=List[TagResponse] ,status_code=status.HTTP_200_OK)
async def get_all_tag(db: Session = Depends(get_db)):
    tags = db.query(TagModel).all()
    return tags

# get subcategory by category id or category slug
@category_router.get("/get_subcat_by_cat_slug/{category_slug}",
                     status_code=status.HTTP_200_OK)
async def get_subcategory_by_cat_id_or_slug(
                                            category_slug: str,
                                            db: Session = Depends(get_db)):
    subcats = await fetch_subcategory_by_cat_id_or_slug(category_slug=category_slug, db=db, slug_or_id="slug")
    # return {"subcats": subcats}
    return subcats

# get all cat and corresponding subcat by user email
@category_router.get("/get_all_cat_subcat_by_email/{user_type}/{email}", 
                     dependencies=[Depends(JWTBearer())],
                     status_code=status.HTTP_200_OK)
async def get_all_cat_subcat_by_user_email(
                                            request: Request,
                                            user_type: str,
                                            email: str,
                                            db: Session = Depends(get_db)):
    all_cats = get_all_cats_by_mail(request=request,
                                    user_type=user_type,
                                    email=email,
                                    db=db)
    return all_cats