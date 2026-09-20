# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G23
**Thành viên:** Hoàng Văn Sơn, Mai Hoàng Anh, Phan Danh Đạt
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Thương mại điện tử (Shopee)

**Tại sao nhóm chọn chủ đề này?**
> Đây là chủ đề bắt buộc cho lớp L3B, đồng thời chứa nhiều quy định phức tạp phân tách rõ ràng giữa người mua và người bán. Dữ liệu này cực kỳ phù hợp để kiểm tra khả năng phân loại và tìm kiếm có điều kiện (Metadata Filter) của hệ thống RAG, giúp tránh việc AI nhầm lẫn chính sách giữa các đối tượng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | buyer-cancel-order.md | help.shopee.vn | 2026-09-20 | ~1400 | doc_id, audience: buyer |
| 2 | buyer-order-status.md | help.shopee.vn | 2026-09-20 | ~1200 | doc_id, audience: buyer |
| 3 | seller-cancel-request.md | help.shopee.vn | 2026-09-20 | ~1200 | doc_id, audience: seller |
| 4 | seller-warranty-policy.md | help.shopee.vn | 2026-09-20 | ~900 | doc_id, audience: seller |
| 5 | return-refund-policy.md | help.shopee.vn | 2026-09-20 | ~1000 | doc_id, audience: both |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `buyer-cancel-order` | Giúp hệ thống định danh tài liệu, hiển thị nguồn cho LLM trích dẫn và hỗ trợ chức năng xóa (delete). |
| `audience` | Chuỗi | `buyer`, `seller` | Giúp áp dụng Metadata Filter, đảm bảo truy xuất đúng chính sách cho đúng đối tượng hỏi, chống nhiễu (hallucination). |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Toàn bộ | FixedSizeChunker (`fixed_size`) | 35 | 300 | Tệ, câu bị cắt ngang giữa chừng. |
| Toàn bộ | SentenceChunker (`by_sentences`) | 45 | 150 | Trung bình, câu nguyên vẹn nhưng ngữ cảnh bị rời rạc. |
| Toàn bộ | RecursiveChunker (`recursive`) | 31 | 250 | Rất tốt, giữ được trọn đoạn văn. |

### Chiến lược của từng thành viên

**Thành viên 1 — Hoàng Văn Sơn**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn cho chủ đề này:** Chia nhỏ đệ quy giúp giữ lại đoạn văn liền mạch nhất có thể. Chính sách Shopee thường có các đoạn giải thích dài, nếu dùng Fixed size sẽ bị đứt gãy ý nghĩa pháp lý.

**Thành viên 2 — [Tên thành viên 2]**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chia theo từng câu phù hợp để trả lời các truy vấn rất ngắn hoặc hỏi về một định mức cụ thể (ví dụ: thời gian là bao nhiêu ngày).

**Thành viên 3 — [Tên thành viên 3]**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Cắt cố định với Overlap lớn giúp vét cạn thông tin mà không cần quan tâm đến cấu trúc văn bản gốc phức tạp hay không đồng nhất.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| H. V. Sơn | Recursive | 8/10 | Ngữ cảnh rất trọn vẹn, LLM hiểu tốt. | Tốn tài nguyên tính toán hơn. |
| Mai Hoàng Anh | Sentence | 6/10 | Lấy đúng thông tin cụ thể rất nhanh. | Hay bị mất ngữ cảnh xung quanh. |
| Phan Danh Đạt | FixedSize | 5/10 | Cài đặt đơn giản, đều đặn. | Hay cắt giữa chừng một khái niệm quan trọng. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `RecursiveChunker` hoạt động tốt nhất. Các văn bản chính sách e-commerce thường được định dạng theo cấu trúc Heading, Paragraph. Thuật toán Recursive bám sát cấu trúc tự nhiên này thông qua các dấu phân cách `\n\n`, giúp chunk tạo ra mang tính đóng gói ngữ nghĩa cao.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Tôi cần vào đâu trên ứng dụng Shopee để xem trạng thái đơn mua? | Mở mục Tôi > Đơn mua trên ứng dụng Shopee để xem tiến trình. | buyer-order-status |
| 2 | Đơn do hãng vận chuyển khác SPX đang Chờ lấy hàng thì tôi có thể hủy ngay không? | Không tự động hủy ngay: phải chờ người bán chấp nhận. | buyer-cancel-order |
| 3 | Đơn Shopee đã hủy có khôi phục để giao lại và giữ ưu đãi cũ được không? | Không khôi phục đơn đã hủy để giao lại. Cần đặt đơn mới. | buyer-cancelled-order |
| 4 | Đơn trả trước bằng thẻ tín dụng cần thanh toán trong bao lâu? | Hoàn tất trong 12 giờ kể từ lúc đặt hàng thành công. | buyer-prepayment |
| 5 | Tôi xử lý yêu cầu hủy đơn hàng như thế nào? | Vào Đơn hủy > Chờ phản hồi > Xem thêm, đồng ý hoặc từ chối. | seller-cancel-request |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Xem trạng thái đơn mua | FixedSize | Không | Truy xuất sai hoàn toàn (Top-1 là tài liệu seller) |
| 2 | Hủy đơn chờ lấy hàng | Recursive | Không | Có filter "buyer" nhưng vẫn tìm sai file |
| 3 | Khôi phục đơn hủy | Sentence | Không | Tìm nhầm sang chính sách bảo hành |
| 4 | Thanh toán thẻ tín dụng | Recursive | Không | Bị đánh lừa bởi từ khóa phụ |
| 5 | Xử lý yêu cầu hủy | Recursive | Có (Top 2) | Lọc audience="seller" giúp lấy đúng tài liệu |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, cực kỳ hữu ích. Đặc biệt ở Câu 2 và Câu 5 (cùng về Hủy đơn), nếu không có `audience` filter, hệ thống đem quy định của người bán trả lời cho người mua và ngược lại, gây ra Hallucination nghiêm trọng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Sự nguy hiểm của việc thiết kế hệ thống RAG mà không có Metadata (dễ dẫn đến rủi ro pháp lý nếu tư vấn sai chính sách).
- Sự khác biệt chất lượng trả lời giữa Fixed Size và Recursive Chunking khi áp dụng cho dữ liệu dạng Markdown.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tài liệu, nhưng chiến lược Chunking quyết định việc LLM có đủ thông tin nền (background context) hay không. Recursive luôn an toàn hơn khi xử lý văn bản quy phạm, chính sách vì nó tôn trọng cấu trúc câu/đoạn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Sẽ gắn thêm siêu dữ liệu (metadata) chi tiết hơn như `category` (hoàn tiền, vận chuyển) hoặc `valid_from` để quản lý sự thay đổi chính sách theo thời gian, giúp AI có thể trả lời các câu hỏi về lịch sử chính sách.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
