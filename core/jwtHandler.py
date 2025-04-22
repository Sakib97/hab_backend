from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from decouple import config
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import time

from model.userModel import UserModel, RefreshTokenModel
from core.database import get_db


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")
# ACCESS_TOKEN_EXPIRE_MINUTES = config("access_token_exp_min")
# REFRESH_TOKEN_EXPIRE_DAYS = config("refresh_token_exp_days")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
# ACCESS_TOKEN_EXPIRE_MINUTES = .5
REFRESH_TOKEN_EXPIRE_DAYS = 1
RESET_PASS_TOKEN_EXP_MIN = 5

access_exp_sec = int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60
refresh_exp_sec = int(REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 60 * 60
reset_pass_exp_sec = int(RESET_PASS_TOKEN_EXP_MIN) * 60
# refresh_exp_sec = 60

# print(JWT_Algorithm)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/user/token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def verify_user_access(user: UserModel):
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        # Trigger user account verification email
        raise HTTPException(
            status_code=400,
            detail="Your account is unverified. We have resend the account verification email.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Function to create JWT token
def create_access_token(data, expires_delta: timedelta = None, token_type = "access"):
    to_encode = data.copy()
    # expire = datetime.now() + timedelta(minutes=60)
    # expire = time.time() + 600
    if token_type == "access":
        expire = time.time() + access_exp_sec
    elif token_type == "refresh":
        expire = time.time() + refresh_exp_sec
    elif token_type == "reset_pass":
        expire = time.time() + reset_pass_exp_sec

    expire_datetime = datetime.fromtimestamp(expire)
    to_encode.update({"exp": expire, "token_type": token_type})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt, expire_datetime



def create_refreshed_access_token(refresh_token, db):
    try:
        # ### While using auth header ####
        # token_type, token = refresh_token.split()
        # if token_type.lower() != "bearer":
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid Authorization header",
        #     ) 

        # While using httponly cookie
        token = refresh_token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("email")
            token_from_db = db.query(RefreshTokenModel.token).filter(RefreshTokenModel.email== email).first()

            if email is None and token_from_db is None: 
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                    detail="Invalid token")

            # Generate a new access token
            new_access_token, exp = create_access_token({"email": email}, token_type="access")
            return new_access_token
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
            )
        
    except Exception as e:
        status_code = getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(
            status_code=status_code,
            detail=f"Internal server error: {e}"
        )


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        # else:
        #     raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = jwt.decode(jwtoken, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            token_type = payload.get("token_type")
            if token_type != "access":
                return False
            return True
        except JWTError:  # Catch specific JWT-related errors
            return False