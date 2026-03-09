---
name: hwp-com-writer
description: "한컴 COM API + HWPX XML 후처리로 행정문서를 정밀 자동 생성하는 하이브리드 스킬. 레퍼런스 서식 분석 → COM으로 문서 생성 → XML 후처리로 COM의 한계 보완."
status: "ACTIVE"
---

# hwp-com-writer — 한컴 COM + XML 하이브리드 문서 자동화 스킬

한글(HWP) COM API로 문서 구조와 서식을 생성하고, HWPX XML 후처리로 COM이 못하는 부분을 보정하는 **하이브리드 방식** 스킬.

## 트리거 조건

- "한글 문서 서식 재현해줘" / "COM 방식으로 한글 문서 만들어줘"
- "레퍼런스 문서와 동일한 서식으로 작성해줘"
- "HWPX 서식 분석해줘" / "행정문서 자동 생성"
- HWP 서식의 **정밀 재현**이 필요한 모든 요청

## 환경 필수조건

```
- Windows (한글 프로그램은 Windows 전용)
- 한글과컴퓨터 한글(HWP) 또는 한컴오피스 설치
- Python 3.10+ (pywin32 호환 필요)
- pip install pywin32
```

## 디렉토리 구조

```
hwp-com-writer/
├── SKILL.md                        ← 이 파일 (에이전트 메인 지침)
├── skill.yaml                      ← Gemini 트리거 정의
├── references/
│   └── full-guide.md               ← 1,100줄짜리 완전 가이드 (심층 참조용)
└── scripts/
    ├── com_core.py                 ← COM 초기화 + 기본 함수 (set_char, set_para 등)
    ├── xml_postprocess.py          ← XML 후처리 4종 (배경색, indent, 표, 자간)
    └── template_filler.py          ← HWPX 템플릿 빈칸 채우기
```

---

## 핵심 아키텍처: COM 생성 + XML 후처리

```
입력 (마크다운/텍스트/데이터)
    │
    ▼
[COM 단계] win32com으로 한글 프로그램 직접 제어
    │  ✅ 페이지 설정, 표 생성, 텍스트 삽입
    │  ✅ 글꼴/크기/색상/자간/정렬/굵기
    │  ✅ 내어쓰기/들여쓰기, 음영(ShadeColor)
    │  ❌ 셀 배경색, treatAsChar, indent 단위
    │
    ▼
  .hwpx 저장 (SaveAs)
    │
    ▼
[XML 후처리 단계] HWPX = ZIP → XML 수정 → 다시 ZIP
    │  ✅ 셀 배경색 (borderFill 추가)
    │  ✅ 표 treatAsChar (글자처럼 취급)
    │  ✅ 내어쓰기 단위 (CHAR → HWPUNIT)
    │  ✅ 자간 최적화 (마지막 줄 1~4글자 올리기)
    │  ✅ 표 너비 강제 설정
    │
    ▼
  최종 .hwpx 완성
```

**왜 하이브리드인가:**
- COM만 쓰면: 셀 배경색 안 됨, 표 속성 제한
- XML만 쓰면: charPr/paraPr ID 할당 등 HWP 엔진 로직을 다 구현해야 함
- COM + XML: COM이 90% 처리 → XML은 나머지 10%만 패치

---

## ★★★ 절대 지켜야 할 규칙 (함정 목록)

### 1. COM 초기화 순서 (반드시 이 순서)

```python
import win32com.client as win32

# 1) EnsureDispatch (Dispatch 아님!)
hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")

# 2) 보안모듈 등록 (없으면 SaveAs 보안오류)
hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")

# 3) 창 표시 (선택)
try: hwp.XHwpWindows.Item(0).Visible = True
except: pass

# 4) 새 문서
hwp.Run("FileNew")
```

- `Dispatch` → 속성 접근 실패. **반드시 `gencache.EnsureDispatch`**
- `RegisterModule` 빠지면 저장 시 보안 오류

### 2. 색상은 BGR (RGB 아님!)

