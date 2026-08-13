from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine, is_sqlite
from app.security import hash_password
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
    School,
    User,
)
from app.scenarios import all_scenarios
from app.schools import MA_SONG_NGAY

log = logging.getLogger("gals.seed")

# Đây là GIÀN GIÁO KIỂM THỬ, không phải mã ứng dụng.
#
# Trước kia file này nằm ở app/seed.py và vòng đời FastAPI gọi nó lúc khởi
# động, nên một cơ sở dữ liệu trống tự mọc ra sáu tài khoản có mật khẩu nằm
# công khai trong mã nguồn. Giờ ứng dụng không gieo gì cả: dữ liệu chỉ xuất
# hiện khi có người tạo ra nó. Những nhân vật dưới đây tồn tại để hơn bốn trăm
# bài kiểm thử có ai đó để đăng nhập, và không đường nào từ app/ gọi tới đây.

# Ba nhân vật mẫu, chỉ dùng trong kiểm thử.
SEED_EMAILS = {
    "giao_vien": "co.mai@gals.demo",
    "hoc_sinh_co_lop": "linh@gals.demo",
    "hoc_sinh_doc_lap": "trang@gals.demo",
}

# Mật khẩu này công khai trong mã nguồn, nên nó tuyệt đối không được tồn tại ở
# nơi có dữ liệu thật. `_refuse_people_on_a_real_database()` bên dưới là thứ
# bảo đảm điều đó, chứ không phải trí nhớ của người deploy.
SEED_PASSWORD = "mat-khau-mau-1234"


def _refuse_people_on_a_real_database() -> None:
    if not is_sqlite:
        raise RuntimeError(
            "Từ chối gieo tài khoản mẫu: DATABASE_URL không phải SQLite. "
            "Mật khẩu mẫu nằm sẵn trong mã nguồn nên không được đặt lên "
            "cơ sở dữ liệu thật."
        )


