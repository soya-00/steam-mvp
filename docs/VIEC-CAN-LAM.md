# Việc cần làm tiếp

*Rà lại: 08/2026.*

Tài liệu này theo dõi trạng thái thật của dự án. Một mục chỉ được đánh dấu xong khi **đã có trong mã nguồn**, không phải khi đã có kế hoạch.

> **Lưu ý về nhánh.** Một phần công việc bên dưới đang nằm trong pull request chưa gộp. Chỗ nào như vậy đều ghi rõ. Đọc từ `main` sẽ không thấy phần đó.

---

## Chặn đường — chưa xong thì chưa được có học sinh thật

Năm việc này đứng trước mọi việc khác. Không phải vì khó nhất, mà vì mọi thứ còn lại đều vô nghĩa nếu thiếu chúng.

- [ ] **Pháp nhân bảo trợ.** Không có pháp nhân thì không ai ký được hợp đồng với nhà trường và không ai nộp được hồ sơ đánh giá tác động. Xem [LEGAL.md](../LEGAL.md).
- [ ] **Sửa lỗi dùng chung tài khoản.** Cả ứng dụng chỉ có ba tài khoản mẫu; hai người cùng nhập mã lớp là cùng một tài khoản và đọc được bài của nhau. **Việc gấp nhất về mặt kỹ thuật.**
- [ ] **PostgreSQL và chỉ gieo dữ liệu khi trống.** Hiện `reset_and_seed()` gọi `drop_all()` trong vòng đời FastAPI — mỗi lần khởi động lại là xoá sạch.
- [ ] **Đăng nhập thật, có mật khẩu, kèm CSRF.** Hiện chỉ là cookie có chữ ký.
- [ ] **Chuyển mã nguồn sang OpenAI.** Nhà cung cấp đã được chốt là OpenAI và `LEGAL.md` viết theo đó, nhưng mã nguồn vẫn đang gọi Gemini: `app/gemini.py`, gói `google-genai`, biến `GEMINI_API_KEY`, hàm `gemini_enabled()` dùng trong template và dòng báo chế độ ngoại tuyến ở chân trang. Xem mục [Nhà cung cấp AI](#nhà-cung-cấp-ai).

Chưa có **file LICENSE**. Không có giấy phép thì mặc định là giữ toàn bộ quyền, dù README mời mọi người clone về chạy. Cần chọn riêng cho mã nguồn và cho nội dung kịch huống.

---

## Nhà cung cấp AI

Đã chốt: **OpenAI**. `LEGAL.md` Mục 6 viết theo lựa chọn này. Phần còn lại là đưa mã nguồn và cấu hình tài khoản về đúng như tài liệu đã mô tả.

### Chuyển mã nguồn

- [ ] Thay `app/gemini.py` bằng đường gọi OpenAI, giữ nguyên hai chế độ (nhập vai và tự do) cùng toàn bộ chế độ ngoại tuyến dựng sẵn.
- [ ] Đổi tên biến môi trường, hàm `gemini_enabled()` và dòng báo ngoại tuyến ở chân trang sang tên trung lập với nhà cung cấp.
- [ ] Giữ nguyên các bất biến đã có phép thử: lọc emoji bằng mã, không chấm điểm, chỉ gửi câu hỏi và câu trả lời hiện tại.
- [ ] Cập nhật `tests/test_gemini_offline.py` theo tên mới.

### Cấu hình tài khoản — bắt buộc trước khi có học sinh thật

Theo `LEGAL.md` Mục 6:

- [ ] **Bật Zero Data Retention (ZDR)** trên tài khoản API.
- [ ] **Tài khoản API do người trưởng thành đứng tên** — cùng người giữ vai "người trưởng thành chịu trách nhiệm" ở Mục 8.
- [ ] **Đặt hạn mức chi tiêu cứng** trên tài khoản.
- [ ] **Thêm lớp kiểm duyệt của nhà cung cấp**, chồng lên bộ lọc cụm từ đang có.
- [ ] **Chỉ gửi nội dung Kho A.** Cần phép thử tự động chặn Kho B lọt vào lời nhắc.
- [ ] **Ghi nhật ký siêu dữ liệu** của các lần chuyển dữ liệu, phục vụ hồ sơ chuyển dữ liệu xuyên biên giới.

---

## Khả năng tiếp cận

Mục tiêu: học sinh khiếm thị dùng được GALS bằng trình đọc màn hình — VoiceOver trên iOS, TalkBack trên Android, NVDA trên Windows.

### Đã làm

- **Liên kết bỏ qua điều hướng** ở đầu mỗi trang, ẩn cho tới khi được focus.
- **Vùng mốc (landmark)** đúng chuẩn: `header`, `nav`, `main`, `footer`. `main` có `id` và `tabindex="-1"`.
- **`aria-current`** trên mục điều hướng đang mở và cấp độ đang làm.
- **Không dùng riêng màu để truyền đạt trạng thái.** Bốn cấp độ có chữ đi kèm: *đã xong · đang làm · chưa tới*.
- **Biểu tượng trang trí** đều có `aria-hidden="true"`.
- **Vùng động (live region)** cho khung trò chuyện, và `role="status"` cho *đang nghĩ…* / *Đã lưu*.
- **Mọi ô nhập liệu đều có `label`**, ẩn bằng `sr-only` khi thiết kế không cần nhãn hiển thị.
- **Vòng focus rõ ràng** qua `:focus-visible`, có token màu riêng để nhìn thấy được trên mọi nền.
- **Nhóm chọn avatar** dùng `fieldset` + `legend`.

### Đã làm — đang chờ gộp

- **Nền tối, và chế độ tương phản cao** dùng chung được với cả nền sáng lẫn nền tối.
- **Bộ chọn giao diện ba trạng thái** (sáng / tối / theo hệ thống), dán lên `<html>` bằng một đoạn chạy chặn trước khi trang vẽ, nên không nhấp nháy khi tải.
- **Nghe theo `prefers-contrast`** và `prefers-color-scheme` khi người dùng chưa chọn gì.
- **Đo tương phản bằng mã, không bằng mắt.** `tests/test_tuong_phan_mau.py` đọc thẳng bảng màu trong `src/input.css` và tính lại tỉ lệ cho cả bốn tổ hợp giao diện.
- **Token đường kẻ riêng (`--c-field-line`)** cho viền ô nhập và rãnh công tắc. `--c-hairline` đủ để chia khối nhưng không bao giờ đạt 3:1, nên trước đó viền ô nhập gần như vô hình ở nền tối.
- **Xử lý `forced-colors`**, và khối `@media print` ép về bản sáng.
- **Công tắc giảm chuyển động và nền phẳng** cho máy không có sẵn cài đặt của hệ điều hành.

> Phép đo tương phản tìm ra **bốn chỗ hụt có sẵn từ trước ở bản sáng**, đều đã sửa: chữ mờ trên nền trắng chỉ đạt 3.21:1, `amber-700` trên nền amber 4.18:1, chữ trắng trên nền teal 4.26:1 và trên nền sci 4.49:1. Hai màu amber và art quá sáng để đội chữ trắng nên bị cấm dùng làm nền đặc, có phép thử canh.

### Chưa làm

- [ ] **Kiểm chứng bằng thiết bị thật.** Ngữ nghĩa đã đúng ở mức mã nguồn và có phép thử canh, nhưng **chưa từng chạy VoiceOver hay TalkBack với giọng đọc tiếng Việt**. Đây là việc quan trọng nhất còn lại của cả mục này.
- [ ] **Dời focus sau khi HTMX cập nhật.** Sau khi gửi tin nhắn, focus nên về ô nhập hoặc tới câu trả lời mới.
- [ ] **Thu hẹp `hx-swap` thành chỉ-thêm-mới**, để trình đọc màn hình không đọc lại cả khung chat sau mỗi lượt.
- [ ] **Nhãn `lang="en"`** cho các đoạn tiếng Anh xen kẽ (tên khoá học, "Follow-up").
- [ ] **Phóng chữ tới 200%** mà không vỡ bố cục — cần kiểm tra lại.
- [ ] Kiểm tra **thứ tự đọc ở Không gian tư duy**: phần đã trả lời nằm ở cột trái, xem như vậy có hợp lý khi nghe không.

---

## Giao diện

Bản dựng lại đã xong và **đang chờ gộp**: vỏ ứng dụng nền sáng có thanh tab, Không gian tư duy hiển thị **mỗi lần một câu hỏi** với cột Dữ kiện tóm tắt bên phải, trang tài khoản, bảng tài khoản ở đầu trang, các trang giáo viên được dựng lại, và chân trang thống nhất cho mọi trang.

Những thứ phải giữ khi sửa tiếp:

- Bảng màu đi qua **một tầng token duy nhất** trong `src/input.css`: giá trị thật nằm ở `:root`, `@theme inline` trỏ tên tiện ích Tailwind vào đó. Không thẻ nào được viết `dark:`.
- Các mốc `aria`, nhãn `sr-only` và thứ tự tiêu đề đã dựng.
- Nguyên tắc: trạng thái không bao giờ chỉ được thể hiện bằng màu.
- Tailwind quét class **tĩnh**. Không ghép chuỗi class trong Jinja — `tests/test_css_build.py` canh việc này.

---

## Nội dung

Ba nhóm nghề trong bảng phân loại **chưa có kịch huống**:

- [ ] Hoá học, kiểm định — *sản phẩm cấp 3: quy trình lấy và kiểm tra mẫu*
- [ ] Quy hoạch, môi trường — *sản phẩm cấp 3: kịch bản sử dụng không gian hoặc giao thông*
- [ ] Truyền thông, ngôn ngữ — *sản phẩm cấp 3: thông điệp cho từng nhóm đối tượng*

Định dạng kịch huống nằm trong `data/scenarios.json`; các trường bắt buộc và phần kiểm tra khi nạp nằm ở `app/scenarios.py`. Bộ nạp **từ chối tải** một nhịp bối cảnh không có trường `facts`.

- [ ] **Quy trình soạn kịch huống.** Hiện là gõ tay JSON lồng nhiều lớp, không mở rộng được cho người khác cùng viết. Cần lệnh kiểm tra `scenarios.json` và một khuôn Markdown → JSON. **Nút thắt tăng trưởng thật của sản phẩm là nội dung, không phải máy chủ.**
- [ ] **Viết lại tài liệu kỹ thuật.** `docs/KY-THUAT.md` đã bị xoá; phần kiến trúc, biến môi trường và cách deploy hiện không có chỗ nào ghi lại.

---

## Cần rà lại

- [ ] **Màn hình giáo viên được suy ra từ mô hình dữ liệu**, vì sơ đồ luồng giáo viên không được cung cấp. Cần đối chiếu với sơ đồ gốc.
- [ ] **Đường gọi AI thật** mới chỉ thử được vài lượt trước khi hết hạn mức của khoá miễn phí. Bộ chặn phía máy chủ đã kiểm thử đầy đủ, nhưng **hành vi của chính mô hình thì chưa** — nhất là các rào an toàn về trẻ vị thành niên và định kiến giới.
- [ ] **Đối chiếu điều khoản của OpenAI về người dùng chưa thành niên** trong triển khai qua nhà trường, và lấy xác nhận bằng văn bản chứ không suy ra từ trang giới thiệu.

---

## Cơ sở dữ liệu và backend

### Hiện tại đang là gì

- **`reset_and_seed()` chạy trong vòng đời FastAPI và gọi `Base.metadata.drop_all()`** (`app/seed.py`). Mỗi lần khởi động lại là **xoá sạch**. Gói miễn phí của Render còn cho dịch vụ ngủ khi vắng người, nên bài của học sinh thường không sống qua một đêm.
- **SQLite nằm trên đĩa tạm.** Mỗi lần deploy cũng xoá.
- **Một tiến trình uvicorn, không có `--workers`.** Và **hiện chưa thêm worker được**: mỗi worker sẽ chạy lại vòng đời rồi xoá bảng ngay dưới chân các worker khác. Chặn đường mở rộng ngang không phải là framework, mà là cách gieo dữ liệu.
- **Lời gọi AI là đồng bộ nằm trong endpoint bất đồng bộ**, nên một lượt AI khoá luôn event loop.
- **Hạn mức chat đếm trong bộ nhớ tiến trình theo cookie**: mất khi khởi động lại, không gắn với người. (Rò rỉ bộ nhớ của bộ đếm đã được chặn bằng trần 2.000 khoá.)
- **`render.yaml` không chạy `npm run build:css`**; `static/css/app.css` được commit sẵn. Chạy được, nhưng bước build CSS là thủ công và có thể lệch khỏi `input.css`.

### Chỗ vỡ trước tiên không phải cơ sở dữ liệu

SQLite gánh một lớp (~40 học sinh) thoải mái, và mọi trang đều render phía máy chủ. Hai chỗ thắt thật sự là **lời gọi AI chặn tiến trình** và **hạn mức của gói miễn phí**: một lớp cùng làm chế độ nhập vai là khoảng 800 lượt gọi cho mỗi kịch huống.

### Thứ tự bắt buộc khi chuyển sang dùng thật

1. **PostgreSQL + chỉ gieo khi trống.** Một thay đổi mở khoá cùng lúc *lưu được dữ liệu* và *chạy nhiều worker*. `app/db.py` đã rẽ nhánh sẵn theo tiền tố `DATABASE_URL`.
2. **Alembic** khi lược đồ ổn định — `create_all` không sửa được bảng đang có dữ liệu.
3. **Đưa lời gọi AI sang threadpool** để một lượt chậm không khoá cả tiến trình.
4. **Hạn mức chat thành cột trong DB**, không phải dict trong bộ nhớ.
5. **`npm run build:css` vào build command của Render.**
6. **Đăng nhập thật** trước khi có dữ liệu thật.
7. **Chuyển hạ tầng về nhà cung cấp đặt tại Việt Nam** — nghĩa vụ lưu trữ trong nước, xem [LEGAL.md](../LEGAL.md).

### Đã sửa

- **Truy vấn N+1 ở phần xuất dữ liệu và các trang tiến độ.** Với lớp 200 học sinh, bản xuất chạy **1.043 truy vấn trong 456 ms** vì danh sách lớp nạp lười từng em một. Dùng `selectinload` và gom theo lớp còn **46 truy vấn trong 79 ms**. Có phép thử đặt trần số truy vấn để lỗi này không quay lại trong im lặng. *(Đang chờ gộp.)*

### Ngoài hạ tầng

- **Đơn vị thuê bao.** Mô hình hiện là `Lớp → giáo viên`, **chưa có `Trường`**. Cần trường học là đơn vị, nhiều giáo viên một trường, và bàn giao khi nhân sự đổi. Rẻ khi chưa có dữ liệu, đắt khi đã có.
- **Trần chi phí theo trường, và xuống cấp êm thay vì báo lỗi.** Chế độ ngoại tuyến **đã dạy trọn một buổi với chi phí AI bằng không** — nên coi đó là một mức sản phẩm có chủ đích, không phải phương án chữa cháy.
- **Vận hành chưa có gì:** sao lưu và diễn tập phục hồi, theo dõi lỗi, giám sát uptime, môi trường staging, quy trình quay lui khi deploy hỏng. Một đợt thử nghiệm có bài thật mà không có sao lưu là kiểu hỏng kết thúc luôn dự án.

---

## Việc kỹ thuật phát sinh từ rà soát pháp lý

Xem [LEGAL.md](../LEGAL.md) cho bối cảnh đầy đủ.

- [ ] **Kiểm soát `journal_entries.image_url`.** Đường dẫn tự do do học sinh dán vào, render thẳng vào `<img src>` trên **trang công khai**. Bộ lọc chỉ soi chữ, không soi liên kết. Học sinh có thể công bố ảnh bất kỳ, kể cả một pixel theo dõi thu địa chỉ IP của mọi em vào xem. **Chỗ hở sắc nhất còn lại.** Cần danh sách nguồn cho phép hoặc tự lưu ảnh.
- [ ] **Tách hai kho dữ liệu** theo Mục 3 của `LEGAL.md`: sản phẩm nhập vai tách khỏi bài phản tư cá nhân, và ranh giới giữa hai kho cũng là ranh giới ra khỏi lãnh thổ.
- [ ] **Mặc định tắt chia sẻ công khai**, bật phải qua duyệt của người lớn.
- [ ] **Bỏ trường tên và email** khỏi bảng người dùng; chuyển sang mã ẩn danh do giáo viên phát.
- [ ] **Bảng ghi nhận sự đồng ý**: mã chủ thể, loại đồng ý, cách kiểm chứng, thời điểm, phiên bản chính sách, phạm vi, trạng thái rút lại.
- [ ] **Trang Điều khoản sử dụng và Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ đọc cho học sinh lớp 10, có nêu rõ phần dữ liệu nhạy cảm và phần công khai về AI.
- [ ] **Ngừng ghi nội dung người dùng ra nhật ký máy chủ.** `LEGAL.md` nói không ghi; `app/routers/phan_hoi.py` hiện vẫn ghi góp ý và báo cáo ra log với nhãn `[GOP-Y]` / `[BAO-CAO]`. Một trong hai phải đổi.
- [ ] **Đưa góp ý ra một nơi sống được.** Hiện nằm trong bảng `reports` (mất khi khởi động lại). Cần cơ sở dữ liệu lâu dài, hoặc đẩy ra webhook / email / issue trên GitHub.
- [ ] **Màn hình đọc báo cáo** cho người vận hành — hiện chưa có chỗ nào xem được, kể cả khi dữ liệu còn.
- [ ] **Quy trình thông báo sự cố trong 72 giờ**, lưu hồ sơ sự cố tối thiểu 5 năm.
- [x] **Ngưỡng an toàn tường minh cho mô hình AI** — trước đây chạy mặc định của nhà cung cấp.
- [x] **Nút báo cáo câu trả lời không phù hợp** của trợ lý AI, kèm nút gửi góp ý.
- [x] **Xuất dữ liệu.** Học sinh tải được toàn bộ bài mình viết dạng JSON. Giáo viên tải được **siêu dữ liệu** của lớp dạng ZIP nhiều bảng CSV — cố ý **không kèm** nội dung nhật ký, tiêu đề do học sinh tự đặt, mô tả hồ sơ, phần tổng hợp của AI hay tên thật. Học sinh hiện ra dưới dạng mã giả danh. *(Đang chờ gộp.)*

---

## Ý tưởng mở rộng — xếp theo mức ưu tiên

Bộ kiểm thử tự động (`tests/`, chạy bằng `pytest`) khoá chặt các bất biến: mọi trang mở được, kịch huống đi trọn, ranh giới riêng tư, bộ lọc đầu vào kể cả các ca va chạm dấu tiếng Việt, không có giao diện chấm điểm, class Tailwind không biến mất khỏi CSS build, tương phản màu, và các mốc trợ năng. CI chạy trên mỗi lần đẩy code.

### Dễ dùng

1. **Nhập mã lớp sau khi đăng ký.** Học sinh độc lập hiện *không bao giờ* vào được lớp; ô mã lớp chỉ tồn tại lúc đăng ký. Cần form ở Trang cá nhân, kèm màn xác nhận nói rõ: vào lớp nghĩa là giáo viên đó đọc được nhật ký. Chạm vào lời hứa riêng tư nên phải làm cẩn thận.
2. **Thẻ "Tiếp tục chỗ đang dở"** trỏ thẳng vào đúng nhịp đang đứng.
3. **Giáo viên: lọc nhật ký theo kịch huống, xuất nhật ký cả lớp ra bản in** — dùng lại hạ tầng in sẵn có.
4. **Meta tags cho link chia sẻ** — dán link vào Zalo/Messenger phải hiện preview tử tế; đây là kênh chia sẻ thật của học sinh Việt Nam. *(Chỉ làm sau khi chia sẻ công khai đã có quy trình duyệt.)*
5. **PWA shell tối thiểu** cho mạng chập chờn ở trường: cache trang vỏ và CSS, để mất mạng giữa chừng không thành màn hình trắng.

### Mở rộng quy mô

6. **Nhiều giáo viên một lớp**, chuyển lớp giữa giáo viên.
7. **Gom chip trạng thái và thẻ-trống thành macro Jinja** — hiện mỗi template tự chép một bản.
