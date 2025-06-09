from model.userModel import UserModel
from fastapi import HTTPException, Request, status, Response, BackgroundTasks

def get_user_name_from_mail(email: str, db) -> str:
    """
    Retrieves the full name of a user based on their email address.

    Args:
        email (str): The email address of the user.
        db: The database session.

    Returns:
        str: The full name of the user, or an empty string if not found.
    """
    try:

        user = db.query(UserModel).filter(UserModel.email == email).first()
        if user:
            return f"{user.first_name} {user.last_name}"
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=str(e)
                )
