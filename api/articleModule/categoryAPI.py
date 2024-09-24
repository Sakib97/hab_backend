from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated, List
from core.database import get_db
from service.articleModule.categoryService import create_category, create_subcategory
from core.jwtHandler import JWTBearer
from request.categoryRequest import CreateCategoryRequest,CreateSubCategoryRequest
from response.categoryResponse import CategoryResponse, SubCategoryResponse
from model.articleModel import CategoryModel, SubcategoryModel

category_router = APIRouter(
    prefix="/category", 
    tags=["Category"])

# create category
@category_router.post("/create_category", dependencies=[Depends(JWTBearer())],status_code=status.HTTP_201_CREATED)
async def create_menu(request: Request,
                      categoryRequest: CreateCategoryRequest,
                      db: Session = Depends(get_db)):
    response = await create_category(request,categoryRequest,db)
    return response

# get all category
@category_router.get("/get_all_cat", response_model=List[CategoryResponse] ,status_code=status.HTTP_200_OK)
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
@category_router.get("/get_all_subcat", response_model=List[SubCategoryResponse] ,status_code=status.HTTP_200_OK)
async def get_all_subcategory(db: Session = Depends(get_db)):
    subcats = db.query(SubcategoryModel).all()
    return subcats

