#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HWP COM 핵심 유틸리티 — 초기화, 서식, 텍스트, 표, 네비게이션
다른 스크립트에서 import하여 사용.

사용법:
    from com_core import init_hwp, set_char, set_para, insert_text, setup_page
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ─── 색상 변환 ───────────────────────────────────────────────

def rgb_to_hwp(r, g, b):
    """RGB → HWP BGR 정수 변환. HWP는 BGR 순서를 사용한다."""
    return (b << 16) | (g << 8) | r


def rgb_to_hex(r, g, b):
    """RGB → #RRGGBB 문자열 (XML 후처리용)"""
    return f"#{r:02X}{g:02X}{b:02X}"


# ─── COM 초기화 ──────────────────────────────────────────────

def init_hwp(visible=True):
    """HWP COM 객체 초기화. 반드시 이 함수를 사용할 것.

    Returns:
        hwp: COM 객체 (HWPFrame.HwpObject)
    """
    import win32com.client as win32

    # 1) EnsureDispatch — Dispatch보다 안정적 (정적 바인딩)
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")

    # 2) 보안모듈 등록 — 없으면 SaveAs 시 보안 오류
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")

    # 3) 창 표시
    if visible:
        try:
            hwp.XHwpWindows.Item(0).Visible = True
        except Exception:
            pass

    return hwp


# ─── 글자 서식 ───────────────────────────────────────────────

def set_char(hwp, face_h="함초롬돋움", face_l="Times New Roman",
             pt=15, bold=0, color=(0, 0, 0), spacing=0, shade_color=None):
    """글자 서식 설정.

    Args:
        face_h: 한글 폰트명
        face_l: 영문 폰트명
        pt: 글자 크기 (포인트)
        bold: 굵기 (0 또는 1)
        color: (R, G, B) 튜플
        spacing: 자간 (-값=좁게)
        shade_color: (R, G, B) 음영색 또는 None (★ None이면 반드시 리셋)
    """
    hcs = hwp.HParameterSet.HCharShape
    hwp.HAction.GetDefault("CharShape", hcs.HSet)
    hcs.FaceNameHangul = face_h
    hcs.FaceNameLatin = face_l
    hcs.Height = int(pt * 100)
    hcs.Bold = int(bold)
    hcs.TextColor = rgb_to_hwp(*color)

    # 자간: 언어별 각각 설정
    for lang in ("Hangul", "Latin", "Hanja", "Japanese", "Other", "Symbol", "User"):
        try:
            setattr(hcs, f"Spacing{lang}", int(spacing))
        except Exception:
            pass

    # ★ ShadeColor 항상 설정 — 안 하면 이전 값이 계속 적용됨
    try:
        if shade_color:
            hcs.ShadeColor = rgb_to_hwp(*shade_color)
        else:
            hcs.ShadeColor = 0xFFFFFFFF  # "none" — 리셋
    except Exception:
        pass

    hwp.HAction.Execute("CharShape", hcs.HSet)


# ─── 문단 서식 ───────────────────────────────────────────────

def set_para(hwp, align=0, line_spacing=180, left=0, indent=0, right=0):
    """문단 서식 설정.

    Args:
        align: 0=양쪽, 1=왼쪽, 2=오른쪽, 3=가운데, 4=배분
        line_spacing: 줄간격 (%)
        left: LeftMargin (HWPUNIT) — 둘째 줄부터의 왼쪽 여백
        indent: Indentation (HWPUNIT) — 음수=내어쓰기, 양수=들여쓰기
        right: RightMargin (HWPUNIT)
    """
    hps = hwp.HParameterSet.HParaShape
    hwp.HAction.GetDefault("ParagraphShape", hps.HSet)
    hps.AlignType = align
    hps.LineSpacingType = 0  # PERCENT
    hps.LineSpacing = line_spacing
    hps.LeftMargin = int(left)
    hps.Indentation = int(indent)
    hps.RightMargin = int(right)
    hwp.HAction.Execute("ParagraphShape", hps.HSet)


# ─── 텍스트 삽입 ─────────────────────────────────────────────

def insert_text(hwp, text):
    """텍스트 삽입 (현재 커서 위치에)."""
    hins = hwp.HParameterSet.HInsertText
    hwp.HAction.GetDefault("InsertText", hins.HSet)
    hins.Text = text
    hwp.HAction.Execute("InsertText", hins.HSet)


# ─── 페이지 설정 ─────────────────────────────────────────────

