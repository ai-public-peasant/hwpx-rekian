#!/usr/bin/env python3
"""예제 2: 표가 포함된 문서 생성

표를 만들고 셀에 내용을 채웁니다.
- 제목 문단 + 표 + 요약 문단
"""

from hwpx import HwpxDocument

doc = HwpxDocument.new()
section = doc.sections[0]

# 제목
doc.add_paragraph("2024년 1분기 매출 보고서", section=section)
doc.add_paragraph("", section=section)

# 매출 표 (4행 x 4열)
table = doc.add_table(rows=4, cols=4, section=section)

# 헤더 행
table.set_cell_text(0, 0, "구분")
table.set_cell_text(0, 1, "1월")
table.set_cell_text(0, 2, "2월")
table.set_cell_text(0, 3, "3월")

# 데이터 행
data = [
    ["국내 매출", "1,200만원", "1,350만원", "1,500만원"],
    ["해외 매출", "800만원", "950만원", "1,100만원"],
    ["합계", "2,000만원", "2,300만원", "2,600만원"],
]
for r_idx, row in enumerate(data):
    for c_idx, text in enumerate(row):
        table.set_cell_text(r_idx + 1, c_idx, text)

# 요약
doc.add_paragraph("", section=section)
doc.add_paragraph("전 분기 대비 매출이 30% 증가하였습니다.", section=section)

doc.save_to_path("table_document.hwpx")
print("생성 완료: table_document.hwpx")
