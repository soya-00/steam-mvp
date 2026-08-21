"""Cấu hình Alembic.

Địa chỉ cơ sở dữ liệu lấy từ `app.db` chứ không chép lại vào alembic.ini: chỗ
đó đã chuẩn hoá "postgres://" thành "postgresql+psycopg://" rồi, và hai nơi
cùng giữ một chuỗi kết nối là hai nơi để lệch nhau.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context

from app.db import Base, engine

# Nạp mọi model để autogenerate nhìn thấy đủ bảng. Import cho tác dụng phụ.
import app.models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite không ALTER được cột tại chỗ; batch mode dựng bảng mới rồi
            # chép sang. Postgres bỏ qua tuỳ chọn này.
            render_as_batch=connection.dialect.name == "sqlite",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
