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

1. **Postgres** — dữ liệu phải sống qua deploy. Vẫn là việc số một của cả dự án. (Gieo dữ liệu đã bỏ hẳn: ứng dụng không tự tạo tài khoản nào.)
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

> Mục này từng mô tả bản demo — xoá sạch cơ sở dữ liệu mỗi lần khởi động, không
> có Alembic, không có mật khẩu. Những điều đó **không còn đúng**; phần dưới đã
> viết lại theo mã hiện tại.

- **Dữ liệu ở lại, và ứng dụng không tự tạo ra dữ liệu nào.** Khởi động không
  ghi một hàng nào; cơ sở dữ liệu mới là cơ sở dữ liệu trống. Nhân vật mẫu nằm
  ở `tests/du_lieu_mau.py` và không đường nào từ `app/` với tới được.
- **Alembic đã có.** `render.yaml` chạy `alembic upgrade head` trước khi mở cổng.
  Mỗi lần đổi mô hình phải kèm một revision; `tests/` có bài đối chiếu lược đồ
  với chuỗi di trú, nên quên revision là hỏng bộ kiểm thử.
- **SQLite chỉ còn dùng cho máy cá nhân và kiểm thử.** Bản triển khai dùng
  Postgres, và `app/config.py` từ chối khởi động nếu thiếu `DATABASE_URL`.
