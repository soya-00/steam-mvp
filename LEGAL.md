# Tuyên bố pháp lý và dữ liệu

**Đọc trang này trước khi cho bất kỳ học sinh có thật nào dùng GALS.**

> **Cập nhật: 08/2026.** Bản trước được viết khi Nghị định 13/2023/NĐ-CP còn hiệu lực. Nghị định đó đã hết hiệu lực. Toàn bộ khung pháp lý bên dưới đã được viết lại.

---

## Tóm tắt trong mười giây

| | |
|---|---|
| GALS hiện là gì | Một **bản mẫu (prototype)**. Chưa phải sản phẩm, chưa có pháp nhân. |
| Dữ liệu gieo sẵn | **Toàn bộ là dữ liệu giả định do AI sinh ra.** Không có học sinh thật nào trong đó. |
| Được nhập thông tin thật vào không | **Không.** Đừng nhập tên thật, trường thật, số điện thoại, email cá nhân. |
| Ai chịu trách nhiệm khi thử nghiệm thật | **Nhà trường là Bên Kiểm soát dữ liệu.** GALS chỉ là Bên Xử lý theo hợp đồng. |
| Đối tượng người dùng | Học sinh THPT. Một phần dưới 16 tuổi — tức là "trẻ em" theo luật Việt Nam. |
| Chính sách tuổi | **Áp dụng mức bảo vệ dành cho trẻ em cho tất cả mọi người dùng**, không phân biệt tuổi. |
| Có phải công cụ hỗ trợ tâm lý không | **Không.** Xem mục [Trợ lý AI](#7-trợ-lý-ai-và-những-điều-gals-không-làm). |

---

## 1. Khung pháp lý hiện hành

Danh sách để tra cứu. **Ngày hiệu lực phải được kiểm tra lại từ nguồn chính thức.**

| Văn bản | Hiệu lực | Vì sao liên quan tới GALS |
|---|---|---|
| **Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15** | 01/01/2026 | Luật gốc. Quyền của chủ thể dữ liệu, sự đồng ý, dữ liệu nhạy cảm, chuyển dữ liệu ra nước ngoài. |
| **Nghị định 356/2025/NĐ-CP** | 01/01/2026 | Hướng dẫn thi hành. Thay thế hoàn toàn Nghị định 13/2023/NĐ-CP. Chứa danh mục dữ liệu nhạy cảm và các biểu mẫu hồ sơ. |
| **Luật Trẻ em 2016 + Nghị định 56/2017/NĐ-CP** | Còn hiệu lực | "Trẻ em" = người dưới 16 tuổi. Bảo vệ thông tin cá nhân của trẻ em trên môi trường mạng. |
| **Luật Trí tuệ nhân tạo số 134/2025/QH15** | 01/03/2026 | Phân loại rủi ro, nghĩa vụ minh bạch, trách nhiệm bồi thường của bên triển khai. Giáo dục là lĩnh vực được nêu tên. |
| **Luật An ninh mạng số 116/2025/QH15** | 01/07/2026 | Hợp nhất Luật An toàn thông tin mạng 2015 và Luật An ninh mạng 2018. Lưu trữ dữ liệu trong nước, nhật ký hệ thống. |
| **Nghị định 147/2024/NĐ-CP** | 25/12/2024 | Quản lý thông tin trên mạng. Tài khoản của trẻ dưới 16 tuổi, ngưỡng cấp phép mạng xã hội, xác thực tài khoản. |
| **Nghị định 53/2022/NĐ-CP** | 01/10/2022 | Chi tiết về nội địa hoá dữ liệu. |

**Không dựa vào tài liệu này cho ngày hiệu lực hay nội dung điều khoản.** Đây là bản đồ để biết cần tra cứu ở đâu và cần hỏi luật sư điều gì.

---

## 2. Dữ liệu nhạy cảm — điều quan trọng nhất trong trang này

Điều 4 Nghị định 356/2025/NĐ-CP xếp **"thông tin về đời sống riêng tư, bí mật cá nhân, bí mật gia đình"** và **tình trạng sức khoẻ** vào nhóm **dữ liệu cá nhân nhạy cảm**.

Nhật ký phản tư của học sinh — theo đúng thiết kế — là loại nội dung đó. GALS giả định trường hợp xấu nhất: **có xử lý dữ liệu nhạy cảm**.

Hệ quả, nói thẳng:

- **Không được dùng quyền hoãn 5 năm** dành cho doanh nghiệp nhỏ và doanh nghiệp khởi nghiệp đối với hồ sơ đánh giá tác động và nhân sự bảo vệ dữ liệu. Quyền hoãn đó không áp dụng cho bên xử lý dữ liệu nhạy cảm.
- **Khi xin sự đồng ý, phải nói rõ với chủ thể rằng đây là dữ liệu nhạy cảm.** Một chính sách quyền riêng tư chung chung là không đủ.
- **Mức xử phạt đối với nhóm dữ liệu này nặng hơn đáng kể.**

Đây là lý do toàn bộ kiến trúc dữ liệu ở Mục 3 được thiết kế như vậy.

---

## 3. Kiến trúc dữ liệu: tách hai kho

**Nguyên tắc: ranh giới giữa hai kho dữ liệu cũng chính là ranh giới ra khỏi lãnh thổ Việt Nam.**

| | **Kho A — Sản phẩm nhập vai** | **Kho B — Phản tư cá nhân** |
|---|---|---|
| Nội dung | Cấp độ 1–3: phương án hệ thống, kế hoạch điều tra, quy trình xử lý sự cố. Học sinh viết với tư cách người làm nghề. | Cấp độ 4 (Phản chiếu), Ý tưởng tự do. Học sinh viết với tư cách chính mình. |
| Phân loại | Dữ liệu cá nhân cơ bản, gắn với mã ẩn danh | **Dữ liệu cá nhân nhạy cảm** |
| Mã hoá khi lưu | Tiêu chuẩn | Mã hoá ở mức trường dữ liệu, khoá không nằm trong cùng cơ sở dữ liệu |
| Giáo viên xem được | Có | Mặc định không. Chỉ khi học sinh chủ động chia sẻ |
| Ghi nhật ký truy cập | Không bắt buộc | **Bắt buộc** — ghi lại mọi lượt đọc |
| Thời hạn lưu | Theo năm học | Tự xoá cuối học kỳ trừ khi học sinh chủ động lưu |
| Được chia sẻ công khai | Có, qua quy trình duyệt | **Không bao giờ** |
| Được gửi ra nước ngoài | Có (tới OpenAI) | **Không bao giờ rời khỏi Việt Nam** |

**Vì sao cách tách này quan trọng:** hồ sơ chuyển dữ liệu ra nước ngoài khi đó chỉ mô tả văn bản nghề nghiệp nhập vai của người dùng ẩn danh — dễ lập, dễ bảo vệ, và mức rủi ro xử phạt thấp hơn hẳn so với hồ sơ bao gồm bài viết phản tư của người chưa thành niên.

Cách tách này cũng giải quyết luôn vấn đề công bố: **chỉ Kho A được chia sẻ**. GALS không bao giờ công bố thông tin đời sống riêng tư của trẻ em, nên yêu cầu "phải có sự đồng ý của cả trẻ em và người đại diện theo pháp luật khi công bố" không phát sinh.

### Định danh

- **Không lưu tên. Không lưu email. Không lưu số điện thoại.**
- Học sinh được nhận **mã ẩn danh** do giáo viên phát.
- Bảng đối chiếu mã ↔ học sinh **giữ trên giấy, ở phía giáo viên**. GALS không bao giờ nhận bảng này.
- **Dữ liệu giả danh vẫn là dữ liệu cá nhân theo luật.** Cách làm này giảm rủi ro, không xoá bỏ nghĩa vụ.

---

## 4. Chính sách độ tuổi

**Áp dụng mức bảo vệ dành cho trẻ em cho tất cả người dùng, không phân biệt tuổi khai báo.**

Lý do:

1. Học sinh lớp 10 có em 15 tuổi — tức là **trẻ em** theo Luật Trẻ em 2016.
2. Trong một năm học, học sinh bước qua mốc 16 tuổi vào ngày sinh nhật. Không hệ thống nào nên phụ thuộc vào việc theo dõi điều đó.
3. Một quy tắc duy nhất dễ giải thích với nhà trường hơn một bảng phân loại theo tuổi.

**Tuổi tự khai báo không phải là biện pháp kiểm chứng.** Người chưa thành niên không thể tự từ bỏ các biện pháp bảo vệ mà pháp luật dành cho họ, và một điều khoản kiểu "bạn tự chịu trách nhiệm về tuổi khai báo" không chuyển được trách nhiệm đó. Tuổi tự khai báo chỉ là một tín hiệu, dùng để định tuyến người dùng.

Ở giai đoạn thử nghiệm qua nhà trường, **cơ chế kiểm chứng thật là nhà trường**: giáo viên nắm danh sách lớp, thư thông báo gửi phụ huynh qua kênh sẵn có của trường.

---

## 5. Các ràng buộc thiết kế để GALS nằm ngoài định nghĩa mạng xã hội

Nghị định 147/2024/NĐ-CP định nghĩa mạng xã hội là hệ thống cho phép người dùng tạo tài khoản, lập trang cá nhân, đăng tải nội dung, chia sẻ và tương tác với cộng đồng.

GALS **chủ động không có** các yếu tố cộng đồng đó. Đây là ràng buộc thiết kế:

- Không bình luận
- Không biểu tượng cảm xúc, không thích, không đánh giá
- Không bảng tin, không trang khám phá, không thư viện bài của học sinh khác
- Không nhắn tin giữa học sinh với học sinh
- Không trang cá nhân mà người khác duyệt xem được
- Liên kết chia sẻ do học sinh gửi tới một người cụ thể, không có cơ chế lan truyền

**Bất kỳ ai đề xuất thêm một trong các tính năng trên đều đang đề xuất một thay đổi pháp lý, không chỉ là thay đổi sản phẩm.**

**Ngưỡng cấp phép:** mạng xã hội trong nước từ **10.000 lượt truy cập/tháng** hoặc trên **1.000 người dùng thường xuyên** phải xin giấy phép. Quy mô thử nghiệm hiện tại nằm dưới ngưỡng này — nhưng ngưỡng sẽ bị vượt qua nếu triển khai rộng.

**Lưu ý dù phân loại thế nào:** liên kết chia sẻ vẫn là **hành vi công bố**. Đường dẫn khó đoán vẫn bị coi là công khai. Vì vậy quy tắc "chỉ chia sẻ Kho A, không bao giờ chia sẻ Kho B" vẫn giữ nguyên.

---

## 6. Dữ liệu đi những đâu

**1. Sang OpenAI (trợ lý AI).**

- Chỉ gửi **nội dung Kho A**: câu hỏi hiện tại của kịch huống và câu trả lời nhập vai hiện tại. Không gửi nhật ký, không gửi phản tư, không gửi định danh.
- Đây là **chuyển dữ liệu cá nhân xuyên biên giới**, phải có hồ sơ đánh giá tác động chuyển dữ liệu ra nước ngoài.
- Phải bật **Zero Data Retention (ZDR)** trên tài khoản API trước khi có học sinh thật.
- Tài khoản API do **người trưởng thành đứng tên**, có hạn mức chi tiêu cứng.
- Khi không cấu hình API, ứng dụng chạy hoàn toàn ngoại tuyến bằng kịch bản dựng sẵn và **không gửi gì đi đâu cả**.

**2. Ra trang chia sẻ.** Chỉ sản phẩm Kho A. Mặc định tắt. Phải qua duyệt.

**3. Ra các trang bên thứ ba.** Mục Tài nguyên liên kết tới Coursera, Khan Academy, YouTube. Bấm vào là rời khỏi GALS.

**4. Nhật ký máy chủ.** Nội dung do người dùng viết **không được ghi ra nhật ký máy chủ**. Góp ý và báo cáo được lưu vào bảng trong cơ sở dữ liệu.

---

## 7. Trợ lý AI và những điều GALS không làm

Trợ lý AI trong GALS **chỉ hỏi lại để học sinh tự nghĩ**. Nó không chấm điểm, không xếp hạng, không đưa đáp án.

Theo Luật Trí tuệ nhân tạo 2025, GALS **công khai rằng người dùng đang tương tác với hệ thống trí tuệ nhân tạo**. Đây là nghĩa vụ pháp lý.

Ứng dụng có bộ lọc đầu vào chạy trên máy chủ, kết hợp với lớp kiểm duyệt của nhà cung cấp mô hình. Khi học sinh viết những câu cho thấy các em có thể đang gặp chuyện nghiêm trọng, trợ lý dừng lại, không phân tích, và hướng các em tới một người lớn đáng tin cậy cùng **Tổng đài quốc gia bảo vệ trẻ em 111**.

**Cần nói thẳng: đây không phải là tính năng an toàn, và không được xem như một.**

- Bộ lọc **sẽ bỏ sót**, nhất là với cách gõ tắt, sai chính tả hoặc không dấu.
- GALS **không phát hiện được** học sinh đang gặp khủng hoảng, và không tuyên bố làm được điều đó.
- GALS **không tự động báo cho ai cả** — không báo giáo viên, không báo phụ huynh, không báo nhà trường.
- GALS **không phải** dịch vụ tư vấn tâm lý, y tế hay pháp lý.

**Cơ chế xử lý là con người.** Trước khi triển khai, nhà trường và GALS thống nhất bằng văn bản một **quy trình cho giáo viên**: giáo viên làm gì khi thấy học sinh có dấu hiệu cần giúp đỡ. Quy trình đó là "đường dẫn xử lý" mà nhà cung cấp mô hình yêu cầu, và là tài liệu quan trọng nhất cần có nếu có chuyện xảy ra.

---

## 8. Mô hình trách nhiệm

| Vai trò | Ai | Làm gì |
|---|---|---|
| **Bên Kiểm soát dữ liệu cá nhân** | Nhà trường | Quyết định mục đích và cách xử lý. Giữ quan hệ với phụ huynh. Giữ bảng đối chiếu mã ↔ học sinh. |
| **Bên Xử lý dữ liệu cá nhân** | GALS (qua pháp nhân bảo trợ) | Chỉ xử lý theo chỉ dẫn của nhà trường, theo hợp đồng. |
| **Bên triển khai** (Luật TTNT) | Nhà trường | Theo khoản 2 Điều 29 Luật TTNT 2025, bên triển khai chịu trách nhiệm bồi thường, sau đó có thể yêu cầu hoàn trả nếu có thoả thuận. **Điều khoản hoàn trả phải nằm trong hợp đồng với nhà trường.** |
| **Người trưởng thành chịu trách nhiệm** | Giáo viên hoặc cố vấn (≥18 tuổi) | Đứng tên tài khoản API, ký các văn bản thay mặt dự án, là đầu mối xử lý. |

**GALS hiện chưa có pháp nhân.** Không pháp nhân thì không ai ký được hợp đồng với nhà trường và không ai nộp được hồ sơ cho cơ quan chuyên trách. Đây là việc chặn đường quan trọng nhất — xem Mục 10.

---

## 9. Luồng pháp lý — từ lúc học sinh vào tới lúc dữ liệu bị xoá

```
[1] Pháp nhân bảo trợ tồn tại
     └─ Không có bước này thì không có bước nào phía sau.

[2] Nhà trường và GALS ký thoả thuận
     ├─ Xác định: trường = Bên Kiểm soát, GALS = Bên Xử lý
     ├─ Kèm quy trình cho giáo viên (Mục 7)
     └─ Kèm điều khoản hoàn trả theo Luật TTNT (Mục 8)

[3] Nhà trường gửi thư thông báo tới phụ huynh
     ├─ Qua kênh sẵn có của trường
     ├─ Nêu rõ: thu thập gì, không thu thập gì, dữ liệu đi đâu
     ├─ Nêu rõ có xử lý dữ liệu nhạy cảm (Mục 2)
     └─ Ghi nhận sự đồng ý của người đại diện theo pháp luật

[4] Giáo viên phát mã ẩn danh cho học sinh
     ├─ Bảng đối chiếu giữ trên giấy, phía giáo viên
     └─ GALS không bao giờ nhận tên thật

[5] Học sinh dùng ứng dụng
     ├─ Kho A ──► lưu, chia sẻ được, gửi được ra nước ngoài
     └─ Kho B ──► mã hoá, không chia sẻ, không ra nước ngoài

[6] Nghĩa vụ định kỳ trong quá trình vận hành
     ├─ Hồ sơ đánh giá tác động xử lý dữ liệu (DPIA)
     │   └─ nộp A05 trong 60 ngày kể từ khi bắt đầu xử lý
     ├─ Hồ sơ chuyển dữ liệu xuyên biên giới (CTIA)
     │   └─ nộp A05 trong 60 ngày kể từ lần chuyển đầu tiên
     ├─ Cập nhật cả hai hồ sơ định kỳ 06 tháng
     ├─ Cập nhật trong 10 ngày khi có thay đổi tổ chức
     └─ Nếu có sự cố: thông báo A05 trong 72 giờ,
         lưu hồ sơ sự cố tối thiểu 05 năm

[7] Quyền của chủ thể dữ liệu
     ├─ Người đại diện theo pháp luật thực hiện thay cho trẻ em
     ├─ Có địa chỉ liên hệ công khai để gửi yêu cầu
     └─ Truy cập · chỉnh sửa · xoá · rút lại sự đồng ý

[8] Kết thúc
     ├─ Kho B tự xoá cuối học kỳ
     ├─ Xoá theo yêu cầu là xoá thật, có ghi nhận sự kiện xoá
     └─ Nếu dự án dừng: xoá dữ liệu, thông báo nhà trường,
         theo kế hoạch dừng hoạt động đã viết sẵn
```

---

## 10. Việc cần làm — theo thứ tự

### Giai đoạn 0 — Trước mọi thứ khác

- [ ] **Tìm pháp nhân bảo trợ.** Trường của chính nhóm, vườn ươm của trường đại học, tổ chức đoàn thể, hoặc một tổ chức phi lợi nhuận sẵn có. Đăng ký pháp nhân riêng mất nhiều tháng; bảo trợ mất vài tuần.
- [ ] **Tìm người trưởng thành chịu trách nhiệm.** Ưu tiên giáo viên tại trường đối tác — cùng một người đóng cả ba vai ở Mục 8.
- [ ] **Kiểm tra lịch sử git xem đã từng commit khoá API chưa.** Nếu có, thu hồi khoá.

### Giai đoạn 1 — Trước khi có học sinh thật

- [ ] **Sửa lỗi dùng chung tài khoản.** Hiện mọi người đăng nhập đều rơi vào một trong ba tài khoản mẫu; hai người cùng nhập mã lớp là cùng một tài khoản và đọc được bài của nhau. **Đây là việc gấp nhất về mặt kỹ thuật.**
- [ ] Bỏ trường **tên** và **email** khỏi bảng người dùng.
- [ ] **Tắt tạm:** Ý tưởng tự do, lưu trữ Cấp độ 4, chia sẻ công khai, ô dán liên kết ảnh.
- [ ] **Đăng nhập thật, có mật khẩu.**
- [ ] **Bảng ghi nhận sự đồng ý:** mã chủ thể, loại đồng ý (`school_mediated` / `guardian` / `self`), cách kiểm chứng, thời điểm, phiên bản chính sách, phạm vi, trạng thái rút lại.
- [ ] Cơ sở dữ liệu lâu dài (PostgreSQL), chỉ gieo dữ liệu khi trống, có sao lưu và diễn tập phục hồi.
- [ ] Chuyển hạ tầng về nhà cung cấp **đặt tại Việt Nam**.
- [ ] Viết **Điều khoản sử dụng** và **Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ để học sinh lớp 10 đọc hiểu, có nêu rõ phần dữ liệu nhạy cảm và phần công khai về AI.
- [ ] Viết **quy trình cho giáo viên** và thống nhất với nhà trường.
- [ ] Viết **kế hoạch dừng hoạt động**: dữ liệu bị xoá ra sao, ai thông báo cho nhà trường.
- [ ] Có **địa chỉ liên hệ công khai** để nhận yêu cầu từ phụ huynh, và người chịu trách nhiệm trả lời.

### Giai đoạn 2 — Trước khi bật AI với học sinh thật

- [ ] Bật **Zero Data Retention** trên tài khoản OpenAI.
- [ ] Thêm **lớp kiểm duyệt của nhà cung cấp**, chồng lên bộ lọc cụm từ hiện có.
- [ ] **Chỉ gửi nội dung Kho A.** Kiểm thử tự động để đảm bảo Kho B không bao giờ lọt vào lời nhắc.
- [ ] Ghi **nhật ký siêu dữ liệu** của các lần chuyển dữ liệu, phục vụ hồ sơ.
- [ ] Lập và nộp **hồ sơ đánh giá tác động xử lý dữ liệu** và **hồ sơ chuyển dữ liệu xuyên biên giới**.
- [ ] Cử **nhân sự phụ trách bảo vệ dữ liệu cá nhân** — quyền hoãn 5 năm không áp dụng khi có dữ liệu nhạy cảm.
- [ ] Xây dựng **quy trình thông báo sự cố trong 72 giờ**.

### Giai đoạn 3 — Trước khi mở đăng ký cá nhân

- [ ] **Đăng ký do người giám hộ khởi tạo** với người dùng dưới 16 tuổi.
- [ ] Xác định lại phân loại theo Nghị định 147 khi tiến gần ngưỡng **10.000 lượt truy cập/tháng** hoặc **1.000 người dùng thường xuyên**.
- [ ] **Xin giấy phép** nếu vượt ngưỡng.
- [ ] Rà soát lại nghĩa vụ **lưu trữ dữ liệu và nhật ký hệ thống**.

---

## 11. Trách nhiệm pháp lý

Phần mềm này được cung cấp nguyên trạng, **không kèm bảo đảm dưới bất kỳ hình thức nào**, cho mục đích trình diễn và giáo dục.

Nhóm phát triển không chịu trách nhiệm cho: mất mát dữ liệu, gián đoạn dịch vụ, nội dung do mô hình AI sinh ra, nội dung do người dùng nhập vào, hay hậu quả của việc dùng bản mẫu này với dữ liệu thật của người thật.

Nếu bạn triển khai GALS cho học sinh có thật, **bạn hoặc nhà trường của bạn là bên chịu trách nhiệm về dữ liệu đó**.

---

## Đây không phải tư vấn pháp lý

Tài liệu này do nhóm làm sản phẩm viết. Nó dùng để **biết cần hỏi gì** trước khi hỏi luật sư.

Trước khi triển khai thật, hãy làm việc với **luật sư Việt Nam** và với **nhà trường**.
