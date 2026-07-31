# Việc cần làm tiếp

---

## Khả năng tiếp cận (accessibility)

Mục tiêu: học sinh khiếm thị dùng được GALS bằng trình đọc màn hình — VoiceOver trên iOS, TalkBack trên Android, NVDA trên Windows.

### Đã làm

- **Liên kết bỏ qua điều hướng** ở đầu mỗi trang, ẩn cho tới khi được focus.
- **Vùng mốc (landmark)** đúng chuẩn: `header`, `nav`, `main`, `footer`. `main` có `id` và `tabindex="-1"` để nhận focus từ liên kết bỏ qua.
- **`aria-current`** trên mục điều hướng đang mở và cấp độ đang làm.
- **Không dùng riêng màu để truyền đạt trạng thái.** Thanh tiến độ bốn cấp độ có chữ đi kèm cho từng mục: *đã xong · đang làm · chưa tới*.
- **Biểu tượng trang trí** (emoji, chấm tròn, mũi tên) đều có `aria-hidden="true"` để không bị đọc thành tên ký tự.
- **Nút đăng xuất** có nhãn đầy đủ cho trình đọc màn hình, thay vì chỉ một chữ cái viết tắt.
- **Vùng động (live region)** cho khung trò chuyện: câu trả lời mới của trợ lý được đọc lên mà người dùng không phải đi tìm.
- **`role="status"`** cho chỉ báo *đang nghĩ…* và thông báo *Đã lưu*.
- **Mọi ô nhập liệu đều có `label`**, ẩn bằng `sr-only` khi thiết kế không cần nhãn hiển thị.
- **Vòng focus rõ ràng** qua `:focus-visible`, và tôn trọng `prefers-reduced-motion`.
- **Nhóm chọn avatar** dùng `fieldset` + `legend`.

### Cần kiểm chứng bằng thiết bị thật

Phần trên là làm đúng theo chuẩn, **nhưng chưa được thử bằng trình đọc màn hình thật**. Đây là việc quan trọng nhất còn lại.

- [ ] Đi hết một kịch huống bằng VoiceOver trên iPhone, chỉ dùng cử chỉ vuốt.
- [ ] Kiểm tra thứ tự đọc ở Không gian tư duy: phần đã đi qua nằm trước ô nhập câu trả lời, xem như vậy có hợp lý khi nghe không.
- [ ] Sau khi HTMX thay nội dung, kiểm tra focus rơi vào đâu — hiện tại chưa chủ động dời focus sau mỗi lượt trò chuyện.
- [ ] Kiểm tra trình đọc màn hình có đọc dấu tiếng Việt đúng không, nhất là với chữ Be Vietnam Pro.
- [ ] Đo độ tương phản màu theo WCAG AA cho toàn bộ bảng màu, đặc biệt chữ xám `--color-ink-faint` trên nền giấy.

### Chưa làm

- [ ] **Dời focus sau khi HTMX cập nhật.** Sau khi gửi tin nhắn, focus nên về ô nhập hoặc tới câu trả lời mới.
- [ ] **Thu nhỏ vùng thay thế của HTMX.** Hiện tại cả khung hội thoại bị thay mới mỗi lượt; nên chỉ thêm phần mới để trình đọc màn hình không đọc lại từ đầu.
- [ ] **Chế độ tương phản cao** và tôn trọng `prefers-contrast`.
- [ ] **Cho phép phóng chữ tới 200%** mà không vỡ bố cục — cần kiểm tra lại.
- [ ] **Nhãn `lang`** cho các đoạn tiếng Anh xen kẽ (tên khoá học, "Follow-up") để trình đọc không đọc bằng giọng tiếng Việt.

---

## Thiết kế lại giao diện

Đã hoãn có chủ đích. Phần khả năng tiếp cận được ưu tiên làm trước vì đó mới là thứ thật sự giúp người khiếm thị — trình đọc màn hình phụ thuộc vào cấu trúc HTML, nhãn và thứ tự đọc, gần như không phụ thuộc vào hình thức.

Khi làm lại giao diện, cần giữ:

- Bảng màu hiện tại (đã trình bày với ban giám khảo, cần liên tục về thị giác).
- Các mốc `aria`, nhãn `sr-only` và thứ tự tiêu đề đã dựng.
- Nguyên tắc: trạng thái không bao giờ chỉ được thể hiện bằng màu.

---

## Nội dung

Ba nhóm nghề trong bảng phân loại **chưa có kịch huống**:

- [ ] Hoá học, kiểm định — *sản phẩm cấp 3: quy trình lấy và kiểm tra mẫu*
- [ ] Quy hoạch, môi trường — *sản phẩm cấp 3: kịch bản sử dụng không gian hoặc giao thông*
- [ ] Truyền thông, ngôn ngữ — *sản phẩm cấp 3: thông điệp cho từng nhóm đối tượng*

