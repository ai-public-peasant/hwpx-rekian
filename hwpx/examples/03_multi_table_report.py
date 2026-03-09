#!/usr/bin/env python3
"""예제 3: 여러 표가 포함된 종합 보고서

여러 섹션에 걸쳐 표와 텍스트를 배치합니다.
- 인사 현황표 + 예산 집행표 + 일정표
"""

from hwpx import HwpxDocument

doc = HwpxDocument.new()
section = doc.sections[0]

# === 인사 현황 ===
doc.add_paragraph("1. 부서별 인원 현황", section=section)
doc.add_paragraph("", section=section)

t1 = doc.add_table(rows=5, cols=3, section=section)
t1.set_cell_text(0, 0, "부서")
t1.set_cell_text(0, 1, "인원")
t1.set_cell_text(0, 2, "비고")

staff = [
    ["기획팀", "12명", "신규 2명"],
    ["개발팀", "25명", "충원 필요"],
    ["디자인팀", "8명", ""],
    ["영업팀", "15명", "지방 파견 3명"],
]
for i, row in enumerate(staff):
    for j, text in enumerate(row):
        t1.set_cell_text(i + 1, j, text)

doc.add_paragraph("", section=section)

# === 예산 집행 현황 ===
doc.add_paragraph("2. 예산 집행 현황", section=section)
doc.add_paragraph("", section=section)

t2 = doc.add_table(rows=4, cols=4, section=section)
t2.set_cell_text(0, 0, "항목")
t2.set_cell_text(0, 1, "예산")
t2.set_cell_text(0, 2, "집행")
t2.set_cell_text(0, 3, "잔액")

budget = [
    ["인건비", "5억원", "3.2억원", "1.8억원"],
    ["운영비", "2억원", "1.5억원", "0.5억원"],
    ["사업비", "3억원", "1.8억원", "1.2억원"],
]
for i, row in enumerate(budget):
    for j, text in enumerate(row):
        t2.set_cell_text(i + 1, j, text)

doc.add_paragraph("", section=section)

# === 주요 일정 ===
doc.add_paragraph("3. 주요 일정", section=section)
doc.add_paragraph("", section=section)

t3 = doc.add_table(rows=4, cols=3, section=section)
t3.set_cell_text(0, 0, "일정")
t3.set_cell_text(0, 1, "내용")
t3.set_cell_text(0, 2, "담당")

schedule = [
    ["3/15", "중간 보고", "기획팀"],
    ["4/01", "시스템 오픈", "개발팀"],
    ["4/30", "최종 보고", "전체"],
]
for i, row in enumerate(schedule):
    for j, text in enumerate(row):
        t3.set_cell_text(i + 1, j, text)

doc.add_paragraph("", section=section)
doc.add_paragraph("이상 보고를 마칩니다.", section=section)

doc.save_to_path("multi_table_report.hwpx")
print("생성 완료: multi_table_report.hwpx")
