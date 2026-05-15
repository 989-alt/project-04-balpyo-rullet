# UI/UX 설계 — 발표 차례 룰렛

## 디자인 브랜드 (final)
- **메인**: Raycast (dark canvas, hairline cards, Inter, 6–10px radii)
- **악센트**: 노란색(`#ffc533`) — 결과 강조 & 0회 학생 점.
- **이유**: 교실 TV의 어두운 환경에서 다크 캔버스가 눈부심 없음. 큰 글씨가 흰색이면 대비 4.5:1 명백 충족(`#ffffff` on `#07080a` ≈ 19:1).

## 화면 구조 (1920×1080 TV 기준, 1024px 이상에서 3-column)

```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER ─ Title (logo dot · "발표 차례 룰렛") + 단축키 힌트 chip      │
├────────────────┬──────────────────────────────────┬──────────────────┤
│  LEFT          │  CENTER (main stage)             │  RIGHT           │
│  명단 입력     │                                  │  학생별 카운트   │
│  - textarea    │   모드 선택 (radio row)          │  - 정렬: 적은 순 │
│  - "적용" btn  │   ──────────────────────         │  - 0회 노란 점   │
│  - 인원수 chip │   ┌─ result-card ─────────┐      │  - 가로 미니바   │
│  - 도움말      │   │  거대 학생 이름         │      │  - "오늘 초기화" │
│                │   │  (numeral + name)      │      │  - "전체 초기화" │
│  ─ 데이터 메뉴 │   └─────────────────────────┘     │                  │
│  · 내보내기    │   [ SPACE / SPIN ] (primary btn) │                  │
│  · 가져오기    │   최근 5명 chips row             │                  │
│  · 효과음 토글 │                                  │                  │
└────────────────┴──────────────────────────────────┴──────────────────┘
```

- 1024px 미만에서는 1 column 스택 (LEFT → CENTER → RIGHT). 모바일에서도 동작은 동일.
- max-width 1600px, 좌우 padding 24px.

## 컬러·타이포 (CSS variable 명세)

```css
--canvas: #07080a;
--surface: #0d0d0d;
--surface-elevated: #101111;
--surface-card: #121212;
--ink: #f4f4f6;        /* 헤딩·이름 */
--body: #cdcdcd;       /* 본문 */
--mute: #9c9c9d;       /* 보조 텍스트 */
--ash: #6a6b6c;
--hairline: #242728;
--hairline-soft: rgba(255,255,255,0.08);
--accent-yellow: #ffc533;
--accent-yellow-soft: rgba(255,197,51,0.15);
--accent-red: #ff6161;
--accent-green: #59d499;
--focus-ring: rgba(87,193,255,0.6);

font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
font-feature-settings: "calt","kern","liga","ss03";
```

- 본문 16~18px / 헤딩 22px / 결과 학생 이름 **clamp(72px, 12vw, 168px)** — TV에서도 큼.
- line-height 본문 1.6 / 결과 1.05.

## 핵심 컴포넌트

### 1. result-card
- bg `--surface`, border 1px `--hairline`, rounded 16px, padding 48px.
- "스핀 중" 동안 빠르게 교체되는 이름들 — 텍스트만 변경, 카드 자체 크기 고정(content jumping 방지).
- 결과 확정 시 이름 색 `--accent-yellow`, 카드 border `--accent-yellow-soft` 1px → 200ms fade.
- 이름 위 작은 캡션: `오늘 N회째 발표 · 전체 M회` (mute 색).

### 2. spin-button
- 큰 primary 흰색 pill (48px height, 24px 좌우 padding). `cursor:pointer`. focus-visible 2px ring (focus-ring color).
- 비활성 상태(명단 0명) → `--ash` 텍스트, disabled cursor. aria-disabled.
- 단축키 표시: 우측에 `[ Space ]` keycap.

### 3. mode-selector
- 가로 radio 3개. `<label>` 안에 `<input type="radio">` + 텍스트.
- 활성: pill-tab-active(surface-elevated + ink). 비활성: pill-tab(transparent + body).
- 라벨: "무작위 / 방금 사람 제외 / 오늘 안 한 사람만".

### 4. roster-textarea
- `<textarea>` 8행, surface-elevated, body-md, hairline 1px, focus시 hairline-strong + ring.
- placeholder: `한 줄에 한 명. 예) 김민지, 박지호, 1. 이수아 ...`
- 우측 chip: 현재 인원수 표시 (`24명`).

### 5. roster-table
- 학생별 row: `[칩 0회] 이름 [hor-bar: today / total]`.
- 0회 학생은 row 좌측에 `--accent-yellow` 4px 원형 dot.
- 가상 스크롤 불필요(최대 40명 가정).

### 6. recent-chips
- 최근 5명 가로 칩 (왼쪽이 최신). 각 칩: `--surface-card` + `--body`, 6px radius.
- 비어있을 때: "아직 호명 없음" mute.

## 인터랙션 / 애니메이션

- 스핀: 1.0s (default). 60fps 텍스트 교체 + 카드 살짝 scale(1 → 1.02 → 1) ease-out.
- prefers-reduced-motion: 150ms simple opacity fade. 텍스트 교체 1회만.
- 모든 transition `cubic-bezier(.2,.8,.2,1)` 200ms.
- 호버: 카드 hairline → hairline-strong. 버튼 색 opacity transition.
- focus-visible 항상 표시. tabindex 자연 순서.

## 접근성

- 결과 이름 영역 `aria-live="polite"`. 스핀 완료 시 스크린리더에게 호명 알림.
- 모든 버튼 `aria-label`(아이콘 only인 경우만). 텍스트 버튼은 보이는 라벨 자체로 충분.
- 색만으로 의미 전달 안 함: 0회 dot 옆에 텍스트 "오늘 0회" 같이 표시.
- 대비: 흰 텍스트 on canvas = 19:1, body text(`#cdcdcd`) on canvas = 13:1 — 모두 통과.
- prefers-reduced-motion 처리.
- 인쇄 미디어 쿼리 (Ctrl+P): 카운트 표만 표시, 흑백.

## 사용자 흐름 (Playwright 검증 시나리오 매핑)

1. 빈 상태 진입 → "명단 비어있음" 안내 + spin 버튼 disabled.
2. textarea에 "민지\n지호\n수아" 입력 + "적용" → 카운트 표 3명, spin enabled, chip "3명".
3. "스핀" 클릭 → 약 1초 후 한 명 이름 강조 표시, 우측 카운트 +1, 최근 chip 추가.
4. 모드 "오늘 안 한 사람만" → 추가 2회 스핀 → 모두 1회 됨 → 다음 스핀 시 자동 초기화 + 안내.
5. "JSON 내보내기" → 파일 다운로드 트리거(Playwright는 다운로드 이벤트 확인).
6. (선택) prefers-reduced-motion 시뮬: 스핀 즉시 결과.

## 안티패턴(이 프로젝트에선 의도적으로 피함)

- 이모지 아이콘 → 인라인 SVG만 사용.
- 외부 CDN(Tailwind/Inter 폰트 CDN) → 전부 vanilla + system font fallback.
- scale 트랜스폼으로 layout shift 유발 → opacity·color만 트랜지션.
- 너무 긴 스핀(>2초) → 1초 default, 사용자가 "긴 스핀" 옵션 추가 안 함.
