from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.paths import DB_PATH, ensure_paths

ensure_paths()
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