def setup_page(hwp, paper_w=59528, paper_h=84188,
               left=5386, right=5386, top=4252, bottom=4252):
    """페이지 설정 (기본값: A4 세로, 여백 19/19/15/15mm).

    주요 단위 변환:
        1mm ≈ 283 HWPUNIT
        210mm = 59528, 297mm = 84188
        19mm = 5386, 15mm = 4252, 20mm = 5670, 10mm = 2835
    """
    sec = hwp.HParameterSet.HSecDef
    hwp.HAction.GetDefault("PageSetup", sec.HSet)
    sec.PageDef.PaperWidth = paper_w
    sec.PageDef.PaperHeight = paper_h
    sec.PageDef.Landscape = 0
    sec.PageDef.LeftMargin = left
    sec.PageDef.RightMargin = right
    sec.PageDef.TopMargin = top
    sec.PageDef.BottomMargin = bottom
    hwp.HAction.Execute("PageSetup", sec.HSet)


def get_body_width(hwp):
    """현재 페이지 설정에서 본문 영역 너비를 계산하여 반환."""
    sec = hwp.HParameterSet.HSecDef
    hwp.HAction.GetDefault("PageSetup", sec.HSet)
    pw = sec.PageDef.PaperWidth
    lm = sec.PageDef.LeftMargin
    rm = sec.PageDef.RightMargin
    return pw - lm - rm


# ─── 네비게이션 ──────────────────────────────────────────────

def force_out_of_table(hwp):
    """표 안에서 강제 탈출. 표 다음에 새 요소를 만들기 전에 반드시 호출."""
    for _ in range(4):
        for cmd in ("TableOut", "CloseEx", "Cancel"):
            try:
                hwp.Run(cmd)
            except Exception:
                pass
        try:
            hwp.Run("MoveDown")
        except Exception:
            pass


# ─── 표 생성 ─────────────────────────────────────────────────

def create_table(hwp, rows, cols, width, col_widths=None, height_type=0):
    """표 생성.

    Args:
        rows: 행 수
        cols: 열 수
        width: 전체 너비 (HWPUNIT). 167mm = 47339
        col_widths: 열별 너비 리스트 (합 = width). None이면 균등 분할
        height_type: 0=자동, 1=고정
    """
    tc = hwp.HParameterSet.HTableCreation
    hwp.HAction.GetDefault("TableCreate", tc.HSet)
    tc.Rows = rows
    tc.Cols = cols
    tc.WidthType = 2  # 절대 크기
    tc.HeightType = height_type
    tc.WidthValue = width

    if col_widths is None:
        col_widths = [width // cols] * cols
        col_widths[-1] = width - sum(col_widths[:-1])  # 나머지 보정

    for i, w in enumerate(col_widths):
        try:
            tc.ColWidth.SetItem(i, w)
        except Exception:
            pass

    hwp.HAction.Execute("TableCreate", tc.HSet)


def set_cell_bg(hwp, rgb):
    """셀 배경색 설정 시도 (COM). ★ 이것은 저장 시 반영되지 않을 수 있음.
    확실한 배경색은 xml_postprocess.py의 add_cell_colors()를 사용."""
    cf = hwp.HParameterSet.HCellBorderFill
    hwp.HAction.GetDefault("CellBorderFill", cf.HSet)
    fa = cf.FillAttr
    color = rgb_to_hwp(*rgb)
    for key in ("type", "Type"):
        try: setattr(fa, key, 1)
        except: pass
    for key in ("WinBrushFaceColor", "FaceColor"):
        try: setattr(fa, key, color)
        except: pass
    try: setattr(fa, "WindowsBrush", 1)
    except: pass
    try: setattr(fa, "WinBrushAlpha", 0)
    except: pass
    hwp.HAction.Execute("CellBorderFill", cf.HSet)


# ─── 편의 함수 ──────────────────────────────────────────────

def line(hwp, text, face_h="함초롬돋움", pt=15, bold=0, color=(0, 0, 0),
         align=0, ls=180, breaks=1, left=0, indent=0, spacing=0):
    """한 줄 텍스트 작성 (서식 + 삽입 + 줄바꿈)."""
    set_char(hwp, face_h=face_h, pt=pt, bold=bold, color=color, spacing=spacing)
    set_para(hwp, align=align, line_spacing=ls, left=left, indent=indent)
    insert_text(hwp, text)
    for _ in range(breaks):
        hwp.Run("BreakPara")


def save_and_quit(hwp, output_path):
    """HWPX로 저장하고 종료."""
    ok = hwp.SaveAs(str(output_path), "HWPX", "")
    hwp.Quit()
    if not ok:
        raise RuntimeError(f"SaveAs failed: {output_path}")
    return ok
