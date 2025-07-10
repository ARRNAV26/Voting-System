from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user
from app.crud import (
    get_suggestion, get_user_vote, create_or_update_vote,
    delete_vote, get_suggestion_vote_count
)
from app.schemas import VoteCreate, User, VoteUpdateMessage
from app.websocket_manager import manager

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("/")
def create_vote(
    vote: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create or update a vote on a suggestion"""
    # Check if suggestion exists
    suggestion = get_suggestion(db=db, suggestion_id=vote.suggestion_id)
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Check if user is trying to vote on their own suggestion
    if suggestion.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot vote on your own suggestion"
        )
    
    # Create or update vote
    db_vote = create_or_update_vote(
        db=db,
        vote=vote,
        user_id=current_user.id
    )
    
    # Get updated vote count
    new_vote_count = get_suggestion_vote_count(db=db, suggestion_id=vote.suggestion_id)
    
    # Get user's current vote
    user_vote = get_user_vote(db=db, user_id=current_user.id, suggestion_id=vote.suggestion_id)
    user_vote_value = user_vote.is_upvote if user_vote else None
    
    # Broadcast vote update to all connected clients
    vote_update = VoteUpdateMessage(
        suggestion_id=vote.suggestion_id,
        new_vote_count=new_vote_count,
        user_vote=user_vote_value
    )
    
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast_vote_update(vote_update))
        else:
            asyncio.run(manager.broadcast_vote_update(vote_update))
    except RuntimeError:
        pass
    
    return {
        "message": "Vote recorded successfully",
        "suggestion_id": vote.suggestion_id,
        "vote_count": new_vote_count,
        "user_vote": user_vote_value
    }


@router.delete("/{suggestion_id}")
def remove_vote(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a user's vote on a suggestion"""
    # Check if suggestion exists
    suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Check if user has voted on this suggestion
    user_vote = get_user_vote(db=db, user_id=current_user.id, suggestion_id=suggestion_id)
    if user_vote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vote found for this suggestion"
        )
    
    # Delete vote
    success = delete_vote(db=db, user_id=current_user.id, suggestion_id=suggestion_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove vote"
        )
    
    # Get updated vote count
    new_vote_count = get_suggestion_vote_count(db=db, suggestion_id=suggestion_id)
    
    # Broadcast vote update to all connected clients
    vote_update = VoteUpdateMessage(
        suggestion_id=suggestion_id,
        new_vote_count=new_vote_count,
        user_vote=None  # User removed their vote
    )
    
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast_vote_update(vote_update))
        else:
            asyncio.run(manager.broadcast_vote_update(vote_update))
    except RuntimeError:
        pass
    
    return {
        "message": "Vote removed successfully",
        "suggestion_id": suggestion_id,
        "vote_count": new_vote_count,
        "user_vote": None
    }


@router.get("/{suggestion_id}")
def get_vote_info(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get vote information for a suggestion"""
    # Check if suggestion exists
    suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Get user's vote
    user_vote = get_user_vote(db=db, user_id=current_user.id, suggestion_id=suggestion_id)
    user_vote_value = user_vote.is_upvote if user_vote else None
    
    # Get total vote count
    vote_count = get_suggestion_vote_count(db=db, suggestion_id=suggestion_id)
    
    return {
        "suggestion_id": suggestion_id,
        "vote_count": vote_count,
        "user_vote": user_vote_value
    } 