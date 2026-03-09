#!/usr/bin/env python3
"""예제 6: 메모(주석)가 포함된 문서 생성

문단에 메모를 달아 리뷰 코멘트를 남깁니다.
"""

from hwpx import HwpxDocument

doc = HwpxDocument.new()
section = doc.sections[0]

# 본문 작성
doc.add_paragraph("제안서 초안", section=section)
doc.add_paragraph("", section=section)

para1 = doc.add_paragraph(
    "본 제안은 AI 기반 문서 자동화 시스템 도입을 제안합니다.",
    section=section,
)
doc.add_paragraph("", section=section)

para2 = doc.add_paragraph(
    "예상 비용은 총 2억원이며, 도입 기간은 6개월입니다.",
    section=section,
)
doc.add_paragraph("", section=section)

para3 = doc.add_paragraph(
    "ROI는 1년 내 150%로 예상됩니다.",
    section=section,
)

# 메모 추가
doc.add_memo_with_anchor(
    "도입 배경을 좀 더 구체적으로 작성 필요",
    paragraph=para1,
    memo_shape_id_ref="0",
)

doc.add_memo_with_anchor(
    "비용 산출 근거 첨부 요망",
    paragraph=para2,
    memo_shape_id_ref="0",
)

doc.add_memo_with_anchor(
    "ROI 산정 기준 확인 필요 - 경영기획팀 검토 요청",
    paragraph=para3,
    memo_shape_id_ref="0",
)

doc.save_to_path("memo_document.hwpx")
print("생성 완료: memo_document.hwpx")
