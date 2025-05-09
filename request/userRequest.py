from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class CreateRoleRequest(BaseModel):
    role_name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class EditUserRequest(BaseModel): 
    first_name: str
    last_name: str
    password: str
    image_url: str
    delete_image_url: str

class PasswordResetEmailRequest(BaseModel):
    email: str 

class PasswordResetTokenRequest(BaseModel):
    reset_token: str 
    new_password: str

class CreateEditorRequest(BaseModel):
    user_id: int 
    user_email: str 
    assigned_cat_id_list: str 
    assigned_cat_name_list: str 

class CreateAuthorRequest(BaseModel):
    user_id: int 
    user_email: str 
    user_name: str 
    assigned_cat_id_list: str 
    assigned_cat_name_list: str 