# Real-Time Voting System for Internal Suggestions

A modern, real-time voting system built with Python FastAPI and React TypeScript for internal company suggestions. Features live vote updates, user authentication, and a beautiful responsive interface.

## Voting Rules and Permissions

### Who Can Vote?
In this voting system, **any authenticated user except the author of a suggestion** can cast a like (upvote) or dislike (downvote) vote for a suggestion.

#### **Detailed Explanation**

1. **Authentication Requirement**
   - Only users who are logged in (i.e., have a valid JWT token) can interact with the voting API.
   - Unauthenticated users cannot vote; the backend will return a 401 Unauthorized error.

2. **Author Restriction**
   - The backend explicitly prevents the author of a suggestion from voting on their own suggestion.
   - In `backend/app/api/votes.py`, before allowing a vote, the code checks:
     ```python
     if suggestion.author_id == current_user.id:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Cannot vote on your own suggestion"
         )
     ```
   - This means: **You cannot like or dislike your own suggestion.**
   - The frontend also disables the voting buttons for the author of the suggestion in `HomePage.tsx`:
     ```ts
     const canVote = user && user.id !== suggestion.author_id;
     ```
   - If you are the author, the like/dislike buttons are not clickable.
   - Even if the frontend is bypassed (e.g., by using Postman), the backend will reject any vote attempt by the author.

3. **One Vote Per User Per Suggestion**
   - Each user can only have one vote (like or dislike) per suggestion.
   - If a user votes again, it updates their previous vote (switches from like to dislike or vice versa).
   - If a user removes their vote, it deletes their vote record for that suggestion.

#### **Summary Table**

| User Type         | Can Like/Dislike? | Notes                                 |
|-------------------|-------------------|---------------------------------------|
| Not logged in     | No                | Must log in to vote                   |
| Suggestion author | No                | Cannot vote on own suggestion         |
| Other user        | Yes               | Can like/dislike once per suggestion  |

#### **Example Scenarios**
- **Alice** creates a suggestion. She cannot vote on it.
- **Bob** logs in and sees Alice’s suggestion. He can like or dislike it.
- **Bob** can change his vote from like to dislike, or remove it.
- **Charlie** (another user) can also vote, but not more than once per suggestion.

**In summary:**
> Only logged-in users who are NOT the author of a suggestion can cast a like or dislike vote for that suggestion. Each user can only vote once per suggestion, and the backend enforces all these rules for security and fairness.

---

## Technical Approach

This real-time voting system is built using a modern full-stack architecture with Python FastAPI as the backend API and React with TypeScript for the frontend. The system employs WebSocket connections for real-time updates, ensuring that vote counts and new suggestions are instantly reflected across all connected clients without requiring page refreshes.

### Backend Architecture (FastAPI)
- **FastAPI Framework**: Leverages FastAPI's automatic OpenAPI documentation, type validation, and high performance for building RESTful APIs
- **WebSocket Support**: Uses FastAPI's built-in WebSocket support for real-time bidirectional communication
- **SQLAlchemy ORM**: Implements a clean data layer with SQLAlchemy for database operations and Alembic for migrations
- **SQLite for Development**: Uses SQLite for easy development setup (PostgreSQL for production)
- **Pydantic Models**: Implements data validation and serialization using Pydantic models
- **CORS Configuration**: Properly configured CORS for secure cross-origin requests
- **Dependency Injection**: Uses FastAPI's dependency injection for clean service architecture

### Frontend Architecture (React + TypeScript)
- **React 18 with TypeScript**: Modern React with strict typing for better development experience
- **Vite Build Tool**: Fast development server and optimized production builds
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **React Query**: For efficient server state management and caching
- **WebSocket Client**: Custom WebSocket hook for real-time updates
- **Responsive Design**: Mobile-first approach with modern UI/UX patterns

