# Tuyên bố pháp lý và dữ liệu

**Đọc trang này trước khi cho bất kỳ học sinh có thật nào dùng GALS.**

*Rà soát gần nhất: 10/08/2026, đối chiếu với khung pháp lý có hiệu lực năm 2026.*

---

## Tóm tắt trong mười giây

| | |
|---|---|
| GALS hiện là gì | Một **bản mẫu (prototype)** làm cho cuộc thi. Không phải sản phẩm thương mại. |
| Dữ liệu gieo sẵn | **Toàn bộ là dữ liệu giả định.** Không có học sinh thật nào trong đó. |
| Bài bạn tự viết | **Có ghi lên máy chủ**, nhưng bị xoá sạch mỗi lần máy chủ khởi động lại. |
| Bài của bạn có riêng tư không | **Không.** Chưa có tài khoản riêng cho từng người — xem mục ngay dưới đây. |
| Được nhập thông tin thật vào không | **Không.** Đừng nhập tên thật, trường thật, số điện thoại, email cá nhân. |
| Có phải công cụ hỗ trợ tâm lý không | **Không.** Xem mục [Trợ lý AI](#trợ-lý-ai-và-những-điều-gals-không-làm). |
| Nhật ký tư duy thuộc loại dữ liệu gì | **Dữ liệu cá nhân nhạy cảm.** Đây là kết luận quan trọng nhất của cả tài liệu — xem [Phần 1](#1-nhật-ký-tư-duy-là-dữ-liệu-cá-nhân-nhạy-cảm). |
| Trợ lý AI có dùng được với học sinh thật không | **Chưa.** Điều khoản của nhà cung cấp đang chặn đúng ca sử dụng này — xem [Phần 4](#4-điều-khoản-của-nhà-cung-cấp-ai-đang-là-một-nút-chặn). |

---

## Chưa có tài khoản riêng — mọi người dùng chung tài khoản

Đây là điều quan trọng nhất trong phần mô tả bản mẫu, và nó **không phải lỗi mới phát sinh** mà là giới hạn có sẵn.

Ứng dụng hiện có đúng **ba tài khoản**, và mọi đường vào đều rơi vào một trong ba:

| Bạn làm gì | Bạn thực sự đăng nhập vào đâu |
|---|---|
| Bấm nút **Demo nhanh** | Một trong ba tài khoản mẫu, tuỳ nút bạn bấm |
| Điền email và mật khẩu ở trang **Đăng nhập** | Tài khoản học sinh mẫu — **email và mật khẩu bạn gõ bị bỏ qua hoàn toàn** |
| **Đăng ký** rồi chọn avatar, *có* nhập mã lớp | Tài khoản học sinh mẫu đang học lớp 11A2 |
| **Đăng ký** rồi chọn avatar, *không* nhập mã lớp | Tài khoản học sinh mẫu độc lập |

Hệ quả, nói thẳng:

- **Hai người cùng nhập mã lớp là cùng một tài khoản.** Người này đọc được nhật ký, hồ sơ và câu trả lời của người kia, và ngược lại.
- **Không có gì là riêng tư giữa những người đang dùng thử.** Lời hứa *"không nhập mã lớp thì giáo viên không xem được"* là **ý định thiết kế**, chưa phải thứ bản mẫu làm được.
- **Đổi avatar là đổi cho tất cả**, vì cùng một bản ghi người dùng.
- Đăng ký **không tạo ra tài khoản mới nào cả**.

**Vì vậy: đừng dùng bản mẫu này để chạy thử với học sinh thật.** Nếu bạn đang cho người khác dùng thử, hãy nói rõ với họ rằng mọi thứ họ viết ra người khác đều đọc được, và đừng để ai viết chuyện cá nhân vào đó.

---

## Tuyên bố về bản mẫu

GALS được xây dựng để trình bày một ý tưởng giáo dục: học sinh THPT hiểu nghề nghiệp bằng cách **nhập vai và tự xử lý một tình huống có thật của nghề**, thay vì đọc lý thuyết.

Bản đang chạy là bản trình diễn. Điều đó có nghĩa là:

- Mọi tài khoản, lớp học, nhật ký, huy hiệu trong ứng dụng đều là **nội dung dựng sẵn**.
- Đăng nhập **không có mật khẩu**. Ai có đường dẫn cũng vào được tài khoản demo.
- **Không có bản sao lưu.** Không có cam kết về thời gian hoạt động.
- Giao diện, nội dung và cách hoạt động **có thể thay đổi bất cứ lúc nào**.

Đừng dùng bản này để lưu bất cứ thứ gì bạn cần giữ lại.

---

## Dữ liệu được lưu như thế nào

**Hiện tại — bản mẫu**

Mọi thứ bạn viết — câu trả lời khi nhập vai, nhật ký, mục hồ sơ, tin nhắn trong Ý tưởng tự do — đều **được gửi lên máy chủ và ghi vào cơ sở dữ liệu ở đó**. Không có gì chỉ nằm lại trên máy của bạn. Điều này là cần thiết để giáo viên đọc được nhật ký, nhưng cũng có nghĩa là **máy khác vẫn thấy được bài của bạn**, và vì chưa có tài khoản riêng nên **người khác cũng thấy**.

Ứng dụng dùng SQLite trên đĩa tạm của máy chủ. Mỗi lần máy chủ khởi động lại, toàn bộ bảng dữ liệu bị xoá và gieo lại từ đầu bằng dữ liệu mẫu. Máy chủ miễn phí còn tự ngủ khi không có ai dùng, nên **bài viết của bạn thường không sống qua một đêm**.

Thứ duy nhất lưu trên máy bạn là **bản nháp đang gõ dở** trong ô trả lời, giữ tạm ở `sessionStorage` của trình duyệt, cùng **cài đặt hiển thị** (sáng/tối, tương phản cao, giảm chuyển động) giữ ở `localStorage`. Cả hai đều không rời khỏi máy bạn.

Điều này là cố ý cho một bản trình diễn: mỗi người vào đều thấy ứng dụng sạch sẽ và đầy đủ nội dung. Nhưng nó cũng có nghĩa là **xoá dữ liệu ở đây không phải là quyền được xoá theo luật** — đó chỉ là mất dữ liệu.

**Những gì mô hình dữ liệu hiện có thể chứa**

Bảng người dùng có trường **tên** và **email**. Nhật ký chứa **văn bản do học sinh tự viết**. Đây là thông tin cá nhân theo đúng nghĩa pháp lý nếu có người thật nhập vào. Bản mẫu chỉ chứa dữ liệu giả — nhưng cấu trúc thì đã sẵn sàng chứa dữ liệu thật, và đó chính là rủi ro.

---

## Dữ liệu đi những đâu

Ba đường ra, cần biết rõ:

**1. Sang máy chủ của Google (trợ lý AI).** Khi bật trợ lý AI, câu trả lời của học sinh được gửi tới Gemini API để sinh câu hỏi phản hồi. Đây là **chuyển dữ liệu cá nhân ra nước ngoài**, và với dữ liệu nhạy cảm thì nó kéo theo một hồ sơ phải nộp — xem [Phần 3](#3-hai-hồ-sơ-phải-nộp-cho-a05). Ứng dụng cố tình gửi ít nhất có thể: chỉ câu hỏi hiện tại và câu trả lời hiện tại, không gửi cả cuốn nhật ký. Khi không có khoá API, ứng dụng chạy hoàn toàn ngoại tuyến bằng kịch bản dựng sẵn và **không gửi gì đi đâu cả**.

**2. Ra trang chia sẻ công khai.** Học sinh có thể bấm chia sẻ một mục hồ sơ. Mục đó nhận một đường dẫn khó đoán và **ai có đường dẫn cũng xem được, không cần đăng nhập**.

> **Đường dẫn khó đoán không phải là riêng tư về mặt pháp lý.** Chia sẻ như vậy là **công bố**. Với trẻ em từ đủ 7 tuổi trở lên, việc công bố thông tin đời sống riêng tư cần **đồng thời sự đồng ý của chính em và của người đại diện theo pháp luật** — không phải một cú bấm nút của học sinh.

**3. Ra các trang bên thứ ba.** Mục Tài nguyên liên kết tới Coursera, Khan Academy, YouTube. Bấm vào là rời khỏi GALS và chịu chính sách của các trang đó. Đây là **liên kết ra ngoài**, không phải nhúng nội dung; nếu sau này nhúng thì phải theo điều khoản của từng nền tảng (YouTube bắt buộc dùng trình phát chính thức) và **tuyệt đối không sao chép nội dung của họ vào `resources.json`**.

**4. Máy chủ đặt ở nước ngoài.** Bản đang chạy deploy trên Render, tức là **dữ liệu nằm ngoài lãnh thổ Việt Nam ngay cả khi không bật AI**. Xem nghĩa vụ lưu trữ trong nước ở [Phần 2](#2-khung-pháp-lý-đang-có-hiệu-lực-2026).

Liên kết ảnh và video do học sinh tự dán vào chỉ nhận `http://` và `https://`. Các dạng khác — đáng kể nhất là `javascript:` — bị chặn, vì mục hồ sơ có thể được chia sẻ công khai và một đường dẫn như vậy sẽ chạy mã trong trình duyệt của người vào xem. **Chặn `javascript:` là cần nhưng chưa đủ**: một đường dẫn ảnh tuỳ ý hiển thị trên trang công khai vẫn là vấn đề bản quyền, kiểm duyệt nội dung và an toàn trẻ em cùng lúc. Phải chuyển sang danh sách nguồn cho phép hoặc tự lưu ảnh.

---

## Ứng dụng đếm những gì

Chỉ **con số tổng, không kèm nội dung, không kèm người**.

Khi bộ lọc chặn một câu, ứng dụng cộng 1 vào bộ đếm theo nhóm — ví dụ `screen.crisis = 12`. Nó **không lưu câu đó**, không lưu ai viết, không lưu lớp nào, không lưu thời điểm cụ thể. Bộ đếm nằm trong bộ nhớ tiến trình và mất khi khởi động lại.

Lý do giữ lại phần này thay vì bỏ hẳn: nếu không đếm gì cả thì **không có cách nào biết bộ lọc có đang chạy hay không**. Im lặng có thể là "không em nào cần tới", mà cũng có thể là "bộ lọc bỏ sót hết". Một con số phân biệt được hai điều đó, và con số thì không nhận dạng được ai.

Bộ đếm này **không hiển thị cho giáo viên**, và đó là chủ ý: một con số kiểu *"lớp bạn có 3 lượt"* sẽ tạo ra lo lắng mà không có cách nào hành động, lại vừa đủ hẹp để đoán ra em nào.

**Nút báo cáo câu trả lời và nút gửi góp ý** thì có lưu nội dung: câu trả lời của trợ lý bị báo cáo, lý do chọn từ danh sách, và phần ghi chú nếu học sinh viết. **Không lưu người gửi.** Ghi chú cũng đi qua chính bộ lọc đầu vào, và mỗi phiên chỉ gửi được 5 lần mỗi giờ để tránh bị lạm dụng.

Nội dung đó đi tới hai chỗ, **và không đi đâu khác** — không email, không dịch vụ bên ngoài:

1. **Một dòng trong bảng `reports`** của cơ sở dữ liệu bản mẫu. Bảng này bị xoá mỗi lần máy chủ khởi động lại, và hiện **chưa có màn hình nào đọc được nó**.
2. **Một dòng trong nhật ký máy chủ**, để người vận hành đọc được thật. Đây là lý do form góp ý có ghi rõ: đừng viết thông tin cá nhân vào đó.

Nói thẳng: ở bản mẫu, góp ý **không chắc còn lại tới hôm sau**. Câu xác nhận sau khi gửi cũng nói đúng như vậy chứ không hứa suông.

---

## Trợ lý AI và những điều GALS không làm

Trợ lý AI trong GALS **chỉ hỏi lại để học sinh tự nghĩ**. Nó không chấm điểm, không xếp hạng, không đưa đáp án.

Ứng dụng có một bộ lọc đầu vào chạy trên máy chủ. Khi học sinh viết những câu cho thấy các em có thể đang gặp chuyện nghiêm trọng, trợ lý **dừng lại, không phân tích, và hướng các em tới một người lớn đáng tin cậy cùng Tổng đài quốc gia bảo vệ trẻ em 111**.

**Cần nói thẳng: đây không phải là tính năng an toàn, và không được xem như một.**

- Bộ lọc dựa trên việc so khớp cụm từ. Nó **sẽ bỏ sót**, nhất là với cách gõ tắt, sai chính tả hoặc không dấu.
- GALS **không phát hiện được** học sinh đang gặp khủng hoảng, và không tuyên bố làm được điều đó.
- GALS **không báo cho ai cả** — không báo giáo viên, không báo phụ huynh, không báo nhà trường.
- GALS **không phải** dịch vụ tư vấn tâm lý, y tế hay pháp lý.

**Người lớn trong phòng học mới là cơ chế bảo vệ, không phải phần mềm.**

> Nguyên văn đoạn này phải được giữ y hệt trong hợp đồng với nhà trường và trong Điều khoản sử dụng. Đó là bằng chứng thiện chí rõ ràng nhất nếu có chuyện xảy ra.

---

# Khung pháp lý và nghĩa vụ tuân thủ

Phần dưới đây dựa trên bản rà soát ngày **10/08/2026**. Nó là **bản đồ để hỏi luật sư**, không phải kết luận pháp lý. Mọi trích dẫn cần đối chiếu lại với văn bản gốc tại `vanban.chinhphu.vn` hoặc `thuvienphapluat.vn` trước khi dựa vào.

Lộ trình chia hai giai đoạn, và các nghĩa vụ bên dưới gắn nhãn theo giai đoạn:

- **[TĐ]** — Giai đoạn 1: **thí điểm tại trường**, nhà trường là bên kiểm soát dữ liệu.
- **[TT]** — Giai đoạn 2: **học sinh tự đăng ký trực tiếp**.
- **[TĐ/TT]** — cả hai giai đoạn.

---

## 1. Nhật ký tư duy là dữ liệu cá nhân nhạy cảm

Đây là kết luận quyết định toàn bộ phần còn lại.

**Nghị định 356/2025/NĐ-CP Điều 4** liệt kê **"thông tin về đời sống riêng tư, bí mật cá nhân, bí mật gia đình"** và tình trạng sức khoẻ vào nhóm **dữ liệu cá nhân nhạy cảm**. Nhật ký tư duy của GALS, theo đúng thiết kế, chính là loại nội dung đó — cả mục đích sư phạm của nó là để học sinh viết ra cách các em nghĩ và cảm nhận.

Đây không phải một ranh giới mờ. Và nó là thứ biến GALS từ *"một dự án edtech nhỏ với nghĩa vụ nhẹ"* thành *"một tổ chức phải gánh gần như toàn bộ nghĩa vụ tuân thủ ngay từ ngày đầu"*.

Hệ quả trực tiếp, và là **câu hỏi đầu tiên phải đặt cho luật sư**: cơ chế **hoãn nghĩa vụ lập hồ sơ đánh giá tác động và bổ nhiệm nhân sự bảo vệ dữ liệu trong 5 năm** dành cho tổ chức nhỏ và doanh nghiệp khởi nghiệp **không áp dụng cho bên xử lý dữ liệu nhạy cảm**. Hãy mặc định là **GALS không được miễn**, rồi lên kế hoạch theo hướng đó.

---

## 2. Khung pháp lý đang có hiệu lực (2026)

| Văn bản | Hiệu lực | Vì sao liên quan tới GALS |
|---|---|---|
| **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** | **01/01/2026** | Đạo luật gốc hiện hành. |
| **Nghị định 356/2025/NĐ-CP** (ban hành 31/12/2025) | **01/01/2026**; **bãi bỏ Nghị định 13/2023** | Danh mục dữ liệu nhạy cảm, cơ chế đồng ý, biểu mẫu hồ sơ đánh giá tác động và thời hạn nộp. |
| **Luật Trí tuệ nhân tạo 134/2025/QH15** | **01/03/2026** | Phân tầng rủi ro, nghĩa vụ công khai đang tương tác với AI, trách nhiệm của bên triển khai. **Giáo dục nằm trong nhóm lĩnh vực được quản lý theo rủi ro.** |
| **Luật An ninh mạng 116/2025/QH15** | **01/07/2026** | Hợp nhất Luật An toàn thông tin mạng 2015 và Luật An ninh mạng 2018. Lưu trữ dữ liệu trong nước, lưu nhật ký hệ thống, thêm quy định bảo vệ trẻ em. |
| **Nghị định 147/2024/NĐ-CP** | 25/12/2024 | Tài khoản của người dưới 16 tuổi, ngưỡng cấp phép mạng xã hội, xác thực người dùng, thời hạn lưu trữ. |
| **Luật Trẻ em 2016 + Nghị định 56/2017/NĐ-CP** | Còn hiệu lực | "Trẻ em" là **người dưới 16 tuổi**, trong khi học sinh THPT ở khoảng 15–18 tuổi. **Một phần người dùng thuộc phạm vi luật này và ứng dụng không phân biệt được.** |

> **Nghị định 13/2023/NĐ-CP đã bị bãi bỏ.** Mọi tài liệu nội bộ còn trích dẫn nó phải được cập nhật sang Luật 91/2025 và Nghị định 356/2025.

---

## 3. Hai hồ sơ phải nộp cho A05

Đây là phần dễ bị hiểu nhầm là "viết tài liệu nội bộ". Không phải. Đây là **hồ sơ nộp cho cơ quan nhà nước, có biểu mẫu và có thời hạn.**

| Hồ sơ | Khi nào phải có | Thời hạn nộp | Ghi chú |
|---|---|---|---|
| **Đánh giá tác động xử lý dữ liệu cá nhân** (ĐGTĐ) | **Từ thời điểm bắt đầu xử lý** | Nộp **một bản chính cho A05 (Bộ Công an) trong 60 ngày** | Kết quả thẩm định trả về trong khoảng 15 ngày. Phải luôn sẵn sàng cho thanh tra. |
| **Đánh giá tác động chuyển dữ liệu ra nước ngoài** (CTIA) | Từ lần chuyển đầu tiên | **60 ngày kể từ lần chuyển đầu tiên**, Mẫu 01a/01b | Áp dụng cho **cả** lời gọi Gemini **lẫn** việc dùng nền tảng đặt ở nước ngoài để xử lý dữ liệu thu thập tại Việt Nam — nghĩa là **cả máy chủ hosting**. |

**Cập nhật định kỳ:** làm mới cả hai hồ sơ **mỗi 6 tháng**, và **trong 10 ngày** khi tổ chức lại, giải thể, hoặc thay đổi bên kiểm soát / bên xử lý / bên thứ ba. Một nhóm học sinh có nhân sự thay hằng năm cần đưa việc này vào lịch cố định.

**Thông báo vi phạm dữ liệu:** **trong 72 giờ** cho A05 theo mẫu quy định, và **lưu hồ sơ sự cố tối thiểu 5 năm**. Hiện GALS **chưa có quy trình sự cố nào cả**.

**Chế tài:** tới **5% doanh thu năm trước** cho vi phạm về chuyển dữ liệu ra nước ngoài; tới **3 tỷ đồng** cho các vi phạm khác, cộng bồi thường dân sự và khả năng truy cứu hình sự. **Đừng mặc định "không có doanh thu thì không bị phạt"** — cách áp dụng cho tổ chức phi lợi nhuận không doanh thu là một câu hỏi mở thật sự, không phải một vùng an toàn.

---

## 4. Điều khoản của nhà cung cấp AI đang là một nút chặn

**Đây là vấn đề chặn đường, không phải việc cần rà soát.**

| Vấn đề | Nguồn | Hệ quả |
|---|---|---|
| Điều khoản bổ sung của Gemini API yêu cầu người phát triển **từ 18 tuổi trở lên** và cam kết **không dùng dịch vụ trong ứng dụng "hướng tới hoặc có khả năng được người dưới 18 tuổi truy cập"** | Gemini API Additional Terms of Service | GALS hướng thẳng tới học sinh 16–18 tuổi ở trường THPT Việt Nam, trong đó một phần dưới 16 tuổi. **[TĐ/TT]** |
| Ở gói miễn phí, **nội dung gửi lên được dùng để cải thiện sản phẩm của Google** | Gemini API Additional Terms | Chỉ gói trả phí (qua dự án Cloud có bật thanh toán) mới có cam kết không huấn luyện trên dữ liệu và mới có phụ lục xử lý dữ liệu ở vai bên xử lý. **Chạy thí điểm với học sinh thật trên gói miễn phí là không bảo vệ được.** **[TĐ]** |

**Các phương án, xếp theo mức tốn kém tăng dần:**

- **(a) Thí điểm với trợ lý AI tắt hẳn.** Chế độ ngoại tuyến dựng sẵn đã có sẵn và đầy đủ. Đây là phương án duy nhất **không cần đàm phán với nhà cung cấp, không cần hồ sơ CTIA, và không chuyển một byte nào ra nước ngoài**. Nó cũng đúng với mục tiêu của một lần thí điểm trung thực: điều cần kiểm chứng là kịch huống nhập vai có hiệu quả hay không, chứ không phải mô hình ngôn ngữ có giỏi hay không.
- **(b) Chuyển sang hợp đồng doanh nghiệp** (điều khoản Google Cloud / Vertex thay cho Additional Terms dành cho lập trình viên) và **lấy câu trả lời bằng văn bản từ nhà cung cấp** về vấn đề độ tuổi. Đừng suy ra từ trang giới thiệu: bề mặt Google Cloud cũng có thông báo 18+.
- **(c) Đổi nhà cung cấp** sang bên có điều khoản nói rõ về người chưa thành niên trong triển khai giáo dục theo hợp đồng với nhà trường.
- **(d) AI qua trung gian giáo viên.** Giáo viên là người gọi API; học sinh không bao giờ gửi chữ tới mô hình. Vụng về về mặt sư phạm, sạch về mặt pháp lý.
- **(e) Mô hình đặt tại Việt Nam.** Giải quyết cùng lúc bài toán lưu trữ trong nước và chuyển dữ liệu xuyên biên giới. Tốn công kỹ thuật nhất.

**Khuyến nghị: chọn (a) cho giai đoạn thí điểm, và chốt giữa (b), (c), (e) trước khi mở đăng ký trực tiếp.** Tắt AI cho lần thí điểm đầu mất ít hơn ta tưởng, và nó gỡ bốn nhánh công việc tuân thủ ra khỏi đường găng.

---

## 5. Đăng ký sự đồng ý

| Nghĩa vụ | Nguồn | Phải làm gì |
|---|---|---|
| **Nói rõ đây là dữ liệu nhạy cảm khi xin đồng ý** | Nghị định 356/2025 | Một thông báo quyền riêng tư chung chung là không đủ. Luồng đồng ý phải nói bằng ngôn ngữ một em 16 tuổi hiểu được rằng nhóm dữ liệu này là nhạy cảm. **[TĐ/TT]** |
| **Đồng ý phải kiểm chứng được, có dấu thời gian, gắn với nội dung cụ thể** | Luật 91/2025 Đ.8–9; NĐ 356 Đ.6 | Ghi lại đã đồng ý điều gì và vào lúc nào. **Ô tích sẵn và mặc định đồng ý bị cấm.** Luồng đăng ký chọn avatar hiện tại **không ghi lại gì cả**. **[TĐ/TT]** |
| **Người dưới 16 tuổi: người đại diện thực hiện quyền** | Luật 91/2025; Luật Trẻ em 2016 | **[TĐ/TT]** |
| **Công bố đời sống riêng tư của trẻ em cần hai chữ ký** | Luật 91/2025, phần về trẻ em | Với trẻ **từ đủ 7 tuổi**, việc công bố cần **đồng ý của cả em và người đại diện theo pháp luật**. Tính năng chia sẻ công khai của GALS **là công bố**, và hiện chỉ là một cú bấm của học sinh. **[TĐ/TT]** |
| **Quyền truy cập, chỉnh sửa, xoá, rút lại đồng ý** | Luật 91/2025 Ch.II | Xoá phải là một chức năng có thật. "Cơ sở dữ liệu bị xoá khi khởi động lại" là **mất dữ liệu**, không phải quyền được xoá. **[TĐ/TT]** |

---

## 6. Lưu trữ trong nước và nhật ký hệ thống

| Nghĩa vụ | Nguồn | Phải làm gì |
|---|---|---|
| **Lưu dữ liệu người dùng Việt Nam tại Việt Nam** | Luật An ninh mạng 116/2025; NĐ 53/2022 | Bản deploy trên Render đang đặt ở nước ngoài. **Xác định GALS nằm bên nào của ngưỡng áp dụng trước khi thí điểm**, và tính trước chi phí một nhà cung cấp trong nước. **[TĐ/TT]** |
| **Lưu nhật ký hệ thống** | Luật An ninh mạng; NĐ 53/2022 | Tối thiểu 12 tháng với nhật ký phục vụ điều tra vi phạm an ninh mạng. **[TĐ/TT]** |
| **Cân đối nghĩa vụ lưu trữ với nguyên tắc tối thiểu hoá dữ liệu** | Xuyên suốt | Hai nghĩa vụ này kéo ngược chiều nhau. Phải **quyết định lịch lưu trữ một cách có chủ ý và viết nó ra**, thay vì để mặc định. **[TĐ/TT]** |

---

## 7. Nghĩa vụ theo Luật Trí tuệ nhân tạo

| Nghĩa vụ | Nguồn | Phải làm gì |
|---|---|---|
| **Công khai rằng người dùng đang tương tác với hệ thống AI** | Luật AI 134/2025 Đ.11 | Giao diện GALS phần lớn đã làm điều này rồi. Cần biến nó thành **một biện pháp được ghi nhận rõ ràng**, không phải một thói quen thiết kế. **[TĐ/TT]** |
| **Phân loại mức độ rủi ro** | Luật AI Đ.9 | Ba mức (cao / trung bình / thấp), xét theo tác động tới quyền con người, an ninh, trật tự công cộng. **Giáo dục nằm trong nhóm lĩnh vực quản lý theo rủi ro.** Hãy giả định trung bình đến cao, **tự lập đánh giá và sẵn sàng bảo vệ nó**. **[TĐ/TT]** |
| **Thời hạn chuyển tiếp** | Luật AI Đ.35 | Hệ thống đã vận hành trước 01/03/2026 có **18 tháng** để tuân thủ nếu thuộc y tế, **giáo dục** hoặc tài chính; 12 tháng với các lĩnh vực khác. **Hệ thống triển khai lần đầu sau 01/03/2026 không có thời gian đệm.** GALS nằm bên nào phụ thuộc vào việc tính "đã vận hành" từ lúc nào — một bản mẫu chạy trên hosting miễn phí là điều còn tranh luận được. Hỏi luật sư. **[TĐ/TT]** |
| **Bên triển khai chịu trách nhiệm bồi thường** | Luật AI Đ.29(2) | Khi hệ thống rủi ro cao được vận hành đúng mà vẫn phát sinh thiệt hại, **bên triển khai** bồi thường, sau đó có thể yêu cầu bên cung cấp / bên phát triển hoàn lại **nếu các bên đã thoả thuận**. Trong mô hình nhà trường là bên kiểm soát, **nhà trường nhiều khả năng là bên triển khai** — nên **điều khoản hoàn lại phải nằm trong hợp đồng với nhà trường, nếu không nhà trường gánh một mình.** Bộ phận pháp chế của trường sẽ nhìn ra điều này. **[TĐ]** |
| **Hành vi bị cấm** | Luật AI Đ.7 | Bao gồm thao túng nhận thức hoặc hành vi con người một cách có hệ thống gây hậu quả nghiêm trọng. Thiết kế "AI chỉ hỏi, không bao giờ trả lời thay" của GALS đứng vững ở đây — nhưng **lý do thiết kế phải được viết thành hồ sơ tuân thủ**, không chỉ nằm trong README. **[TĐ/TT]** |

---

## 8. GALS có phải là mạng xã hội không

Câu hỏi phân loại này quyết định bốn nghĩa vụ bên dưới nó.

| Nghĩa vụ | Nguồn | Phải làm gì |
|---|---|---|
| **Xác định GALS có phải "mạng xã hội"** | NĐ 147/2024 Đ.23–27 | Mạng xã hội là hệ thống cho người dùng tạo tài khoản, lập trang cá nhân, đăng nội dung, chia sẻ và tương tác. Bảng tin lớp, mục hồ sơ chia sẻ được và đường dẫn công khai **đẩy GALS về phía định nghĩa đó**; còn một công cụ đóng, chỉ trong phạm vi lớp, thì gần với **trang thông tin điện tử nội bộ** và không cần giấy phép. **[TĐ/TT]** |
| **Ngưỡng cấp phép** | NĐ 147/2024 | Mạng xã hội trong nước có **từ 10.000 lượt truy cập/tháng hoặc trên 1.000 người dùng thường xuyên hằng tháng** phải có giấy phép; dưới ngưỡng thì theo chế độ thông báo nhẹ hơn. **Thí điểm vài lớp nằm dưới ngưỡng. Triển khai toàn quốc thì không.** Nộp hồ sơ **trước** khi vượt ngưỡng, không phải sau. **[TT]** |
| **Tài khoản người dưới 16 tuổi phải do cha mẹ hoặc người giám hộ đăng ký và giám sát** | NĐ 147/2024 Đ.23(2)(đ) | Nếu thuộc diện mạng xã hội, đây là **yêu cầu kiến trúc bắt buộc**, không phải một dòng chính sách. **[TĐ/TT]** |
| **Tài khoản phải được xác thực** | NĐ 147/2024 | Xác thực bằng số điện thoại di động Việt Nam (hoặc số định danh cá nhân); chỉ tài khoản đã xác thực mới được đăng và chia sẻ. **Điều này xung đột trực diện với thiết kế mã ẩn danh mà tài liệu này khuyến nghị.** Không thể vừa là nền tảng dùng bí danh không xác thực, vừa là mạng xã hội có giấy phép. **Đây là một đánh đổi thiết kế có hệ quả pháp lý, và nên chốt ngay bây giờ.** **[TT]** |
| **Lưu thông tin tài khoản, thời điểm đăng nhập/đăng xuất, địa chỉ IP ≥ 2 năm** | NĐ 147/2024 | Lại mâu thuẫn với nguyên tắc tối thiểu hoá. **[TT]** |

---

## 9. Nội dung, sở hữu trí tuệ và phía nhà trường

| Vấn đề | Phải làm gì |
|---|---|
| **Kho mã chưa có file LICENSE** | Không có giấy phép thì mặc định là **giữ toàn bộ quyền**, dù README mời mọi người clone về chạy. Người đóng góp lẫn nhà trường đều không có cơ sở rõ ràng. Chọn giấy phép — và **chọn riêng cho mã nguồn và cho nội dung kịch huống**, vì hai thứ này có thể cần điều khoản khác nhau. |
| **Học sinh giữ quyền tác giả với những gì các em viết** | Nhật ký và mục hồ sơ là tác phẩm của học sinh. Việc lưu trữ, hiển thị và chia sẻ cần một phạm vi cho phép ghi trong Điều khoản sử dụng, và với người chưa thành niên thì do người giám hộ cùng đồng ý. **Đừng đòi rộng hơn mức cần**: một phạm vi hẹp, chỉ đủ để vận hành dịch vụ, dễ được nhà trường chấp nhận hơn nhiều. |
| **Ô dán ảnh và liên kết tự do** | Vừa là vấn đề bản quyền, vừa là kiểm duyệt nội dung, vừa là an toàn trẻ em. Chuyển sang danh sách nguồn cho phép hoặc tự lưu ảnh trên máy chủ. |
| **Phê duyệt phía ngành giáo dục** | Không có một cửa phê duyệt quốc gia duy nhất cho một công cụ bổ trợ trên lớp, nhưng nhà trường và Sở GD&ĐT sẽ có quy trình riêng. Hướng đi chung của ngành (học bạ số, cơ sở dữ liệu ngành, kết nối VNeID) khiến các trường ngày càng thận trọng với việc ai được chạm vào dữ liệu học sinh. **Hãy tính một chu kỳ phê duyệt phía trường tính bằng tháng.** |
| **Pháp nhân** | **Hồ sơ ĐGTĐ và CTIA do một pháp nhân nộp, và hợp đồng với nhà trường do một pháp nhân ký.** Một nhóm học sinh chưa đăng ký **không thể** là bên kiểm soát hay bên xử lý dữ liệu. Dù chọn hình thức nào — hội, tổ chức khoa học và công nghệ, quỹ xã hội, hay doanh nghiệp xã hội — **nó phải tồn tại trước khi thí điểm, không phải sau.** Thời gian đăng ký sẽ quyết định ngày thí điểm. |

---

## Trách nhiệm pháp lý

Phần mềm này được cung cấp nguyên trạng, **không kèm bảo đảm dưới bất kỳ hình thức nào**, cho mục đích trình diễn và giáo dục.

Nhóm phát triển không chịu trách nhiệm cho: mất mát dữ liệu, gián đoạn dịch vụ, nội dung do mô hình AI sinh ra, nội dung do người dùng nhập vào, hay hậu quả của việc dùng bản mẫu này với dữ liệu thật của người thật.

Nếu bạn triển khai GALS cho học sinh có thật, **bạn hoặc nhà trường của bạn là bên chịu trách nhiệm về dữ liệu đó**, không phải bản mẫu này.

---

## Cần làm gì trước khi dùng với học sinh thật

Đây là ranh giới giữa *bản mẫu* và *thí điểm thật*. Chưa xong danh sách này thì chưa được nhập dữ liệu thật.

**Chặn đường — phải xong trước tiên**

- [ ] **Lập pháp nhân.** Không có pháp nhân thì không nộp được hồ sơ và không ký được hợp đồng với trường.
- [ ] **Hỏi luật sư câu số 1**: nhật ký tư duy có phải dữ liệu cá nhân nhạy cảm không, và GALS có được hưởng cơ chế hoãn 5 năm dành cho tổ chức nhỏ không.
- [ ] **Chốt phương án AI.** Khuyến nghị: **tắt trợ lý AI cho lần thí điểm đầu**, dùng chế độ ngoại tuyến đã có sẵn.
- [ ] **Chọn giấy phép cho kho mã** (riêng cho mã nguồn, riêng cho nội dung).

**Hồ sơ và quy trình**

- [ ] Hồ sơ **đánh giá tác động xử lý dữ liệu cá nhân**, nộp A05 trong 60 ngày, làm mới mỗi 6 tháng.
- [ ] Hồ sơ **đánh giá tác động chuyển dữ liệu ra nước ngoài** — cần cho cả AI **và** cho hosting đặt ở nước ngoài.
- [ ] Quy trình **thông báo vi phạm dữ liệu trong 72 giờ**, lưu hồ sơ sự cố tối thiểu 5 năm.
- [ ] **Tự phân loại mức rủi ro theo Luật AI** và viết ra lập luận.
- [ ] Xác định **GALS có thuộc diện mạng xã hội** theo NĐ 147/2024 hay không.

**Mô hình trách nhiệm**

- [ ] Chốt bằng văn bản: **nhà trường là bên kiểm soát, GALS là bên xử lý**.
- [ ] Đưa **điều khoản hoàn lại theo Luật AI Đ.29(2)** vào hợp đồng với nhà trường.
- [ ] **Thiết kế để không nắm thông tin định danh**: giáo viên phát mã ẩn danh, bảng đối chiếu giữ trên giấy. *Lưu ý xung đột với yêu cầu xác thực tài khoản ở Phần 8 — phải chốt đánh đổi.*
- [ ] Bỏ hoặc để trống trường **tên** và **email**.

**Dữ liệu**

- [ ] Cơ sở dữ liệu lâu dài (PostgreSQL) và **chỉ gieo dữ liệu khi trống**.
- [ ] Sao lưu và **diễn tập phục hồi**.
- [ ] **Lịch lưu trữ viết thành văn bản**, cân đối giữa nghĩa vụ lưu nhật ký và nguyên tắc tối thiểu hoá.
- [ ] Cơ chế **xoá theo yêu cầu** của từng học sinh, hoạt động thật.
- [ ] Xác định nghĩa vụ **lưu trữ dữ liệu trong nước** và chuẩn bị chuyển sang nhà cung cấp Việt Nam.

**Đồng ý và công bố**

- [ ] **Ghi nhận sự đồng ý**: kiểm chứng được, có dấu thời gian, gắn nội dung cụ thể, không tích sẵn.
- [ ] Thông báo rõ trong luồng đồng ý rằng **đây là dữ liệu nhạy cảm**.
- [ ] Quy trình **đồng ý của cha mẹ hoặc người giám hộ** trước khi có tài khoản thật.
- [ ] **Mặc định tắt chia sẻ công khai**; bật phải qua duyệt của người lớn — và với trẻ từ đủ 7 tuổi cần **cả hai chữ ký**.
- [ ] **Kiểm soát ảnh và liên kết do học sinh dán vào**: danh sách nguồn cho phép hoặc tự lưu ảnh.
- [ ] Viết **Điều khoản sử dụng** và **Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ để học sinh lớp 10 đọc hiểu, có đủ hai mục bắt buộc: thông báo dữ liệu nhạy cảm và công khai việc dùng AI.

**Xác thực**

- [ ] Đăng nhập thật. Hiện tại chỉ là cookie có chữ ký, **không có mật khẩu**.
- [ ] Ghi nhật ký kiểm toán cho việc đồng ý — đây là một phần của xác thực, không phải tính năng để sau.

---

## Những gì chưa tra được — nêu ra thay vì đoán

1. **Phạm vi chính xác của nghĩa vụ lưu trữ trong nước** theo Luật An ninh mạng 116/2025: dịch vụ nhỏ, phi thương mại có thuộc diện không, và các ngưỡng của NĐ 53/2022 còn nguyên hay đã đổi.
2. **Điều khoản doanh nghiệp của Vertex AI / Google Cloud có cùng hạn chế dưới 18 tuổi hay không.** Bề mặt Google Cloud cũng hiện thông báo 18+. **Phải lấy xác nhận bằng văn bản từ Google, không dựa vào bài viết trên blog.**
3. **Chế tài tính theo doanh thu áp dụng thế nào với tổ chức phi lợi nhuận không doanh thu.**
4. **Bộ GD&ĐT hoặc Sở GD&ĐT có yêu cầu phê duyệt riêng nào** cho công cụ bổ trợ trên lớp. Thực tế khác nhau theo tỉnh — hỏi thẳng trường đối tác, càng sớm càng tốt.
5. **Nghị định hướng dẫn Luật AI** đã ban hành chưa và quy định gì về tiêu chí phân tầng rủi ro, cách gắn nhãn.
6. **Năng lực đồng ý của người 16–17 tuổi** — tương tác giữa quy định về người chưa thành niên trong Bộ luật Dân sự và các điều khoản về trẻ em của Luật 91/2025. Đây là điểm thật sự chưa rõ và đáng xin một ý kiến riêng.

---

## Câu hỏi mang tới cho luật sư

Mang theo tài liệu này và một sơ đồ một trang về đường đi của dữ liệu. Thứ tự đã được sắp sao cho một câu trả lời "không" ở trên tiết kiệm chi phí cho những câu bên dưới.

**Câu hỏi ngưỡng**

1. Nhật ký tư duy của học sinh, có thể chứa dấu hiệu về trạng thái cảm xúc, có phải **dữ liệu cá nhân nhạy cảm** theo NĐ 356/2025 Đ.4 không?
2. Nếu có, một tổ chức phi lợi nhuận do học sinh lập ra có được hưởng **cơ chế hoãn** nghĩa vụ ĐGTĐ và nhân sự bảo vệ dữ liệu không?
3. Một nhóm học sinh có thể lập **pháp nhân** dạng nào, chi phí và thời gian đăng ký ra sao, và pháp nhân đó có được làm bên kiểm soát / bên xử lý và ký hợp đồng với trường không?
4. Học sinh **16 và 17 tuổi** tự đồng ý cho việc xử lý dữ liệu nhạy cảm được không, hay mọi người dùng đều cần người giám hộ đồng ý?

**Câu hỏi về kiến trúc**

5. Với **thiết kế mã ẩn danh** (giáo viên giữ bảng đối chiếu trên giấy, GALS không nhận tên), GALS có còn đang xử lý dữ liệu cá nhân không? Câu trả lời có đổi không nếu giáo viên định danh ngược được?
6. GALS có phải **"mạng xã hội"** theo NĐ 147/2024, hay là trang thông tin điện tử nội bộ? Tính năng chia sẻ công khai và việc giáo viên xem được cả lớp có làm đổi câu trả lời không?
7. Nếu là mạng xã hội, dung hoà **yêu cầu xác thực tài khoản** với thiết kế ẩn danh bằng cách nào?
8. **Nghĩa vụ lưu trữ trong nước** có áp dụng với quy mô của chúng tôi không, và hosting ở nước ngoài có vi phạm không?

**Câu hỏi về AI**

9. Một **trợ lý hội thoại dùng cho người chưa thành niên trong môi trường giáo dục** rơi vào mức rủi ro nào theo Luật AI Đ.9?
10. GALS có được hưởng **thời hạn chuyển tiếp 18 tháng** cho lĩnh vực giáo dục theo Đ.35 không, khi nó đã chạy công khai dưới dạng bản mẫu trước 01/03/2026? Thế nào là "đã vận hành"?
11. Trong triển khai tại trường, **nhà trường có phải bên triển khai** theo Đ.29(2) không, và điều khoản hoàn lại nên viết thế nào?
12. Gửi bài viết của học sinh tới một **nhà cung cấp AI ở nước ngoài mà điều khoản của họ cấm dùng cho dịch vụ có người dưới 18 tuổi truy cập** có tạo ra trách nhiệm nào ngoài vi phạm hợp đồng không — cụ thể, nó có làm mất tính hợp pháp của chính việc chuyển dữ liệu theo Luật 91/2025 Đ.20 không?

**Câu hỏi về quy trình**

13. Hướng dẫn cụ thể việc **nộp hồ sơ ĐGTĐ và CTIA cho A05**: biểu mẫu, ngôn ngữ, ai ký, thời gian thực tế, và điều gì xảy ra nếu kết quả thẩm định là "chưa đạt".
14. **Hợp đồng với nhà trường** phải có gì để việc phân vai kiểm soát / xử lý có hiệu lực, và bộ phận pháp chế của một trường công sẽ yêu cầu thêm điều gì?
15. **Mức tuân thủ tối thiểu để chạy thí điểm hai lớp ở một trường là gì**, và bao nhiêu phần trong danh sách trên có thể hoãn tới khi vượt ngưỡng của NĐ 147/2024?

> **Câu 15 là câu quan trọng nhất.** Tất cả những phần trên mô tả toàn bộ nghĩa vụ. Thứ thật sự cần là **con đường hợp pháp ngắn nhất để đưa sản phẩm tới ba mươi học sinh thật ở một trường** — và một luật sư được hỏi thẳng như vậy sẽ trả lời hữu ích hơn nhiều so với một luật sư nhận được danh sách mong muốn.

---

## Nguồn đã tra

Văn bản gốc — cần đối chiếu toàn văn:

- Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15
- Nghị định 356/2025/NĐ-CP
- Luật Trí tuệ nhân tạo 134/2025/QH15
- Luật An ninh mạng 116/2025/QH15
- Nghị định 147/2024/NĐ-CP
- Luật Trẻ em 2016 và Nghị định 56/2017/NĐ-CP

Phân tích thứ cấp: bản tin pháp lý của EY Việt Nam về NĐ 356/2025 và Luật An ninh mạng 116/2025; bình luận của Frasers Vietnam, Apolat Legal, YP Law về giai đoạn chuyển tiếp; Gemini API Additional Terms of Service (`ai.google.dev/gemini-api/terms`); Google Cloud Service Specific Terms.

---

## Đây không phải tư vấn pháp lý

Tài liệu này do nhóm làm sản phẩm viết, không phải do luật sư viết. Nó dùng để **biết cần hỏi gì**, không phải để thay thế việc hỏi.

Trước khi triển khai thật, hãy làm việc với **luật sư Việt Nam** và với **nhà trường** — nhà trường thường đã có sẵn quan hệ và cơ sở pháp lý với phụ huynh, và đó là con đường ngắn nhất để làm đúng.
