from pydantic import BaseModel

class CategoryResponse(BaseModel):
    category_id: int 
    category_name: str 
    category_slug: str 
    category_order: int 

    class Config():
        orm_mode = True

class SubCategoryResponse(BaseModel):
    subcategory_id: int 
    subcategory_name: str 
    category_id: int 
    category_name: str 
    subcategory_slug: str
    subcategory_order: int 

    class Config():
        orm_mode = True