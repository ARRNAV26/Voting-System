from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.crud import get_user_by_username, create_user, create_user_async
from app.schemas import User, UserCreate, Token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User)
async def register(user: UserCreate, db = Depends(get_db)):
    """Register a new user (async, aiosqlite)"""
    # Check if username already exists
    cursor = await db.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    db_user = await cursor.fetchone()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Check if email already exists
    cursor = await db.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    db_user = await cursor.fetchone()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = await create_user_async(db=db, user=user, hashed_password=hashed_password)
    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    """Login and get access token (async)"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information (async)"""
    return current_user 