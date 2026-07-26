# GALS

**Thử làm nghề trước khi phải chọn nghề.**

Nền tảng web giúp học sinh THPT tập tư duy thiết kế thông qua những tình huống nghề nghiệp có thật — dữ liệu chưa đầy đủ, các bên liên quan muốn những điều khác nhau, và không có đáp án nào sẵn.

Sản phẩm nhắm vào ba khoảng trống: học sinh THPT ít được thực hành tư duy thiết kế, ít được khám phá nghề nghiệp, và vẫn còn định kiến giới trong các ngành STEAM.

> **Không chấm điểm. Không xếp hạng. Không có "đáp án mẫu".**
> Đây là công cụ, không phải khoá học tuyến tính — học sinh quay lại và khám phá tự do bất cứ lúc nào.

---

## Trạng thái hiện tại

Đây là **bản mẫu tương tác đang xây dựng dở**, mới xong Giai đoạn 1 trong 5.

| | Hạng mục | Trạng thái |
|---|---|---|
| 1 | Khung ứng dụng, hệ thống thiết kế, đăng nhập giả, khung điều hướng | ✅ Xong |
| 2a | Nội dung kịch huống | ⏳ 2/5 kịch huống |
| 2b | Luồng học sinh trọn vẹn | ⬜ Chưa |
| 3 | Luồng giáo viên | ⬜ Chưa |
| 4 | Tích hợp Gemini (hai chế độ trò chuyện) | ⬜ Chưa |
| 5 | Hoàn thiện, deploy, kịch bản demo | ⬜ Chưa |

**Chạy được ngay:** trang chủ, đăng ký, đăng nhập, chọn avatar, ba tài khoản Demo nhanh, trang cá nhân với dữ liệu mẫu.
**Chưa dựng:** bốn nhánh trải nghiệm (đang là trang giữ chỗ), khu giáo viên, và toàn bộ phần AI.

---

## Cài đặt

Cần **Python 3.11+** và **Node 18+** (Node chỉ dùng để build CSS).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

npm install
npm run build:css

.venv/bin/uvicorn app.main:app --reload
```

Mở http://127.0.0.1:8000

Khi sửa CSS, chạy song song `npm run watch:css`. **Nhớ commit lại `static/css/app.css`** — file build được commit vào repo vì Render không có Node.

Cơ sở dữ liệu SQLite được **xoá và gieo lại mỗi lần khởi động**, nên cứ xoá `gals.db` thoải mái.

---

## Biến môi trường

Sao chép `.env.example` thành `.env`. Không commit `.env`.

| Biến | Bắt buộc | Ý nghĩa |
|---|---|---|
| `GEMINI_API_KEY` | Không | Khoá API Gemini ([lấy tại đây](https://aistudio.google.com/apikey)). Để trống thì ứng dụng chạy ở **chế độ demo ngoại tuyến** — AI trả lời bằng kịch bản dựng sẵn, mọi màn hình vẫn bấm được. |
| `GEMINI_MODEL` | Không | Ghi đè tên model. Bỏ trống thì ứng dụng tự dò model flash mới nhất lúc khởi động qua `models.list()`. |
| `SECRET_KEY` | Nên đặt khi deploy | Khoá ký cookie phiên đăng nhập. |

Khoá API **chỉ nằm ở phía máy chủ**, không bao giờ gửi xuống trình duyệt.

---

## Kịch bản demo cho ban giám khảo — dưới 5 phút

Ở màn hình đăng nhập có khối **Demo nhanh** với ba nút, không cần gõ gì.

**1. Học sinh (có lớp) — khoảng 2 phút**
Bấm **Học sinh (có lớp)** → vào thẳng trang cá nhân của Linh, lớp 11A2.
Chỉ ra: tiến độ được mô tả bằng *hành trình* chứ không phải điểm số; lời nhắn riêng tư từ cô Mai; bốn nhánh trải nghiệm không có thứ tự bắt buộc.

**2. Học sinh (độc lập) — khoảng 1 phút**
Đăng xuất → bấm **Học sinh (độc lập)**.
Chỉ ra: cùng một sản phẩm, nhưng không thuộc lớp nào và không giáo viên nào xem được — quyền riêng tư là mặc định, không phải tuỳ chọn.

**3. Giáo viên — khoảng 1 phút**
Đăng xuất → bấm **Giáo viên** để xem khu giáo viên.

**4. Đăng ký thử — khoảng 1 phút**
Đăng xuất → **Đăng ký** → điền gì cũng được, mã lớp `GALS-11A2` → chọn avatar.
Chỉ ra: mã lớp không bắt buộc, và phần giải thích rõ hệ quả của việc điền hay bỏ trống.

> Cả bốn nhánh trải nghiệm và khu giáo viên hiện là trang giữ chỗ — sẽ dựng ở Giai đoạn 2 và 3.

---

## Kiến trúc

| Lớp | Công nghệ |
|---|---|
| Máy chủ | FastAPI (Python 3.11+) |
| Giao diện | Jinja2, render phía máy chủ |
| Tương tác | HTMX (tự host, không CDN) |
| CSS | Tailwind v4 qua Tailwind CLI, build ra file tĩnh |
| Dữ liệu | SQLite + SQLAlchemy, gieo lại mỗi lần khởi động |
| AI | `google-genai` (SDK Gemini hiện hành) |

```
app/
  main.py          Khởi tạo FastAPI, gieo dữ liệu lúc khởi động
  config.py        5 lĩnh vực STEAM, thứ tự ưu tiên model, trần 30 lượt chat
  models.py        Bảng dữ liệu, cộng Feedback và GuidedSession
  seed.py          Xoá và gieo lại toàn bộ mỗi lần khởi động
  auth.py          Phiên đăng nhập bằng cookie đã ký
  scenarios.py     Nạp và kiểm tra kịch huống  ← đọc file này trước
  routers/         auth · student · teacher · chat
  templates/       base + auth/ + student/ + teacher/
