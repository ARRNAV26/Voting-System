from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, select, case
from typing import List, Optional, Dict
from app.schemas import UserCreate, SuggestionCreate, VoteCreate
import aiosqlite


# User CRUD operations (async)
async def get_user(db, user_id: int):
    """Get user by ID (async)"""
    cursor = await db.execute("SELECT id, username, email, is_active, created_at, hashed_password FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None

async def get_user_by_username(db, username: str):
    """Get user by username (async)"""
    cursor = await db.execute("SELECT id, username, email, is_active, created_at, hashed_password FROM users WHERE username = ?", (username,))
    row = await cursor.fetchone()
    return dict(row) if row else None

async def get_user_by_email(db, email: str):
    """Get user by email (async)"""
    cursor = await db.execute("SELECT id, username, email, is_active, created_at, hashed_password FROM users WHERE email = ?", (email,))
    row = await cursor.fetchone()
    return dict(row) if row else None


def create_user(db: Session, user: UserCreate, hashed_password: str) -> Dict:
    """Create a new user"""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return dict(db_user)


async def create_user_async(db, user: UserCreate, hashed_password: str) -> Dict:
    """Create a new user asynchronously using aiosqlite"""
    query = """
        INSERT INTO users (username, email, hashed_password, is_active, created_at)
        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
    """
    await db.execute(query, (user.username, user.email, hashed_password))
    await db.commit()
    # Fetch the newly created user
    cursor = await db.execute("SELECT id, username, email, is_active, created_at FROM users WHERE username = ?", (user.username,))
    row = await cursor.fetchone()
    if row:
        return dict(row)
    return None


# Suggestion CRUD operations (async)
async def get_suggestion(db, suggestion_id: int):
    """Get suggestion by ID (async)"""
    cursor = await db.execute("SELECT * FROM suggestions WHERE id = ?", (suggestion_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None

async def get_suggestions(db, skip: int = 0, limit: int = 100, category: Optional[str] = None, status: Optional[str] = None, user_id: int = None):
    """Get suggestions with optional filtering (async)"""
    query = "SELECT * FROM suggestions WHERE 1=1"
    params = []
    if category is not None:
        query += " AND category = ?"
        params.append(category)
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    if user_id:
        query += " AND author_id = ?"
        params.append(user_id)
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor = await db.execute(query, tuple(params))
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

async def create_suggestion(db, suggestion: SuggestionCreate, author_id: int):
    """Create a new suggestion (async)"""
    query = """
        INSERT INTO suggestions (title, description, category, author_id, status, created_at)
        VALUES (?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
    """
    await db.execute(query, (suggestion.title, suggestion.description, suggestion.category, author_id))
    await db.commit()
    cursor = await db.execute("SELECT * FROM suggestions WHERE rowid = last_insert_rowid()")
    row = await cursor.fetchone()
    return dict(row) if row else None

async def update_suggestion(db, suggestion_id: int, suggestion_update: dict):
    """Update a suggestion (async)"""
    # Build dynamic update query
    fields = []
    values = []
    for field, value in suggestion_update.items():
        if value is not None:
            fields.append(f"{field} = ?")
            values.append(value)
    if not fields:
        return await get_suggestion(db, suggestion_id)
    fields.append("updated_at = CURRENT_TIMESTAMP")
    query = f"UPDATE suggestions SET {', '.join(fields)} WHERE id = ?"
    values.append(suggestion_id)
    await db.execute(query, tuple(values))
    await db.commit()
    return await get_suggestion(db, suggestion_id)

async def delete_suggestion(db, suggestion_id: int):
    """Delete a suggestion (async)"""
    await db.execute("DELETE FROM suggestions WHERE id = ?", (suggestion_id,))
    await db.commit()
    return True


# Vote CRUD operations (async)
async def get_user_vote(db, user_id: int, suggestion_id: int):
    """Get user's vote on a specific suggestion (async)"""
    cursor = await db.execute("SELECT * FROM votes WHERE user_id = ? AND suggestion_id = ?", (user_id, suggestion_id))
    row = await cursor.fetchone()
    return dict(row) if row else None

async def create_or_update_vote(db, vote: VoteCreate, user_id: int):
    """Create or update a user's vote on a suggestion (async)"""
    existing_vote = await get_user_vote(db, user_id, vote.suggestion_id)
    if existing_vote:
        await db.execute("UPDATE votes SET is_upvote = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?", (vote.is_upvote, existing_vote['id']))
        await db.commit()
        return await get_user_vote(db, user_id, vote.suggestion_id)
    else:
        await db.execute(
            "INSERT INTO votes (user_id, suggestion_id, is_upvote, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, vote.suggestion_id, vote.is_upvote)
        )
        await db.commit()
        return await get_user_vote(db, user_id, vote.suggestion_id)

async def delete_vote(db, user_id: int, suggestion_id: int):
    """Delete a user's vote on a suggestion (async)"""
    await db.execute("DELETE FROM votes WHERE user_id = ? AND suggestion_id = ?", (user_id, suggestion_id))
    await db.commit()
    return True

async def get_suggestion_vote_count(db, suggestion_id: int):
    """Get the vote count for a suggestion (async)"""
    cursor = await db.execute(
        "SELECT SUM(CASE WHEN is_upvote THEN 1 ELSE -1 END) as vote_count FROM votes WHERE suggestion_id = ?",
        (suggestion_id,)
    )
    row = await cursor.fetchone()
    return row["vote_count"] if row and row["vote_count"] is not None else 0


# Statistics and analytics
async def get_suggestions_by_category(db) -> list:
    """Get suggestion count by category (async)"""
    cursor = await db.execute(
        "SELECT category, COUNT(id) as count FROM suggestions GROUP BY category"
    )
    rows = await cursor.fetchall()
    return [{"category": row["category"], "count": row["count"]} for row in rows]

async def get_top_suggestions(db, limit: int = 10) -> list:
    """Get top suggestions by vote count (descending) (async)"""
    # Get suggestions with vote counts
    query = '''
        SELECT s.*, COALESCE(SUM(CASE WHEN v.is_upvote THEN 1 ELSE -1 END), 0) as vote_count
        FROM suggestions s
        LEFT JOIN votes v ON s.id = v.suggestion_id
        GROUP BY s.id
        ORDER BY vote_count DESC, s.created_at DESC
        LIMIT ?
    '''
    cursor = await db.execute(query, (limit,))
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


def get_user_suggestions(db: Session, user_id: int) -> List[Dict]:
    """Get all suggestions by a specific user"""
    return db.query(Suggestion).filter(Suggestion.author_id == user_id).all()


def get_user_votes(db: Session, user_id: int) -> List[Dict]:
    """Get all votes by a specific user"""
    return db.query(Vote).filter(Vote.user_id == user_id).all() 