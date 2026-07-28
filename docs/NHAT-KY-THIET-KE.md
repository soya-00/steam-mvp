# Nhật ký thiết kế GALS

Ghi lại **vì sao** sản phẩm được làm như hiện tại: những quyết định đã chốt, những phương án đã bị loại, các lỗi phát hiện được và hướng đi tiếp.

Mục đích: người đọc sau này (kể cả chính tác giả sau vài tháng) hiểu được lý do đằng sau từng lựa chọn, thay vì phải đoán.

---

## Nguyên tắc xuyên suốt

Bốn điều dưới đây quyết định hầu hết các lựa chọn kỹ thuật và nội dung. Khi phân vân, luôn quay về đây.

| Nguyên tắc | Hệ quả trong sản phẩm |
|---|---|
| **Không chấm điểm** | Không có thang điểm, không xếp hạng, không "đáp án mẫu" ở bất kỳ màn hình nào. AI cũng bị cấm chấm trong lời nhắc hệ thống. |
| **Công cụ, không phải khoá học** | Vào nhánh nào trước cũng được, bỏ dở giữa chừng được, làm lại được. Không có "bài 1 → bài 2". |
| **Riêng tư là mặc định** | Học sinh không nhập mã lớp thì không giáo viên nào xem được gì. Mọi mục trong hồ sơ mặc định riêng tư. |
| **Mỗi nghề nghĩ một kiểu** | Design Thinking chỉ là khung dẫn dắt. Nội dung bên trong phải đúng cách nghề đó thu thập bằng chứng và ra quyết định. |

---

## Các giai đoạn

### Giai đoạn 1 — Nền móng

Viết lại bản mẫu HTML một file (dùng `localStorage`) thành ứng dụng render phía máy chủ.

**Đã chốt**

- **FastAPI + Jinja2 + HTMX**, không dùng React/Vue. Ứng dụng chủ yếu là form và trang nội dung; thêm một framework client-side chỉ làm chậm máy yếu và làm khó trình đọc màn hình.
- **Tailwind build thật**, không dùng CDN. File CSS build ra được commit vào repo để môi trường deploy chỉ cần Python.
- **Chữ tự host**: Be Vietnam Pro (tiêu đề) + Lexend (nội dung). Be Vietnam Pro do xưởng chữ Việt làm, dấu được vẽ từ đầu chứ không gắn thêm vào chữ Latin. Không phụ thuộc CDN nước ngoài.
- **Bảng màu giữ nguyên** từ các sơ đồ đã trình bày với ban giám khảo — liên tục về thị giác là có chủ đích.

**Đã loại**

- Dùng lại truyện của bản mẫu cũ. Nội dung mới đi theo hướng khác hẳn.
- CDN cho font và HTMX: mạng chậm hoặc bị chặn lúc chấm thi là hỏng cả buổi.

---

### Giai đoạn 2 — Nội dung và luồng học sinh

**Quyết định quan trọng nhất của cả dự án: cấu trúc kịch huống.**

Kịch huống **không phải** mô tả phẳng. Mỗi cái là một kịch bản đi qua bốn cấp độ, mỗi cấp độ là một mảng `beats` **có thứ tự**, đan xen khối bối cảnh với câu hỏi.

Nhãn và số lượng beat **khác nhau giữa các kịch huống** — kịch huống của An dùng "Câu hỏi nhỏ 1–3", của Hoa dùng "Câu hỏi 1–4" cùng những nhãn riêng như "Mục tiêu của các bên", "Trường hợp ngoại lệ". Vì vậy **nhãn nằm trong dữ liệu, không nằm trong code**. Nếu hard-code nhãn thì mỗi kịch huống mới lại phải sửa code.

**Hai trường giữ cho mỗi nghề đúng là nghề đó**

- `domain_skills` — phương pháp chuyên môn cấp độ đó phải dùng tới.
- `creation_output` — **cấp độ Sáng tạo thật sự tạo ra cái gì**, và thường không phải một ứng dụng.

Lý do: nếu nghề nào cũng chỉ "phỏng vấn người dùng rồi thiết kế app", người học sẽ hiểu sai bản chất nghề nghiệp. Giao diện cấp độ 3 và lời nhắc AI đều đọc `creation_output`.

**Năm kịch huống, mỗi lĩnh vực STEAM một cái**

| Lĩnh vực | Nhóm nghề | Nhân vật | Cấp độ 3 tạo ra |
|---|---|---|---|
| Khoa học | Y sinh, dịch tễ | An | Kế hoạch điều tra và phòng ngừa |
| Nghệ thuật | Thiết kế | Hoa | Bản mẫu kiểm tra giả định |
| Kỹ thuật | Năng lượng | Hằng | Phương án hệ thống + kế hoạch thử nghiệm |
| Công nghệ | An ninh mạng | Quyên | Quy trình phản ứng sự cố |
| Toán | Phân tích dữ liệu | Ngọc | Mô hình phân bổ ngân sách |

