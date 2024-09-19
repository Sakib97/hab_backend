from core.database import Base
from sqlalchemy import Boolean, Column, Integer, String,DateTime, func
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(100))
    image_url = Column(String)
    delete_image_url = Column(String)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class RoleModel(Base):  # authorities role - like sadmin, admin, editor, sub-editor, general user
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100))
    role_code = Column(Integer)

    # authorities = Column(String)

class PermissionModel(Base): # permissions like - User:read, Post:update, Comment:delete etc.
    __tablename__ = "permissions"
    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(255))

class RolePermissionModel(Base): # Who has which permission like - sadmin has Comment:delete permission
    __tablename__ = "role_permissions"
    role_permission_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer)
    permission_id = Column(Integer)
    permission_name = Column(String(255))

class UserRoleModel(Base): 
    __tablename__ = "user_role"
    user_role_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    email = Column(String(255))
    # role_id = Column(Integer)
    role_name_list = Column(String)
    role_code_list = Column(String)

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    ref_token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    email = Column(String(255))
    token = Column(String)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)


class EditorModel(Base):
    __tablename__ = "editor"
    editor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_email = Column(String(255))
    assigned_cat_id_list = Column(String)
    assigned_cat_name_list = Column(String)

class AuthorModel(Base):
    __tablename__ = "author"
    author_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_email = Column(String(255))
    user_name = Column(String(255))
    assigned_cat_id_list = Column(String)
    assigned_cat_name_list = Column(String)







