# GALS

**Thử làm nghề trước khi phải chọn nghề.**

---

## GALS là gì?

GALS là một trang web cho học sinh cấp 3.

Thay vì đọc lý thuyết về nghề nghiệp, học sinh được **đóng vai một người đang đi làm thật** và tự xử lý một tình huống có thật của nghề đó.

Ví dụ: em vào vai một kỹ sư năng lượng, được gọi tới một trạm y tế ngoài đảo vì tủ đựng vắc-xin cứ bị mất điện. Ai cũng bảo là do ắc quy hỏng. Nhưng số liệu lại chưa đủ để khẳng định điều đó.

Không có đáp án sẵn. Có một trợ lý AI đi cùng, nhưng **nó chỉ hỏi lại chứ không giải hộ**.

### Ba điều GALS muốn giải quyết

1. Học sinh cấp 3 ít được thực hành **tư duy thiết kế** — tức là cách nghĩ để giải quyết một vấn đề chưa rõ ràng.
2. Học sinh ít có cơ hội **thử nghề trước khi chọn ngành**.
3. Nhiều em vẫn nghĩ một số ngành STEAM "không dành cho con gái".

### Ba điều GALS cố tình KHÔNG có

- **Không chấm điểm.** Không có bài kiểm tra, không có thang điểm.
- **Không xếp hạng.** Không so sánh em này với em kia.
- **Không có "đáp án mẫu".** Vì ngoài đời cũng không có.

> Đây là **công cụ**, không phải khoá học. Em muốn nhảy sang phần nào, quay lại từ đầu, hay bỏ dở giữa chừng đều được.

---

## Thử demo

### Cách nhanh nhất: 3 nút bấm

Ở màn hình đăng nhập có mục **Demo nhanh** với 3 nút. Bấm một cái là vào thẳng, **không cần đăng ký, không cần gõ gì**:

| Nút | Bạn sẽ thấy |
|---|---|
| **Giáo viên** | Lớp học có sẵn học sinh và bài làm |
| **Học sinh (có lớp)** | Một em đang học lớp 11A2 của cô Mai |
| **Học sinh (độc lập)** | Một em tự học, không thuộc lớp nào |

Bạn cũng có thể đăng nhập bằng **email và mật khẩu bất kỳ** — gõ gì cũng vào được, vì đây là bản demo.

### Chạy trên máy của bạn

Cần cài sẵn **Python** và **Node.js**. Mở cửa sổ dòng lệnh (Terminal) rồi gõ lần lượt:

```bash
# 1. Tải mã nguồn về
git clone https://github.com/soya-00/steam-mvp.git
cd steam-mvp

# 2. Cài các thư viện cần thiết
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install
npm run build:css

# 3. Chạy
.venv/bin/uvicorn app.main:app --reload
```

Xong rồi mở trình duyệt vào **http://127.0.0.1:8000**