```python
def rgb_to_hwp(r, g, b):
    return (b << 16) | (g << 8) | r

# 빨간색: rgb_to_hwp(255, 0, 0) = 255 (RGB와 동일하게 보이지만 우연)
# 파란색: rgb_to_hwp(0, 0, 255) = 16711680 (RGB와 다름!)
```

### 3. ShadeColor 리셋 필수

```python
# 음영 적용 후 다음 텍스트에서 반드시 리셋
hcs.ShadeColor = 0xFFFFFFFF  # "none"
# 안 하면 이전 음영이 계속 적용됨 (COM 내부 캐시 문제)
```

### 4. 네임스페이스 독립 정규식 (가장 중요!)

COM이 생성한 HWPX와 HWP가 직접 저장한 HWPX의 네임스페이스가 다르다:
- HWP 직접 저장: `<hp:tbl>`, `<hh:charPr>`, `<hc:left>`
- COM 생성: `<ns0:tbl>`, `<ns1:charPr>`, `<ns2:switch>`

```python
# ❌ 틀림 — 한쪽에서만 동작
re.search(r'<hp:tbl', content)

# ✅ 맞음 — 어느 네임스페이스든 매칭
re.search(r'<[^>]*:tbl\b', content)
```

### 5. itemCnt 업데이트 필수

header.xml에 charPr, paraPr, borderFill을 추가하면 **부모 태그의 itemCnt를 반드시 수정**:

```python
# borderFill 3개 → 6개로 늘렸으면:
header = re.sub(
    r'(<[^>]*:borderFills\b[^>]*)\bitemCnt="\d+"',
    r'\1itemCnt="6"', header
)
# 이거 빠지면 HWP가 추가된 항목을 무시함
```

### 6. 표 안에서 반드시 빠져나오기

```python
def force_out_of_table(hwp):
    for _ in range(4):
        try: hwp.Run("TableOut")
        except: pass
        try: hwp.Run("CloseEx")
        except: pass
        hwp.Run("MoveDown")
# 안 하면 다음 표가 이전 표 안에 중첩됨
```

### 7. `<*:t>` 태그 정규식 주의

```python
# ❌ :t 뒤에 다른 문자 매칭 (table, text 등)
re.compile(r'<[^>]*?:t[^>]*?>')

# ✅ 정확히 :t 태그만
re.compile(r'<[^>]*?:t>|<[^>]*?:t\s[^>]*?>')
```

---

## DO NOT USE (크래시/미작동 확인됨)

| API | 문제 |
|-----|------|
| `CellBorderFill Execute()로 배경색` | Execute()가 FillAttr을 HSet에 직렬화 안 함 → 저장 시 무시 |
| `SetPosBySet(ctrl.GetAnchorPos(0))` | HWP 프로세스 종료 (크래시) |
| `HParameterSet.HTableDef` | 존재하지 않는 속성 |
| `InitScan()/GetText()` | 파라미터 형식 문제로 텍스트 미반환 |
| `MoveNextChar로 표 진입` | 커서가 표 안으로 안 들어감 → `MoveDown` 사용 |
| bat 파일로 Python 실행 | exit 0 반환하지만 미실행 → bash에서 직접 실행 |

---

## 워크플로우 1: 레퍼런스 문서 서식 재현

### Step 1: 레퍼런스 HWPX 분석

```python
import zipfile, re

with zipfile.ZipFile("reference.hwpx") as z:
    hdr = z.read("Contents/header.xml").decode("utf-8")
    sec = z.read("Contents/section0.xml").decode("utf-8")

# charPr에서 폰트/크기/색상 추출
for m in re.finditer(r'<[^>]*charPr\b[^>]*id="(\d+)"[^>]*height="(\d+)"[^>]*textColor="([^"]*)"', hdr):
    print(f"charPr id={m.group(1)}, height={int(m.group(2))/100}pt, color={m.group(3)}")

# borderFill에서 배경색 추출
for m in re.finditer(r'faceColor="([^"]*)"', hdr):
    print(f"배경색: {m.group(1)}")
```

