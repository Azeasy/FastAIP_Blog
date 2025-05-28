# FastAPI Blog API

A FastAPI-based blog API with user authentication and post management.

## Features

- User authentication (signup, login)
- Create, read, and delete blog posts
- Token-based authentication
- Request validation
- Response caching

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   ENV=DEV

   DATABASE_URL=postgresql+asyncpg://user:pass@db/db_name
   TEST_DATABASE_URL=postgresql+asyncpg://user:pass@db/test_db
   POSTGRES_USER=user
   POSTGRES_PASSWORD=pass
   POSTGRES_PORT=5432
   POSTGRES_HOST=localhost

   SECRET_KEY=your_secret
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # Redis configuration
   REDIS_HOST=redis
   # For local development without Docker
   # REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Run migrations:
   ```
   alembic upgrade head
   ```

5. Start the server:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Docker Setup

1. Build and start the containers:
   ```
   docker-compose up --build -d
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Posts
- `POST /posts/` - Create a new post
- `GET /posts/` - Get all posts for the authenticated user
- `DELETE /posts/{post_id}` - Delete a post

## Documentation

API documentation is available at `/docs` or `/redoc` when the server is running.
