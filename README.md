# 한글 재기안머신 (hwpx-rekian)

> **AI 기반 HWPX 행정문서 자동 작성 도구** — AI Agent Skill 패키지

한글(HWP/HWPX) 파일을 읽고, 생성하고, 자동으로 채워주는 두 가지 스킬을 담은 패키지입니다.
대한민국 지방자치단체·공공기관의 행정문서 작성 자동화를 목적으로 만들어졌습니다.
HWP 파일은 한글과컴퓨터 공식 애드인인 HWPX 변환기를 사용하여 HWPX로 변환하여 다룹니다.
https://www.hancom.com/support/downloadCenter/download 에서 다운로드하세요.

---

## 크레딧

| 기여자 | 역할 |
|--------|------|
| [Canine89 / 박현규](https://github.com/Canine89/hwpxskill) ([스레드 @limedaddy_8924](https://www.threads.net/@limedaddy_8924) / [유튜브 @편집자P](https://www.youtube.com/@editorp89)) | hwpx 스킬 원작자 | | hwpx 스킬 원작자 |
| 경상남도 남해군(행정안전부 파견) 이경수 주무관 ([유튜브 @공무원코딩](https://www.youtube.com/@publicCoding) / 온나라 커뮤니티 범정부오피스) | 행정문서 자동화(범피스) 개발자 |
| [ai-public-peasant](https://github.com/ai-public-peasant) | 패키징·통합·개선 |

---

## 포함 스킬

### 1. `hwpx` — HWPX 순수 파이썬 스킬
- HWPX(XML 기반 한글 파일) 생성·편집·파싱
- 외부 프로그램 없이 동작 (한컴오피스 불필요)
- 표, 문단, 서식, 페이지 나누기 지원

### 2. `hwp-com-writer` — HWP COM + HWPX 하이브리드 스킬
- 한컴 COM API로 정밀 문서 생성
- 레퍼런스 서식 분석 → COM 생성 → XML 후처리 파이프라인
- Windows 환경 + 한컴오피스 설치 필요

---

## 권장 모델

> **2026년 3월 8일 기준, Codex 5.4에서 가장 좋은 결과가 나옵니다.**

| 모델 | 평가 |
|------|------|
| **GPT-5.4 Codex** | ✅ 최우선 권장 — 코드 생성 정확도 및 HWPX 구조 이해도 최상 |
| Claude Opus 4.6 | 권장 |
| Claude Sonnet | 단순 반복 작업, 취합 |

---

## 설치

```bash
# 1. 레포 클론
git clone https://github.com/ai-public-peasant/hwpx-rekian.git

# 2. 스킬 디렉터리에 복사 또는 심링크
# hwpx/ → ~/.claude/skills/hwpx/
# hwp-com-writer/ → ~/.claude/skills/hwp-com-writer/
```

---

## 사용법

Claude Code/Codex에서 아래와 같이 호출합니다.

```
/hwpx 보고서 초안 작성해줘 — 제목: 2026년 AI 도입 계획
/hwp-com-writer 레퍼런스 서식 기반으로 기안문 채워줘
```

---

## 라이선스

MIT License
원작 스킬 라이선스를 각 하위 디렉터리에서 확인하세요.
