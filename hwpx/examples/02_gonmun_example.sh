#!/bin/bash
# 02_gonmun_example.sh ??怨듬Ц ?쒗뵆由우쑝濡?臾몄꽌 鍮뚮뱶 ?덉젣
#
# 怨듬Ц ?쒗뵆由우쓽 placeholder瑜??ㅼ젣 ?댁슜?쇰줈 援먯껜??section0.xml???묒꽦?섏뿬 鍮뚮뱶?쒕떎.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${VENV:-$(cd "$SKILL_DIR/../.." && pwd)/.venv/bin/activate}"
source "$VENV"

# 怨듬Ц ?쒗뵆由우쑝濡?鍮뚮뱶 (湲곕낯 placeholder ?ы븿)
OUTPUT="/tmp/gonmun_example.hwpx"
python3 "$SKILL_DIR/scripts/build_hwpx.py" \
  --template gonmun \
  --title "異쒗뙋 肄섑뀗痢??묒쓽 嫄? \
  --creator "怨⑤뱺?섎퉿" \
  --output "$OUTPUT"

# 寃利?
python3 "$SKILL_DIR/scripts/validate.py" "$OUTPUT"

# ?띿뒪??異붿텧 ?뺤씤
echo ""
echo "=== 異붿텧???띿뒪??==="
python3 "$SKILL_DIR/scripts/text_extract.py" "$OUTPUT"

echo ""
echo "?앹꽦 ?꾨즺: $OUTPUT"

