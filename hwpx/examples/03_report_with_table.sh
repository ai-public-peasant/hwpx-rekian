#!/bin/bash
# 03_report_with_table.sh — 표 포함 보고서 예제
#
# 보고서 템플릿을 사용하고, 커스텀 section0.xml로 표를 포함한 보고서를 생성한다.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${VENV:-$(cd "$SKILL_DIR/../.." && pwd)/.venv/bin/activate}"
source "$VENV"

# section0.xml 작성 (표 포함)
SECTION=$(mktemp /tmp/section0_XXXX.xml)
cat > "$SECTION" << 'XMLEOF'
<?xml version='1.0' encoding='UTF-8'?>
<hs:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
        xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section">
  <!-- secPr: A4 세로 -->
  <hp:p id="1000000001" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">
        <hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>
        <hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>
        <hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>
        <hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>
        <hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY">
          <hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/>
        </hp:pagePr>
        <hp:footNotePr>
          <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>
          <hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>
          <hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/>
          <hp:numbering type="CONTINUOUS" newNum="1"/>
          <hp:placement place="EACH_COLUMN" beneathText="0"/>
        </hp:footNotePr>
        <hp:endNotePr>
          <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>
          <hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>
          <hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>
          <hp:numbering type="CONTINUOUS" newNum="1"/>
          <hp:placement place="END_OF_DOCUMENT" beneathText="0"/>
        </hp:endNotePr>
        <hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">
          <hp:offset left="1417" right="1417" top="1417" bottom="1417"/>
        </hp:pageBorderFill>
        <hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">
          <hp:offset left="1417" right="1417" top="1417" bottom="1417"/>
        </hp:pageBorderFill>
        <hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">
          <hp:offset left="1417" right="1417" top="1417" bottom="1417"/>
        </hp:pageBorderFill>
      </hp:secPr>
      <hp:ctrl>
        <hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/>
      </hp:ctrl>
    </hp:run>
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>

  <!-- 빈 줄 -->
  <hp:p id="1000000002" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>

  <!-- 제목: charPr 7 = 20pt bold, paraPr 20 = CENTER -->
  <hp:p id="1000000003" paraPrIDRef="20" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="7">
      <hp:t>2025년 상반기 매출 보고서</hp:t>
    </hp:run>
  </hp:p>

  <!-- 빈 줄 -->
  <hp:p id="1000000004" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>

  <!-- 소제목: charPr 8 = 14pt bold -->
  <hp:p id="1000000005" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="8">
      <hp:t>1. 매출 현황</hp:t>
    </hp:run>
  </hp:p>

  <hp:p id="1000000006" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:t>2025년 상반기 부서별 매출 현황은 다음과 같습니다.</hp:t>
    </hp:run>
  </hp:p>

  <!-- 빈 줄 -->
  <hp:p id="1000000007" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>

  <!-- 표: 3행 3열, 본문폭 42520 -->
  <hp:p id="1000000008" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:tbl id="1000000099" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" rowCnt="3" colCnt="3" cellSpacing="0" borderFillIDRef="3" noAdjust="0">
        <hp:sz width="42520" widthRelTo="ABSOLUTE" height="7200" heightRelTo="ABSOLUTE" protect="0"/>
        <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
        <hp:outMargin left="0" right="0" top="0" bottom="0"/>
        <hp:inMargin left="0" right="0" top="0" bottom="0"/>
        <!-- 헤더 행: borderFill 4 (배경색) -->
        <hp:tr>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="4">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000010">
                <hp:run charPrIDRef="9"><hp:t>부서</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="0" rowAddr="0"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="4">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000011">
                <hp:run charPrIDRef="9"><hp:t>매출(억원)</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="1" rowAddr="0"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="4">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000012">
                <hp:run charPrIDRef="9"><hp:t>전년대비</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="2" rowAddr="0"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14174" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
        </hp:tr>
        <!-- 데이터 행 1 -->
        <hp:tr>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000013">
                <hp:run charPrIDRef="0"><hp:t>영업부</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="0" rowAddr="1"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000014">
                <hp:run charPrIDRef="0"><hp:t>125</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="1" rowAddr="1"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000015">
                <hp:run charPrIDRef="0"><hp:t>+12%</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="2" rowAddr="1"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14174" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
        </hp:tr>
        <!-- 데이터 행 2 -->
        <hp:tr>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000016">
                <hp:run charPrIDRef="0"><hp:t>마케팅부</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="0" rowAddr="2"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000017">
                <hp:run charPrIDRef="0"><hp:t>89</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="1" rowAddr="2"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14173" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
          <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="3">
            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
              <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="1000000018">
                <hp:run charPrIDRef="0"><hp:t>+5%</hp:t></hp:run>
              </hp:p>
            </hp:subList>
            <hp:cellAddr colAddr="2" rowAddr="2"/>
            <hp:cellSpan colSpan="1" rowSpan="1"/>
            <hp:cellSz width="14174" height="2400"/>
            <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
          </hp:tc>
        </hp:tr>
      </hp:tbl>
    </hp:run>
  </hp:p>

  <!-- 빈 줄 -->
  <hp:p id="1000000020" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>

  <!-- 소제목 -->
  <hp:p id="1000000021" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="8">
      <hp:t>2. 결론</hp:t>
    </hp:run>
  </hp:p>

  <hp:p id="1000000022" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:t>전년 대비 전체 매출이 증가하였으며, 하반기에도 지속적인 성장이 예상됩니다.</hp:t>
    </hp:run>
  </hp:p>
</hs:sec>
XMLEOF

# 빌드
OUTPUT="/tmp/report_with_table.hwpx"
python3 "$SKILL_DIR/scripts/build_hwpx.py" \
  --template report \
  --section "$SECTION" \
  --title "2025년 상반기 매출 보고서" \
  --creator "경영기획팀" \
  --output "$OUTPUT"

# 검증
python3 "$SKILL_DIR/scripts/validate.py" "$OUTPUT"

# 정리
rm -f "$SECTION"
echo "생성 완료: $OUTPUT"