def _seed(db: Session) -> None:
    _refuse_people_on_a_real_database()
    scenarios = all_scenarios()
    by_field = {s.field: s for s in scenarios}
    first = scenarios[0]

    # Băm một lần rồi dùng lại: Argon2 cố tình tốn thời gian, băm sáu lần làm
    # mỗi bài kiểm thử chậm thêm thấy rõ mà chẳng được gì.
    bam = hash_password(SEED_PASSWORD)

    truong = School(
        ten="THPT Nguyễn Trãi",
        tinh_thanh="Hà Nội",
        ma_giao_vien="MAUGIAOVIEN",
        ma_het_han=datetime.now() + timedelta(days=MA_SONG_NGAY),
        lien_he_ten="Thầy Hùng",
        lien_he_email="hop.tac@thpt-nguyentrai.demo",
    )
    db.add(truong)
    db.flush()

    teacher = User(
        name="Cô Mai",
        email=SEED_EMAILS["giao_vien"],
        role="teacher",
        avatar_id="avatar-6",
        password_hash=bam,
        school_id=truong.id,
    )
    linh = User(
        name="Nguyễn Khánh Linh",
        email=SEED_EMAILS["hoc_sinh_co_lop"],
        role="student",
        avatar_id="avatar-2",
        password_hash=bam,
    )
    trang = User(
        name="Phạm Thuỳ Trang",
        email=SEED_EMAILS["hoc_sinh_doc_lap"],
        role="student",
        avatar_id="avatar-4",
        password_hash=bam,
    )
    classmates = [
        User(name="Trần Gia Bảo", email="bao@gals.demo", role="student",
             avatar_id="avatar-1", password_hash=bam),
        User(name="Lê Minh Anh", email="minhanh@gals.demo", role="student",
             avatar_id="avatar-3", password_hash=bam),
        User(name="Đỗ Hải Yến", email="haiyen@gals.demo", role="student",
             avatar_id="avatar-5", password_hash=bam),
    ]
    db.add_all([teacher, linh, trang, *classmates])
    db.flush()

    # Tiền tố hồ sơ đặt sẵn và cố ý không giống mã lớp — mẫu gieo phải trông
    # đúng như dữ liệu thật, không thì đọc mẫu sẽ hiểu nhầm là hai thứ này liên
    # quan tới nhau.
    lop_11a2 = Class(teacher_id=teacher.id, class_code="GALS-11A2",
                     roster_prefix="HSK7Q2",
                     name="11A2 — Chuyên đề STEAM", school_id=truong.id)
    lop_10b1 = Class(teacher_id=teacher.id, class_code="GALS-10B1",
                     roster_prefix="HSM4TB",
                     name="10B1 — Hướng nghiệp sớm", school_id=truong.id)
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
        class_id=lop_11a2.id,
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
        class_id=lop_11a2.id,
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
        class_id=lop_11a2.id,
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

    toan = by_field["Toán"]
    ngoc_answers = [
        "Em thấy 'khó khăn nhất' và 'học lực tốt nhất' là hai tiêu chí khác nhau, mà đề "
        "bài lại nói như thể chúng luôn đi cùng nhau. Em muốn hỏi lại ban điều hành: một "
        "em rất khó khăn nhưng học lực chỉ trung bình thì có được xét không?",
        "Em biết được có 62 em thuộc cả hai nhóm, tức là nếu chỉ trao cho nhóm đó thì vừa "
        "đủ 60 suất như năm ngoái. Nhưng em chưa biết trong 180 em hộ nghèo thì mức khó "
        "khăn chênh nhau ra sao, vì thu nhập là do người nộp tự khai.",
        "Em nghĩ là không so trực tiếp được. Mỗi trường ra đề và chấm khác nhau, nên 8,0 ở "
        "trường này chưa chắc bằng 8,0 ở trường kia. Muốn so thì có lẽ phải xếp hạng trong "
        "từng trường trước rồi mới ghép lại.",
        "Bài toán không còn là chọn 60 em nghèo nhất và giỏi nhất nữa. Giấy chứng nhận cận "
        "nghèo phụ thuộc vào quy trình của từng xã, còn điểm thấp có khi lại là dấu hiệu "
        "của hoàn cảnh khó chứ không phải của học kém.",
        "Em phát biểu lại là: chia 900 triệu sao cho tiền tới được những em mà khoản này "
        "thay đổi được nhiều nhất, trong điều kiện dữ liệu về hoàn cảnh không chính xác "
        "đều nhau giữa các hồ sơ. Giả định của em là quỹ chấp nhận trao ít suất hơn nhưng "
        "mỗi suất lớn hơn.",
        "Em muốn nghe giáo viên giới thiệu trước, vì họ biết hoàn cảnh thật của các em hơn "
        "tờ đơn. Nhưng mỗi thầy cô chỉ biết lớp mình, nên nghe xong em vẫn phải đối chiếu "
        "lại với hồ sơ.",
    ]
    ngoc_replies = [
        "Bạn vừa tách được hai tiêu chí mà đề bài gộp làm một. Nếu ban điều hành trả lời "
        "rằng phải đủ cả hai, số hồ sơ còn lại sẽ thay đổi thế nào?",
        "Chỗ bạn dừng lại ở 'thu nhập là tự khai' là chỗ đáng dừng. Có dấu hiệu nào khác "
        "trong hồ sơ giúp bạn đoán được mức tin cậy của phần tự khai đó không?",
        "Bạn đã nghĩ tới việc xếp hạng trong từng trường. Nếu một trường chỉ có ba em nộp "
        "đơn thì thứ hạng ở đó nói lên được điều gì?",
        "Bạn vừa nhận ra hai tiêu chí có thể kéo ngược nhau. Nếu đúng như vậy, khi buộc "
        "phải chọn thì bạn nghiêng về nhóm nào, và vì sao?",
        "Cách phát biểu lại của bạn đã hỏi về tác động chứ không chỉ về xếp loại. Ai sẽ là "
        "người chịu thiệt nếu số suất giảm xuống?",
        "Bạn tự nêu giới hạn của nguồn tin ngay khi chọn nó. Ngoài giáo viên, còn ai biết "
        "hoàn cảnh của các em mà chưa xuất hiện trong danh sách của bạn?",
    ]

    ngoc_entries: list[dict] = []
    answer_index = 0
    for stage_index, stage in enumerate(toan.stages[:2]):
        last_beat = 3 if stage_index == 1 else len(stage.beats)
        for beat in stage.beats[:last_beat]:
            ngoc_entries.append(
                {
                    "kind": beat.type,
                    "stage": stage.name,
                    "label": beat.label or stage.name,
                    "text": beat.text,
                    "answer": ngoc_answers[answer_index] if beat.needs_answer else "",
                }
            )
            if beat.needs_answer:
                ngoc_entries.append(
                    {
                        "kind": "ai",
                        "stage": stage.name,
                        "label": "Người đồng hành",
                        "text": ngoc_replies[answer_index],
                        "answer": "",
                    }
                )
                answer_index += 1
        if stage_index == 0 and stage.closing:
            ngoc_entries.append(
                {
                    "kind": "closing",
                    "stage": stage.name,
                    "label": f"Câu kết cấp độ · {stage.name}",
                    "text": stage.closing,
                    "answer": ngoc_answers[answer_index],
                }
            )
            ngoc_entries.append(
                {
                    "kind": "ai",
                    "stage": stage.name,
                    "label": "Người đồng hành",
                    "text": ngoc_replies[answer_index],
                    "answer": "",
                }
            )
            answer_index += 1

    db.add(
        GuidedSession(
            student_id=linh.id,
            scenario_id=toan.id,
            stage_index=1,
            beat_index=3,
            finished=False,
            transcript=json.dumps(ngoc_entries, ensure_ascii=False),
            created_at=now - timedelta(hours=6),
        )
    )

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
    """Xoá sạch rồi gieo lại. Chỉ dùng cho kiểm thử và cho môi trường dev."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()
