# get category and subcategory names from their IDs
from sqlalchemy.orm import Session
from model.articleModel import CategoryModel, SubcategoryModel
from core.database import get_db
from fastapi import Depends, HTTPException, status

def get_cat_subcat_name(cat_id: int, subcat_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Retrieves the category and subcategory names based on their IDs.

    Args:
        cat_id (int): The ID of the category.
        subcat_id (int): The ID of the subcategory.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the category and subcategory names.
    """
    try:
        category = db.query(CategoryModel).filter(CategoryModel.category_id == cat_id).first()
        subcategory = db.query(SubcategoryModel).filter(SubcategoryModel.category_id == subcat_id).first()

        if not category or not subcategory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category or Subcategory not found"
            )

        return {
            "category_name": category.name,
            "subcategory_name": subcategory.name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
def get_cat_name(cat_id: int, db: Session = Depends(get_db)) -> str:
    """
    Retrieves the category name based on its ID.

    Args:
        cat_id (int): The ID of the category.
        db (Session): The database session.

    Returns:
        str: The name of the category.
    """
    try:
        category = db.query(CategoryModel).filter(CategoryModel.category_id == cat_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category.category_name
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_subcat_name(subcat_id: int, db: Session = Depends(get_db)) -> str:
    """
    Retrieves the subcategory name based on its ID.

    Args:
        subcat_id (int): The ID of the subcategory.
        db (Session): The database session.

    Returns:
        str: The name of the subcategory.
    """
    try:
        subcategory = db.query(SubcategoryModel).filter(SubcategoryModel.subcategory_id == subcat_id).first()
        if not subcategory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found"
            )
        return subcategory.subcategory_name
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )