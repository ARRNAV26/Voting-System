from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user
from app.crud import (
    get_suggestions, get_suggestion, create_suggestion, update_suggestion,
    delete_suggestion, get_suggestions_by_category, get_top_suggestions
)
from app.schemas import Suggestion, SuggestionCreate, SuggestionUpdate, User
from app.websocket_manager import manager
from app.schemas import SuggestionUpdateMessage
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("/", response_model=List[Suggestion])
def read_suggestions(
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all suggestions with optional filtering and limit, sorted by upvotes if limit is set"""
    try:
        if limit is not None:
            # Return top 'limit' suggestions by upvotes
            suggestions = get_top_suggestions(db=db, limit=limit)
            return suggestions
        suggestions = get_suggestions(
            db=db,
            skip=skip,
            limit=100,
            category=category,
            status=status
        )
        return suggestions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/top", response_model=List[Suggestion])
def read_top_suggestions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get top suggestions by vote count"""
    try:
        suggestions = get_top_suggestions(db=db, limit=limit)
        return suggestions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/categories")
def read_suggestion_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get suggestion count by category"""
    try:
        categories = get_suggestions_by_category(db=db)
        return categories
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/", response_model=Suggestion)
def create_new_suggestion(
    suggestion: SuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new suggestion"""
    try:
        db_suggestion = create_suggestion(
            db=db,
            suggestion=suggestion,
            author_id=current_user.id
        )
        
        # Broadcast new suggestion to all connected clients
        suggestion_data = {
            "id": db_suggestion.id,
            "title": db_suggestion.title,
            "description": db_suggestion.description,
            "category": db_suggestion.category,
            "status": db_suggestion.status,
            "author_id": db_suggestion.author_id,
            "vote_count": db_suggestion.vote_count,
            "created_at": db_suggestion.created_at.isoformat(),
            "author": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        }
        
        # Broadcast to all connected clients
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, schedule the broadcast
                loop.create_task(manager.broadcast_new_suggestion(suggestion_data))
            else:
                # If we're not in an async context, run the broadcast
                asyncio.run(manager.broadcast_new_suggestion(suggestion_data))
        except RuntimeError:
            # Handle case where no event loop is available
            pass
        
        return db_suggestion
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{suggestion_id}", response_model=Suggestion)
def read_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific suggestion by ID"""
    try:
        suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        return suggestion
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/{suggestion_id}", response_model=Suggestion)
def update_suggestion_by_id(
    suggestion_id: int,
    suggestion_update: SuggestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a suggestion"""
    try:
        # Check if suggestion exists
        db_suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
        if db_suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Check if user is the author
        if db_suggestion.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this suggestion"
            )
        
        # Update suggestion
        updated_suggestion = update_suggestion(
            db=db,
            suggestion_id=suggestion_id,
            suggestion_update=suggestion_update.dict(exclude_unset=True)
        )
        
        # Broadcast update to all connected clients
        suggestion_update_msg = SuggestionUpdateMessage(suggestion=updated_suggestion)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast_suggestion_update(suggestion_update_msg))
            else:
                asyncio.run(manager.broadcast_suggestion_update(suggestion_update_msg))
        except RuntimeError:
            pass
        
        return updated_suggestion
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/{suggestion_id}/status", response_model=Suggestion)
def update_suggestion_status(
    suggestion_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the status of a suggestion (active -> implemented/rejected)"""
    try:
        # print(f"[DEBUG] PATCH /suggestions/{suggestion_id}/status called with:")
        # print(f"  suggestion_id: {suggestion_id}")
        # print(f"  new_status: {new_status}")
        # print(f"  current_user.id: {getattr(current_user, 'id', None)}")
        db_suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
        if db_suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        if db_suggestion.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active suggestions can be updated"
            )
        if new_status not in ["implemented", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'implemented' or 'rejected'"
            )
        if db_suggestion.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this suggestion's status"
            )
        updated_suggestion = update_suggestion(
            db=db,
            suggestion_id=suggestion_id,
            suggestion_update={"status": new_status}
        )
        from app.schemas import SuggestionUpdateMessage
        import asyncio
        suggestion_update_msg = SuggestionUpdateMessage(suggestion=updated_suggestion)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast_suggestion_update(suggestion_update_msg))
            else:
                asyncio.run(manager.broadcast_suggestion_update(suggestion_update_msg))
        except RuntimeError:
            pass
        return updated_suggestion
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/{suggestion_id}")
def delete_suggestion_by_id(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a suggestion"""
    try:
        # Check if suggestion exists
        db_suggestion = get_suggestion(db=db, suggestion_id=suggestion_id)
        if db_suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Check if user is the author
        if db_suggestion.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this suggestion"
            )
        
        # Delete suggestion
        success = delete_suggestion(db=db, suggestion_id=suggestion_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete suggestion"
            )
        
        return {"message": "Suggestion deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") 