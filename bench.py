import json
import re
from pathlib import Path

# Import các lớp từ mã nguồn bạn đã viết
from src.chunking import RecursiveChunker, SentenceChunker, FixedSizeChunker
from src.store import EmbeddingStore
from src.models import Document

def parse_markdown(filepath):
    """Đọc file markdown và tách metadata, nội dung."""
    content = filepath.read_text(encoding='utf-8')
    if '---' not in content:
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) >= 3:
        fm_raw = parts[1]
        text_content = parts[2].strip()
        metadata = dict(re.findall(r'^(\w+):\s*(.+)$', fm_raw, re.M))
        # Làm sạch metadata
        for k, v in metadata.items():
            metadata[k] = v.strip('"\'')
        return metadata, text_content
    return {}, content

def main():
    # 1. Khởi tạo Chunker (BẠN CÓ THỂ ĐỔI CHIẾN LƯỢC Ở ĐÂY)
    # Ví dụ: Dùng RecursiveChunker
    chunker = RecursiveChunker(chunk_size=300)
    # chunker = SentenceChunker(max_sentences_per_chunk=3)
    # chunker = FixedSizeChunker(chunk_size=300, overlap=50)

    # 2. Khởi tạo Store
    store = EmbeddingStore()
    docs_to_add = []

    # 3. Đọc dữ liệu từ data/ecommerce
    data_dir = Path('data/ecommerce')
    print("Đang nạp tài liệu từ:", data_dir)
    
    for filepath in data_dir.glob('*.md'):
        metadata, content = parse_markdown(filepath)
        doc_id = metadata.get('doc_id', filepath.stem)
        
        # Chia nhỏ nội dung thành các chunk
        chunks = chunker.chunk(content)
        
        # Tạo Document cho từng chunk
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{doc_id}#{i}", 
                content=chunk_text, 
                metadata=metadata
            )
            docs_to_add.append(doc)

    print(f"Tổng số chunk tạo ra: {len(docs_to_add)}")
    
    # 4. Đưa vào Store
    store.add_documents(docs_to_add)
    print(f"Đã lưu vào Vector Store thành công.\n")

    # 5. Đọc 5 câu hỏi benchmark
    queries_file = data_dir / 'benchmark_queries.json'
    with open(queries_file, 'r', encoding='utf-8') as f:
        benchmark_data = json.load(f)
    
    # 6. Chạy Đánh giá và lưu ra file
    output_file = Path('ket_qua_benchmark.txt')
    with open(output_file, 'w', encoding='utf-8') as f_out:
        
        for q in benchmark_data['queries']:
            question = q['question']
            filter_meta = q.get('metadata_filter')
            
            f_out.write(f"Câu hỏi: {question}\n")
            f_out.write(f"Metadata filter: {filter_meta}\n")
            
            print(f"Đang tìm kiếm cho: {question}")
            
            # Nếu có bộ lọc thì dùng search_with_filter, nếu không dùng search
            if filter_meta:
                results = store.search_with_filter(question, top_k=3, metadata_filter=filter_meta)
            else:
                results = store.search(question, top_k=3)
                
            for idx, res in enumerate(results, 1):
                doc_id = res['metadata'].get('doc_id', 'Unknown')
                score = res.get('score', 0)
                content = res.get('content', '')[:150].replace('\n', ' ') # Lấy 150 ký tự đầu cho gọn
                
                line = f"  Top {idx} | Nguồn: {doc_id} | Điểm: {score:.4f}\n  Trích đoạn: {content}...\n"
                f_out.write(line)
            
            f_out.write("-" * 50 + "\n")
            
    print(f"\nTuyệt vời! Kết quả đã được lưu vào file: {output_file}")

if __name__ == '__main__':
    main()
