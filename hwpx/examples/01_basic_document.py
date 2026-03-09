#!/usr/bin/env python3
"""예제 1: 기본 문서 생성

가장 기본적인 HWPX 문서를 만듭니다.
- 제목 + 본문 문단 여러 개
- 파일로 저장
"""

from hwpx import HwpxDocument

doc = HwpxDocument.new()
section = doc.sections[0]

doc.add_paragraph("프로젝트 보고서", section=section)
doc.add_paragraph("", section=section)  # 빈 줄
doc.add_paragraph("1. 프로젝트 개요", section=section)
doc.add_paragraph("본 프로젝트는 한글 문서 자동화를 위한 도구를 개발하는 것을 목표로 합니다.", section=section)
doc.add_paragraph("", section=section)
doc.add_paragraph("2. 추진 배경", section=section)
doc.add_paragraph("기존 수작업으로 진행하던 문서 작업을 자동화하여 업무 효율성을 높이고자 합니다.", section=section)
doc.add_paragraph("", section=section)
doc.add_paragraph("3. 기대 효과", section=section)
doc.add_paragraph("문서 작성 시간 50% 단축 및 오류 감소가 기대됩니다.", section=section)

doc.save_to_path("basic_document.hwpx")
print("생성 완료: basic_document.hwpx")