> **Không có khoá AI cũng chạy được.** Lúc đó trợ lý trả lời bằng câu có sẵn, và trang web nói rõ điều này. Mọi nút bấm vẫn hoạt động bình thường. Muốn bật AI thật thì xem mục [Bật trợ lý AI](#bật-trợ-lý-ai) bên dưới.

---

## Học sinh dùng như thế nào?

Sau khi đăng nhập, em vào **Trang cá nhân**. Từ đây toả ra 4 hướng, **đi hướng nào trước cũng được**:

```
                      TRANG CÁ NHÂN
                            │
        ┌──────────┬────────┴────────┬──────────┐
        │          │                 │          │
   Dự án học tập  Hồ sơ         Huy hiệu   Tài nguyên
                năng lực                     miễn phí
```

### 1 · Dự án học tập — phần chính

Đây là nơi em đóng vai và xử lý tình huống. Các bước:

| Bước | Em làm gì |
|---|---|
| **Chọn lĩnh vực** | 5 lĩnh vực STEAM: Khoa học, Công nghệ, Kỹ thuật, Nghệ thuật, Toán |
| **Chọn tình huống** | Mỗi lĩnh vực có một tình huống nghề nghiệp |
| **Nhập vai** | Em trở thành nhân vật đó — ví dụ "Hằng, kỹ sư năng lượng" |
| **Đi 4 cấp độ** | Đọc bối cảnh → trả lời câu hỏi → gặp tình tiết mới → trả lời tiếp |
| **Nhìn lại** | AI tóm tắt lại cách em đã nghĩ. **Không chấm điểm** |
| **Nộp dự án** | Viết mô tả, thêm ảnh hoặc video nếu muốn |
| **Nhận huy hiệu** | Tự động, ghi nhận là em đã đi qua chặng này |

**Bốn cấp độ** là bốn kiểu suy nghĩ khác nhau:

1. **Hiểu vấn đề** — Đọc số liệu. Đâu là điều chắc chắn, đâu là mình đang đoán?
2. **Đồng cảm** — Ai bị ảnh hưởng? Họ muốn những thứ khác nhau ra sao?
3. **Sáng tạo** — Đề xuất một phương án, trong điều kiện thiếu thời gian và thiếu tiền.
4. **Phản chiếu** — Kết quả ra vậy, nhưng liệu có cách giải thích nào khác không?

> **Mỗi nghề làm ra một thứ khác nhau** ở cấp độ Sáng tạo. Kỹ sư năng lượng làm *phương án hệ thống*. Chuyên viên dịch tễ làm *kế hoạch điều tra*. Chuyên viên an ninh mạng làm *quy trình xử lý sự cố*. Không phải nghề nào cũng "làm một cái app".

### 2 · Hồ sơ năng lực

Mọi thứ em làm **tự động gom lại** thành hồ sơ. Em không phải tự sắp xếp.

Em có toàn quyền sửa mô tả, đổi phân loại, và chọn mục nào cho người khác xem.

Ở đây còn có **Ý tưởng tự do** — trò chuyện với AI mà không cần theo khuôn khổ nào. Kể về điều em để ý thấy, thắc mắc, hay thấy khó chịu. Khi AI nhận ra em vừa nói ra một ý hay, nó sẽ hỏi:

> *"Thêm ý tưởng này vào Hồ sơ?"*

**Em bấm đồng ý thì mới lưu.** Và kể cả khi đã lưu, mục đó vẫn để **riêng tư** — muốn cho người khác xem thì phải bấm chia sẻ một lần nữa. AI không bao giờ tự đăng thứ gì.

### 3 · Huy hiệu

Ghi lại những nơi em đã đi qua — **không phải em làm tốt đến đâu**.

Có cả huy hiệu chưa mở khoá, kèm gợi ý lĩnh vực tiếp theo nên thử. Gợi ý này không mang nghĩa "em còn thiếu", mà là "chỗ kia có kiểu suy nghĩ khác, biết đâu em thích".

### 4 · Tài nguyên miễn phí

Khoá học và video chọn lọc từ Khan Academy, Coursera, YouTube — lọc theo lĩnh vực. Tất cả đều mở, không cần tài khoản GALS để học.

Kèm thông báo về hội thảo và talkshow liên quan.

---

## Giáo viên dùng như thế nào?

| Bước | Thầy cô làm gì |
|---|---|
| **Tạo lớp** | Hệ thống sinh ra một mã lớp, ví dụ `GALS-11A2` |
| **Đọc mã cho học sinh** | Các em nhập mã này khi đăng ký |
| **Giao nhiệm vụ** | Chọn một tình huống cụ thể, hoặc mở cả lĩnh vực cho các em tự chọn. Làm trên mạng hoặc thảo luận tại lớp |
| **Đọc nhật ký** | Xem cách từng em suy nghĩ — không phải bài nộp để chấm |
| **Nhắn riêng** | Lời nhắn chỉ em đó đọc được |
| **Gửi thông báo** | Báo cả lớp về buổi hội thảo, talkshow |

**Không có bảng điểm ở bất cứ đâu.** Thầy cô đọc được quá trình suy nghĩ, không phải kết quả đúng sai.

### Về quyền riêng tư

Học sinh **không nhập mã lớp** thì không giáo viên nào xem được bài của em — kể cả nhật ký. Đây là **mặc định**, không phải một tuỳ chọn phải đi tìm để bật.

Em vẫn dùng được đầy đủ mọi tính năng.

---

## Kịch bản demo 5 phút cho ban giám khảo

### 1 · Nhập vai — 2 phút *(phần quan trọng nhất)*

**Học sinh (có lớp)** → **Dự án học tập** → **Kỹ thuật** → *Vì sao tủ vắc-xin cứ mất điện?* → **Bắt đầu**

Bấm đi vài nhịp. Điều đáng chú ý:

- Học sinh **nhập vai kỹ sư**, không phải làm bài tập về kỹ thuật.
- Số liệu **cố tình chưa đủ để kết luận** — 7/9 lần mất điện vào buổi tối, nhưng cũng vừa lắp thêm hai máy điều hoà.
- Trợ lý **hỏi lại chứ không giảng**.

### 2 · AI đề nghị, học sinh quyết định — 1 phút

**Hồ sơ năng lực** → **Ý tưởng tự do** → gõ hai câu bất kỳ về chuyện gì đó ở trường.

Sau lượt thứ hai, trợ lý hiện nút **"Thêm ý tưởng này vào Hồ sơ?"**. Bấm đồng ý thì mục vào hồ sơ nhưng **vẫn riêng tư**.

### 3 · Quyền riêng tư — 1 phút

Đăng xuất → **Học sinh (độc lập)**. Cùng một sản phẩm, nhưng em này không thuộc lớp nào và không ai xem được bài của em.

### 4 · Phía giáo viên — 1 phút

Đăng xuất → **Giáo viên** → lớp **11A2** → **Nguyễn Khánh Linh**

Thầy cô đọc nhật ký tư duy, không có bảng điểm. Nhận xét là lời nhắn riêng — quay lại tài khoản học sinh sẽ thấy nó trên trang cá nhân.

> Thử tìm điểm số ở phía học sinh cũng được — **không có**. Đó là chủ ý thiết kế, không phải chưa làm xong.

---

## Bật trợ lý AI

Không bắt buộc. Không có khoá thì trang web vẫn chạy đủ, chỉ là trợ lý trả lời bằng câu dựng sẵn.

Muốn dùng AI thật:

1. Lấy khoá miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey)
2. Tạo một file tên `.env` ngay trong thư mục dự án
3. Viết vào đó một dòng:

```
GEMINI_API_KEY=khoa-cua-ban-o-day
```

4. Chạy lại ứng dụng

> ⚠️ **Đừng bao giờ chia sẻ khoá này cho ai, và đừng đưa nó lên GitHub.** File `.env` đã được cấu hình để git bỏ qua. Khoá miễn phí cũng có giới hạn số lượt mỗi ngày.

---

## Dành cho người phát triển

<details>
<summary><strong>Công nghệ sử dụng</strong></summary>

<br>

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

**Biến môi trường** (tất cả đều không bắt buộc):

| Biến | Ý nghĩa |
|---|---|
| `GEMINI_API_KEY` | Khoá Gemini. Bỏ trống → chế độ demo ngoại tuyến |
| `GEMINI_MODEL` | Ghi đè tên model. Bỏ trống → tự dò model flash mới nhất |
| `SECRET_KEY` | Khoá ký cookie. Nên đặt khi deploy |

Cơ sở dữ liệu bị xoá và gieo lại mỗi lần khởi động — cứ xoá `gals.db` thoải mái.

⚠️ Tailwind quét class **tĩnh**. Đừng ghép chuỗi kiểu `border-l-{{ color }}` trong Jinja — class sẽ không được sinh ra. Luôn để tên class đủ chữ trong dữ liệu.

</details>

<details>
<summary><strong>Thêm kịch huống mới</strong></summary>

<br>

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

**Vì sao có `domain_skills` và `creation_output`:** Design Thinking chỉ là khung dẫn dắt. Nội dung bên trong phải thể hiện đúng cách mỗi nghề thu thập bằng chứng và ra quyết định. Nếu nghề nào cũng chỉ "phỏng vấn người dùng rồi thiết kế ứng dụng", người học sẽ hiểu sai bản chất nghề nghiệp.

| Nghề | Sản phẩm của cấp độ Sáng tạo |
|---|---|
| Chuyên viên tài chính | Mô hình phân bổ ngân sách |
| Kỹ sư năng lượng | Phương án hệ thống và kế hoạch thử nghiệm |
| Chuyên viên hoá học | Quy trình lấy và kiểm tra mẫu |
| Chuyên viên dịch tễ | Kế hoạch điều tra và phòng ngừa |
| Chuyên viên an ninh mạng | Quy trình phản ứng sự cố |
| Nhà quy hoạch | Kịch bản sử dụng không gian hoặc giao thông |
| Nhà truyền thông | Thông điệp cho từng nhóm đối tượng |

</details>

<details>
<summary><strong>Deploy lên Render</strong></summary>

<br>

File `render.yaml` đã có sẵn — trỏ Render vào repo này và chọn *Blueprint*.

```
Build:  pip install -r requirements.txt
Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Sau khi tạo service, vào **Environment** của Render và điền `GEMINI_API_KEY` (`SECRET_KEY` được Render tự sinh).

- **Không cần Node khi deploy.** CSS đã build sẵn và commit vào repo.
- **SQLite bị đặt lại mỗi lần deploy** — không sao, dữ liệu tự gieo lại.
- **Gói miễn phí có cold start.** Nếu máy chủ ngủ, lượt truy cập đầu mất 30–60 giây. Nên mở trước trang chủ vài phút trước giờ chấm.

</details>

<details>
<summary><strong>Hệ thống thiết kế</strong></summary>

<br>

Bảng màu giữ nguyên từ các sơ đồ đã trình bày với ban giám khảo, khai báo một lần trong `src/input.css`:

| Vai trò | Mã màu |
|---|---|
| Thân/hệ thống | `#4A4E9C` |
| Dự án học tập | `#1F8A70` |
| Hồ sơ năng lực | `#C98A2E` |
| Huy hiệu | `#8B4B6B` |
| Tài nguyên | `#4F6F94` |
| Nền giấy ấm | `#F6F5F1` |

Chữ: **Be Vietnam Pro** cho tiêu đề (xưởng chữ Việt, dấu được vẽ từ đầu) + **Lexend** cho nội dung. Cả hai tự host, không phụ thuộc CDN.

</details>

<details>
<summary><strong>Còn cần rà lại</strong></summary>

<br>

- **Màn hình giáo viên được suy ra từ mô hình dữ liệu**, vì sơ đồ luồng giáo viên không được cung cấp. Cần đối chiếu với sơ đồ gốc.
- Ba nhóm nghề trong bảng phân loại **chưa có kịch huống**: Hoá học/kiểm định, Quy hoạch/môi trường, Truyền thông/ngôn ngữ.

</details>

---

*Toàn bộ dữ liệu trong ứng dụng là dữ liệu giả định cho bản mẫu.*
