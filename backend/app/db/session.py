"""
Database session management module.

This module provides database session factories and connection pool management
for SQLAlchemy. It supports both sync and async operations.
"""
import os
from contextlib import contextmanager
from typing import Generator, AsyncGenerator

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import (
    Session,
    sessionmaker,
    SessionLocal as SQLAlchemySessionLocal,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
    AsyncSessionLocal,
)

from app.core.config import settings
from app.db.base import Base


class DatabaseManager:
    """
    Database manager for handling SQLAlchemy sessions and engine lifecycle.
    
    This class manages both synchronous and asynchronous database connections
    with proper connection pooling and configuration.
    """
    
    def __init__(self) -> None:
        self._sync_engine = None
        self._async_engine = None
        self._sync_session_factory = None
        self._async_session_factory = None
    
    @property
    def sync_engine(self):
        """Get or create synchronous engine."""
        if self._sync_engine is None:
            # Build sync database URL
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "merma_db")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "")
            
            # Validate required environment variables
            missing_vars = []
            if not db_password:
                missing_vars.append("POSTGRES_PASSWORD")
            if not db_user:
                missing_vars.append("POSTGRES_USER")
            
            if missing_vars:
                raise ValueError(
                    f"Missing required database environment variables: {', '.join(missing_vars)}"
                )
            
            # Create sync engine with connection pooling
            self._sync_engine = create_engine(
                f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
                poolclass=pool.QueuePool,
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
            )
            
            # Create tables if they don't exist
            Base.metadata.create_all(self._sync_engine)
            
        return self._sync_engine
    
    @property
    def async_engine(self) -> AsyncEngine:
        """Get or create asynchronous engine."""
        if self._async_engine is None:
            # Build async database URL
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "merma_db")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "")
            
            # Validate required environment variables
            missing_vars = []
            if not db_password:
                missing_vars.append("POSTGRES_PASSWORD")
            if not db_user:
                missing_vars.append("POSTGRES_USER")
            
            if missing_vars:
                raise ValueError(
                    f"Missing required database environment variables: {', '.join(missing_vars)}"
                )
            
            # Create async engine with connection pooling
            self._async_engine = create_async_engine(
                f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
            )
            
        return self._async_engine
    
    @property
    def sync_session_factory(self):
        """Get or create synchronous session factory."""
        if self._sync_session_factory is None:
            self._sync_session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.sync_engine,
            )
        return self._sync_session_factory
    
    @property
    def async_session_factory(self):
        """Get or create asynchronous session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._async_session_factory
    
    def get_sync_session(self) -> Session:
        """Create a new synchronous database session."""
        return self.sync_session_factory()
    
    def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create a new asynchronous database session."""
        async with self.async_session_factory() as session:
            yield session
    
    @contextmanager
    def sync_session(self) -> Generator[Session, None, None]:
        """
        Context manager for synchronous sessions.
        
        Automatically handles commit and rollback.
        """
        session = self.get_sync_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for asynchronous sessions.
        
        Automatically handles commit and rollback.
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def dispose(self) -> None:
        """Dispose all database engines and connections."""
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
        if self._async_engine:
            self._async_engine.dispose()
            self._async_engine = None
        self._sync_session_factory = None
        self._async_session_factory = None


# Global database manager instance
db_manager = DatabaseManager()


class SessionLocal:
    """
    Synchronous database session class.
    
    This is the primary session class used throughout the application
    for synchronous database operations.
    """
    
    def __init__(self) -> Session:
        self._session = None
    
    def __enter__(self) -> Session:
        self._session = db_manager.get_sync_session()
        return self._session
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session:
            if exc_type is not None:
                self._session.rollback()
            else:
                self._session.commit()
            self._session.close()
    
    def __call__(self) -> Session:
        """Allow using SessionLocal as a dependency in FastAPI."""
        return db_manager.get_sync_session()


# Legacy compatibility: Session database session factory
Session: sessionmaker = db_manager.sync_session_factory


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting database sessions.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = db_manager.get_sync_session()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting async database sessions.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with db_manager.async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def init_database() -> None:
    """
    Initialize database tables and run migrations.
    
    This function creates all tables defined by models that inherit from Base.
    It should be called during application startup.
    """
    engine = db_manager.sync_engine
    Base.metadata.create_all(bind=engine)


def drop_database() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data. Use with caution.
    """
    engine = db_manager.sync_engine
    Base.metadata.drop_all(bind=engine)


def check_database_health() -> dict:
    """
    Check database connection health.
    
    Returns:
        dict: Health status including connection state.
    """
    import psycopg2
    from sqlalchemy import text
    
    try:
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB", "merma_db")
        db_user = os.getenv("POSTGRES_USER", "postgres")
        db_password = os.getenv("POSTGRES_PASSWORD", "")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "version": version[0] if version else None,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
