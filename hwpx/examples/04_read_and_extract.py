#!/usr/bin/env python3
"""예제 4: 기존 HWPX 문서 읽기 및 텍스트 추출

기존 문서를 열어서:
- 전체 텍스트 추출 (표 포함)
- 문단별 순회
- 섹션 정보 확인
"""

import sys

from hwpx import HwpxDocument, TextExtractor

if len(sys.argv) < 2:
    print("사용법: python 04_read_and_extract.py <문서경로.hwpx>")
    sys.exit(1)

hwpx_path = sys.argv[1]

# 방법 1: TextExtractor로 전체 텍스트 추출
print("=== 전체 텍스트 (표 포함) ===")
with TextExtractor(hwpx_path) as ext:
    text = ext.extract_text(
        include_nested=True,
        object_behavior="nested",
        skip_empty=True,
    )
    print(text)

print()

# 방법 2: 문단별 순회
print("=== 문단별 순회 ===")
with TextExtractor(hwpx_path) as ext:
    for section in ext.iter_sections():
        print(f"\n[섹션 {section.index}: {section.name}]")
        for para in ext.iter_paragraphs(section, include_nested=False):
            para_text = para.text()
            if para_text.strip():
                print(f"  문단 {para.index}: {para_text[:80]}")

print()

# 방법 3: HwpxDocument로 구조 확인
print("=== 문서 구조 ===")
doc = HwpxDocument.open(hwpx_path)
print(f"섹션 수: {len(doc.sections)}")
print(f"전체 문단 수: {len(doc.paragraphs)}")
for i, section in enumerate(doc.sections):
    print(f"  섹션 {i}: 문단 {len(section.paragraphs)}개")
doc.close()
