# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Văn Sơn
**Nhóm:** G23
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Nghĩa là hai vector biểu diễn văn bản có góc hợp bởi chúng rất nhỏ (gần bằng 0 độ), chứng tỏ hai đoạn văn bản này có cùng hướng ý nghĩa (ngữ nghĩa) và rất giống nhau về mặt nội dung.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi rất thích ăn phở bò."
- Câu B: "Món phở bò là món ăn yêu thích nhất của tôi."
- Tại sao tương đồng: Khác nhau về cấu trúc câu và từ vựng nhưng cùng chung một lớp nghĩa cốt lõi.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi rất thích ăn phở bò."
- Câu B: "Thị trường chứng khoán hôm nay giảm điểm mạnh."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn không liên quan đến nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Độ tương tự Cosine đo lường "hướng" của vector (tính chất ngữ nghĩa) mà không bị ảnh hưởng bởi độ dài của vector. Nếu dùng Euclid, một câu dài và một câu ngắn dù cùng nghĩa vẫn có thể bị coi là cách xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Công thức: ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 22.11
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên (thành 25 chunks). Ta muốn overlap lớn hơn để đảm bảo các câu bị cắt ở rìa không bị mất ngữ cảnh (giữ trọn vẹn ý nghĩa kết nối giữa hai đoạn).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
> Sử dụng Regex (Positive Lookbehind `(?<=[.!?])\s+`) để tách câu ngay sau các dấu ngắt câu mà không làm mất đi các dấu này. Xử lý ngoại lệ loại bỏ các câu rỗng bằng cách `.strip()` và kiểm tra khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
> Thuật toán đệ quy thử cắt bằng các dấu phân cách từ lớn (`\n\n`) đến bé (`""`). Base case là khi chuỗi hiện tại đã nhỏ hơn `chunk_size` hoặc khi không còn dấu phân cách nào (buộc phải cắt theo `chunk_size`). Sau khi cắt, phải có bước nối lại các đoạn ngắn cho sát với `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
> Gắn cờ ép buộc dùng In-memory (bỏ qua ChromaDB), lưu mỗi record dưới dạng dictionary vào một list. Khi tìm kiếm, duyệt mảng để tính Cosine Similarity (dùng dot_product) rồi sắp xếp kết quả giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
> Bắt buộc lọc metadata **trước** để tạo ra một tập records ứng viên, sau đó mới tính điểm trên tập này để không bị mất slot top_k. Việc xóa sử dụng List Comprehension để loại bỏ những bản ghi có chứa `doc_id` tương ứng.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
> Lấy top_k kết quả, dựng thành chuỗi ngữ cảnh có đánh số `[1] (Nguồn: doc_id)`. Truyền chuỗi này vào prompt và ra lệnh cho LLM chỉ được trả lời từ ngữ cảnh, nếu không có phải báo không biết, đồng thời phải trích dẫn số thứ tự ở cuối câu.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
=========================================== test session starts ============================================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- D:\AI_Thuc_Chien\Day7\K4-L3B-Data-Foundations\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\AI_Thuc_Chien\Day7\K4-L3B-Data-Foundations
collected 42 items                                                                                          

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                 [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                          [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                   [  7%] 
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                    [  9%] 
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                         [ 11%] 
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED         [ 14%] 
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED               [ 16%] 
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                [ 19%] 
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED              [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                [ 26%] 
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                           [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                       [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                 [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED        [ 35%] 
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED            [ 38%] 
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED      [ 40%] 
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED            [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                  [ 47%] 
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                    [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                          [ 52%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED               [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                 [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED     [ 59%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                  [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                           [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                          [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                     [ 69%] 
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                 [ 71%] 
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED            [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                      [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                [ 80%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED           [ 85%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED          [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED         [ 92%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED  [ 95%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================================ 42 passed in 0.16s ============================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách trả hàng trong 7 ngày | Khách hàng có thể hoàn trả trong một tuần | cao | 0.85 | Đúng |
| 2 | Sản phẩm được bảo hành 12 tháng | Bảo hành 1 năm cho tất cả sản phẩm | cao | 0.82 | Đúng |
| 3 | Thời gian giao hàng là 3 ngày | Cửa hàng đóng cửa vào cuối tuần | thấp | 0.12 | Đúng |
| 4 | Tôi muốn mua điện thoại | Điện thoại này giá bao nhiêu | cao | 0.76 | Đúng |
| 5 | Apple ra mắt iPhone mới | Quả táo này rất ngon | thấp | 0.15 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Cặp số 5 khá bất ngờ vì cùng có từ "táo" (Apple) nhưng điểm tương tự lại thấp. Điều này chứng tỏ Embedding thực sự "hiểu" được ngữ cảnh của từ ngữ (công ty công nghệ vs trái cây) chứ không đơn thuần chỉ so khớp mặt chữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tôi cần vào đâu trên ứng dụng Shopee để xem trạng thái đơn mua? | Nguồn: seller-failed-delivery. Trích đoạn: "Hàng hỏng hoặc trạng thái không khớp..." | 0.2416 | Không | (Trả lời sai do Top-1 là chính sách người bán) |
| 2 | Đơn do hãng vận chuyển khác SPX đang Chờ lấy hàng thì tôi có thể hủy ngay không? | Nguồn: buyer-order-status. Trích đoạn: "Trên ứng dụng, mở Tôi > Đơn mua để xem tiến trình..." | 0.2128 | Liên quan một phần | Không hủy ngay được, phải chờ xác nhận... |
| 3 | Đơn Shopee đã hủy có khôi phục để giao lại và giữ ưu đãi cũ được không? | Nguồn: seller-warranty-policy. Trích đoạn: "Người bán chịu trách nhiệm xử lý yêu cầu bảo hành..." | 0.2741 | Không | (Lại lấy nhầm tài liệu của seller) |
| 4 | Đơn trả trước bằng thẻ tín dụng hoặc ghi nợ cần thanh toán trong bao lâu, nếu quá hạn thì sao? | Nguồn: return-refund-policy. Trích đoạn: "Khối metadata phía trên là template mẫu..." | 0.2606 | Không | (Nhầm sang metadata mẫu thay vì nội dung) |
| 5 | Tôi xử lý yêu cầu hủy đơn hàng như thế nào? | Nguồn: seller-failed-delivery. Trích đoạn: "Hàng hỏng hoặc trạng thái không khớp..." | 0.1786 | Không | (Chưa lấy đúng bài Hủy đơn) |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (Câu 1 có ở Top 2, Câu 3 có ở Top 2, Câu 5 có ở Top 2)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Kết quả chạy thực tế cho thấy đôi khi Top-1 không phải là kết quả tốt nhất. Việc lấy Top-3 và dùng Metadata Filter (lọc theo audience) là cực kỳ quan trọng để LLM có đủ thông tin và không bị nhầm lẫn giữa người mua - người bán.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |
