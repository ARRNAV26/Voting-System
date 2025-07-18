from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user
from app.crud import (
    get_suggestions, get_suggestion, create_suggestion, update_suggestion,
    delete_suggestion, get_suggestions_by_category, get_top_suggestions, get_user, get_suggestion_vote_count
)
from app.schemas import Suggestion, SuggestionCreate, SuggestionUpdate, User
from app.websocket_manager import manager
from app.schemas import SuggestionUpdateMessage

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("/", response_model=List[Suggestion])
async def read_suggestions(
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all suggestions with optional filtering and limit, sorted by upvotes if limit is set (async)"""
    if limit is not None:
        suggestions = await get_top_suggestions(db=db, limit=limit)
    else:
        suggestions = await get_suggestions(
            db=db,
            skip=skip,
            limit=100,
            category=category if category is not None else None,
            status=status if status is not None else None
        )
    enriched = []
    for s in suggestions:
        author = await get_user(db, s["author_id"]) if s else None
        s = dict(s) if s else {}
        if author:
            s["author"] = {
                "id": author["id"],
                "username": author["username"],
                "email": author["email"],
                "is_active": author["is_active"],
                "created_at": author["created_at"]
            }
        else:
            s["author"] = None
        # Add vote_count
        s["vote_count"] = await get_suggestion_vote_count(db, s["id"])
        enriched.append(s)
    return enriched


@router.get("/top", response_model=List[Suggestion])
async def read_top_suggestions(
    limit: int = Query(10, ge=1, le=50),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get top suggestions by vote count (async)"""
    suggestions = await get_top_suggestions(db=db, limit=limit)
    enriched = []
    for s in suggestions:
        author = await get_user(db, s["author_id"]) if s else None
        s = dict(s) if s else {}
        if author:
            s["author"] = {
                "id": author["id"],
                "username": author["username"],
                "email": author["email"],
                "is_active": author["is_active"],
                "created_at": author["created_at"]
            }
        else:
            s["author"] = None
        # Add vote_count
        s["vote_count"] = await get_suggestion_vote_count(db, s["id"])
        enriched.append(s)
    return enriched


@router.get("/categories")
async def read_suggestion_categories(
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get suggestion count by category (async)"""
    categories = await get_suggestions_by_category(db=db)
    return categories


@router.post("/", response_model=Suggestion)
async def create_new_suggestion(
    suggestion: SuggestionCreate,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new suggestion (async)"""
    db_suggestion = await create_suggestion(
        db=db,
        suggestion=suggestion,
        author_id=current_user["id"]
    )
    db_suggestion = dict(db_suggestion) if db_suggestion else {}
    db_suggestion["author"] = {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }
    # Add vote_count
    db_suggestion["vote_count"] = await get_suggestion_vote_count(db, db_suggestion["id"])
    # Broadcast new suggestion to all connected clients
    suggestion_data = dict(db_suggestion)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast_new_suggestion(suggestion_data))
        else:
            asyncio.run(manager.broadcast_new_suggestion(suggestion_data))
    except RuntimeError:
        pass
    return db_suggestion


@router.get("/{suggestion_id}", response_model=Suggestion)
async def read_suggestion(
    suggestion_id: int,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific suggestion by ID (async)"""
    suggestion = await get_suggestion(db=db, suggestion_id=suggestion_id)
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    author = await get_user(db, suggestion["author_id"]) if suggestion else None
    suggestion = dict(suggestion) if suggestion else {}
    if author:
        suggestion["author"] = {
            "id": author["id"],
            "username": author["username"],
            "email": author["email"],
            "is_active": author["is_active"],
            "created_at": author["created_at"]
        }
    else:
        suggestion["author"] = None
    # Add vote_count
    suggestion["vote_count"] = await get_suggestion_vote_count(db, suggestion["id"])
    return suggestion


@router.put("/{suggestion_id}", response_model=Suggestion)
async def update_suggestion_by_id(
    suggestion_id: int,
    suggestion_update: SuggestionUpdate,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a suggestion (async)"""
    db_suggestion = await get_suggestion(db=db, suggestion_id=suggestion_id)
    if db_suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    if db_suggestion["author_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this suggestion"
        )
    updated_suggestion = await update_suggestion(
        db=db,
        suggestion_id=suggestion_id,
        suggestion_update=suggestion_update.dict(exclude_unset=True)
    )
    author = await get_user(db, updated_suggestion["author_id"]) if updated_suggestion else None
    updated_suggestion = dict(updated_suggestion) if updated_suggestion else {}
    if author:
        updated_suggestion["author"] = {
            "id": author["id"],
            "username": author["username"],
            "email": author["email"],
            "is_active": author["is_active"],
            "created_at": author["created_at"]
        }
    else:
        updated_suggestion["author"] = None
    # Add vote_count
    updated_suggestion["vote_count"] = await get_suggestion_vote_count(db, updated_suggestion["id"])
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


@router.patch("/{suggestion_id}/status", response_model=Suggestion)
async def update_suggestion_status(
    suggestion_id: int,
    new_status: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update the status of a suggestion (active -> implemented/rejected) (async)"""
    db_suggestion = await get_suggestion(db=db, suggestion_id=suggestion_id)
    if db_suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    if db_suggestion["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active suggestions can be updated"
        )
    if new_status not in ["implemented", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'implemented' or 'rejected'"
        )
    if db_suggestion["author_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this suggestion's status"
        )
    updated_suggestion = await update_suggestion(
        db=db,
        suggestion_id=suggestion_id,
        suggestion_update={"status": new_status}
    )
    author = await get_user(db, updated_suggestion["author_id"]) if updated_suggestion else None
    updated_suggestion = dict(updated_suggestion) if updated_suggestion else {}
    if author:
        updated_suggestion["author"] = {
            "id": author["id"],
            "username": author["username"],
            "email": author["email"],
            "is_active": author["is_active"],
            "created_at": author["created_at"]
        }
    else:
        updated_suggestion["author"] = None
    # Add vote_count
    updated_suggestion["vote_count"] = await get_suggestion_vote_count(db, updated_suggestion["id"])
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


@router.delete("/{suggestion_id}")
async def delete_suggestion_by_id(
    suggestion_id: int,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a suggestion (async)"""
    db_suggestion = await get_suggestion(db=db, suggestion_id=suggestion_id)
    if db_suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    if db_suggestion["author_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this suggestion"
        )
    await delete_suggestion(db=db, suggestion_id=suggestion_id)
    return {"message": "Suggestion deleted successfully"} 