### Real-Time Communication
- **WebSocket Protocol**: Bidirectional communication for instant updates
- **Event-Driven Architecture**: Backend broadcasts events to all connected clients
- **Connection Management**: Proper WebSocket connection handling with reconnection logic
- **State Synchronization**: Frontend maintains local state that syncs with server state

### Security & Best Practices
- **Input Validation**: Comprehensive validation on both frontend and backend
- **Rate Limiting**: Prevents abuse with proper rate limiting
- **Error Handling**: Graceful error handling with user-friendly messages
- **Type Safety**: Full TypeScript coverage for better code quality
- **Environment Configuration**: Proper environment variable management
- **Docker Support**: Containerized deployment for easy scaling

### Assumptions Made
1. **Single Organization**: The system is designed for internal use within one organization
2. **Simple Authentication**: Basic session-based authentication (can be extended to OAuth/JWT)
3. **SQLite for Development**: Uses SQLite for easy development (PostgreSQL for production)
4. **Modern Browser Support**: Targets modern browsers with WebSocket support
5. **Development Environment**: Assumes Node.js and Python 3.8+ are available
6. **Network Requirements**: Assumes stable network connection for WebSocket functionality

### Development Workflow
- **Hot Reload**: Both frontend and backend support hot reloading for rapid development
- **API Documentation**: Auto-generated OpenAPI docs for easy API exploration
- **Type Safety**: End-to-end type safety from database to frontend
- **Testing Strategy**: Unit tests for backend services, integration tests for API endpoints
- **Deployment Ready**: Docker configuration for easy deployment and scaling

This architecture ensures scalability, maintainability, and a smooth developer experience while providing a robust real-time voting platform.

## Features

- 🔐 **User Authentication**: Secure login/register with JWT tokens
- 💬 **Real-time Updates**: Live vote counts and new suggestions via WebSocket
- 🎯 **Voting System**: Upvote/downvote suggestions with instant feedback
- 📊 **Top Suggestions**: View most popular suggestions
- 🔍 **Search & Filter**: Find suggestions by category, status, or text
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- ⚡ **Fast Performance**: Optimized with React Query and Vite
- 🎨 **Modern UI**: Beautiful interface with Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Option 1: Automatic Setup (Recommended)

Run the setup script to automatically configure everything:

```bash
python setup.py
```

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## Development

### Backend Development

- **API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs
- **Database**: Uses SQLite for development (PostgreSQL for production)
- **Authentication**: JWT-based authentication with secure password hashing
- **Real-time**: WebSocket support for live updates

### Frontend Development

- **Hot Reload**: Vite provides instant hot module replacement
- **Type Safety**: Full TypeScript coverage
- **State Management**: React Query for server state, Context for auth
- **Styling**: Tailwind CSS with custom components

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suggestions table
CREATE TABLE suggestions (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    author_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Votes table
CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    suggestion_id INTEGER REFERENCES suggestions(id),
    is_upvote BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, suggestion_id)
);
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Suggestions
- `GET /api/suggestions` - Get all suggestions
- `GET /api/suggestions/top` - Get top suggestions
- `POST /api/suggestions` - Create new suggestion
- `GET /api/suggestions/{id}` - Get specific suggestion
- `PUT /api/suggestions/{id}` - Update suggestion
- `DELETE /api/suggestions/{id}` - Delete suggestion

### Votes
- `POST /api/votes` - Create/update vote
- `DELETE /api/votes/{suggestion_id}` - Remove vote
- `GET /api/votes/{suggestion_id}` - Get vote info

### WebSocket
- `WS /api/ws/{user_id}` - Real-time connection

## Deployment

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build individually:**
   ```bash
   # Backend
   cd backend
   docker build -t voting-backend .
   docker run -p 8000:8000 voting-backend

   # Frontend
   cd frontend
   docker build -t voting-frontend .
   docker run -p 3000:3000 voting-frontend
   ```

### Production Considerations

- Use environment variables for sensitive data
- Set up proper CORS origins
- Configure database connection pooling
- Enable HTTPS in production
- Set up monitoring and logging
- Use Redis for session storage (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team. 