from __future__ import annotations

import re

from app.scenarios import all_scenarios
from tests.conftest import login_independent, login_student, login_teacher

HREF = re.compile(r'href="(/[^"#]*)"')


def test_student_pages_and_links(client):
    login_student(client)
    urls = [
        "/", "/trang-ca-nhan", "/du-an", "/ho-so", "/ho-so/chia-se",
        "/ho-so/y-tuong-tu-do", "/huy-hieu", "/tai-nguyen",
        "/dang-nhap", "/dang-ky", "/chon-avatar",
    ]
    for s in all_scenarios():
        urls += [f"/du-an/{s.id}", f"/du-an/{s.id}/khong-gian-tu-duy", f"/du-an/{s.id}/nop"]

    seen: set[str] = set()
    for u in urls:
        r = client.get(u)
        assert r.status_code == 200, u
        seen.update(HREF.findall(r.text))

    dead = [h for h in sorted(seen) if client.get(h).status_code not in (200, 303, 307)]
    assert dead == []


def test_teacher_pages_and_links(client):
    login_teacher(client)
    home = client.get("/giao-vien")
    assert home.status_code == 200

    urls = ["/giao-vien", "/giao-vien/thong-bao", "/giao-vien/tai-lieu"]
    urls += [f"/giao-vien/tai-lieu/{s.id}" for s in all_scenarios()]
    for cid in set(re.findall(r'/giao-vien/lop/(\d+)"', home.text)):
        urls.append(f"/giao-vien/lop/{cid}")
        lop = client.get(f"/giao-vien/lop/{cid}").text
        urls += [f"/giao-vien/hoc-sinh/{sid}" for sid in set(re.findall(r'/giao-vien/hoc-sinh/(\d+)"', lop))]

    seen: set[str] = set()
    for u in urls:
        r = client.get(u)
        assert r.status_code == 200, u
        seen.update(HREF.findall(r.text))

    dead = [h for h in sorted(seen) if client.get(h).status_code not in (200, 303, 307)]
    assert dead == []


def test_unknown_page_renders_404(client):
    assert client.get("/khong-ton-tai").status_code == 404


def test_teacher_dashboard_says_what_is_true_now(client):
    login_teacher(client)
    page = client.get("/giao-vien").text
    for phrase in [
        "đang trong giai đoạn thử nghiệm",
        "chưa có sao lưu",
        "chỉ đọc được phần học sinh nộp",
        "đừng để học sinh nhập thông tin thật",
        "không phải công cụ hỗ trợ tâm lý",
    ]:
        assert phrase.lower() in page.lower(), phrase

    # Tài khoản đã là thật, dữ liệu đã ở lại. Hai câu cũ giờ là nói sai.
    for gone in ["không được lưu lại", "xoá sạch"]:
        assert gone.lower() not in page.lower(), gone


def test_legal_notice_exists_and_is_linked_everywhere(client):
    from pathlib import Path

    legal = Path("LEGAL.md").read_text(encoding="utf-8")
    for heading in ["Tuyên bố về bản mẫu", "Dữ liệu đi những đâu", "Trách nhiệm pháp lý"]:
        assert heading in legal, heading
    assert "111" in legal

    assert "LEGAL.md" in Path("README.md").read_text(encoding="utf-8")

    login_independent(client)
    assert "LEGAL.md" in client.get("/trang-ca-nhan").text


def test_field_page_explains_how_scenarios_are_built(client):
    login_independent(client)
    page = client.get("/du-an").text
    assert "Các tình huống ở đây được dựng thế nào" in page
    for claim in [
        "đi tìm bằng chứng theo cách riêng",
        "Sản phẩm cuối mỗi nghề một khác",
        "cố tình chưa đủ để kết luận",
        "dữ liệu giả định",
    ]:
        assert claim in page, claim


MARKETING = ["/", "/kham-pha", "/linh-vuc", "/ve-chung-toi"]


def test_public_pages_open_without_login(client):
    client.get("/dang-xuat")
    for url in MARKETING:
        r = client.get(url)
        assert r.status_code == 200, url
        assert "Đăng ký miễn phí" in r.text, url
        assert "/ve-chung-toi" in r.text, url


def test_explore_filters_by_field(client):
    all_page = client.get("/kham-pha").text
    assert all_page.count("Bắt đầu tình huống này") == len(all_scenarios())

    one = client.get("/kham-pha?linh_vuc=khoa_hoc").text
    assert one.count("Bắt đầu tình huống này") == 1
    assert "Khoa học" in one

    assert client.get("/kham-pha?linh_vuc=khong-co-that").status_code == 200


def test_landing_roadmap_has_all_three_stops(client):
    page = client.get("/").text
    assert page.count('class="road-stop"') == 3
    for gone in ["Điểm số", "So sánh với bạn khác", "Đáp án mẫu"]:
        assert gone in page
    assert page.count("Thay vào đó") == 3


def test_about_page_still_reaches_the_legal_notice(client):
    page = client.get("/ve-chung-toi").text
    assert "LEGAL.md" in page
    assert "Nguyên tắc chúng tôi giữ" in page


# Những câu chỉ đúng khi cả ứng dụng còn dùng chung ba tài khoản. Bây giờ mỗi
# người một tài khoản và dữ liệu ở lại, nên chúng là nói sai — nguy hiểm hơn cả
# im lặng, vì người đọc sẽ tin.
LOI_HUA_CU = [
    "ai cũng đọc được bài của người khác",
    "ba tài khoản dùng chung",
    "bị xoá mỗi lần máy chủ khởi động lại",
    "không được lưu lại",
]


def test_every_public_page_footer_tells_the_truth_about_accounts(client):
    from pathlib import Path

    disclaimer = Path("DISCLAIMER.md").read_text(encoding="utf-8")
    for heading in ["Mỗi người một tài khoản riêng", "Không bảo đảm"]:
        assert heading in disclaimer, heading
    assert "111" in disclaimer

    for url in MARKETING:
        page = client.get(url).text
        assert "đang trong giai đoạn thử nghiệm" in page.lower(), url
        assert "/chinh-sach-rieng-tu" in page, url


def test_no_page_still_carries_a_claim_from_the_shared_account_days(client):
    """Bài canh cho cả hai chiều: bỏ demo đi thì phải bỏ luôn lời cảnh báo về demo."""
    login_teacher(client)
    trang = MARKETING + ["/giao-vien", "/tai-khoan"]
    for url in trang:
        page = client.get(url).text.lower()
        for cau in LOI_HUA_CU:
            assert cau not in page, f"{url} còn câu cũ: {cau}"
