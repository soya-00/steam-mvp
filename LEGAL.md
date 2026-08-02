# Tuyên bố pháp lý và dữ liệu

**Đọc trang này trước khi cho bất kỳ học sinh có thật nào dùng GALS.**

---

## Tóm tắt trong mười giây

| | |
|---|---|
| GALS hiện là gì | Một **bản mẫu (prototype)** làm cho cuộc thi. Không phải sản phẩm thương mại. |
| Dữ liệu trong ứng dụng | **Toàn bộ là dữ liệu giả định.** Không có học sinh thật nào trong đó. |
| Dữ liệu có được lưu lại không | **Không.** Máy chủ khởi động lại là xoá sạch, kể cả bài bạn vừa viết. |
| Được nhập thông tin thật vào không | **Không.** Đừng nhập tên thật, trường thật, số điện thoại, email cá nhân. |
| Có phải công cụ hỗ trợ tâm lý không | **Không.** Xem mục [Trợ lý AI](#trợ-lý-ai-và-những-điều-gals-không-làm). |

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

Ứng dụng dùng SQLite trên đĩa tạm của máy chủ. Mỗi lần máy chủ khởi động lại, toàn bộ bảng dữ liệu bị xoá và gieo lại từ đầu bằng dữ liệu mẫu. Máy chủ miễn phí còn tự ngủ khi không có ai dùng, nên **bài viết của bạn thường không sống qua một đêm**.

Điều này là cố ý cho một bản trình diễn: mỗi người vào đều thấy ứng dụng sạch sẽ và đầy đủ nội dung. Nhưng nó cũng có nghĩa là **xoá dữ liệu ở đây không phải là quyền được xoá theo luật** — đó chỉ là mất dữ liệu.

**Những gì mô hình dữ liệu hiện có thể chứa**

Bảng người dùng có trường **tên** và **email**. Nhật ký chứa **văn bản do học sinh tự viết**. Đây là thông tin cá nhân theo đúng nghĩa pháp lý nếu có người thật nhập vào. Bản mẫu chỉ chứa dữ liệu giả — nhưng cấu trúc thì đã sẵn sàng chứa dữ liệu thật, và đó chính là rủi ro.

---

## Dữ liệu đi những đâu

Ba đường ra, cần biết rõ:

**1. Sang máy chủ của Google (trợ lý AI).** Khi bật trợ lý AI, câu trả lời của học sinh được gửi tới Gemini API để sinh câu hỏi phản hồi. Đây là **chuyển dữ liệu ra ngoài lãnh thổ Việt Nam**. Ứng dụng cố tình gửi ít nhất có thể: chỉ câu hỏi hiện tại và câu trả lời hiện tại, không gửi cả cuốn nhật ký. Khi không có khoá API, ứng dụng chạy hoàn toàn ngoại tuyến bằng kịch bản dựng sẵn và **không gửi gì đi đâu cả**.

**2. Ra trang chia sẻ công khai.** Học sinh có thể bấm chia sẻ một mục hồ sơ. Mục đó nhận một đường dẫn khó đoán và **ai có đường dẫn cũng xem được, không cần đăng nhập**.

> **Đường dẫn khó đoán không phải là riêng tư về mặt pháp lý.** Chia sẻ như vậy là **công bố**. Với người chưa thành niên, công bố bài viết cá nhân cần sự đồng ý của cha mẹ hoặc người giám hộ, không chỉ là một cú bấm nút của học sinh.

**3. Ra các trang bên thứ ba.** Mục Tài nguyên liên kết tới Coursera, Khan Academy, YouTube. Bấm vào là rời khỏi GALS và chịu chính sách của các trang đó.

Liên kết ảnh và video do học sinh tự dán vào chỉ nhận `http://` và `https://`. Các dạng khác — đáng kể nhất là `javascript:` — bị chặn, vì mục hồ sơ có thể được chia sẻ công khai và một đường dẫn như vậy sẽ chạy mã trong trình duyệt của người vào xem.

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

Nói thẳng: ở bản mẫu, góp ý **không chắc còn lại tới hôm sau**. Câu xác nhận sau khi gửi cũng nói đúng như vậy chứ không hứa suông. Muốn góp ý sống được thật thì cần cơ sở dữ liệu lâu dài hoặc gửi ra một nơi bên ngoài — xem [Việc cần làm tiếp](docs/VIEC-CAN-LAM.md).

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

---

## Trách nhiệm pháp lý

Phần mềm này được cung cấp nguyên trạng, **không kèm bảo đảm dưới bất kỳ hình thức nào**, cho mục đích trình diễn và giáo dục.

Nhóm phát triển không chịu trách nhiệm cho: mất mát dữ liệu, gián đoạn dịch vụ, nội dung do mô hình AI sinh ra, nội dung do người dùng nhập vào, hay hậu quả của việc dùng bản mẫu này với dữ liệu thật của người thật.

Nếu bạn triển khai GALS cho học sinh có thật, **bạn hoặc nhà trường của bạn là bên chịu trách nhiệm về dữ liệu đó**, không phải bản mẫu này.

---

## Cần làm gì trước khi dùng với học sinh thật

Đây là ranh giới giữa *bản mẫu* và *thử nghiệm thật*. Chưa xong danh sách này thì chưa được nhập dữ liệu thật.

**Về mô hình trách nhiệm**

- [ ] Chốt ai là **bên kiểm soát dữ liệu**. Khuyến nghị: **nhà trường là bên kiểm soát, GALS chỉ là bên xử lý** theo hợp đồng.
- [ ] Tốt hơn nữa: **thiết kế để không nắm thông tin định danh**. Giáo viên phát mã ẩn danh cho học sinh, bảng đối chiếu mã ↔ học sinh giữ trên giấy ở phía giáo viên. GALS không bao giờ biết tên thật.
- [ ] Bỏ hoặc để trống trường **tên** và **email** trong bảng người dùng.

**Về dữ liệu**

- [ ] Cơ sở dữ liệu lâu dài (PostgreSQL) và **chỉ gieo dữ liệu khi trống**, thay cho việc xoá sạch mỗi lần khởi động.
- [ ] Sao lưu và **diễn tập phục hồi**.
- [ ] Quy định **thời hạn lưu trữ** và cơ chế **xoá theo yêu cầu** của từng học sinh.
- [ ] Quy trình **thông báo khi lộ lọt dữ liệu**.

**Về đồng ý và công bố**

- [ ] Quy trình **đồng ý của cha mẹ hoặc người giám hộ** trước khi có tài khoản thật.
- [ ] **Mặc định tắt chia sẻ công khai**; muốn bật phải qua giáo viên hoặc phụ huynh duyệt.
- [ ] **Kiểm soát ảnh và liên kết do học sinh dán vào.** Hiện trường ảnh nhận đường dẫn tự do và hiển thị thẳng lên trang công khai — cần danh sách nguồn cho phép hoặc tự lưu ảnh trên máy chủ.
- [ ] Viết **Điều khoản sử dụng** và **Chính sách quyền riêng tư** bằng tiếng Việt, đủ dễ để học sinh lớp 10 đọc hiểu.

**Về AI**

- [ ] **Hồ sơ đánh giá tác động chuyển dữ liệu ra nước ngoài** cho việc gọi Gemini.
- [ ] Đối chiếu **điều khoản của nhà cung cấp AI về người dùng chưa thành niên**.
- [ ] Có nút **báo cáo câu trả lời không phù hợp**.

**Về xác thực**

- [ ] Đăng nhập thật. Hiện tại chỉ là cookie có chữ ký, **không có mật khẩu**.

---

## Khung pháp lý cần đối chiếu

Danh sách để bắt đầu tra cứu, **không phải kết luận pháp lý**:

- **Luật Trẻ em 2016** — quyền bí mật đời sống riêng tư của trẻ em; công bố thông tin đời sống riêng tư của trẻ em cần có sự đồng ý. Lưu ý: "trẻ em" theo luật Việt Nam là **người dưới 16 tuổi**, trong khi học sinh THPT ở khoảng 15–18 tuổi — nghĩa là **một phần người dùng thuộc phạm vi luật này và ứng dụng không phân biệt được**.
- **Nghị định 56/2017/NĐ-CP** — bảo vệ thông tin cá nhân của trẻ em trên môi trường mạng.
- **Nghị định 13/2023/NĐ-CP** về bảo vệ dữ liệu cá nhân, và **Luật Bảo vệ dữ liệu cá nhân được thông qua năm 2025**.

> Hiệu lực thi hành và các nghị định hướng dẫn của luật năm 2025 **phải được tra cứu lại từ nguồn chính thức**. Đừng dựa vào tài liệu này cho thời điểm hiệu lực.

Nhật ký tư duy là bài viết phản tư cá nhân và **có thể chứa dấu hiệu về sức khoẻ tinh thần** — đó chính là lý do bộ lọc khủng hoảng tồn tại. Loại dữ liệu này thường được xếp vào nhóm **dữ liệu cá nhân nhạy cảm**, chặt hơn nhiều so với một cái tên và một địa chỉ email.

---

## Đây không phải tư vấn pháp lý

Tài liệu này do nhóm làm sản phẩm viết, không phải do luật sư viết. Nó dùng để **biết cần hỏi gì**, không phải để thay thế việc hỏi.

Trước khi triển khai thật, hãy làm việc với **luật sư Việt Nam** và với **nhà trường** — nhà trường thường đã có sẵn quan hệ và cơ sở pháp lý với phụ huynh, và đó là con đường ngắn nhất để làm đúng.