Ba kịch huống tự viết **cố ý đặt nhân vật nữ vào những nghề bị mặc định là của nam** — đó là cách trực tiếp nhất để chạm vào vấn đề định kiến giới trong STEAM. Cấp độ 4 của mọi kịch huống đều kết thúc bằng bằng chứng **mơ hồ có chủ đích**, kèm một yếu tố gây nhiễu mà học sinh phải tự nhận ra (ba tuần nắng liên tục, kỳ thi vừa kết thúc, không có nhóm đối chứng).

**Ba cạnh nối chéo trong sơ đồ là đường đi thật, không phải trang trí**: vòng lặp về Trang cá nhân từ bất cứ đâu; lối rẽ từ Không gian tư duy sang Ý tưởng tự do; và cả Nộp dự án lẫn Ý tưởng tự do đều dẫn tới Link chia sẻ.

---

### Giai đoạn 3 — Luồng giáo viên

Đọc cùng những bảng dữ liệu mà học sinh ghi vào, nên hoạt động của học sinh hiện ra ngay bên phía giáo viên.

**Đã chốt**

- Không có bảng điểm. Danh sách lớp hiện số bài nhật ký, số dự án đã nộp, số huy hiệu — **không có thứ hạng, không sắp xếp theo thành tích**.
- Nhận xét là **lời nhắn riêng tư**, đóng khung trong giao diện như một tin nhắn chứ không phải một đánh giá.
- Phân quyền kiểm tra ở **cả đọc lẫn ghi**: hàm gửi nhận xét kiểm tra lại quyền thay vì tin vào form gửi lên.

**Cần lưu ý:** sơ đồ luồng giáo viên chưa bao giờ được cung cấp, nên các màn hình này **suy ra từ mô hình dữ liệu**. Cần đối chiếu lại với sơ đồ gốc.

---

### Giai đoạn 4 — Tích hợp Gemini

**Đã chốt**

- **Đổi `google-generativeai` sang `google-genai`.** Gói cũ đóng băng ở 0.8.6, Google ngừng hỗ trợ từ 30/11/2025. Cùng nhà cung cấp, cùng model, chỉ khác thư viện.
- **Không hard-code tên model.** Dò bằng `models.list()` lúc khởi động theo thứ tự ưu tiên, cho phép ghi đè bằng biến môi trường.
- **AI đề nghị, học sinh quyết định.** Ở chế độ tự do, model có thể kết thúc lượt bằng một dòng đánh dấu; máy chủ tách dòng đó ra và hiện nút *"Thêm ý tưởng này vào Hồ sơ?"*. Bấm đồng ý thì mục vào hồ sơ nhưng **vẫn riêng tư** — muốn công khai phải bấm lần nữa. **AI không bao giờ tự đăng.**
- **Chế độ demo ngoại tuyến** khi chưa có khoá API: trả lời bằng kịch bản dựng sẵn, giao diện nói rõ. Mọi màn hình vẫn bấm được.

---

### Giai đoạn 5 — Hoàn thiện, tài liệu, deploy

`render.yaml`, README viết cho người không rành kỹ thuật, kịch bản demo dưới 5 phút cho ban giám khảo.

---

### Giai đoạn 6 — Khả năng tiếp cận và dạy không cần thiết bị

**Khả năng tiếp cận** (nhắm tới VoiceOver trên iOS và TalkBack trên Android): liên kết bỏ qua điều hướng, vùng mốc, thứ tự tiêu đề, nhãn cho mọi ô nhập, `aria-live` cho phần chat cập nhật bằng HTMX, `aria-current` cho mục đang mở, và trạng thái từng cấp độ được nói thành lời chứ không chỉ hiện bằng màu.

**Tài liệu in cho buổi học tại lớp**: không phải trường nào cũng có phòng máy. Bản in kèm trang hướng dẫn riêng cho thầy cô, mỗi cấp độ sang một trang mới, có dòng kẻ để học sinh viết tay. **Máy in là tuỳ chọn** — đọc to phần bối cảnh và chép câu hỏi lên bảng vẫn dạy được.

---

### Giai đoạn 7 — Hình minh hoạ và giao diện hợp lứa tuổi

Mỗi lĩnh vực STEAM có một hình vector, vẽ bằng đúng màu thương hiệu của lĩnh vực.

**Vì sao vẽ hình học, không vẽ người:** vẽ người là phải chọn giới tính, độ tuổi, ngoại hình — đúng thứ định kiến sản phẩm đang muốn tránh. Hình hình học né hẳn vấn đề đó, lại nhẹ và rõ ở mọi kích thước.

**Vì sao không dùng ảnh stock:** không kiểm chứng được đường dẫn ảnh từ môi trường phát triển. Ghi đại một đường dẫn từ trí nhớ là cách đã hai lần dẫn tới sai (số phiên bản thư viện, tên model). Ảnh hỏng lúc chấm thi còn tệ hơn là không có ảnh. Vẫn để sẵn hai trường `image_url` / `image_alt` cho ai muốn thay bằng ảnh thật, và hình vector đóng vai trò dự phòng.

