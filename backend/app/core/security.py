import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY and os.getenv("ENVIRONMENT", "development") == "production":
    raise RuntimeError("SECRET_KEY environment variable is required in production")
if not SECRET_KEY:
    SECRET_KEY = "supersecretkey"

ALGORITHM = "HS256"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], issuer="resilienceops", audience="resilienceops-users", options={"require": ["exp", "iss", "aud", "sub"]})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development" and token == "dev-token":
        return {"sub": "dev-user"}
        
    return verify_token(token)

def require_operator(current_user: dict = Depends(get_current_user)):
    environment = os.getenv("ENVIRONMENT", "development")
    roles = current_user.get("roles", [])
    if "operator" not in roles:
        if environment != "development" or current_user.get("sub") != "dev-user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Operator role required.",
            )
    return current_user
