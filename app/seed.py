from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.auth import DEMO_ACCOUNTS
from app.db import Base, SessionLocal, engine
from app.models import (
    GuidedSession,
    Assignment,
    Badge,
    Class,
    ClassMembership,
    Feedback,
    JournalEntry,
    Notification,
    PortfolioEntry,
    User,
)
from app.scenarios import all_scenarios

log = logging.getLogger("gals.seed")


def _seed(db: Session) -> None:
    scenarios = all_scenarios()
    by_field = {s.field: s for s in scenarios}
    first = scenarios[0]

    teacher = User(
        name="Cô Mai",
        email=DEMO_ACCOUNTS["giao_vien"],
        role="teacher",
        avatar_id="avatar-6",
    )
    linh = User(
        name="Nguyễn Khánh Linh",
        email=DEMO_ACCOUNTS["hoc_sinh_co_lop"],
        role="student",
        avatar_id="avatar-2",
    )
    trang = User(
        name="Phạm Thuỳ Trang",
        email=DEMO_ACCOUNTS["hoc_sinh_doc_lap"],
        role="student",
        avatar_id="avatar-4",
    )
    classmates = [
        User(name="Trần Gia Bảo", email="bao@gals.demo", role="student", avatar_id="avatar-1"),
        User(name="Lê Minh Anh", email="minhanh@gals.demo", role="student", avatar_id="avatar-3"),
        User(name="Đỗ Hải Yến", email="haiyen@gals.demo", role="student", avatar_id="avatar-5"),
    ]
    db.add_all([teacher, linh, trang, *classmates])
    db.flush()

    lop_11a2 = Class(teacher_id=teacher.id, class_code="GALS-11A2", name="11A2 — Chuyên đề STEAM")
    lop_10b1 = Class(teacher_id=teacher.id, class_code="GALS-10B1", name="10B1 — Hướng nghiệp sớm")
    db.add_all([lop_11a2, lop_10b1])
    db.flush()

    db.add_all(
        [
            ClassMembership(student_id=linh.id, class_id=lop_11a2.id),
            ClassMembership(student_id=classmates[0].id, class_id=lop_11a2.id),
            ClassMembership(student_id=classmates[1].id, class_id=lop_11a2.id),
            ClassMembership(student_id=classmates[2].id, class_id=lop_10b1.id),
        ]
    )

    db.add_all(
        [
            Assignment(
                class_id=lop_11a2.id,
                scenario_id=first.id,
                mode="online",
                note="Các em làm theo nhịp của mình, không cần xong trong một buổi.",
            ),
            Assignment(
                class_id=lop_10b1.id,
                field="Nghệ thuật",
                mode="offline",
                note="Thảo luận nhóm tại lớp, ghi lại phần suy nghĩ vào nhật ký sau.",
            ),
        ]
    )

    now = datetime.now()

    linh_entry = JournalEntry(
        student_id=linh.id,
        scenario_id=first.id,
        source="guided",
        title=f"Nhật ký — {first.title}",
        content=(
            "Em nghĩ chưa thể kết luận căng tin là nguyên nhân. 31/38 em bị bệnh có ăn ở "
            "căng tin, nhưng 80% cả trường cũng ăn ở đó, nên tỉ lệ này chưa nói lên nhiều. "
            "Em muốn so sánh tỉ lệ mắc giữa nhóm ăn và nhóm không ăn. Em cũng chú ý là "
            "biểu mẫu tự khai có thể làm số liệu lệch."
        ),
        submitted=True,
        image_url="",
        video_url="",
        created_at=now - timedelta(days=2),
    )
    bao_entry = JournalEntry(
        student_id=classmates[0].id,
        scenario_id=first.id,
        source="guided",
        title=f"Nhật ký — {first.title}",
        content=(
            "Em thấy phần khó nhất là hai lớp vừa đi dã ngoại về. Nếu chỉ nhìn vào căng tin "
            "thì sẽ bỏ qua khả năng lây từ chuyến đi đó."
        ),
        submitted=False,
        created_at=now - timedelta(days=1),
    )
    minhanh_entry = JournalEntry(
        student_id=classmates[1].id,
        scenario_id=first.id,
        source="freeform",
        title="Ý tưởng tự do — hộp báo triệu chứng ẩn danh",
        content=(
            "Ý tưởng: đặt một hộp báo triệu chứng ẩn danh ở ký túc xá, để các bạn sợ bỏ thi "
            "vẫn báo được mà không sợ bị gọi tên."
        ),
        created_at=now - timedelta(hours=6),
    )
    db.add_all([linh_entry, bao_entry, minhanh_entry])
    db.flush()

    db.add_all(
        [
            PortfolioEntry(
                student_id=linh.id,
                journal_entry_id=linh_entry.id,
                category="ca_hai",
                description=(
                    "Kế hoạch điều tra đợt bệnh ở trường nội trú — tập trung vào việc so sánh "
                    "đúng nhóm trước khi kết luận nguyên nhân."
                ),
                shared=True,
                order_index=0,
                created_at=now - timedelta(days=2),
            ),
            PortfolioEntry(
                student_id=classmates[1].id,
                journal_entry_id=minhanh_entry.id,
                category="ky_thuat",
                description="Hộp báo triệu chứng ẩn danh cho ký túc xá.",
                shared=False,
                order_index=0,
                created_at=now - timedelta(hours=6),
            ),
        ]
    )

    walked = [
        (
            "Hiểu vấn đề",
            "Câu hỏi nhỏ 1",
            "Bạn chú ý đến điều gì từ những dữ liệu này?",
            "31/38 bạn bị ốm có ăn ở căng tin nghe thì nhiều, nhưng gần như cả trường "
            "đều ăn ở đó nên con số này chưa nói lên gì. Em muốn biết trong nhóm KHÔNG "
            "ăn căng tin thì bao nhiêu bạn bị ốm. Không có số đó thì em chưa so sánh được.",
        ),
        (
            "Hiểu vấn đề",
            "Câu hỏi nhỏ 2",
            "Điều gì bạn đang chắc chắn, điều gì bạn đang giả định?",
            "Em chắc là có 38 bạn ốm và hai lớp vừa đi dã ngoại về. Em đang giả định "
            "là các bạn nhớ đúng mình đã ăn gì — mà cái này thì em không chắc, vì bảng "
            "hỏi là tự khai và mọi người thường nhớ nhầm.",
        ),
        (
            "Đồng cảm",
            "Câu hỏi nhỏ 1",
            "Bạn muốn tìm hiểu góc nhìn của ai trước?",
            "Em muốn hỏi các bạn bị ốm mà KHÔNG báo với y tế trường. Mấy bạn sắp thi "
            "học kỳ chắc sợ bị cho nghỉ nên giấu. Nếu chỉ đếm người đã báo thì em đang "
            "bỏ sót đúng nhóm cần biết nhất.",
        ),
        (
            "Sáng tạo",
            "Câu hỏi nhỏ 1",
            "Trước khi có kết quả xét nghiệm, kế hoạch của bạn cần đạt những gì?",
            "Kế hoạch của em: lập bảng so sánh hai nhóm ăn và không ăn căng tin, hỏi "
            "riêng hai lớp đi dã ngoại, và làm một kênh báo triệu chứng ẩn danh để các "
            "bạn sợ bỏ thi vẫn báo được. Em không đóng cửa căng tin ngay vì chưa có bằng chứng.",
        ),
        (
            "Phản chiếu",
            "Câu hỏi nhỏ 1",
            "Bạn diễn giải những kết quả này như thế nào?",
            "Em vẫn thấy có cách giải thích khác: có thể nguồn lây là chuyến dã ngoại, "
            "còn căng tin chỉ là chỗ đông người nên trông giống nguyên nhân. Nếu nhóm "
            "không ăn căng tin cũng ốm nhiều thì em sẽ phải bỏ giả thuyết ban đầu.",
        ),
    ]
    linh_session = GuidedSession(
        student_id=linh.id,
        scenario_id=first.id,
        stage_index=len(first.stages),
        beat_index=0,
        finished=True,
        synthesis=(
            "Điều đáng chú ý nhất ở bạn là chỗ bạn không tin ngay vào con số 31/38. Bạn "
            "nhận ra rằng một tỉ lệ chỉ có nghĩa khi đặt cạnh nhóm để so sánh, và bạn tự "
            "nói ra mình cần dữ liệu của nhóm không ăn căng tin — đó chính là cách người "
            "làm dịch tễ đọc số liệu.\n\n"
            "Bạn cũng tự chỉ ra giả định của mình về bảng hỏi tự khai, thay vì để nó trôi "
            "qua. Ở phần đồng cảm, bạn nghĩ tới nhóm giấu bệnh vì sợ lỡ kỳ thi — nhóm này "
            "không xuất hiện trong bất kỳ bảng số liệu nào, và bạn vẫn nhớ tới họ.\n\n"
            "Trong kế hoạch, bạn chấp nhận đánh đổi: không đóng cửa căng tin vội, dù làm "
            "vậy sẽ trông quyết đoán hơn. Và đến cuối bạn vẫn để ngỏ khả năng chuyến dã "
            "ngoại mới là nguồn lây. Chỗ bạn còn chưa chắc chắn không phải là chỗ thiếu — "
            "đó là chỗ bạn biết mình cần quay lại khi có thêm dữ kiện."
        ),
        transcript=json.dumps(
            [
                {
                    "kind": "question",
                    "stage": stage,
                    "label": label,
                    "text": text,
                    "answer": answer,
                }
                for stage, label, text, answer in walked
            ],
            ensure_ascii=False,
        ),
        created_at=now - timedelta(days=2),
    )
    db.add(linh_session)

    db.add(
        Feedback(
            teacher_id=teacher.id,
            student_id=linh.id,
            journal_entry_id=None,
            content=(
                "Cô đọc cả bốn cấp độ của em rồi. Điều cô muốn em giữ lại là thói quen "
                "hỏi \u201cso với nhóm nào?\u201d trước khi kết luận — cái đó dùng được ở "
                "rất nhiều môn, không riêng gì phần này. Buổi sau em thử kể lại cho cả "
                "lớp nghe cách em nghĩ nhé, cô nghĩ các bạn sẽ học được."
            ),
            created_at=now - timedelta(hours=20),
        )
    )

    db.add_all(
        [
            Badge(student_id=linh.id, badge_type="nhap_vai_dau_tien", earned_at=now - timedelta(days=2)),
            Badge(student_id=linh.id, badge_type="khoa_hoc", earned_at=now - timedelta(days=2)),
            Badge(student_id=classmates[0].id, badge_type="nhap_vai_dau_tien", earned_at=now - timedelta(days=1)),
        ]
    )

    db.add(
        Feedback(
            teacher_id=teacher.id,
            student_id=linh.id,
            journal_entry_id=linh_entry.id,
            content=(
                "Cô rất thích chỗ em nhận ra 31/38 chưa đủ để kết luận. Đó đúng là cách một "
                "người làm dịch tễ suy nghĩ. Lần tới em thử viết rõ mình cần so sánh với "
                "nhóm nào nhé."
            ),
            created_at=now - timedelta(days=1),
        )
    )

    db.add_all(
        [
            Notification(
                type="talkshow",
                title="Talkshow: Một ngày của kỹ sư năng lượng",
                content=(
                    "Khách mời chia sẻ về công việc vận hành lưới điện và những quyết định "
                    "phải đưa ra khi dữ liệu chưa đầy đủ. Miễn phí, có phiên hỏi đáp."
                ),
                field="Kỹ thuật",
                created_at=now - timedelta(days=3),
            ),
            Notification(
                type="workshop",
                title="Workshop: Đọc dữ liệu trước khi tin vào nó",
                content=(
                    "Buổi thực hành hai giờ về cách nhận ra thiên lệch trong khảo sát — "
                    "dành cho học sinh THPT, không yêu cầu kiến thức thống kê trước."
                ),
                field="Toán",
                created_at=now - timedelta(days=1),
            ),
            Notification(
                class_id=lop_11a2.id,
                type="workshop",
                title="Buổi hướng dẫn nộp dự án (lớp 11A2)",
                content="Cô Mai sẽ hướng dẫn cách viết phần mô tả dự án vào tiết sinh hoạt thứ Sáu.",
                created_at=now - timedelta(hours=10),
            ),
        ]
    )

    db.commit()

    log.info(
        "Đã gieo dữ liệu: %d người dùng, %d lớp, %d kịch huống (%s)",
        db.query(User).count(),
        db.query(Class).count(),
        len(scenarios),
        ", ".join(sorted(by_field)),
    )


def reset_and_seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()
