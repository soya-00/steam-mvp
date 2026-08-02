
# GALS

**Thử làm nghề trước khi phải chọn nghề.**

### 👉 [Dùng thử tại steam-mvp.onrender.com](https://steam-mvp.onrender.com)

Không cần cài gì, không cần đăng ký. Ở màn hình đăng nhập có mục **Demo nhanh** — bấm một nút là vào thẳng.

> Lần vào đầu tiên có thể mất 30–60 giây vì máy chủ miễn phí đang "ngủ dậy".

> [!IMPORTANT]
> **Đây là bản mẫu trình diễn, chưa có tài khoản riêng cho từng người.**
> Cả ứng dụng hiện chỉ có **ba tài khoản dùng chung** — mọi người đăng nhập đều rơi vào
> một trong ba tài khoản đó, nên **ai cũng đọc được bài của người khác**.
> Những gì bạn viết **có được ghi lên máy chủ**, nhưng bị xoá sạch mỗi lần máy chủ khởi
> động lại. Đừng nhập thông tin thật và đừng dùng bản này để chạy thử với học sinh thật.
> Chi tiết ở **[LEGAL.md](LEGAL.md)** — lưu trữ dữ liệu, phạm vi trách nhiệm, và danh
> sách việc bắt buộc phải làm trước.

---

## GALS là gì?

Một trang web cho học sinh cấp 3.

Thay vì đọc lý thuyết về nghề nghiệp, học sinh **đóng vai một người đang đi làm thật** và tự xử lý một tình huống có thật của nghề đó.

Ví dụ: em vào vai kỹ sư năng lượng, được gọi tới một trạm y tế ngoài đảo vì tủ vắc-xin cứ mất điện. Ai cũng bảo tại ắc quy hỏng. Nhưng số liệu chưa đủ để khẳng định.

Có trợ lý AI đi cùng, nhưng **nó chỉ hỏi lại chứ không giải hộ**.

**GALS cố tình không có:** điểm số · xếp hạng · đáp án mẫu.

---

## Học sinh dùng như thế nào?

Đăng nhập xong là vào **Trang cá nhân**. Từ đây có 4 hướng, đi hướng nào trước cũng được:

| Nhánh | Em làm gì |
|---|---|
| **Dự án học tập** | Chọn lĩnh vực → chọn tình huống → nhập vai → đi 4 cấp độ → nộp dự án |
| **Hồ sơ năng lực** | Xem lại việc đã làm. Có cả trò chuyện tự do với AI |
| **Huy hiệu** | Ghi lại nơi đã đi qua, kèm gợi ý lĩnh vực nên thử tiếp |
| **Tài nguyên** | Khoá học và video miễn phí theo lĩnh vực |

### Bốn cấp độ là bốn kiểu suy nghĩ

1. **Hiểu vấn đề** — Đâu là điều chắc chắn, đâu là mình đang đoán?
2. **Đồng cảm** — Ai bị ảnh hưởng? Họ muốn những thứ khác nhau ra sao?
3. **Sáng tạo** — Đề xuất phương án, trong điều kiện thiếu thời gian và thiếu tiền.
4. **Phản chiếu** — Có cách giải thích nào khác không?

> **Mỗi nghề làm ra một thứ khác nhau.** Kỹ sư năng lượng làm *phương án hệ thống*. Chuyên viên dịch tễ làm *kế hoạch điều tra*. Chuyên viên an ninh mạng làm *quy trình xử lý sự cố*. Không phải nghề nào cũng "làm một cái app".

### AI đề nghị, học sinh quyết định

Trong phần trò chuyện tự do, khi AI thấy em vừa nói ra một ý hay, nó hỏi: *"Thêm ý tưởng này vào Hồ sơ?"*

Em bấm đồng ý thì mới lưu. Và kể cả khi đã lưu, mục đó vẫn **riêng tư** — muốn cho người khác xem phải bấm chia sẻ lần nữa.

---

## Giáo viên dùng như thế nào?

Tạo lớp → đọc mã lớp cho học sinh → giao nhiệm vụ → đọc nhật ký → nhắn riêng cho từng em.

**Không có bảng điểm ở bất cứ đâu.** Thầy cô đọc được cách các em suy nghĩ, không phải kết quả đúng sai.

**Dạy được không cần thiết bị.** Khi giao nhiệm vụ làm tại lớp, có nút **in tài liệu** — kèm hướng dẫn ngắn cho thầy cô. Học sinh chỉ cần giấy và bút. Không có máy in cũng dạy được: đọc to phần bối cảnh, chép câu hỏi lên bảng.

**Quyền riêng tư — thiết kế là vậy, bản mẫu thì chưa:** ý định của sản phẩm là học sinh không nhập mã lớp thì không giáo viên nào xem được bài của em, và đó là mặc định chứ không phải tuỳ chọn phải đi tìm.

> Nhưng **bản mẫu hiện tại chưa làm được điều đó**, vì chưa có tài khoản riêng cho từng người: mọi người dùng chung ba tài khoản có sẵn. Ranh giới riêng tư giữa các học sinh **chỉ tồn tại trên thiết kế**, chưa có thật trong bản đang chạy. Xem [LEGAL.md](LEGAL.md).

---

## Chạy trên máy của bạn

Cần có **Python** và **Node.js**. Mở Terminal rồi gõ:

```bash
git clone https://github.com/soya-00/steam-mvp.git
cd steam-mvp

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install && npm run build:css

.venv/bin/uvicorn app.main:app --reload
```

Mở trình duyệt vào **http://127.0.0.1:8000**

Chạy bộ kiểm thử (không bắt buộc): `pip install -r requirements-dev.txt` rồi `pytest`

---

## Tài liệu thêm

- [Nhật ký thiết kế](docs/NHAT-KY-THIET-KE.md) — vì sao sản phẩm được làm như hiện tại: từng giai đoạn, quyết định đã chốt, lỗi đã gặp và hướng đi tiếp
- [Hướng dẫn kỹ thuật](docs/KY-THUAT.md) — kiến trúc, cách thêm kịch huống, cách deploy, cách bật AI
- [Việc cần làm tiếp](docs/VIEC-CAN-LAM.md) — khả năng tiếp cận, các nhóm nghề chưa có kịch huống
- [**Tuyên bố pháp lý và dữ liệu**](LEGAL.md) — dữ liệu được lưu ra sao, đi những đâu, ai chịu trách nhiệm, và phải làm gì trước khi dùng với học sinh thật

---

*Dữ liệu gieo sẵn trong ứng dụng là dữ liệu giả định. Những gì người dùng tự viết thì được ghi lên máy chủ, dùng chung giữa mọi người, và bị xoá mỗi lần máy chủ khởi động lại.*
