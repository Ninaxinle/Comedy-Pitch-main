import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL - defaults to SQLite for development, can be overridden for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./comedy_peach.db")

# SQLAlchemy engine configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine) 