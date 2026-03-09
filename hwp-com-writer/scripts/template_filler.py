#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HWPX 템플릿 빈칸 채우기 — COM 없이 XML 직접 편집만으로 동작

기존 HWPX 서식의 빈 불릿(❍, ◦, - 등)을 찾아 내용을 채워넣는다.
한글 프로그램이 설치되어 있지 않아도 동작한다.

사용법:
    from template_filler import fill_template

    fill_template(
        template="양식.hwpx",
        output="완성본.hwpx",
        summary=["◦ 요약1", "◦ 요약2"],
        body=["  ❍ 본문1", "  ❍ 본문2", "    - 세부사항"]
    )
"""
import os
import re
import sys
import shutil
import zipfile
from pathlib import Path

# Windows cp949 출력 문제 방지
if sys.platform == 'win32':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass


def fill_template(template, output, summary=None, body=None, temp_dir=None):
    """HWPX 템플릿의 빈 불릿에 내용을 채워넣기.

    Args:
        template: 원본 HWPX 템플릿 경로
        output: 출력 HWPX 경로
        summary: 요약 불릿 리스트 (◦ 로 시작하는 항목들)
        body: 본문 불릿 리스트 (❍, - 로 시작하는 항목들)
        temp_dir: 임시 디렉토리 경로 (None이면 자동 생성)

    Returns:
        int: 교체된 불릿 수
    """
    if summary is None:
        summary = []
    if body is None:
        body = []

    if temp_dir is None:
        temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), 'hwpx_template_fill')

    # 1. Unzip
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)
    with zipfile.ZipFile(template, 'r') as z:
        z.extractall(temp_dir)
    print(f"[1] Template unzipped: {template}")

    # 2. Read section0.xml
    sec_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    with open(sec_path, 'r', encoding='utf-8') as f:
        xml = f.read()

    # 3. Find <*:t> elements (정확히 :t 태그만, :text/:table 등 제외)
    t_pat = re.compile(
        r'(<[^>]*?:t>|<[^>]*?:t\s[^>]*?>)'  # opening: <*:t> or <*:t attr>
        r'(.*?)'                               # content (non-greedy)
        r'(</[^>]*?:t>)',                      # closing: </*:t>
        re.DOTALL
    )
    matches = list(t_pat.finditer(xml))
    print(f"[2] Found {len(matches)} <t> elements")

    # 4. 불릿 분류
    summary_positions = []  # ◦ (U+25E6)
    body_positions = []     # ❍ (U+274D) 또는 - (dash)

    for m in matches:
        content = m.group(2).strip()
        # ◦ — 요약 박스
        if content in ('\u25e6', '\u25e6 '):
            summary_positions.append(m)
        # ❍ — 본문 1레벨
        elif content in ('\u274d', '\u274d '):
            body_positions.append(m)
        # - — 본문 2레벨 (독립된 대시만)
        elif content in ('-', '- '):
            body_positions.append(m)

    # 공백으로 감싸진 불릿도 확인 (확장 검색)
    expected_body = len(body)
    if len(body_positions) < expected_body:
        for m in matches:
            if m in summary_positions or m in body_positions:
                continue
            stripped = m.group(2).strip()
            if stripped == '\u274d':
                body_positions.append(m)
            elif stripped == '-':
                body_positions.append(m)
        body_positions.sort(key=lambda x: x.start())

    print(f"[3] Summary: {len(summary_positions)}, Body: {len(body_positions)}")

    # 5. 내용 채우기
    replacements = []

    for i, m in enumerate(summary_positions):
        if i < len(summary):
            replacements.append((m.start(2), m.end(2), summary[i]))

    for i, m in enumerate(body_positions):
        if i < len(body):
            replacements.append((m.start(2), m.end(2), body[i]))

    # 뒤에서부터 교체 (위치 보존)
    replacements.sort(key=lambda x: x[0], reverse=True)

    for start, end, text in replacements:
        xml = xml[:start] + text + xml[end:]

    print(f"[4] Made {len(replacements)} replacements")

    # 6. 저장
    with open(sec_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    # 7. Repack
    if os.path.exists(output):
        os.remove(output)

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(temp_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, temp_dir)
                if arcname == 'mimetype':
                    zout.write(fpath, arcname, compress_type=zipfile.ZIP_STORED)
                else:
                    zout.write(fpath, arcname)

    # 정리
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"[5] Output: {output} ({os.path.getsize(output)} bytes)")
    return len(replacements)


if __name__ == '__main__':
    # 사용 예시
    import argparse
    parser = argparse.ArgumentParser(description='HWPX 템플릿 빈칸 채우기')
    parser.add_argument('template', help='HWPX 템플릿 경로')
    parser.add_argument('output', help='출력 HWPX 경로')
    args = parser.parse_args()

    # 예시 데이터 (실제 사용 시 교체)
    fill_template(
        template=args.template,
        output=args.output,
        summary=["◦ 요약 항목 1", "◦ 요약 항목 2"],
        body=["  ❍ 본문 항목 1", "  ❍ 본문 항목 2"]
    )