### Step 2: COM으로 문서 생성

`scripts/com_core.py`의 함수들을 사용:

```python
import sys; sys.path.insert(0, "SKILL_DIR/scripts")
from com_core import init_hwp, set_char, set_para, insert_text, setup_page, force_out_of_table

hwp = init_hwp()
setup_page(hwp)

set_char(hwp, face_h="함초롬돋움", pt=14, bold=1, color=(0, 0, 255))
set_para(hwp, align=3, line_spacing=170)
insert_text(hwp, "제목 텍스트")
hwp.Run("BreakPara")

hwp.SaveAs("output.hwpx", "HWPX", "")
hwp.Quit()
```

### Step 3: XML 후처리

```python
from xml_postprocess import apply_table_postprocess, apply_indent_unit_postprocess, apply_spacing_optimization

apply_table_postprocess("output.hwpx")
apply_indent_unit_postprocess("output.hwpx")
apply_spacing_optimization("output.hwpx")
```

---

## 워크플로우 2: HWPX 템플릿 빈칸 채우기

기존 HWPX 서식의 빈 불릿(❍, ◦, - 등)에 내용을 채워넣는 방식.
COM 없이 XML 직접 편집만으로 동작. 한글 프로그램 불필요.

```python
from template_filler import fill_template

fill_template(
    template="양식.hwpx",
    output="완성본.hwpx",
    summary=["◦ 요약1", "◦ 요약2"],
    body=["  ❍ 본문1", "  ❍ 본문2", "    - 세부사항"]
)
```

**동작 원리:**
1. HWPX ZIP 해제 → `section0.xml` 읽기
2. `<*:t>` 태그에서 빈 불릿 기호(◦, ❍, -) 찾기
3. 해당 태그의 텍스트를 새 내용으로 교체
4. 뒤에서부터 교체하여 위치 보존
5. ZIP 재압축

---

## 단위 변환표

```
1 pt = 100 HWPUNIT
1 mm = 283.46 HWPUNIT
167 mm (표 너비) = 47339 HWPUNIT
A4 가로 (210mm) = 59528 HWPUNIT
A4 세로 (297mm) = 84188 HWPUNIT
19mm 여백 = 5386 HWPUNIT
15mm 여백 = 4252 HWPUNIT
```

---

## COM API 핵심 패턴

### GetDefault → 속성 설정 → Execute (3단계)

모든 COM 서식 조작은 이 패턴:

```python
param_set = hwp.HParameterSet.H서식종류
hwp.HAction.GetDefault("액션이름", param_set.HSet)
param_set.속성명 = 값
hwp.HAction.Execute("액션이름", param_set.HSet)
```

### 글자 서식 (CharShape)

```python
hcs = hwp.HParameterSet.HCharShape
hwp.HAction.GetDefault("CharShape", hcs.HSet)
hcs.FaceNameHangul = "함초롬돋움"
hcs.FaceNameLatin = "Times New Roman"
hcs.Height = 1400                       # 14pt (pt × 100)
hcs.Bold = 1
hcs.TextColor = rgb_to_hwp(0, 0, 255)  # BGR!
# 자간: 언어별 각각 설정
for lang in ("Hangul", "Latin", "Hanja", "Japanese", "Other", "Symbol", "User"):
    setattr(hcs, f"Spacing{lang}", -3)
# ★ ShadeColor 항상 설정 (리셋 포함)
hcs.ShadeColor = 0xFFFFFFFF  # none (리셋)
hwp.HAction.Execute("CharShape", hcs.HSet)
```

### 문단 서식 (ParaShape)

