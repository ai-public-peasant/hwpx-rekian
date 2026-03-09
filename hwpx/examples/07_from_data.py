#!/usr/bin/env python3
"""예제 7: 데이터(dict/list)로부터 문서 자동 생성

Python 데이터 구조를 받아 자동으로 HWPX 문서를 만드는 패턴.
실무에서 DB 조회 결과, API 응답, CSV 데이터 등을 문서화할 때 사용합니다.
"""

from hwpx import HwpxDocument


def create_report(title: str, sections_data: list[dict], output_path: str) -> None:
    """데이터로부터 보고서 HWPX를 생성합니다.

    Args:
        title: 문서 제목
        sections_data: 섹션별 데이터. 각 항목:
            - "heading": 소제목
            - "paragraphs": 본문 문단 리스트 (선택)
            - "table": {"headers": [...], "rows": [[...], ...]} (선택)
        output_path: 출력 파일 경로
    """
    doc = HwpxDocument.new()
    section = doc.sections[0]

    # 제목
    doc.add_paragraph(title, section=section)
    doc.add_paragraph("", section=section)

    for data in sections_data:
        # 소제목
        if "heading" in data:
            doc.add_paragraph(data["heading"], section=section)
            doc.add_paragraph("", section=section)

        # 본문 문단
        for para_text in data.get("paragraphs", []):
            doc.add_paragraph(para_text, section=section)

        # 표
        table_data = data.get("table")
        if table_data:
            headers = table_data["headers"]
            rows = table_data["rows"]
            num_rows = len(rows) + 1  # +1 for header
            num_cols = len(headers)

            table = doc.add_table(num_rows, num_cols, section=section)

            # 헤더
            for c, h in enumerate(headers):
                table.set_cell_text(0, c, h)

            # 데이터
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    table.set_cell_text(r + 1, c, str(cell))

        doc.add_paragraph("", section=section)

    doc.save_to_path(output_path)
    print(f"생성 완료: {output_path}")


# === 사용 예시 ===
if __name__ == "__main__":
    report_data = [
        {
            "heading": "1. 서버 현황",
            "table": {
                "headers": ["서버명", "IP", "상태", "CPU 사용률"],
                "rows": [
                    ["web-01", "10.0.1.10", "정상", "45%"],
                    ["web-02", "10.0.1.11", "정상", "52%"],
                    ["db-01", "10.0.2.10", "경고", "78%"],
                    ["db-02", "10.0.2.11", "정상", "35%"],
                ],
            },
        },
        {
            "heading": "2. 장애 이력",
            "paragraphs": [
                "금월 장애 발생 건수: 2건",
                "주요 원인: 디스크 용량 부족 (1건), 네트워크 타임아웃 (1건)",
            ],
            "table": {
                "headers": ["일시", "서버", "원인", "조치"],
                "rows": [
                    ["2/5 14:30", "db-01", "디스크 풀", "로그 정리 및 증설"],
                    ["2/12 09:15", "web-01", "네트워크 타임아웃", "스위치 재부팅"],
                ],
            },
        },
        {
            "heading": "3. 조치 계획",
            "paragraphs": [
                "- db-01 서버 디스크 500GB 증설 예정 (3월 1주)",
                "- 네트워크 모니터링 알림 임계치 조정",
                "- 월간 디스크 정리 자동화 스크립트 배포",
            ],
        },
    ]

    create_report("월간 인프라 운영 보고서", report_data, "infra_report.hwpx")
