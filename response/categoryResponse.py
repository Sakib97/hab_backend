from pydantic import BaseModel

class CategoryResponse(BaseModel):
    category_id: int 
    category_name: str 
    category_slug: str 
    category_order: int 
    is_enabled: bool
    class Config():
        from_attributes = True

class SubCategoryResponse(BaseModel): 
    subcategory_id: int 
    subcategory_name: str 
    category_id: int 
    category_name: str 
    subcategory_slug: str
    subcategory_order: int 
    is_enabled: bool
    class Config():
        from_attributes = True

class TagResponse(BaseModel):
    tag_id: int
    tag_name: str
    tag_slug: str 
    class Config():
        from_attributes = True