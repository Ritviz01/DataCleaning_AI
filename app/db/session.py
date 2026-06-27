import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# Load connection string from env or default to SQLite
# Note: For SQLite, we use sqlite:///./dataclean.db
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dataclean.db")

# Setup engine
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Session factories
db_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

SessionLocal = scoped_session(db_session)

# Base class for models
Base = declarative_base()

# FastAPI DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)

# Auto-initialize database tables on import
init_db()
