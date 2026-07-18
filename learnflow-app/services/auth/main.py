# Auth Service - Authentication and Authorization
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import secrets
import jwt
from passlib.context import CryptContext

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, HealthResponse
)

settings.service_name = "auth-service"

app = create_app("auth-service", "Auth Service - Authentication & Authorization")

# JWT Configuration
SECRET_KEY = settings.jwt_secret if hasattr(settings, 'jwt_secret') else "learnflow-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Role definitions
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"


# Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserInDB(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    password_hash: str
    email_verified: bool = False
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    email_verified: bool
    avatar_url: Optional[str] = None
    timezone: str
    language: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    sub: str
    email: str
    role: UserRole
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str
    role: UserRole = UserRole.STUDENT


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class EmailVerificationRequest(BaseModel):
    token: str


# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT Token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Token blacklist (in production, use Redis)
_token_blacklist = set()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if token in _token_blacklist:
        raise HTTPException(status_code=401, detail="Token revoked")
    
    token_data = decode_token(token)
    return {
        "sub": token_data.sub,
        "email": token_data.email,
        "role": token_data.role
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    # In production, check user status in database
    return current_user


def require_role(allowed_roles: List[UserRole]):
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# ============================================
# Mock User Storage (In production: database)
# ============================================

_users_db: Dict[str, Dict] = {}
_refresh_tokens: Dict[str, Dict] = {}


def create_user_record(user_data: UserCreate) -> Dict:
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    return {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "status": UserStatus.ACTIVE,
        "password_hash": hash_password(user_data.password),
        "email_verified": False,
        "avatar_url": None,
        "timezone": "UTC",
        "language": "en",
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
        "last_login_ip": None
    }


async def get_user_by_email(email: str) -> Optional[Dict]:
    for user in _users_db.values():
        if user["email"] == email:
            return user
    return None


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    return _users_db.get(user_id)


async def create_user(user_data: UserCreate) -> Dict:
    user = create_user_record(user_data)
    _users_db[user["id"]] = user
    return user


async def update_user(user_id: str, updates: Dict) -> Optional[Dict]:
    if user_id not in _users_db:
        return None
    _users_db[user_id].update(updates)
    _users_db[user_id]["updated_at"] = datetime.now(timezone.utc)
    return _users_db[user_id]


async def delete_user(user_id: str) -> bool:
    if user_id in _users_db:
        del _users_db[user_id]
        return True
    return False


# ============================================
# API Endpoints
# ============================================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """Register a new user"""
    # Check if email exists
    if await get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await create_user(user_data)
    
    # Generate verification token (in production, send email)
    verification_token = secrets.token_urlsafe(32)
    await cache_set(f"verify:{verification_token}", user["id"], 86400)
    
    # In production: send verification email
    logger.info(f"Verification token for {user['email']}: {verification_token}")
    
    return UserResponse(**user)


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """Login with email and password"""
    user = await get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if user["status"] != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    # Create tokens
    access_token_data = {
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Store refresh token
    _refresh_tokens[refresh_token] = {
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc),
        "remember_me": False
    }
    
    # Update last login
    client_ip = request.client.host if request else None
    await update_user(user["id"], {
        "last_login_at": datetime.now(timezone.utc),
        "last_login_ip": client_ip
    })
    
    user_response = UserResponse(**user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@app.post("/auth/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    if request.refresh_token not in _refresh_tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_data = _refresh_tokens[request.refresh_token]
    user = await get_user_by_id(token_data["user_id"])
    
    if not user or user["status"] != UserStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Create new tokens
    access_token_data = {
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(access_token_data)
    new_refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Rotate refresh token
    del _refresh_tokens[request.refresh_token]
    _refresh_tokens[new_refresh_token] = {
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc),
        "remember_me": token_data.get("remember_me", False)
    }
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user)
    )


@app.post("/auth/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Logout and revoke tokens"""
    # In production, would blacklist the access token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        _token_blacklist.add(token)
    
    return {"message": "Successfully logged out"}


@app.post("/auth/verify-email", response_model=dict)
async def verify_email(request: EmailVerificationRequest):
    """Verify email with token"""
    user_id = await cache_get(f"verify:{request.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await update_user(user_id, {"email_verified": True})
    await cache_set(f"verify:{request.token}", "", 1)  # Invalidate token
    
    return {"message": "Email verified successfully"}


@app.post("/auth/resend-verification", response_model=dict)
async def resend_verification(
    current_user: dict = Depends(get_current_user)
):
    """Resend email verification"""
    user = await get_user_by_id(current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["email_verified"]:
        return {"message": "Email already verified"}
    
    verification_token = secrets.token_urlsafe(32)
    await cache_set(f"verify:{verification_token}", user["id"], 86400)
    
    # In production: send email
    logger.info(f"Resent verification token for {user['email']}: {verification_token}")
    
    return {"message": "Verification email sent"}


@app.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset"""
    user = await get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    reset_token = secrets.token_urlsafe(32)
    await cache_set(f"reset:{reset_token}", user["id"], 3600)
    
    # In production: send reset email
    logger.info(f"Password reset token for {user['email']}: {reset_token}")
    
    return {"message": "If the email exists, a reset link has been sent"}


@app.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Confirm password reset"""
    user_id = await cache_get(f"reset:{request.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    await update_user(user_id, {
        "password_hash": hash_password(request.new_password),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Invalidate reset token
    await cache_set(f"reset:{request.token}", "", 1)
    
    # Invalidate all refresh tokens (security)
    tokens_to_delete = [
        token for token, data in _refresh_tokens.items()
        if data["user_id"] == user_id
    ]
    for token in tokens_to_delete:
        del _refresh_tokens[token]
    
    return {"message": "Password reset successfully"}


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    user = await get_user_by_id(current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@app.patch("/auth/me", response_model=UserResponse)
async def update_me(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    user = await update_user(current_user["sub"], updates.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@app.post("/auth/change-password")
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True, min_length=8),
    current_user: dict = Depends(get_current_user)
):
    """Change password"""
    user = await get_user_by_id(current_user["sub"])
    if not user or not verify_password(current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password incorrect")
    
    await update_user(user["id"], {
        "password_hash": hash_password(new_password),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Invalidate all refresh tokens (force re-login)
    tokens_to_delete = [
        token for token, data in _refresh_tokens.items()
        if data["user_id"] == user["id"]
    ]
    for token in tokens_to_delete:
        del _refresh_tokens[token]
    
    return {"message": "Password changed successfully. Please log in again."}


@app.delete("/auth/me")
async def delete_account(
    password: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Delete own account"""
    user = await get_user_by_id(current_user["sub"])
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Password incorrect")
    
    await delete_user(user["id"])
    return {"message": "Account deleted successfully"}


# Admin endpoints
@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    page: int = 1,
    size: int = 20,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """List all users (admin only)"""
    users = list(_users_db.values())
    
    if role:
        users = [u for u in users if u["role"] == role]
    if status:
        users = [u for u in users if u["status"] == status]
    
    # Pagination
    start = (page - 1) * size
    end = start + size
    
    return [UserResponse(**u) for u in users[start:end]]


@app.patch("/admin/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: str,
    updates: UserUpdate,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Update user (admin only)"""
    user = await update_user(user_id, updates.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@app.patch("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: UserStatus,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Update user status (admin only)"""
    user = await update_user(user_id, {"status": status})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User status updated to {status}"}


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="auth-service",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)