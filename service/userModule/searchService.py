from fastapi import HTTPException, Request, status, Response, BackgroundTasks
from datetime import datetime
from model.userModel import UserModel, UserRoleModel, RefreshTokenModel
from service.common.roleFinder import get_role_list
from service.userModule.userService import get_current_user_profile
import ast

def search_user_by_query(
    request: Request, 
    query: str, 
    db
):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        # user_role_obj, user_role_list = get_role_list(user_email, db)

        if not current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Invalid user!")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required.")
        # Search for users by email or username
        query_lower = f"%{query.lower()}%"
        users = db.query(UserModel).filter(
            (UserModel.email.ilike(query_lower)) | 
            (UserModel.first_name.ilike(query_lower)) |
            (UserModel.last_name.ilike(query_lower)) 
        ).limit(10).all()

        # exclude the current user from the search results
        users = [user for user in users if user.email != user_email]
        # exclude users who has role of ONLY 2024 (default user role)
        final_users = []
        for user in users:
            # print(f"Checking user: {user.email}")
            user_role_obj, user_role_list = get_role_list(user.email, db)
            if 2024 in user_role_list and len(user_role_list) == 1:
                pass
            else:
                final_users.append(user)
            
        return [
            {
                "user_id": user.user_id,
                "full_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            }
            for user in final_users
        ]
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
                )
   