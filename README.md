# GALS

**Thử làm nghề trước khi phải chọn nghề.**

Nền tảng web giúp học sinh THPT tập tư duy thiết kế thông qua những tình huống nghề nghiệp có thật — dữ liệu chưa đầy đủ, các bên liên quan muốn những điều khác nhau, và không có đáp án nào sẵn.

Sản phẩm nhắm vào ba khoảng trống: học sinh THPT ít được thực hành tư duy thiết kế, ít được khám phá nghề nghiệp, và vẫn còn định kiến giới trong các ngành STEAM.

> **Không chấm điểm. Không xếp hạng. Không có "đáp án mẫu".**
> Đây là công cụ, không phải khoá học tuyến tính — học sinh quay lại và khám phá tự do bất cứ lúc nào.

---

## Trạng thái hiện tại

Bản mẫu đã **chạy được trọn vẹn cả hai vai**. 41 màn hình, 5 kịch huống, không có link chết.

| | Hạng mục | Trạng thái |
|---|---|---|
| 1 | Khung ứng dụng, hệ thống thiết kế, đăng nhập giả, khung điều hướng | ✅ |
| 2a | Nội dung kịch huống — 5 kịch huống, mỗi lĩnh vực STEAM một cái | ✅ |
| 2b | Luồng học sinh trọn vẹn (4 nhánh + 3 cạnh nối chéo) | ✅ |
| 3 | Luồng giáo viên, dùng chung dữ liệu với học sinh | ✅ |
| 4 | Tích hợp Gemini — hai chế độ trò chuyện + tổng hợp cuối hành trình | ✅ |
| 5 | Hoàn thiện, cấu hình deploy, README | ✅ |

**Hai điểm cần biết trước khi chấm:**

- **Chưa có khoá Gemini** thì ứng dụng chạy ở *chế độ demo ngoại tuyến* — trợ lý trả lời bằng kịch bản dựng sẵn, mọi màn hình vẫn bấm được đầy đủ. Giao diện nói rõ điều này, không giả vờ là AI thật. Đường gọi API thật đã viết xong nhưng **chưa được kiểm chứng** vì phiên xây dựng không có khoá.
- **Màn hình giáo viên được suy ra từ mô hình dữ liệu**, vì sơ đồ luồng giáo viên không được cung cấp. Cần rà lại với sơ đồ gốc.

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
Đi theo đúng thứ tự dưới đây sẽ thấy trọn câu chuyện.

### 1 · Nhập vai — khoảng 2 phút *(phần quan trọng nhất)*

Bấm **Học sinh (có lớp)** → **Dự án học tập** → **Kỹ thuật** →
*Vì sao tủ vắc-xin cứ mất điện?*

Bấm **Bắt đầu** rồi đi vài nhịp. Điều đáng chú ý:

- Học sinh nhập vai **Hằng, kỹ sư năng lượng** — không phải làm bài tập về kỹ thuật.
- Dữ liệu **cố tình chưa đủ để kết luận**: 7/9 lần mất điện vào buổi tối, nhưng cũng vừa lắp thêm hai máy điều hoà. Câu hỏi không có đáp án đúng.
- Trợ lý **hỏi lại chứ không giảng**, và hỏi theo cách một kỹ sư năng lượng suy nghĩ.
- Ở cấp độ Sáng tạo, sản phẩm cần tạo ra là **phương án hệ thống và kế hoạch thử nghiệm** — mỗi nghề tạo ra một thứ khác nhau, không nghề nào cũng "làm một cái app".

> Muốn xem nhanh phần cuối: bấm tiếp tới hết cấp độ 4 sẽ thấy mục **Nhìn lại cùng bạn** — không điểm, không đáp án mẫu, chỉ phản chiếu lại chính lời học sinh đã viết.

### 2 · Ý tưởng tự do — khoảng 1 phút

**Hồ sơ năng lực** → **Ý tưởng tự do**. Gõ hai câu bất kỳ về một chuyện bạn để ý ở trường.

Sau lượt thứ hai, trợ lý hiện nút **&ldquo;Thêm ý tưởng này vào Hồ sơ?&rdquo;**.
Đây là điểm mấu chốt: **AI đề nghị, học sinh quyết định.** Bấm đồng ý thì mục vào hồ sơ nhưng vẫn **riêng tư** — muốn công khai phải bấm chia sẻ lần nữa. Không có gì tự xuất hiện.

### 3 · Quyền riêng tư — khoảng 1 phút

Đăng xuất → **Học sinh (độc lập)**.

Cùng một sản phẩm, nhưng em này không thuộc lớp nào và **không giáo viên nào xem được** — đây là mặc định, không phải tuỳ chọn phải đi tìm.

### 4 · Phía giáo viên — khoảng 1 phút

Đăng xuất → **Giáo viên** → mở lớp **11A2** → chọn **Nguyễn Khánh Linh**.

- Giáo viên đọc **nhật ký tư duy**, không phải bài nộp để chấm.
- **Không có bảng điểm, không có xếp hạng** ở bất cứ đâu.
- Nhận xét là **lời nhắn riêng tư**, chỉ em đó đọc được — quay lại tài khoản học sinh sẽ thấy nó trên trang cá nhân.

> Thử tìm điểm số ở phía học sinh cũng được — không có. Đó là chủ ý thiết kế, không phải chưa làm.

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

Chạy trên **Render.com** (gói web service miễn phí). File `render.yaml` đã có sẵn — trỏ Render vào repo này và chọn *Blueprint* là xong.

```
Build:  pip install -r requirements.txt
Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Sau khi tạo service, vào phần **Environment** của Render và điền `GEMINI_API_KEY` (`SECRET_KEY` được Render tự sinh). Không điền khoá thì ứng dụng vẫn chạy đủ ở chế độ demo ngoại tuyến.

Vài điểm đáng lưu ý:

- **Không cần Node khi deploy.** CSS đã build sẵn và commit vào `static/css/app.css`.
- **SQLite bị đặt lại mỗi lần deploy** — không sao, dữ liệu tự gieo lại, và mỗi lượt chấm bắt đầu từ trạng thái sạch.
- **Gói miễn phí có cold start.** Nếu máy chủ ngủ, lượt truy cập đầu mất khoảng 30–60 giây. Nên mở trước trang chủ vài phút trước giờ chấm. Nếu thấy chậm quá thì Railway.app là phương án thay thế với cùng hai lệnh trên.

---

*Toàn bộ dữ liệu trong ứng dụng là dữ liệu giả định cho bản mẫu.*
