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
