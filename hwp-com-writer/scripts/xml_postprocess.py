#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HWPX XML 후처리 유틸리티
COM이 생성한 HWPX 파일에서 COM으로 처리할 수 없는 부분을 보정한다.

주요 기능:
1. apply_table_postprocess()    — 표 treatAsChar + 너비 강제
2. apply_indent_unit_postprocess() — 내어쓰기 단위 CHAR→HWPUNIT
3. apply_spacing_optimization()    — 자간 최적화 (마지막 줄 1~4글자)
4. add_cell_colors()               — 셀 배경색 추가 (borderFill)

★ 모든 정규식은 네임스페이스 독립적 (ns0:, ns1:, hp:, hh: 등 모두 매칭)
"""
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path


# ─── 공통: HWPX ZIP 열기/닫기 ────────────────────────────────

def _unzip_hwpx(hwpx_path):
    """HWPX를 임시 디렉토리에 풀기. (tmp_dir, header_path, section_paths) 반환."""
    tmp_dir = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        z.extractall(tmp_dir)
    header = tmp_dir / "Contents" / "header.xml"
    sections = sorted((tmp_dir / "Contents").glob("section*.xml"))
    return tmp_dir, header, sections


def _rezip_hwpx(hwpx_path, tmp_dir):
    """임시 디렉토리를 HWPX로 재압축."""
    hwpx = Path(hwpx_path)
    with zipfile.ZipFile(hwpx, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(tmp_dir)
                if str(arcname) == 'mimetype':
                    zout.write(fp, arcname, compress_type=zipfile.ZIP_STORED)
                else:
                    zout.write(fp, arcname)


def _cleanup(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)


# ─── 1. 표 속성 후처리 (treatAsChar + 너비) ──────────────────

def apply_table_postprocess(hwpx_path, summary_width=47339):
    """표 treatAsChar=1 설정 + 보고요지 표 너비 강제.

    Args:
        hwpx_path: HWPX 파일 경로
        summary_width: 1열 표(보고요지)의 너비 (HWPUNIT). 167mm = 47339
    """
    tmp_dir, _, sections = _unzip_hwpx(hwpx_path)
    try:
        chapter_count = 0
        summary_count = 0

        for sec_file in sections:
            content = sec_file.read_text(encoding="utf-8")

            def fix_tbl(m):
                nonlocal chapter_count, summary_count
                tbl_block = m.group(0)
                is_chapter = 'colCnt="4"' in tbl_block
                is_summary = 'colCnt="1"' in tbl_block
                if not is_chapter and not is_summary:
                    return tbl_block

                # pos 태그: treatAsChar=1
                def fix_pos(pm):
                    nonlocal chapter_count, summary_count
                    pos_tag = pm.group(0)
                    pos_tag = re.sub(r'treatAsChar="[^"]*"', 'treatAsChar="1"', pos_tag)
                    if is_chapter:
                        pos_tag = re.sub(r'horzRelTo="[^"]*"', 'horzRelTo="PARA"', pos_tag)
                        pos_tag = re.sub(r'horzAlign="[^"]*"', 'horzAlign="LEFT"', pos_tag)
                        chapter_count += 1
                    elif is_summary:
                        summary_count += 1
                    return pos_tag

                # 네임스페이스 독립 매칭
                tbl_block = re.sub(r'<[^>]*:pos\b[^/]*/>', fix_pos, tbl_block, count=1)
                tbl_block = re.sub(r'<pos\b[^/]*/>', fix_pos, tbl_block, count=1)

                # 보고요지 표 너비 강제
                if is_summary and summary_width:
                    tbl_block = re.sub(
                        r'(<[^>]*:sz\b[^>]*)\bwidth="[^"]*"',
                        rf'\1width="{summary_width}"', tbl_block
                    )
                    tbl_block = re.sub(
                        r'(<sz\b[^>]*)\bwidth="[^"]*"',
                        rf'\1width="{summary_width}"', tbl_block
                    )
                return tbl_block

            content = re.sub(
                r'<[^>]*:tbl\b[^>]*>.*?</[^>]*:tbl>',
                fix_tbl, content, flags=re.DOTALL
            )
            sec_file.write_text(content, encoding="utf-8")

        _rezip_hwpx(hwpx_path, tmp_dir)
        print(f"[tbl-postprocess] chapter={chapter_count}, summary={summary_count}")
    except Exception as e:
        print(f"[warn] table postprocess failed: {e}")
    finally:
        _cleanup(tmp_dir)


# ─── 2. 내어쓰기 단위 수정 (CHAR → HWPUNIT) ─────────────────

def apply_indent_unit_postprocess(hwpx_path):
    """HwpUnitChar switch 블록의 margin을 default 값으로 통일.

    COM이 생성한 HWPX에는 모든 paraPr에 switch 블록이 존재:
    - HwpUnitChar case: unit="CHAR" (HWP 새 버전이 우선 읽음 → "ch" 표시)
    - default case: unit="HWPUNIT" (정상 값)
    해결: HwpUnitChar case의 margin을 default 값으로 교체.
    """
    tmp_dir, header_path, _ = _unzip_hwpx(hwpx_path)
    try:
        content = header_path.read_text(encoding="utf-8")
        fixed = 0

        def fix_switch(m):
            nonlocal fixed
            switch_block = m.group(0)

            default_match = re.search(
                r'<[^>]*:default>(.*?)</[^>]*:default>',
                switch_block, re.DOTALL
            )
            if not default_match:
                return switch_block

            def_margin = re.search(
                r'(<[^>]*:margin>.*?</[^>]*:margin>)',
                default_match.group(1), re.DOTALL
            )
            if not def_margin:
                return switch_block

            case_match = re.search(
                r'(<[^>]*:case[^>]*HwpUnitChar[^>]*>)(.*?)(</[^>]*:case>)',
                switch_block, re.DOTALL
            )
            if not case_match:
                return switch_block

            case_margin = re.search(
                r'<[^>]*:margin>.*?</[^>]*:margin>',
                case_match.group(2), re.DOTALL
            )
            if not case_margin:
                return switch_block

            if case_margin.group(0) == def_margin.group(1):
                return switch_block  # 이미 동일

            new_case = case_match.group(2).replace(
                case_margin.group(0), def_margin.group(1), 1
            )
            fixed += 1
            return switch_block.replace(case_match.group(2), new_case, 1)

        content = re.sub(
            r'<[^>]*:switch>.*?</[^>]*:switch>',
            fix_switch, content, flags=re.DOTALL
        )
        header_path.write_text(content, encoding="utf-8")
        _rezip_hwpx(hwpx_path, tmp_dir)
        print(f"[indent-unit] fixed {fixed} HwpUnitChar switch blocks")
    except Exception as e:
        print(f"[warn] indent unit postprocess failed: {e}")
    finally:
        _cleanup(tmp_dir)


# ─── 3. 자간 최적화 ─────────────────────────────────────────

def apply_spacing_optimization(hwpx_path, spacing_adjust=-3,
                                min_text_len=15, min_horzsize=30000):
    """마지막 줄에 1~4글자만 남은 단락의 자간을 줄여 위로 올림.

    lineseg textpos로 마지막 줄 글자수 판별 → charPr spacing 축소 복제본 생성.

    Args:
        spacing_adjust: 자간 축소량 (기본 -3)
        min_text_len: 이보다 짧은 텍스트(제목 등)는 제외
        min_horzsize: 이보다 좁은 셀(표 내부)은 제외
    """
    hwpx = Path(hwpx_path)
    tmp_dir, header_path, sections = _unzip_hwpx(hwpx_path)
    try:
        hdr = header_path.read_text(encoding="utf-8")

        # 기존 charPr 최대 ID
        # 네임스페이스 독립적으로 매칭
        charpr_ids = [int(x) for x in re.findall(r'<[^>]*:charPr\b[^>]*\bid="(\d+)"', hdr)]
        if not charpr_ids:
            charpr_ids = [int(x) for x in re.findall(r'<charPr\b[^>]*\bid="(\d+)"', hdr)]
        max_id = max(charpr_ids) if charpr_ids else 0
        next_id = max_id + 1

        cloned = {}  # original_id -> new_id
        new_charpr_xml = []
        optimized = 0

        for sec_file in sections:
            sec = sec_file.read_text(encoding="utf-8")

            def process_para(pm):
                nonlocal next_id, optimized
                p_open, p_body, p_close = pm.group(1), pm.group(2), pm.group(3)

                # lineseg 추출
                ls_tags = re.findall(
                    r'<[^>]*lineseg[^>]*textpos="(\d+)"[^>]*horzsize="(\d+)"[^>]*/>', p_body
                )
                if len(ls_tags) < 2:
                    return pm.group(0)

                if int(ls_tags[-1][1]) < min_horzsize:
                    return pm.group(0)

                texts = re.findall(r'>([^<]+)</', p_body)
                total_text = "".join(t for t in texts if t.strip())
                if len(total_text) < min_text_len:
                    return pm.group(0)

                last_line_chars = len(total_text) - int(ls_tags[-1][0])
                if not (1 <= last_line_chars <= 4):
                    return pm.group(0)

                run_refs = re.findall(r'charPrIDRef="(\d+)"', p_body)
                if not run_refs:
                    return pm.group(0)

                new_body = p_body
                for orig_id_str in set(run_refs):
                    orig_id = int(orig_id_str)
                    if orig_id in cloned:
                        new_id_val = cloned[orig_id]
                    else:
                        # 원본 charPr 찾기 (네임스페이스 독립)
                        cp_match = re.search(
                            r'(<[^>]*:charPr\b[^>]*\bid="' + str(orig_id) + r'"[^>]*>.*?</[^>]*:charPr>)',
                            hdr, re.DOTALL
                        )
                        if not cp_match:
                            continue
                        cp_block = cp_match.group(1)
                        new_id_val = next_id
                        next_id += 1

                        new_block = re.sub(
                            r'id="' + str(orig_id) + r'"',
                            f'id="{new_id_val}"', cp_block, count=1
                        )

                        def adjust_spacing(sm):
                            tag = sm.group(0)
                            for lang in ("hangul", "latin", "hanja", "japanese",
                                         "other", "symbol", "user"):
                                def reduce(vm):
                                    return f'{lang}="{int(vm.group(1)) + spacing_adjust}"'
                                tag = re.sub(f'{lang}="(-?\\d+)"', reduce, tag)
                            return tag

                        new_block = re.sub(
                            r'<[^>]*:spacing\b[^/]*/>', adjust_spacing, new_block
                        )
                        cloned[orig_id] = new_id_val
                        new_charpr_xml.append(new_block)

                    new_body = new_body.replace(
                        f'charPrIDRef="{orig_id_str}"',
                        f'charPrIDRef="{new_id_val}"'
                    )

                optimized += 1
                return p_open + new_body + p_close

            sec = re.sub(
                r'(<[^>]*:p\b[^>]*>)(.*?)(</[^>]*:p>)',
                process_para, sec, flags=re.DOTALL
            )
            sec_file.write_text(sec, encoding="utf-8")

        # header.xml에 새 charPr 삽입 + itemCnt 업데이트
        if new_charpr_xml:
            insert_xml = "\n".join(new_charpr_xml)
            hdr = re.sub(
                r'(</[^>]*:charPrs>)', insert_xml + r'\1', hdr
            )
            new_count = len(charpr_ids) + len(new_charpr_xml)
            hdr = re.sub(
                r'(<[^>]*:charPrs\b[^>]*)\bitemCnt="\d+"',
                rf'\1itemCnt="{new_count}"', hdr
            )
            header_path.write_text(hdr, encoding="utf-8")

        _rezip_hwpx(hwpx_path, tmp_dir)
        print(f"[spacing] optimized {optimized} paragraphs, "
              f"created {len(new_charpr_xml)} new charPr entries")
    except Exception as e:
        print(f"[warn] spacing optimization failed: {e}")
    finally:
        _cleanup(tmp_dir)


# ─── 4. 셀 배경색 추가 ──────────────────────────────────────

def add_cell_colors(hwpx_path, cell_color_map):
    """셀 배경색을 XML로 직접 추가.

    COM의 CellBorderFill Execute()는 배경색을 저장하지 않으므로
    header.xml에 borderFill을 직접 추가하고 section0.xml의
    tc borderFillIDRef를 교체한다.

    Args:
        hwpx_path: HWPX 파일 경로
        cell_color_map: {셀순서(0-based): "#RRGGBB"} 딕셔너리
            예: {0: "#364878", 1: "#B3C5F3", 2: "#D6D6D6"}
    """
    if not cell_color_map:
        return

    tmp_dir, header_path, sections = _unzip_hwpx(hwpx_path)
    try:
        hdr = header_path.read_text(encoding="utf-8")

        # 기존 borderFill 최대 ID + itemCnt
        bf_ids = [int(x) for x in re.findall(r'<[^>]*:borderFill\b[^>]*\bid="(\d+)"', hdr)]
        if not bf_ids:
            bf_ids = [int(x) for x in re.findall(r'borderFill\b[^>]*\bid="(\d+)"', hdr)]
        max_bf_id = max(bf_ids) if bf_ids else 0

        # 테두리 있는 기존 borderFill을 템플릿으로 사용 (보통 id=3 정도)
        template_match = re.search(
            r'(<[^>]*:borderFill\b[^>]*\bid="(\d+)"[^>]*>)(.*?)(</[^>]*:borderFill>)',
            hdr, re.DOTALL
        )
        if not template_match:
            print("[warn] no borderFill template found")
            _cleanup(tmp_dir)
            return

        template_open = template_match.group(1)
        template_body = template_match.group(3)
        template_close = template_match.group(4)

        # 색상별 새 borderFill 생성
        unique_colors = sorted(set(cell_color_map.values()))
        color_to_id = {}
        new_bf_xml = []

        for color_hex in unique_colors:
            new_id = max_bf_id + 1 + len(new_bf_xml)
            color_to_id[color_hex] = new_id

            # 템플릿 복제 + ID 교체
            new_open = re.sub(r'id="\d+"', f'id="{new_id}"', template_open, count=1)

            # fillBrush 교체/추가
            new_body = re.sub(
                r'<[^>]*:fillBrush>.*?</[^>]*:fillBrush>',
                '', template_body, flags=re.DOTALL
            )
            # 네임스페이스 접두사 추출
            ns_match = re.search(r'<([^:>]+):borderFill', template_open)
            ns_prefix = ns_match.group(1) if ns_match else "hh"
            # hc 접두사 추측 (보통 hh → hc)
            hc_prefix = ns_prefix.replace("hh", "hc") if "hh" in ns_prefix else ns_prefix

            fill_xml = (
                f'<{hc_prefix}:fillBrush>'
                f'<{hc_prefix}:winBrush faceColor="{color_hex}" '
                f'hatchColor="#FFFFFF" alpha="0"/>'
                f'</{hc_prefix}:fillBrush>'
            )
            new_body = new_body.rstrip() + fill_xml

            new_bf_xml.append(new_open + new_body + template_close)

        # header.xml에 삽입 + itemCnt 업데이트
        insert_point = re.search(r'</[^>]*:borderFills>', hdr)
        if insert_point:
            hdr = hdr[:insert_point.start()] + "\n".join(new_bf_xml) + "\n" + hdr[insert_point.start():]

        new_count = len(bf_ids) + len(new_bf_xml)
        hdr = re.sub(
            r'(<[^>]*:borderFills\b[^>]*)\bitemCnt="\d+"',
            rf'\1itemCnt="{new_count}"', hdr
        )
        header_path.write_text(hdr, encoding="utf-8")

        # section0.xml에서 tc borderFillIDRef 교체
        for sec_file in sections:
            sec = sec_file.read_text(encoding="utf-8")
            tc_count = [0]

            def replace_tc(m):
                idx = tc_count[0]
                tc_count[0] += 1
                if idx in cell_color_map:
                    color_hex = cell_color_map[idx]
                    new_id = color_to_id[color_hex]
                    return re.sub(
                        r'borderFillIDRef="[^"]*"',
                        f'borderFillIDRef="{new_id}"',
                        m.group(0)
                    )
                return m.group(0)

            sec = re.sub(r'<[^>]*:tc\b[^>]*>', replace_tc, sec)
            sec_file.write_text(sec, encoding="utf-8")

        _rezip_hwpx(hwpx_path, tmp_dir)
        print(f"[cell-colors] added {len(new_bf_xml)} borderFills, "
              f"mapped {len(cell_color_map)} cells")
    except Exception as e:
        print(f"[warn] cell color postprocess failed: {e}")
    finally:
        _cleanup(tmp_dir)


# ─── 파이프라인 ──────────────────────────────────────────────

def postprocess_pipeline(hwpx_path, cell_colors=None,
                          fix_treat_as_char=True, fix_indent_unit=True,
                          optimize_spacing=True, table_width=47339):
    """XML 후처리 전체 파이프라인.

    Args:
        hwpx_path: HWPX 파일 경로
        cell_colors: {셀순서: "#RRGGBB"} 딕셔너리 또는 None
        fix_treat_as_char: 표 treatAsChar=1 적용 여부
        fix_indent_unit: 내어쓰기 단위 CHAR→HWPUNIT 수정 여부
        optimize_spacing: 자간 최적화 여부
        table_width: 보고요지 표 너비 (HWPUNIT)
    """
    print(f"[postprocess] Starting pipeline for {hwpx_path}")

    if fix_treat_as_char:
        apply_table_postprocess(hwpx_path, summary_width=table_width)

    if fix_indent_unit:
        apply_indent_unit_postprocess(hwpx_path)

    if optimize_spacing:
        apply_spacing_optimization(hwpx_path)

    if cell_colors:
        add_cell_colors(hwpx_path, cell_colors)

    print(f"[postprocess] Pipeline complete")
