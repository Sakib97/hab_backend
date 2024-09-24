from fastapi import HTTPException, Request, status, Response, BackgroundTasks
from model.userModel import UserRoleModel
import ast

def get_role_list(user_email, db):
    user_role = db.query(UserRoleModel).filter(UserRoleModel.email == user_email).first()
    if not user_role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User Role Not Found")
    
    role_code_as_list = ast.literal_eval(user_role.role_code_list)
    return role_code_as_list
