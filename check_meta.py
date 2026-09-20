import re
from pathlib import Path

D = Path('data/ecommerce')
REQ = ['doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience']
mds = sorted(D.glob('*.md'))
ids, auds = [], {}

print("-" * 50)
for p in mds:
    content = p.read_text(encoding='utf-8')
    if '---' in content:
        fm_raw = content.split('---')[1]
        fm = dict(re.findall(r'^(\w+):\s*(.+)$', fm_raw, re.M))
        
        doc_id = fm.get('doc_id', '').strip('"\'')
        ids.append(doc_id)
        
        aud = fm.get('audience', 'None').strip('"\'')
        auds[aud] = auds.get(aud, 0) + 1
        
        is_ok = all(k in fm for k in REQ) and doc_id == p.stem
        status = 'OK' if is_ok else 'THIEU METADATA (hoặc sai doc_id)'
        print(f'{p.name:40} {status}')
    else:
        print(f'{p.name:40} KHONG CO FRONTMATTER')

print("-" * 50)
print('Tổng số file:', len(mds), '(Cần 5-10 file)')
print('Phân loại Audience:', auds)
