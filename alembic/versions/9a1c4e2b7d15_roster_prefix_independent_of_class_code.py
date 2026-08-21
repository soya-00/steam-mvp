"""roster prefix independent of class code

Bản trước điền `roster_prefix = class_code`, tức là vẫn buộc mã ẩn danh vào một
chuỗi có thể đổi. Bản này cắt hẳn quan hệ đó: mỗi lớp nhận một tiền tố sinh
riêng, dạng "HS…", không bao giờ trùng mã lớp (mã lớp luôn bắt đầu bằng "GALS-")
và không bao giờ đổi nữa.

Đây là lần đổi tên mã ẩn danh duy nhất, và nó xảy ra trước khi có lớp thật nào
chạy. Sau mốc này thì không còn đường nào làm mã ẩn danh đổi được.

Revision ID: 9a1c4e2b7d15
Revises: 3443629b0ff3
Create Date: 2026-08-13 06:02:00.000000

"""
import random
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9a1c4e2b7d15'
down_revision: Union[str, Sequence[str], None] = '3443629b0ff3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BANG = "ABCDEFGHJKLMNPQRTUVWXYZ23456789"


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, roster_prefix FROM classes")).fetchall()

    # Giữ lại những tiền tố đã đúng dạng, để chạy lại bản này không đổi tên ai
    # lần thứ hai.
    da_dung = {r[1] for r in rows if r[1] and r[1].startswith("HS")}

    for class_id, prefix in rows:
        if prefix and prefix.startswith("HS"):
            continue
        moi = _sinh(da_dung)
        da_dung.add(moi)
        bind.execute(
            sa.text("UPDATE classes SET roster_prefix = :p WHERE id = :i"),
            {"p": moi, "i": class_id},
        )


def _sinh(da_dung: set[str]) -> str:
    for do_dai in (4, 5, 6):
        for _ in range(50):
            ma = "HS" + "".join(random.choice(_BANG) for _ in range(do_dai))
            if ma not in da_dung:
                return ma
    raise RuntimeError("Không sinh được tiền tố hồ sơ mới sau nhiều lần thử.")


def downgrade() -> None:
    """Downgrade schema."""
    # Không có đường lùi có nghĩa: tiền tố cũ được suy ra từ mã lớp, mà mã lớp
    # có thể đã đổi từ lúc đó. Dựng lại chỉ tạo ra một giá trị sai trông như
    # đúng.
    pass
