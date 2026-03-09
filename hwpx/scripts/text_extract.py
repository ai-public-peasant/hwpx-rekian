#!/usr/bin/env python3
"""Extract text from an HWPX document without external hwpx package dependency.

Usage:
    python text_extract.py document.hwpx
    python text_extract.py document.hwpx --format markdown
    python text_extract.py document.hwpx --include-tables
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HP_NS = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
HS_NS = 'http://www.hancom.co.kr/hwpml/2011/section'
NS = {'hp': HP_NS, 'hs': HS_NS}

TAG_SEC = f'{{{HS_NS}}}sec'
TAG_P = f'{{{HP_NS}}}p'
TAG_T = f'{{{HP_NS}}}t'
TAG_RUN = f'{{{HP_NS}}}run'
TAG_TBL = f'{{{HP_NS}}}tbl'
TAG_SUBLIST = f'{{{HP_NS}}}subList'
TAG_TC = f'{{{HP_NS}}}tc'


def open_section_root(hwpx_path: str) -> ET.Element:
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(hwpx_path, 'r') as zf:
            zf.extract('Contents/section0.xml', tmpdir)
        section_path = Path(tmpdir) / 'Contents' / 'section0.xml'
        root = ET.parse(section_path).getroot()
        sec = root if root.tag == TAG_SEC else root.find(f'.//{TAG_SEC}')
        return sec if sec is not None else root
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def get_text_recursive(node: ET.Element, *, include_tables: bool) -> str:
    parts: list[str] = []

    if node.tag == TAG_T and node.text:
        parts.append(node.text)

    for child in node:
        if child.tag == TAG_TBL:
            if include_tables:
                parts.append(get_table_text(child, include_tables=include_tables))
            continue
        parts.append(get_text_recursive(child, include_tables=include_tables))

    return ''.join(parts)


def get_table_text(tbl: ET.Element, *, include_tables: bool) -> str:
    rows: list[str] = []
    for tc in tbl.iter(TAG_TC):
        cell_parts: list[str] = []
        for sublist in tc.findall(f'.//{TAG_SUBLIST}'):
            for para in sublist.findall(TAG_P):
                text = get_paragraph_text(para, include_tables=include_tables).strip()
                if text:
                    cell_parts.append(text)
        cell_text = ' '.join(cell_parts).strip()
        if cell_text:
            rows.append(cell_text)
    return '\n'.join(rows)


def get_paragraph_text(para: ET.Element, *, include_tables: bool) -> str:
    parts: list[str] = []
    for run in para.findall(TAG_RUN):
        parts.append(get_text_recursive(run, include_tables=include_tables))
    return ''.join(parts)


def iter_paragraphs(root: ET.Element) -> list[dict[str, str | bool]]:
    paragraphs: list[dict[str, str | bool]] = []

    def walk(node: ET.Element, *, nested: bool = False) -> None:
        for para in node.findall(TAG_P):
            text = get_paragraph_text(para, include_tables=False).strip()
            if text:
                paragraphs.append({'text': text, 'nested': nested})
            for tbl in para.findall(f'.//{TAG_TBL}'):
                for sublist in tbl.findall(f'.//{TAG_SUBLIST}'):
                    walk(sublist, nested=True)

    walk(root, nested=False)
    return paragraphs


def extract_plain(hwpx_path: str, *, include_tables: bool = False) -> str:
    root = open_section_root(hwpx_path)
    lines: list[str] = []
    for para in root.findall(TAG_P):
        text = get_paragraph_text(para, include_tables=include_tables).strip()
        if text:
            lines.append(text)
    return '\n'.join(lines)


def extract_markdown(hwpx_path: str) -> str:
    root = open_section_root(hwpx_path)
    lines: list[str] = []
    for para in iter_paragraphs(root):
        text = str(para['text'])
        if not text:
            continue
        if para['nested']:
            lines.append(f'  {text}')
        else:
            lines.append(text)
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Extract text from an HWPX document')
    parser.add_argument('input', help='Path to .hwpx file')
    parser.add_argument('--format', '-f', choices=['plain', 'markdown'], default='plain')
    parser.add_argument('--include-tables', action='store_true', help='Include text from tables and nested objects (plain mode)')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(f'Error: File not found: {args.input}', file=sys.stderr)
        sys.exit(1)

    result = extract_markdown(args.input) if args.format == 'markdown' else extract_plain(args.input, include_tables=args.include_tables)

    if args.output:
        Path(args.output).write_text(result, encoding='utf-8')
        print(f'Extracted to: {args.output}', file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
