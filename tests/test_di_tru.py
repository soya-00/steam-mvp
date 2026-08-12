"""Di trú lược đồ.

`create_all()` tạo được bảng còn thiếu nhưng **không** thêm được cột vào bảng
đã tồn tại. Chừng nào còn xoá sạch mỗi lần khởi động thì không sao; có một tài
khoản thật trên Postgres rồi thì cột mới sẽ bị bỏ qua trong im lặng, và truy
vấn đầu tiên chạm tới nó sẽ đổ với "column does not exist".

Bài quan trọng nhất ở đây là bài đối chiếu: model đổi mà quên viết bản di trú
thì nó đỏ, chứ không đợi tới lúc triển khai mới biết.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


def _alembic(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    import os

    moi_truong = {**os.environ, **(env or {})}
    return subprocess.run(
        ["python", "-m", "alembic", *args],
        cwd=GOC,
        capture_output=True,
        text=True,
        env=moi_truong,
    )


def test_the_migrations_build_the_same_schema_the_models_describe(tmp_path):
    """Chạy hết chuỗi di trú trên một cơ sở dữ liệu trống, rồi hỏi Alembic xem
    còn gì khác với model không. Còn khác nghĩa là thiếu một bản di trú."""
    db = tmp_path / "kiem-tra.db"
    env = {"DATABASE_URL": f"sqlite:///{db}"}

    lam = _alembic("upgrade", "head", env=env)
    assert lam.returncode == 0, lam.stderr

    doi_chieu = _alembic("check", env=env)
    assert doi_chieu.returncode == 0, (
        "Model và chuỗi di trú đã lệch nhau. Chạy:\n"
        "  alembic revision --autogenerate -m \"mô tả thay đổi\"\n\n" + doi_chieu.stderr
    )


def test_there_is_exactly_one_head(tmp_path):
    """Hai nhánh di trú song song thì `upgrade head` không biết chọn đường nào."""
    ra = _alembic("heads")
    assert ra.returncode == 0, ra.stderr
    dong = [d for d in ra.stdout.splitlines() if "(head)" in d]
    assert len(dong) == 1, ra.stdout


def test_the_deploy_runs_migrations_before_opening_the_port():
    render = (GOC / "render.yaml").read_text(encoding="utf-8")
    assert "alembic upgrade head" in render
    assert render.index("alembic upgrade head") < render.index("uvicorn")


def test_the_deploy_has_a_database_and_reads_its_url():
    render = (GOC / "render.yaml").read_text(encoding="utf-8")
    assert "databases:" in render
    assert "DATABASE_URL" in render
    assert "fromDatabase" in render


def test_no_secret_is_written_into_the_deploy_file():
    """Khoá chỉ sống trong bảng biến môi trường của nơi triển khai."""
    render = (GOC / "render.yaml").read_text(encoding="utf-8")
    for khoa in [
        "GEMINI_API_KEY", "GOOGLE_CLIENT_SECRET", "MICROSOFT_CLIENT_SECRET", "MAIL_API_KEY"
    ]:
        assert khoa in render, khoa
        sau = render.split(khoa, 1)[1][:80]
        assert "sync: false" in sau, f"{khoa} phải để sync: false"


def test_create_all_never_runs_against_a_real_database(monkeypatch):
    """Trên Postgres, dựng bảng là việc của Alembic. Nếu create_all() vẫn chạy
    ở đó thì mọi cột thêm sau này sẽ bị bỏ qua mà không ai biết."""
    import app.seed as seed

    da_goi = []
    monkeypatch.setattr(seed, "is_sqlite", False)
    monkeypatch.setattr(
        seed.Base.metadata, "create_all", lambda **kw: da_goi.append(kw)
    )
    monkeypatch.setattr(seed, "_seed", lambda db: None)

    try:
        seed.seed_if_empty()
    except Exception:
        # Không kết nối được Postgres ở đây cũng không sao — điều cần biết là
        # create_all() có được gọi hay không.
        pass
    assert da_goi == []
