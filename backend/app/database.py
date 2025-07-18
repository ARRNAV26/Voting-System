import aiosqlite
from app.config import settings

# Async dependency for aiosqlite connection
def get_db_path():
    if settings.ENVIRONMENT == "test":
        return ":memory:"
    elif settings.DATABASE_URL.startswith("sqlite"):
        # Extract file path from DATABASE_URL (e.g., sqlite:///./voting_system.db)
        return settings.DATABASE_URL.replace("sqlite:///", "")
    else:
        raise RuntimeError("aiosqlite is only supported for SQLite databases.")

async def get_db():
    """Async dependency to get aiosqlite connection"""
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    """Create tables if they do not exist (for aiosqlite)"""
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                author_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY(author_id) REFERENCES users(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                suggestion_id INTEGER NOT NULL,
                is_upvote BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, suggestion_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(suggestion_id) REFERENCES suggestions(id)
            )
        ''')
        await db.commit() 