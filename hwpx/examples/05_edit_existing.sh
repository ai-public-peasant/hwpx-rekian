#!/bin/bash
# 예제 5: 기존 문서의 XML을 직접 편집하는 워크플로우
#
# python-hwpx API로 처리하기 어려운 작업 (페이지 설정, 글꼴 변경 등)에 사용합니다.
# 1) unpack: HWPX → 디렉토리 (XML pretty-print)
# 2) XML 직접 편집 (sed, Claude Edit 도구 등)
# 3) pack: 디렉토리 → HWPX (mimetype 순서 보장)
#
# 사용법:
#   bash 05_edit_existing.sh input.hwpx

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$SCRIPT_DIR/../../../.venv/bin/activate"

if [ -z "$1" ]; then
    echo "사용법: bash $0 <input.hwpx>"
    exit 1
fi

INPUT="$1"
BASENAME=$(basename "$INPUT" .hwpx)
WORK_DIR="./${BASENAME}_unpacked"
OUTPUT="./${BASENAME}_edited.hwpx"

echo "=== Step 1: Unpack ==="
source "$VENV"
python3 "$SCRIPT_DIR/scripts/office/unpack.py" "$INPUT" "$WORK_DIR"

echo ""
echo "=== 편집 대상 파일 ==="
echo "  본문: $WORK_DIR/Contents/section0.xml"
echo "  스타일: $WORK_DIR/Contents/header.xml"
echo "  설정: $WORK_DIR/settings.xml"
echo ""
echo "이제 XML 파일을 편집하세요."
echo "편집 완료 후 다음 명령으로 다시 패키징합니다:"
echo ""
echo "  source $VENV"
echo "  python3 $SCRIPT_DIR/scripts/office/pack.py $WORK_DIR $OUTPUT"
echo "  python3 $SCRIPT_DIR/scripts/validate.py $OUTPUT"
