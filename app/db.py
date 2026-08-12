from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# Render phát biến DATABASE_URL bắt đầu bằng "postgres://", còn SQLAlchemy 2
# chỉ hiểu "postgresql://". Sửa ở đây thay vì bắt người deploy nhớ.
_url = DATABASE_URL
if _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql+psycopg://", 1)
elif _url.startswith("postgresql://"):
    _url = _url.replace("postgresql://", "postgresql+psycopg://", 1)

_is_sqlite = _url.startswith("sqlite")

engine = create_engine(
    _url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    # Gói miễn phí của nhà cung cấp Postgres hay cắt kết nối đang rỗi; không có
    # pre_ping thì lượt truy cập đầu sau khi ngủ sẽ lỗi thay vì chỉ chậm.
    pool_pre_ping=not _is_sqlite,
    pool_recycle=280 if not _is_sqlite else -1,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
