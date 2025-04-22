from pydantic import BaseModel
from datetime import datetime

# Model for the user role
class UserRoleResponse(BaseModel):
    # role_id: int
    role_name_list: str
    role_code_list: str

    class Config:
        from_attributes = True

# Model for the user
class CreateUserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    role: UserRoleResponse  # Embedding the role data inside the user

    class Config:
        from_attributes = True