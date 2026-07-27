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
