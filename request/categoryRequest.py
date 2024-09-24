from pydantic import BaseModel

class CreateCategoryRequest(BaseModel):
    category_name: str 
    category_slug: str
    category_order: int

class CreateSubCategoryRequest(BaseModel):
    subcategory_name: str 
    category_id: int
    category_name: str
    subcategory_slug: str
    subcategory_order: int