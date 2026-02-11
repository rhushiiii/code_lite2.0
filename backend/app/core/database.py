from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _apply_user_table_migrations() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "users" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("users")}

    with engine.begin() as connection:
        if "github_token_encrypted" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN github_token_encrypted VARCHAR(1024)"))
        if "github_username" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN github_username VARCHAR(255)"))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _apply_user_table_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
