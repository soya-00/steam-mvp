"""Những thứ chỉ hỏng lúc đã triển khai thật.

Cả ba nhóm ở đây đều là loại hỏng im lặng: máy chủ báo xanh, trang mở được, và
thứ mất đi thì vài ngày sau mới có người phát hiện. Nên chúng cần bài kiểm thử
hơn là những chỗ hỏng ồn ào.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


def _chay(argv: list[str], env: dict[str, str] | None = None):
    moi_truong = {**os.environ, "PYTHONPATH": str(GOC)}
    moi_truong.pop("DATABASE_URL", None)
    if env:
        moi_truong.update(env)
    return subprocess.run(
        [sys.executable, *argv],
        cwd=GOC,
        env=moi_truong,
        capture_output=True,
        text=True,
    )


# ------------------------------------------------------- chốt chặn DATABASE_URL

def test_the_app_refuses_to_boot_on_a_server_without_a_database_url():
    """Không có chốt này thì thiếu biến là rơi về SQLite trên ổ đĩa tạm: khởi
    động ngon, kiểm tra sức khoẻ xanh, và mọi tài khoản biến mất ở lần triển
    khai sau."""
    r = _chay(["-c", "import app.config"], {"RENDER": "true"})
    assert r.returncode != 0
    assert "DATABASE_URL" in r.stderr


def test_the_same_boot_is_fine_on_a_laptop():
    r = _chay(["-c", "import app.config; print(app.config.DATABASE_URL)"])
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().startswith("sqlite:")


def test_a_server_with_a_database_url_boots():
    r = _chay(
        ["-c", "import app.config; print(app.config.DATABASE_URL)"],
        {"RENDER": "true", "DATABASE_URL": "sqlite:///:memory:"},
    )
    assert r.returncode == 0, r.stderr


# ------------------------------------------------------------ trang sức khoẻ

def test_the_health_check_reports_ok_when_the_database_answers(client):
    r = client.get("/suc-khoe")
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "ok"


def test_the_health_check_needs_no_login(client_tho):
    """Máy dò bên ngoài không có tài khoản, và không nên có."""
    assert client_tho.get("/suc-khoe").status_code == 200


def test_the_health_check_gives_nothing_away(client):
    """Một trang sức khoẻ liệt kê phiên bản thư viện là một trang do thám miễn
    phí. Ở đây chỉ có đúng một từ."""
    noi_dung = client.get("/suc-khoe").text
    assert set(json.loads(noi_dung)) == {"trang_thai"}
    for tu_cam in ("version", "python", "sqlalchemy", "traceback", "sqlite", "postgres"):
        assert tu_cam not in noi_dung.lower()


def test_the_health_check_really_touches_the_database(client, monkeypatch):
    """Trả 200 mà không hỏi cơ sở dữ liệu thì nó chỉ chứng minh tiến trình còn
    sống — mà đó không phải câu hỏi."""
    import app.main as main

    class HongHan:
        def __enter__(self):
            raise RuntimeError("cơ sở dữ liệu không với tới được")

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(main, "SessionLocal", lambda: HongHan())
    r = client.get("/suc-khoe")
    assert r.status_code == 503
    assert r.json()["trang_thai"] == "loi"


# --------------------------------------------------------- sao lưu và phục hồi

def test_a_backup_restores_into_an_empty_database_row_for_row(tmp_path):
    """Một bản sao lưu chưa thử phục hồi thì chưa phải bản sao lưu."""
    tep = tmp_path / "sao-luu.json"
    dich = tmp_path / "dich.db"

    r = _chay(["-m", "app.quan_tri", "sao-luu", str(tep)])
    assert r.returncode == 0, r.stderr
    assert tep.exists()

    dem = (
        "import app.models;"
        "from app.db import Base, SessionLocal;"
        "db=SessionLocal();"
        "print({t.name: len(db.execute(t.select()).fetchall())"
        " for t in Base.metadata.sorted_tables})"
    )
    truoc = eval(_chay(["-c", dem]).stdout)

    moi_truong = {"DATABASE_URL": f"sqlite:///{dich}"}
    assert _chay(["-m", "alembic", "upgrade", "head"], moi_truong).returncode == 0
    r = _chay(
        ["-m", "app.quan_tri", "phuc-hoi", str(tep), "--chac-chan"], moi_truong
    )
    assert r.returncode == 0, r.stderr

    sau = eval(_chay(["-c", dem], moi_truong).stdout)
    assert sau == truoc
    assert sum(truoc.values()) > 0


def test_restoring_without_the_confirmation_flag_changes_nothing(tmp_path):
    tep = tmp_path / "sao-luu.json"
    dich = tmp_path / "dich.db"
    assert _chay(["-m", "app.quan_tri", "sao-luu", str(tep)]).returncode == 0

    moi_truong = {"DATABASE_URL": f"sqlite:///{dich}"}
    _chay(["-m", "alembic", "upgrade", "head"], moi_truong)
    r = _chay(["-m", "app.quan_tri", "phuc-hoi", str(tep)], moi_truong)
    assert r.returncode == 1
    assert "--chac-chan" in r.stdout


def test_a_backup_will_not_silently_overwrite_an_earlier_one(tmp_path):
    tep = tmp_path / "sao-luu.json"
    assert _chay(["-m", "app.quan_tri", "sao-luu", str(tep)]).returncode == 0
    lan_hai = _chay(["-m", "app.quan_tri", "sao-luu", str(tep)])
    assert lan_hai.returncode == 1
    assert "--ghi-de" in lan_hai.stdout


def test_a_backup_from_a_different_format_version_is_refused(tmp_path):
    """Nạp một tệp mã này không hiểu thì hỏng nửa chừng, sau khi đã xoá sạch."""
    tep = tmp_path / "la.json"
    tep.write_text(json.dumps({"phien_ban": 99, "bang": {}}), encoding="utf-8")
    r = _chay(["-m", "app.quan_tri", "phuc-hoi", str(tep), "--chac-chan"])
    assert r.returncode == 1
    assert "phiên bản" in r.stdout


# ------------------------------------------- ứng dụng không tự gieo dữ liệu nào

def test_starting_up_writes_nothing_to_an_empty_database(tmp_path):
    """Cơ sở dữ liệu mới phải ở nguyên là cơ sở dữ liệu trống.

    Trước đây vòng đời FastAPI gọi `seed_if_empty()`, nên lần khởi động đầu tiên
    tự tạo sáu tài khoản — trong đó có một tài khoản giáo viên, với mật khẩu nằm
    công khai trong mã nguồn.
    """
    dich = tmp_path / "trong.db"
    moi_truong = {"DATABASE_URL": f"sqlite:///{dich}"}
    assert _chay(["-m", "alembic", "upgrade", "head"], moi_truong).returncode == 0

    khoi_dong = (
        "from fastapi.testclient import TestClient;"
        "from app.main import app;"
        "import app.models as m;"
        "from app.db import SessionLocal;"
        "c = TestClient(app);"
        "c.__enter__();"
        "print(c.get('/').status_code);"
        "db = SessionLocal();"
        "print(db.query(m.User).count(), db.query(m.Class).count(),"
        " db.query(m.School).count(), db.query(m.JournalEntry).count())"
    )
    r = _chay(["-c", khoi_dong], moi_truong)
    assert r.returncode == 0, r.stderr
    trang_chu, dem = r.stdout.strip().splitlines()
    assert trang_chu == "200"
    assert dem == "0 0 0 0", f"khởi động đã tạo ra dữ liệu: {dem}"


def test_no_demo_account_can_be_reached_from_the_application():
    """Nhân vật mẫu là giàn giáo kiểm thử. Nếu app/ với tới được chúng thì một
    ngày nào đó chúng sẽ có mặt trên máy chủ thật."""
    for tep in (GOC / "app").rglob("*.py"):
        nguon = tep.read_text(encoding="utf-8")
        assert "du_lieu_mau" not in nguon, tep
        assert "@gals.demo" not in nguon, tep
        assert "mat-khau-mau" not in nguon, tep


def test_the_application_no_longer_has_a_seeding_entry_point():
    tep = GOC / "app" / "seed.py"
    assert not tep.exists(), "app/seed.py đã chuyển sang tests/du_lieu_mau.py"
    for nguon in (GOC / "app").rglob("*.py"):
        assert "seed_if_empty" not in nguon.read_text(encoding="utf-8"), nguon


# --------------------------------------------------- quản trị vẫn không có route

def test_the_backup_commands_added_no_web_route():
    """Chính sách riêng tư 6.3 nói GALS không có giao diện quản trị trên web.
    Sao lưu là việc nguy hiểm nhất trong cả tệp — nó đọc được mọi nhật ký."""
    nguon = (GOC / "app" / "quan_tri.py").read_text(encoding="utf-8")
    assert "APIRouter" not in nguon
    assert "@app." not in nguon
