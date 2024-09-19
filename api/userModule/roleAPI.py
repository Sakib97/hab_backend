from fastapi import APIRouter, HTTPException, Depends, status
from core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

from model.userModel import RoleModel
from request.userRequest import CreateRoleRequest

role_router = APIRouter(
    prefix="/role", 
    tags=["Role"])

# create role
@role_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_role(data: CreateRoleRequest,
                      db: Session = Depends(get_db)):
    role = db.query(RoleModel).filter(RoleModel.role_name == data.role_name).first()
    if role: 
        raise HTTPException(status_code=422, detail="Role already exists.")
    
    new_role = RoleModel(
        role_name = data.role_name
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

