from __future__ import annotations

from app.scenarios import all_scenarios
from tests.conftest import login_student

# Các cụm khẳng định SỰ TỒN TẠI của điểm/xếp hạng. Không dùng từ đơn lẻ như
# "điểm số" vì phần giới thiệu cố tình viết "không có điểm số".
BANNED = [
    "Bảng xếp hạng",
    "Điểm số của bạn",
    "Điểm của bạn",
    "Xếp hạng lớp",
    "Xếp hạng của bạn",
    "điểm trung bình của bạn",
    "/10 điểm",
    "Hạng nhất lớp",
]


def test_no_grading_ui_anywhere_student_facing(client):
    login_student(client)
    urls = ["/", "/trang-ca-nhan", "/du-an", "/ho-so", "/huy-hieu", "/tai-nguyen",
            "/ho-so/y-tuong-tu-do", "/ho-so/chia-se"]
    for s in all_scenarios():
        urls += [f"/du-an/{s.id}", f"/du-an/{s.id}/khong-gian-tu-duy"]
    for u in urls:
        page = client.get(u).text
        for phrase in BANNED:
            assert phrase not in page, f"{phrase!r} xuất hiện ở {u}"


def test_synthesis_has_no_grading(client):
    login_student(client)
    sid = all_scenarios()[0].id
    for _ in range(250):
        page = client.get(f"/du-an/{sid}/khong-gian-tu-duy")
        if "đã đi hết bốn cấp độ" in page.text.lower():
            break
        client.post(f"/du-an/{sid}/tiep", data={"tra_loi": "Em chưa chắc chắn lắm."})
    final = client.get(f"/du-an/{sid}/khong-gian-tu-duy").text
    for phrase in BANNED + ["đáp án đúng là", "xếp loại"]:
        assert phrase not in final
