# Hướng dẫn kỹ thuật

Tài liệu cho người phát triển. Phần dành cho người dùng nằm ở [README](../README.md).

---

## Công nghệ

| Lớp | Công nghệ |
|---|---|
| Máy chủ | FastAPI (Python 3.11+) |
| Giao diện | Jinja2, render phía máy chủ |
| Tương tác | HTMX (tự host, không CDN) |
| CSS | Tailwind v4 qua Tailwind CLI |
| Dữ liệu | SQLite + SQLAlchemy, gieo lại mỗi lần khởi động |
| AI | `google-genai` (SDK Gemini hiện hành) |

```
app/
  main.py          Khởi tạo FastAPI, gieo dữ liệu lúc khởi động
  config.py        5 lĩnh vực STEAM, thứ tự ưu tiên model, trần 30 lượt chat
  models.py        Bảng dữ liệu
  seed.py          Xoá và gieo lại toàn bộ mỗi lần khởi động
  auth.py          Phiên đăng nhập bằng cookie đã ký
  scenarios.py     Nạp và kiểm tra kịch huống  ← đọc file này trước
  gemini.py        Hai chế độ trò chuyện + rào an toàn
  routers/         auth · student · teacher · chat
  templates/
data/
  scenarios.json   Nội dung kịch huống
  resources.json   Tài nguyên miễn phí theo lĩnh vực
static/css/app.css File CSS đã build — có commit vào repo
legacy/            Bản mẫu HTML cũ, chỉ để tham khảo
```

Cơ sở dữ liệu bị xoá và gieo lại mỗi lần khởi động — cứ xoá `gals.db` thoải mái.

> ⚠️ Tailwind quét class **tĩnh**. Đừng ghép chuỗi kiểu `border-l-{{ color }}` trong Jinja — class sẽ không được sinh ra. Luôn để tên class đủ chữ trong dữ liệu.

---

## Bật trợ lý AI

Không bắt buộc. Không có khoá thì ứng dụng vẫn chạy đủ, chỉ là trợ lý trả lời bằng câu dựng sẵn, và giao diện nói rõ điều đó.

1. Lấy khoá miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey)
2. Tạo file `.env` ở thư mục gốc dự án
3. Thêm một dòng:

```
GEMINI_API_KEY=khoa-cua-ban
```

4. Chạy lại ứng dụng

> ⚠️ **Không bao giờ commit khoá này.** File `.env` đã nằm trong `.gitignore`. Khi deploy thì điền khoá trong bảng Environment của Render, không đưa vào mã nguồn.

### Biến môi trường

| Biến | Ý nghĩa |
|---|---|
| `GEMINI_API_KEY` | Khoá Gemini. Bỏ trống → chế độ demo ngoại tuyến |
| `GEMINI_MODEL` | Ghi đè tên model. Bỏ trống → tự dò model flash mới nhất |
| `SECRET_KEY` | Khoá ký cookie. Nên đặt khi deploy |

### Kiểm tra khoá đã chạy chưa

Cuối mỗi trang, dòng *"Đang chạy ở chế độ demo ngoại tuyến"* sẽ biến mất khi có khoá.

Nhưng dòng đó chỉ báo là **tìm thấy khoá**, không đảm bảo khoá **dùng được**. Nếu khoá sai hoặc hết hạn mức, ứng dụng lặng lẽ quay về câu dựng sẵn. Muốn chắc thì mở *Ý tưởng tự do* gửi một tin nhắn — câu trả lời thật sẽ nhắc tới nội dung bạn vừa viết.

### Lưu ý về model dòng flash

Model flash bật "suy nghĩ" mặc định, và phần suy nghĩ **ăn chung hạn mức output**. Đo thực tế: 381/400 token rơi vào phần suy nghĩ, chỉ còn 15 token cho câu trả lời → cụt giữa câu.

Cách tắt lại khác nhau giữa các đời model (`thinking_budget=0` bị từ chối trên `gemini-flash-latest`). `app/gemini.py` thử lần lượt vài cách và nhớ cách nào được chấp nhận, đồng thời luôn để hạn mức output rộng để phòng trường hợp không tắt được.

---

## Thêm kịch huống mới

Kịch huống **không phải** mô tả phẳng. Mỗi kịch huống là kịch bản đi qua bốn cấp độ, mỗi cấp độ là một mảng `beats` **có thứ tự**, đan xen khối bối cảnh với câu hỏi.

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
  "domain_skills": ["Phương pháp khoa học", "Dịch tễ học"],
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

Design Thinking chỉ là khung dẫn dắt. Nội dung bên trong phải thể hiện đúng cách mỗi nghề thu thập bằng chứng và ra quyết định. Nếu nghề nào cũng chỉ "phỏng vấn người dùng rồi thiết kế ứng dụng", người học sẽ hiểu sai bản chất nghề nghiệp.

| Nghề | Sản phẩm của cấp độ Sáng tạo |
|---|---|
| Chuyên viên tài chính | Mô hình phân bổ ngân sách |
| Kỹ sư năng lượng | Phương án hệ thống và kế hoạch thử nghiệm |
| Chuyên viên hoá học | Quy trình lấy và kiểm tra mẫu |
| Chuyên viên dịch tễ | Kế hoạch điều tra và phòng ngừa |
| Chuyên viên an ninh mạng | Quy trình phản ứng sự cố |
| Nhà quy hoạch | Kịch bản sử dụng không gian hoặc giao thông |
| Nhà truyền thông | Thông điệp cho từng nhóm đối tượng |

Giao diện cấp độ 3 và lời nhắc gửi cho AI đều đọc `creation_output`.

---

## Deploy lên Render

File `render.yaml` đã có sẵn — trỏ Render vào repo và chọn *Blueprint*, Render tự điền mọi trường.

Nếu tạo Web Service thủ công:

```
Build:  pip install -r requirements.txt
Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

`$PORT` phải giữ nguyên, đừng thay bằng số cụ thể. `--host 0.0.0.0` để ứng dụng nhận kết nối từ bên ngoài.

- **Không cần Node khi deploy.** CSS đã build sẵn và commit vào repo.
- **SQLite bị đặt lại mỗi lần deploy** — không sao, dữ liệu tự gieo lại.
- **Gói miễn phí có cold start.** Lượt truy cập đầu sau khi ngủ mất 30–60 giây.

---

## Hệ thống thiết kế

Bảng màu khai báo một lần trong `src/input.css`:

| Vai trò | Mã màu |
|---|---|
| Thân/hệ thống | `#4A4E9C` |
| Dự án học tập | `#1F8A70` |
| Hồ sơ năng lực | `#C98A2E` |
| Huy hiệu | `#8B4B6B` |
| Tài nguyên | `#4F6F94` |
| Nền giấy ấm | `#F6F5F1` |

Chữ: **Be Vietnam Pro** cho tiêu đề (xưởng chữ Việt, dấu được vẽ từ đầu) + **Lexend** cho nội dung. Cả hai tự host, không phụ thuộc CDN.

### Bản in

`src/input.css` có khối `@media print` riêng cho trang tài liệu buổi học: ẩn phần điều hướng, mỗi cấp độ sang một trang mới, và hiện dòng kẻ để học sinh viết tay. Xem `app/templates/teacher/tai_lieu_in.html`.
