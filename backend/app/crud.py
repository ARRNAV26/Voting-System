from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, select, case
from typing import List, Optional
from app.models import User, Suggestion, Vote
from app.schemas import UserCreate, SuggestionCreate, VoteCreate


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    """Create a new user"""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Suggestion CRUD operations
def get_suggestion(db: Session, suggestion_id: int) -> Optional[Suggestion]:
    """Get suggestion by ID"""
    return db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()


def get_suggestions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Suggestion]:
    """Get suggestions with optional filtering"""
    query = db.query(Suggestion)
    
    if category:
        query = query.filter(Suggestion.category == category)
    if status:
        query = query.filter(Suggestion.status == status)
    if user_id:
        query = query.filter(Suggestion.author_id == user_id)
    
    return query.offset(skip).limit(limit).all()


def create_suggestion(db: Session, suggestion: SuggestionCreate, author_id: int) -> Suggestion:
    """Create a new suggestion"""
    db_suggestion = Suggestion(
        **suggestion.dict(),
        author_id=author_id
    )
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def update_suggestion(db: Session, suggestion_id: int, suggestion_update: dict) -> Optional[Suggestion]:
    """Update a suggestion"""
    db_suggestion = get_suggestion(db, suggestion_id)
    if not db_suggestion:
        return None
    
    for field, value in suggestion_update.items():
        if value is not None:
            setattr(db_suggestion, field, value)
    
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def delete_suggestion(db: Session, suggestion_id: int) -> bool:
    """Delete a suggestion"""
    db_suggestion = get_suggestion(db, suggestion_id)
    if not db_suggestion:
        return False
    
    db.delete(db_suggestion)
    db.commit()
    return True


# Vote CRUD operations
def get_user_vote(db: Session, user_id: int, suggestion_id: int) -> Optional[Vote]:
    """Get user's vote on a specific suggestion"""
    return db.query(Vote).filter(
        and_(Vote.user_id == user_id, Vote.suggestion_id == suggestion_id)
    ).first()


def create_or_update_vote(db: Session, vote: VoteCreate, user_id: int) -> Vote:
    """Create or update a user's vote on a suggestion"""
    existing_vote = get_user_vote(db, user_id, vote.suggestion_id)
    
    if existing_vote:
        # Update existing vote
        existing_vote.is_upvote = vote.is_upvote
        db.commit()
        db.refresh(existing_vote)
        return existing_vote
    else:
        # Create new vote
        db_vote = Vote(
            user_id=user_id,
            suggestion_id=vote.suggestion_id,
            is_upvote=vote.is_upvote
        )
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote


def delete_vote(db: Session, user_id: int, suggestion_id: int) -> bool:
    """Delete a user's vote on a suggestion"""
    vote = get_user_vote(db, user_id, suggestion_id)
    if not vote:
        return False
    
    db.delete(vote)
    db.commit()
    return True


def get_suggestion_vote_count(db: Session, suggestion_id: int) -> int:
    """Get the vote count for a suggestion"""
    suggestion = get_suggestion(db, suggestion_id)
    if not suggestion:
        return 0
    return suggestion.vote_count


# Statistics and analytics
def get_suggestions_by_category(db: Session) -> List[dict]:
    """Get suggestion count by category"""
    result = db.query(
        Suggestion.category,
        func.count(Suggestion.id).label('count')
    ).group_by(Suggestion.category).all()
    
    return [{"category": row.category, "count": row.count} for row in result]


def get_top_suggestions(db: Session, limit: int = 10) -> List[Suggestion]:
    """Get top suggestions by vote count (descending)"""
    # Annotate each suggestion with its vote count
    vote_count_subq = (
        db.query(
            Vote.suggestion_id,
            func.sum(case((Vote.is_upvote == True, 1), else_=-1)).label('vote_count')
        )
        .group_by(Vote.suggestion_id)
        .subquery()
    )
    # Join suggestions with their vote counts, order by vote_count desc
    suggestions = (
        db.query(Suggestion)
        .outerjoin(vote_count_subq, Suggestion.id == vote_count_subq.c.suggestion_id)
        .order_by(desc(vote_count_subq.c.vote_count), desc(Suggestion.created_at))
        .limit(limit)
        .all()
    )
    return suggestions


def get_user_suggestions(db: Session, user_id: int) -> List[Suggestion]:
    """Get all suggestions by a specific user"""
    return db.query(Suggestion).filter(Suggestion.author_id == user_id).all()


def get_user_votes(db: Session, user_id: int) -> List[Vote]:
    """Get all votes by a specific user"""
    return db.query(Vote).filter(Vote.user_id == user_id).all() 