Cách viết xem [Hướng dẫn kỹ thuật](KY-THUAT.md#thêm-kịch-huống-mới).

---

## Cần rà lại

- [ ] **Màn hình giáo viên được suy ra từ mô hình dữ liệu**, vì sơ đồ luồng giáo viên không được cung cấp. Cần đối chiếu với sơ đồ gốc.
- [ ] **Đường gọi Gemini thật** mới chỉ thử được vài lượt trước khi hết hạn mức của khoá miễn phí. Nên chạy thử lại đầy đủ cả hai chế độ trước khi chấm.

---

## Ý tưởng mở rộng — brainstorm có xếp hạng ưu tiên

Đã có bộ kiểm thử tự động (`tests/`, chạy bằng `pytest`) khoá chặt các bất biến: mọi trang mở được, kịch huống đi trọn, ranh giới riêng tư, bộ lọc đầu vào (kể cả các ca va chạm dấu tiếng Việt), không có giao diện chấm điểm, class Tailwind không biến mất khỏi CSS build, và các mốc trợ năng. CI chạy trên mỗi lần đẩy code.

### Mở rộng quy mô

1. **Postgres + chỉ gieo khi trống** — dữ liệu phải sống qua deploy. Vẫn là việc số một của cả dự án.
2. **Quy trình soạn kịch huống** — lệnh kiểm tra `scenarios.json` + khuôn Markdown → JSON, để giáo viên và người viết nội dung soạn được kịch huống mà không phải gõ tay JSON lồng nhiều lớp. Nội dung là nút thắt tăng trưởng thật của sản phẩm.
3. **Hạn mức chat theo người dùng, lưu trong DB** — hiện đếm trong bộ nhớ theo cookie: đúng cho demo, nhưng mất khi restart và không gắn với người. (Rò rỉ bộ nhớ của bộ đếm đã được chặn bằng trần 2.000 khoá.)
4. **Nhiều giáo viên một lớp**, chuyển lớp giữa giáo viên.

### Nhất quán thiết kế

5. **Gom chip trạng thái và thẻ-trống thành macro Jinja** — hiện mỗi template tự chép một bản. (Breadcrumb đã gom xong thành `partials/breadcrumb.html`, dùng ở 9 trang.)
6. **Một trang design-token duy nhất** trong docs: màu, chữ, bo góc, chuyển động — để người làm sau không phải đọc `input.css` để đoán hệ thống.

### Dễ dùng

7. **Nhập mã lớp sau khi đăng ký** — học sinh độc lập hiện *không bao giờ* vào được lớp; ô mã lớp chỉ tồn tại lúc đăng ký. Cần form "Nhập mã lớp" ở Trang cá nhân, kèm màn xác nhận nói rõ: vào lớp nghĩa là giáo viên đó đọc được nhật ký. Chạm vào lời hứa riêng tư nên phải làm cẩn thận, không làm vội.
8. **Thẻ "Tiếp tục chỗ đang dở"** nổi bật trên Trang cá nhân, trỏ thẳng vào đúng beat đang đứng. (Ô trả lời đã tự lưu nháp — đóng tab giữa chừng không mất chữ nữa.)
9. **Giáo viên: lọc nhật ký theo kịch huống, xuất nhật ký cả lớp ra bản in** — dùng lại hạ tầng in sẵn có.
10. **Meta tags cho link chia sẻ** — dán link hồ sơ vào Zalo/Messenger phải hiện preview tử tế; đây là kênh chia sẻ thật của học sinh Việt Nam.
11. **PWA shell tối thiểu** cho mạng chập chờn ở trường: cache trang vỏ và CSS, để mất mạng giữa chừng không thành màn hình trắng.

### Tiếp cận (bổ sung thứ tự làm cho checklist ở trên)

12. **Dời focus sau mỗi lượt HTMX** — việc còn lại quan trọng nhất với người dùng trình đọc màn hình.
13. **Thu hẹp `hx-swap` thành chỉ-thêm-mới** để trình đọc không đọc lại cả khung chat sau mỗi lượt.
14. **`lang="en"`** cho các đoạn tiếng Anh xen kẽ (tên khoá học, "Follow-up").
15. **Kịch bản kiểm thử VoiceOver/TalkBack từng bước** trên máy thật, giọng đọc tiếng Việt.

---

## Cơ sở dữ liệu và backend

### Hiện tại đang là gì

- **`reset_and_seed()` chạy trong vòng đời FastAPI và gọi `Base.metadata.drop_all()`** (`app/seed.py`). Mỗi lần khởi động lại là **xoá sạch**. Gói miễn phí của Render còn cho dịch vụ ngủ khi vắng người, nên bài của học sinh thường không sống qua một đêm. Đúng cho bản trình diễn — mỗi người vào đều thấy ứng dụng sạch và đầy đủ nội dung — nhưng không dùng thật được.
- **SQLite nằm trên đĩa tạm.** Mỗi lần deploy cũng xoá.
- **Một tiến trình uvicorn, không có `--workers`.** Và **hiện chưa thêm worker được**: mỗi worker sẽ chạy lại vòng đời rồi xoá bảng ngay dưới chân các worker khác. Chặn đường mở rộng ngang không phải là framework, mà là cách gieo dữ liệu.
- **Lời gọi Gemini là đồng bộ nằm trong endpoint bất đồng bộ**, nên một lượt AI khoá luôn event loop. Với một tiến trình, số lượt AI chạy thật sự song song xấp xỉ bằng một.
- **Hạn mức chat đếm trong bộ nhớ tiến trình theo cookie**: mất khi khởi động lại, không gắn với người, không chia sẻ giữa các worker.
- **`render.yaml` không chạy `npm run build:css`**; `static/css/app.css` được commit sẵn. Chạy được, nhưng bước build CSS là thủ công và có thể lệch khỏi `input.css`.

### Chỗ vỡ trước tiên không phải cơ sở dữ liệu

SQLite gánh một lớp (~40 học sinh) thoải mái, và mọi trang đều render phía máy chủ, không có trạng thái phía trình duyệt. Hai chỗ thắt thật sự là **lời gọi Gemini chặn tiến trình** và **hạn mức của gói Gemini miễn phí**: một lớp cùng làm chế độ nhập vai là khoảng 800 lượt gọi cho mỗi kịch huống.

### Thứ tự bắt buộc khi chuyển sang dùng thật

1. **PostgreSQL + chỉ gieo khi trống.** Một thay đổi mở khoá cùng lúc *lưu được dữ liệu* và *chạy nhiều worker*. `app/db.py` đã rẽ nhánh sẵn theo tiền tố `DATABASE_URL`.
2. **Alembic** khi lược đồ ổn định — `create_all` không sửa được bảng đang có dữ liệu.
3. **Đưa lời gọi Gemini sang threadpool** để một lượt AI chậm không khoá cả tiến trình.
4. **Hạn mức chat thành cột trong DB**, không phải dict trong bộ nhớ.
5. **`npm run build:css` vào build command của Render.**
6. **Đăng nhập thật** trước khi có dữ liệu thật. Cookie có chữ ký, không mật khẩu — ổn cho bản mẫu, không ổn từ giây phút một em viết nhật ký thật.

### Ngoài hạ tầng

- **Đơn vị thuê bao.** Mô hình hiện là `Lớp → giáo viên`, **chưa có `Trường`**. Cần trường học là đơn vị, nhiều giáo viên một trường, và bàn giao khi nhân sự đổi. Rẻ khi chưa có dữ liệu, đắt khi đã có.
- **Trần chi phí theo trường, và xuống cấp êm thay vì báo lỗi.** Chế độ ngoại tuyến (`_offline_guided`, `_offline_freeform`) **đã dạy trọn một buổi với chi phí AI bằng không** — nên coi đó là một mức sản phẩm có chủ đích, không phải phương án chữa cháy không ai nhắc tới.
- **Nút thắt tăng trưởng là soạn nội dung**, không phải máy chủ. Năm kịch huống viết tay, mỗi kịch huống bốn cấp độ — thêm máy chủ không thêm được kịch huống.
- **Vận hành chưa có gì:** sao lưu và diễn tập phục hồi, theo dõi lỗi, giám sát uptime, môi trường staging, quy trình quay lui khi deploy hỏng. Một đợt thử nghiệm có bài thật mà không có sao lưu là kiểu hỏng kết thúc luôn dự án.

### Việc kỹ thuật phát sinh từ rà soát pháp lý

Xem [LEGAL.md](../LEGAL.md) cho bối cảnh đầy đủ.

- [ ] **Kiểm soát `journal_entries.image_url`.** Đây là đường dẫn tự do do học sinh dán vào, được render thẳng vào `<img src>` trên **trang công khai**. Bộ lọc chỉ soi chữ, không soi liên kết hay ảnh. Học sinh có thể công bố ảnh bất kỳ, kể cả một pixel theo dõi thu địa chỉ IP của mọi em vào xem. **Chỗ hở sắc nhất còn lại.** Cần danh sách nguồn cho phép hoặc tự lưu ảnh.
- [x] **Ngưỡng an toàn tường minh cho Gemini** — trước đây chạy mặc định của nhà cung cấp.
- [ ] **Mặc định tắt chia sẻ công khai**, bật phải qua duyệt.
- [ ] **Bỏ trường tên và email** khỏi bảng người dùng; chuyển sang mã ẩn danh do giáo viên phát.
- [ ] **Trang Điều khoản sử dụng và Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ đọc cho học sinh lớp 10.
- [ ] **Nút báo cáo câu trả lời không phù hợp** của trợ lý AI.
