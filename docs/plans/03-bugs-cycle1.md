# Bugs · Cycle 1

> Cycle 1: 9/9 e2e checks pass. No P0/P1 functional bugs, but visual issues from screenshot review.

## P1 — visual

### B1. 빈 상태 결과 카드의 placeholder 가 tofu 박스로 렌더링
- **재현**: 첫 진입 → 결과 카드 가운데 `— · —` 텍스트가 3개의 거대한 흰 박스로 보임.
- **원인**: 폴백 폰트(Liberation Sans 등)가 큰 사이즈에서 em-dash `—`·middot `·` glyph 미보유 → `.notdef` 글리프(흰 사각형) 렌더.
- **기대**: 빈 상태에 적절한 한국어 placeholder 또는 자연스러운 시각.
- **수정안**: placeholder 텍스트 제거 또는 한국어로 교체 (`준비됨`). 그리고 빈 상태에서는 result-name 자체를 `visibility:hidden` / `opacity:0`로 처리해 caption만 보이게.

### B2. 스핀 버튼 색이 트랜지션 중에 captured (114,114,114) → 흰색 아님
- **재현**: `loadDemo` 직후 또는 spin 결과 직후 즉시 스크린샷 → 버튼 배경이 회색.
- **원인**: `.btn` 의 `transition: background-color .2s` 가 disabled→enabled 토글 후 200ms 동안 진행 중인 상태를 캡처.
- **기대**: 결과 노출 즉시 버튼이 흰색.
- **수정안**: `.btn-primary` 의 background/color transition 만 50ms로 단축 (또는 0). 호버용 트랜지션은 유지.

## Console / page errors
- 없음.

## P2 — nice-to-have
- 결과 카드의 result-num·result-stat가 빈 상태에서 빈 div 자리로 22px·20px 차지 → 시각 공백. min-height 제거하면 reveal 시 layout shift 발생하므로 그대로 유지가 합리적이지만, 빈 상태 caption 한 줄로 합치는 것도 가능. **이번 사이클은 보류.**
