from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now()


class School(Base):
    """Trường đối tác. Hàng ở đây chỉ được tạo khi đã ký thoả thuận — không có
    đường nào cho người dùng tự thêm trường, nếu không thì ô chọn trường chỉ
    còn là trang trí."""

    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten: Mapped[str] = mapped_column(String(160))
    tinh_thanh: Mapped[str] = mapped_column(String(80), default="")

    # Mã dành cho giáo viên, khác hoàn toàn với mã lớp của học sinh: mã lớp cho
    # vào một lớp, mã này cho quyền đọc bài của cả trường. Vì thế nó hết hạn.
    ma_giao_vien: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    ma_het_han: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    hoat_dong: Mapped[bool] = mapped_column(Boolean, default=True)
    doi_tac_tu: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    lien_he_ten: Mapped[str] = mapped_column(String(120), default="")
    lien_he_email: Mapped[str] = mapped_column(String(200), default="")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    avatar_id: Mapped[str] = mapped_column(String(40), default="avatar-1")

    school_id: Mapped[int | None] = mapped_column(
        ForeignKey("schools.id"), nullable=True, index=True
    )
    # hoat_dong | tam_khoa. Chỉ dùng để đình chỉ: mã giáo viên hết hạn chặn
    # được việc tạo thêm tài khoản, nhưng không thu hồi được tài khoản đã tạo.
    status: Mapped[str] = mapped_column(String(20), default="hoat_dong")

    # Rỗng với tài khoản đăng nhập bằng Google — người đó chưa từng đặt mật khẩu.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Nhà cung cấp OAuth và định danh ổn định bên đó. Không dùng email làm khoá
    # nối, vì trường học đổi email cho học sinh là chuyện thường.
    oauth_provider: Mapped[str | None] = mapped_column(String(20), nullable=True)
    oauth_sub: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    memberships: Mapped[list["ClassMembership"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    badges: Mapped[list["Badge"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def can_teach(self) -> bool:
        """Cửa duy nhất dẫn tới bài của học sinh. Vai trò thôi chưa đủ — tài
        khoản bị đình chỉ vẫn còn role='teacher'."""
        return self.role == "teacher" and self.status == "hoat_dong"


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    class_code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(160))

    # Lưu thẳng chứ không suy ra từ giáo viên: theo LEGAL.md nhà trường là bên
    # kiểm soát dữ liệu, nên giáo viên chuyển trường không được kéo theo lớp cũ.
    school_id: Mapped[int | None] = mapped_column(
        ForeignKey("schools.id"), nullable=True, index=True
    )

    teacher: Mapped["User"] = relationship()
    memberships: Mapped[list["ClassMembership"]] = relationship(
        back_populates="klass", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="klass", cascade="all, delete-orphan"
    )

    @property
    def students(self) -> list["User"]:
        return [m.student for m in self.memberships]


class ClassMembership(Base):

    __tablename__ = "class_memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)

    student: Mapped["User"] = relationship(back_populates="memberships")
    klass: Mapped["Class"] = relationship(back_populates="memberships")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    scenario_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    field: Mapped[str | None] = mapped_column(String(80), nullable=True)
    mode: Mapped[str] = mapped_column(String(20), default="online")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    klass: Mapped["Class"] = relationship(back_populates="assignments")


class JournalEntry(Base):

    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scenario_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(240), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    ai_transcript: Mapped[str] = mapped_column(Text, default="")

    image_url: Mapped[str] = mapped_column(String(500), default="")
    video_url: Mapped[str] = mapped_column(String(500), default="")
    submitted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    student: Mapped["User"] = relationship(back_populates="journal_entries")
    portfolio_entries: Mapped[list["PortfolioEntry"]] = relationship(
        back_populates="journal_entry", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="journal_entry", cascade="all, delete-orphan"
    )


class PortfolioEntry(Base):
    __tablename__ = "portfolio_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    category: Mapped[str] = mapped_column(String(30), default="ca_hai")
    description: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    shared: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    student: Mapped["User"] = relationship()
    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="portfolio_entries")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    badge_type: Mapped[str] = mapped_column(String(60))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    student: Mapped["User"] = relationship(back_populates="badges")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int | None] = mapped_column(
        ForeignKey("classes.id"), nullable=True, index=True
    )
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(240), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    field: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Feedback(Base):

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"), nullable=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    teacher: Mapped["User"] = relationship(foreign_keys=[teacher_id])
    student: Mapped["User"] = relationship(foreign_keys=[student_id])
    journal_entry: Mapped["JournalEntry | None"] = relationship(back_populates="feedback")


class Report(Base):

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(40), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    reported_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class GuidedSession(Base):

    __tablename__ = "guided_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scenario_id: Mapped[str] = mapped_column(String(80), index=True)
    stage_index: Mapped[int] = mapped_column(Integer, default=0)
    beat_index: Mapped[int] = mapped_column(Integer, default=0)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    synthesis: Mapped[str] = mapped_column(Text, default="")
    transcript: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    student: Mapped["User"] = relationship()