- **Vẫn một tiến trình uvicorn, không có `--workers`.** Nhưng lý do đã đổi: gieo
  dữ liệu không còn cản trở, chỗ cản bây giờ là bộ đếm chống thử mật khẩu nằm
  trong bộ nhớ (xem mục [Vận hành](#vận-hành)).
- **Lời gọi Gemini là đồng bộ nằm trong endpoint bất đồng bộ**, nên một lượt AI khoá luôn event loop. Với một tiến trình, số lượt AI chạy thật sự song song xấp xỉ bằng một.
- **Hạn mức chat đếm trong bộ nhớ tiến trình theo cookie**: mất khi khởi động lại, không gắn với người, không chia sẻ giữa các worker.
- **`render.yaml` không chạy `npm run build:css`**; `static/css/app.css` được commit sẵn. Chạy được, nhưng bước build CSS là thủ công và có thể lệch khỏi `input.css`.

### Chỗ vỡ trước tiên không phải cơ sở dữ liệu

SQLite gánh một lớp (~40 học sinh) thoải mái, và mọi trang đều render phía máy chủ, không có trạng thái phía trình duyệt. Hai chỗ thắt thật sự là **lời gọi Gemini chặn tiến trình** và **hạn mức của gói Gemini miễn phí**: một lớp cùng làm chế độ nhập vai là khoảng 800 lượt gọi cho mỗi kịch huống.

### Thứ tự bắt buộc khi chuyển sang dùng thật

1. ~~**PostgreSQL + chỉ gieo khi trống.**~~ Mã đã xong; còn lại là **dựng cơ sở
   dữ liệu thật trên Render và triển khai một lần** — chưa chạy lần nào với
   Postgres, nên đây vẫn là việc số một.
2. ~~**Alembic**~~ — đã có, và `render.yaml` chạy `alembic upgrade head` trước khi mở cổng.
3. **Đưa lời gọi Gemini sang threadpool** để một lượt AI chậm không khoá cả tiến trình.
4. **Hạn mức chat thành cột trong DB**, không phải dict trong bộ nhớ. Cùng gốc
   với bộ đếm chống thử mật khẩu ở mục [Vận hành](#vận-hành), và cùng một mốc
   phải sửa: ngày thêm worker thứ hai.
5. **`npm run build:css` vào build command của Render.**
6. ~~**Đăng nhập thật**~~ — đã có: mật khẩu băm bằng Argon2id, CSRF, chống thử
   sai, đặt lại mật khẩu.

### Ngoài hạ tầng

- **Đơn vị thuê bao.** Mô hình hiện là `Lớp → giáo viên`, **chưa có `Trường`**. Cần trường học là đơn vị, nhiều giáo viên một trường, và bàn giao khi nhân sự đổi. Rẻ khi chưa có dữ liệu, đắt khi đã có.
- **Trần chi phí theo trường, và xuống cấp êm thay vì báo lỗi.** Chế độ ngoại tuyến (`_offline_guided`, `_offline_freeform`) **đã dạy trọn một buổi với chi phí AI bằng không** — nên coi đó là một mức sản phẩm có chủ đích, không phải phương án chữa cháy không ai nhắc tới.
- **Nút thắt tăng trưởng là soạn nội dung**, không phải máy chủ. Năm kịch huống viết tay, mỗi kịch huống bốn cấp độ — thêm máy chủ không thêm được kịch huống.
- **Vận hành:** xem mục [Vận hành](#vận-hành) bên dưới. Sao lưu, diễn tập phục hồi và trang sức khoẻ đã có; môi trường staging và quy trình quay lui thì chưa.

### Việc kỹ thuật phát sinh từ rà soát pháp lý

Xem [LEGAL.md](../LEGAL.md) cho bối cảnh đầy đủ.

- [ ] **Kiểm soát `journal_entries.image_url`.** Đây là đường dẫn tự do do học sinh dán vào, được render thẳng vào `<img src>` trên **trang công khai**. Bộ lọc chỉ soi chữ, không soi liên kết hay ảnh. Học sinh có thể công bố ảnh bất kỳ, kể cả một pixel theo dõi thu địa chỉ IP của mọi em vào xem. **Chỗ hở sắc nhất còn lại.** Cần danh sách nguồn cho phép hoặc tự lưu ảnh.
- [x] **Ngưỡng an toàn tường minh cho Gemini** — trước đây chạy mặc định của nhà cung cấp.
- [ ] **Mặc định tắt chia sẻ công khai**, bật phải qua duyệt.
- [ ] **Bỏ trường tên và email** khỏi bảng người dùng; chuyển sang mã ẩn danh do giáo viên phát.
- [ ] **Trang Điều khoản sử dụng và Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ đọc cho học sinh lớp 10.
- [x] **Nút báo cáo câu trả lời không phù hợp** của trợ lý AI, kèm nút gửi góp ý.
- [ ] **Đưa góp ý ra một nơi sống được.** Hiện góp ý nằm trong bảng `reports` (mất khi khởi động lại) và trong nhật ký máy chủ (đọc được nhưng chỉ trong thời gian lưu log). Cần một trong hai: cơ sở dữ liệu lâu dài, hoặc đẩy ra webhook / email / issue trên GitHub. Đây là phần còn thiếu thật sự của tính năng này.
- [ ] **Màn hình đọc báo cáo** cho người vận hành — hiện chưa có chỗ nào xem được, kể cả khi dữ liệu còn.

---

## Vận hành

Phần này ghi những thứ chỉ hỏng sau khi đã triển khai, và những giới hạn đã biết
mà cố ý chưa sửa. Ghi ra để lần sau không phải suy lại từ đầu.

### Ứng dụng không gieo dữ liệu

Khởi động **không ghi một hàng nào**. Cơ sở dữ liệu mới là cơ sở dữ liệu trống,
và nó ở nguyên như vậy cho tới khi có người tạo ra dữ liệu. Không còn tài khoản
mẫu nào trong `app/` — những nhân vật `@gals.demo` đã chuyển hẳn sang
`tests/du_lieu_mau.py`, là giàn giáo kiểm thử, và `tests/test_van_hanh.py` chặn
mọi đường từ `app/` gọi ngược lại.

Dựng một bản chạy thật, từ trống hoàn toàn:

```
alembic upgrade head                                  # dựng lược đồ
python -m app.quan_tri truong-them "THPT Nguyễn Trãi" --tinh "Hà Nội"
python -m app.quan_tri ma "THPT Nguyễn Trãi"          # in mã giáo viên, sống 3 ngày
```

Đưa mã đó cho giáo viên; họ tự đăng ký ở `/dang-ky/giao-vien`, tự tạo lớp, và
đọc mã lớp cho học sinh. Không có bước nào ứng dụng tự quyết định thay bạn.

Xem những gì đang có, và dọn:

```
python -m app.quan_tri truong-liet-ke
python -m app.quan_tri ma-ai "THPT Nguyễn Trãi"   # ai đã lập tài khoản bằng mã hiện tại
python -m app.quan_tri xoa-cho                    # yêu cầu xoá đang chờ
python -m app.quan_tri xoa <email> --chac-chan
```

### Chốt chặn `DATABASE_URL`

`app/config.py` **từ chối khởi động** nếu biến `RENDER` có mặt mà `DATABASE_URL`
thì không. Không có chốt này, thiếu biến sẽ rơi về SQLite trên ổ đĩa tạm: ứng
dụng khởi động bình thường, trang sức khoẻ báo xanh, và toàn bộ tài khoản biến
mất ở lần triển khai kế tiếp — không có dấu hiệu nào cho tới khi một thầy cô
đăng nhập không được. Trên máy cá nhân thì vẫn rơi về SQLite như cũ.

Ép chốt này chạy ở nơi khác bằng `GALS_YEU_CAU_DATABASE_URL=1`.

### Trang sức khoẻ

`GET /suc-khoe` chạy một câu truy vấn thật rồi mới trả `{"trang_thai": "ok"}`;
không truy vấn được thì trả 503. `render.yaml` trỏ `healthCheckPath` vào đây chứ
không vào `/`, vì trang chủ vẽ được kể cả khi cơ sở dữ liệu đã chết.

Trang này không cần đăng nhập, không chạm dữ liệu của ai, và cố ý không kể gì về
bên trong — một trang sức khoẻ liệt kê phiên bản thư viện là một trang do thám
miễn phí.

- [ ] **Nối một máy dò bên ngoài** (UptimeRobot hoặc tương đương, gói miễn phí)
      vào `https://<tên miền>/suc-khoe`, 5 phút một lần, báo về email dự án.
      Đây là việc cấu hình, không phải việc code, và chưa làm.

### Sao lưu và diễn tập phục hồi

```
python -m app.quan_tri sao-luu  sao-luu-2026-08-13.json
python -m app.quan_tri phuc-hoi sao-luu-2026-08-13.json --chac-chan
```

Đây là **tuyến thứ hai** nằm dưới bản sao lưu tự động hằng ngày của gói Postgres
trả phí, không phải để thay thế nó. Giá trị thật của nó là làm cho việc diễn tập
phục hồi trở nên khả thi mà không đụng vào bản chạy thật.

**Tệp sao lưu chứa toàn bộ dữ liệu cá nhân**, kể cả nhật ký học sinh và mã băm
mật khẩu. Giữ nó như giữ chính cơ sở dữ liệu: không đưa lên kho mã, không gửi
qua ứng dụng nhắn tin, xoá khi không cần nữa.

**Diễn tập đã chạy — 13/08/2026.** Đổ dữ liệu mẫu (30 hàng, 15 bảng) ra tệp, nạp
vào một cơ sở dữ liệu SQLite trống đã chạy `alembic upgrade head`, rồi đếm lại:
số hàng từng bảng khớp tuyệt đối, và soi tay thì mã băm Argon2, nội dung nhật ký
và mốc thời gian tới từng micro giây đều nguyên vẹn.
`tests/test_van_hanh.py` chạy lại đúng vòng đó trong mỗi lần kiểm thử, nên nó
không thể mục đi trong im lặng.

- [ ] **Diễn tập lại trên Postgres thật** sau khi triển khai. Vòng vừa rồi là
      SQLite → SQLite; kiểu dữ liệu của Postgres có thể khác ở chỗ không ngờ.

### Giới hạn đã biết: bộ đếm chống thử mật khẩu nằm trong bộ nhớ

`app/throttle.py` đếm trong bộ nhớ tiến trình. Hệ quả: chạy **nhiều hơn một
worker web** thì hạn mức thực tế nhân lên theo số worker, và khởi động lại là
xoá sạch bộ đếm.

Chấp nhận được khi còn chạy một tiến trình, tức là suốt đợt thử nghiệm. **Mốc
phải sửa: ngày thêm worker thứ hai** — lúc đó bộ đếm phải chuyển vào Postgres,
không có ngoại lệ, vì nó là hàng rào duy nhất trước việc dò mã giáo viên.

### Cố ý không dùng dịch vụ theo dõi lỗi của bên thứ ba

Không có Sentry hay tương đương, và đây là quyết định chứ không phải thiếu sót.
Một vết lỗi (traceback) có thể mang theo nguyên văn nhật ký của học sinh, nên
gắn dịch vụ đó vào là biến nó thành một bên xử lý dữ liệu không được kê khai —
đúng thứ mà Chính sách quyền riêng tư nói là không có. Thay vào đó ghi log có
cấu trúc vào luồng log của nhà cung cấp: bất tiện hơn, và nhất quán với việc
không có mã của bên thứ ba ở bất cứ đâu khác.

Ngày nào muốn đổi ý thì phải cập nhật Mục V của Chính sách quyền riêng tư trước,
không phải sau.

### Chưa có

- [ ] Môi trường staging.
- [ ] Quy trình quay lui khi một lần triển khai hỏng.
- [ ] Cảnh báo khi tỉ lệ lỗi tăng — hiện chỉ có "còn sống hay không".