---

### Giai đoạn 8 — Chặn đầu vào xấu

Học sinh cấp 3 sẽ thử gõ bậy, gõ linh tinh, hoặc thử "bẻ" AI. Xử lý ở **phía máy chủ, trước khi gọi API**: nhanh hơn, đoán trước được, không tốn hạn mức, và **không thể "lỡ" tiếp chuyện**.

Năm nhóm bị chặn: nói tục · gõ linh tinh · cố bẻ lời nhắc hệ thống · dấu hiệu khủng hoảng tâm lý · đầu vào quá dài.

Ở chế độ nhập vai, đầu vào bị chặn **không làm tiến sang beat tiếp theo và không ghi vào nhật ký** — vừa tránh việc bấm bừa cho xong, vừa tránh để lời nói tục nằm trong nhật ký mà giáo viên sẽ đọc.

**Lỗi nghiêm trọng phát hiện khi kiểm thử:** bản đầu tiên bỏ dấu tiếng Việt trước khi so khớp. Cách đó làm **"các"** (từ cực kỳ thông dụng) trùng với một từ tục, **"buổi"** trùng với một từ tục, và **"từ từ"** trùng với cách viết không dấu của "tự tử". Một em viết *"các bạn"* sẽ bị gắn cờ nói tục; viết *"từ từ đã"* sẽ nhận được thông điệp khủng hoảng tâm lý. Với sản phẩm lấy an toàn tâm lý làm gốc, đây là lỗi phá hỏng niềm tin. **Đã sửa: từ tiếng Việt so khớp nguyên dấu**, chỉ những từ viết tắt vốn không dấu mới so khớp kiểu ASCII.

---

## Những lỗi đáng nhớ

| Lỗi | Vì sao khó thấy | Cách tránh sau này |
|---|---|---|
| Tailwind không sinh class ghép động | Không báo lỗi. Ba trong bốn nhánh mất thanh màu mà build vẫn "thành công" | Luôn để **tên class đủ chữ** trong dữ liệu, không ghép chuỗi trong Jinja |
| Câu trả lời AI bị cắt giữa chừng | Chế độ ngoại tuyến che mất hoàn toàn | Model dòng flash bật "suy nghĩ" mặc định, phần suy nghĩ **ăn chung hạn mức output** (381/400 token). Để hạn mức rộng |
| Số phiên bản thư viện nhớ sai | Cài vẫn chạy, chỉ là cũ | Luôn `pip index versions` trước khi ghim |
| Bỏ dấu tiếng Việt khi lọc từ tục | Chỉ lộ ra khi thử với câu tiếng Việt thật | So khớp nguyên dấu với từ tiếng Việt |
| Regex xoá chú thích CSS ăn mất `/**/` | `@source "app/**/*.html"` thành đường dẫn sai, build vẫn chạy | Kiểm tra class có thật sự nằm trong CSS build ra |

---

## Hướng đi tiếp

Xếp theo mức độ quan trọng.

**1 · Dữ liệu không sống qua lần khởi động lại**
Toàn bộ bị xoá và gieo lại mỗi lần chạy. Ổn cho bản demo, nhưng hỏng hẳn vào ngày một học sinh thật mất nhật ký của mình. Đây là khoảng cách lớn nhất giữa "bản mẫu" và "dùng được". Cần đổi sang Postgres và bỏ lệnh gieo lại.

**2 · Phần AI mới được thử rất ít với model thật**
Hạn mức miễn phí hết sau vài lượt gọi. Bộ chặn phía máy chủ đã kiểm thử đầy đủ, nhưng **hành vi của chính model thì chưa** — nhất là các rào an toàn về trẻ vị thành niên và định kiến giới.

**3 · Năm kịch huống là khoảng hai giờ nội dung**
Ba nhóm nghề trong bảng phân loại vẫn chưa có kịch huống: Hoá học/kiểm định, Quy hoạch/môi trường, Truyền thông/ngôn ngữ. Ngoài ra, viết kịch huống hiện là gõ tay JSON lồng nhiều lớp — cách này không mở rộng được cho người khác cùng viết.

**4 · Phần trình đọc màn hình chưa thử trên máy thật**
Ngữ nghĩa HTML đã viết đúng và đã kiểm tra ở mức mã nguồn, nhưng chưa từng chạy VoiceOver hay TalkBack với giọng đọc tiếng Việt.

**5 · Luồng giáo viên vẫn là suy đoán**
Dựng từ mô hình dữ liệu vì thiếu sơ đồ. Hợp lý, nhưng chưa được xác nhận.

**6 · Xác thực là giả**
Mọi email/mật khẩu đều vào được tài khoản demo. Đúng với mục tiêu bản mẫu, nhưng phải làm thật trước khi có học sinh thật.
