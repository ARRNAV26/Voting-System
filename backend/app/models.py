from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    suggestions = relationship("Suggestion", back_populates="author")
    votes = relationship("Vote", back_populates="user")


class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(20), default="active")  # active, implemented, rejected
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="suggestions")
    votes = relationship("Vote", back_populates="suggestion", cascade="all, delete-orphan")
    
    @property
    def vote_count(self):
        """Calculate total votes for this suggestion"""
        return sum(1 for vote in self.votes if vote.is_upvote) - sum(1 for vote in self.votes if not vote.is_upvote)


class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    suggestion_id = Column(Integer, ForeignKey("suggestions.id"), nullable=False)
    is_upvote = Column(Boolean, nullable=False)  # True for upvote, False for downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="votes")
    suggestion = relationship("Suggestion", back_populates="votes")
    
    # Unique constraint to prevent multiple votes from same user on same suggestion
    __table_args__ = (UniqueConstraint('user_id', 'suggestion_id', name='unique_user_suggestion_vote'),) 