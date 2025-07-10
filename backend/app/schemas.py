from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Suggestion schemas
class SuggestionBase(BaseModel):
    title: str
    description: str
    category: str


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class Suggestion(SuggestionBase):
    id: int
    status: str
    author_id: int
    vote_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    
    class Config:
        from_attributes = True


class SuggestionWithVotes(Suggestion):
    votes: List["Vote"] = []
    
    class Config:
        from_attributes = True


# Vote schemas
class VoteBase(BaseModel):
    is_upvote: bool


class VoteCreate(VoteBase):
    suggestion_id: int


class Vote(VoteBase):
    id: int
    user_id: int
    suggestion_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: dict


class VoteUpdateMessage(BaseModel):
    suggestion_id: int
    new_vote_count: int
    user_vote: Optional[bool] = None


class SuggestionUpdateMessage(BaseModel):
    suggestion: Suggestion


# Response schemas
class PaginatedResponse(BaseModel):
    items: List[Suggestion]
    total: int
    page: int
    size: int
    pages: int


# Update forward references
SuggestionWithVotes.model_rebuild() 