```python
hps = hwp.HParameterSet.HParaShape
hwp.HAction.GetDefault("ParagraphShape", hps.HSet)
hps.AlignType = 0     # 0=양쪽, 1=왼쪽, 2=오른쪽, 3=가운데, 4=배분
hps.LineSpacingType = 0  # 0=PERCENT
hps.LineSpacing = 170
hps.LeftMargin = 1000    # 왼쪽 여백 10pt (줄바꿈 후 시작 위치)
hps.Indentation = -2150  # 내어쓰기 (음수=내어쓰기)
hwp.HAction.Execute("ParagraphShape", hps.HSet)
```

### 표 생성

```python
tc = hwp.HParameterSet.HTableCreation
hwp.HAction.GetDefault("TableCreate", tc.HSet)
tc.Rows = 1; tc.Cols = 4
tc.WidthType = 2          # 절대 크기
tc.WidthValue = 47339      # 167mm
tc.ColWidth.SetItem(0, 2400)
tc.ColWidth.SetItem(1, 600)
# ...
hwp.HAction.Execute("TableCreate", tc.HSet)

# 셀 이동
hwp.Run("TableRightCell")
hwp.Run("TableLowerCell")
```

### 페이지 설정

```python
sec = hwp.HParameterSet.HSecDef
hwp.HAction.GetDefault("PageSetup", sec.HSet)
sec.PageDef.PaperWidth = 59528     # A4 가로 (210mm)
sec.PageDef.PaperHeight = 84188    # A4 세로 (297mm)
sec.PageDef.LeftMargin = 5386      # 19mm
sec.PageDef.RightMargin = 5386
sec.PageDef.TopMargin = 4252       # 15mm
sec.PageDef.BottomMargin = 4252
hwp.HAction.Execute("PageSetup", sec.HSet)
```

### 저장

```python
hwp.SaveAs(str(output_path), "HWPX", "")
hwp.Quit()
```

---

## HWPX 파일 구조 요약

```
파일.hwpx (ZIP)
├── Contents/
│   ├── header.xml     ← 스타일 정의 (charPr, paraPr, borderFill, fontface)
│   └── section0.xml   ← 본문 (단락, 표, 텍스트)
├── META-INF/
│   ├── container.xml
│   └── manifest.xml
├── settings.xml
└── version.xml
```

- **header.xml**: 모든 서식이 ID로 관리됨. `charPr id="5"`를 정의하면 본문에서 `charPrIDRef="5"`로 참조
- **section0.xml**: `<hp:p>` 단락 안에 `<hp:run charPrIDRef="N">` → `<hp:t>텍스트</hp:t>`
- **borderFill**: 셀 테두리+배경색. `<hp:tc borderFillIDRef="N">`으로 참조
- **COM 생성 HWPX에만 존재**: `<ns2:switch>` 블록 (HwpUnitChar/default 이중 표현)

---

## 심층 참조

더 자세한 내용은 `references/full-guide.md`를 참조.
1,100줄 분량으로 Phase 0~5 전체 시행착오, 디버깅 방법, 버전 히스토리 포함.


## When To Switch From XML To COM

Use this skill as the default fallback when `hwpx` reaches structural validity but still fails visually in Hancom.

### Prefer COM when
- the reference cover has fixed boxes for date, department, approval, or stamps
- visible text sits inside table cells or anchored controls
- the body uses many small runs or text nodes for one rendered line
- exact visual reproduction matters more than raw generation speed

### Core operating rule
Work from the reference document layout and replace visible text in place.
Do not rebuild the document from scratch unless the document is structurally simple.

### In-place replacement rules
1. Open the original reference document or a direct working copy.
2. Keep the cover/header/table/text-box structure intact.
3. Replace text at the existing position first; only create new objects when the reference truly has no slot.
4. For box or cell content, target the inner paragraph/cell text, not the surrounding paragraph index guessed from XML alone.
5. If XML inspection is still useful, use `hwpx` only for analysis and hand the final write-back to COM.

### Recommended handoff from `hwpx`
- Use `analyze_template.py` or XML inspection to identify paragraph, run, and cell structure.
- If red flags appear, stop patching XML repeatedly.
- Move to COM for the final pass and let Hancom recalculate layout natively.