data/
  scenarios.json   Nội dung kịch huống
  resources.json   Tài nguyên miễn phí theo lĩnh vực
src/input.css      Token bảng màu @theme + lớp component
static/css/app.css File CSS đã build — có commit vào repo
legacy/            Bản mẫu HTML cũ, chỉ để tham khảo
```

### Hệ thống thiết kế

Bảng màu giữ nguyên từ các sơ đồ đã trình bày với ban giám khảo, khai báo một lần trong `src/input.css`:

| Vai trò | Mã màu |
|---|---|
| Thân/hệ thống | `#4A4E9C` |
| Dự án học tập | `#1F8A70` |
| Hồ sơ năng lực | `#C98A2E` |
| Huy hiệu | `#8B4B6B` |
| Tài nguyên | `#4F6F94` |
| Nền giấy ấm | `#F6F5F1` |

Chữ: **Be Vietnam Pro 800** cho tiêu đề (xưởng chữ Việt, dấu được vẽ từ đầu) + **Lexend** cho nội dung. Cả hai tự host, không phụ thuộc CDN.

> ⚠️ Tailwind quét class **tĩnh**. Đừng ghép chuỗi kiểu `border-l-{{ color }}` trong Jinja — class sẽ không được sinh ra. Luôn để tên class đủ chữ trong dữ liệu.

---

## Thêm kịch huống mới

Kịch huống **không phải** mô tả phẳng. Mỗi kịch huống là một kịch bản đi qua bốn cấp độ — *Hiểu vấn đề → Đồng cảm → Sáng tạo → Phản chiếu* — trong đó mỗi cấp độ là một mảng `beats` **có thứ tự**, đan xen khối bối cảnh với câu hỏi.

Nhãn và số lượng beat khác nhau giữa các kịch huống, nên nhãn nằm trong dữ liệu chứ không nằm trong code.

```jsonc
{
  "id": "dich-te-truong-noi-tru",
  "field": "Khoa học",              // 1 trong 5 lĩnh vực STEAM
  "career_group": "Y sinh, dịch tễ",
  "title": "Điều gì đang khiến học sinh bị ốm?",
  "role": "Chuyên viên dịch tễ học",
  "protagonist": "An",
  "has_female_protagonist": true,
  "knowledge": "Sinh học – vi sinh vật, cơ chế lây bệnh…",
  "domain_skills": ["Phương pháp khoa học", "Dịch tễ học", "Đạo đức nghiên cứu"],
  "creation_output": "Kế hoạch điều tra và phòng ngừa",
  "disclaimer": "Các dữ liệu sau là dữ liệu giả định cho prototype.",
  "description": "Tóm tắt ngắn hiển thị ở thẻ chọn kịch huống",
  "stages": [
    {
      "key": "hieu_van_de",          // hieu_van_de | dong_cam | sang_tao | phan_chieu
      "name": "Hiểu vấn đề",
      "beats": [
        { "type": "context",  "label": "Bối cảnh ban đầu", "text": "…" },
        { "type": "question", "label": "Câu hỏi nhỏ 1",    "text": "…" },
        { "type": "followup", "label": "Follow-up",        "text": "…" }
      ],
      "closing": "Câu hỏi khép lại cấp độ"
    }
  ]
}
```

`type` nhận `context` (khối kể chuyện, không cần trả lời), `question` và `followup` (học sinh trả lời).

### Vì sao có `domain_skills` và `creation_output`

Design Thinking chỉ là **khung dẫn dắt tư duy**. Nội dung bên trong phải thể hiện đúng cách mỗi nghề thu thập bằng chứng và ra quyết định. Nếu nghề nào cũng chỉ "phỏng vấn người dùng rồi thiết kế ứng dụng", người học sẽ hiểu sai bản chất nghề nghiệp.

`creation_output` quy định **cấp độ 3 thật sự tạo ra cái gì** — và thường không phải một ứng dụng:

| Nghề | Sản phẩm của cấp độ Sáng tạo |
|---|---|
| Chuyên viên tài chính | Mô hình phân bổ ngân sách |
| Kỹ sư năng lượng | Phương án hệ thống và kế hoạch thử nghiệm |
| Chuyên viên hoá học | Quy trình lấy và kiểm tra mẫu |
| Chuyên viên dịch tễ | Kế hoạch điều tra và phòng ngừa |
| Chuyên viên an ninh mạng | Quy trình phản ứng sự cố |
| Nhà quy hoạch | Kịch bản sử dụng không gian hoặc giao thông |
| Nhà truyền thông | Thông điệp cho từng nhóm đối tượng |

Giao diện cấp độ 3 và prompt AI đều đọc trường này.

---

## Deploy

Dự kiến chạy trên **Render.com** (gói web service miễn phí).

```
Build:  pip install -r requirements.txt
Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Đặt `GEMINI_API_KEY` và `SECRET_KEY` trong phần Environment của Render. SQLite bị đặt lại mỗi lần deploy — không sao, dữ liệu tự gieo lại.

`render.yaml` sẽ được thêm ở Giai đoạn 5.

---

*Toàn bộ dữ liệu trong ứng dụng là dữ liệu giả định cho bản mẫu.*
