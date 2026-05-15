# Fixes · Cycle 1

## B1 — Tofu placeholder 수정
- HTML 초기 `— · —` → `준비됨` (한국어, 시스템 폰트 보장).
- JS `renderAll` 동일 텍스트로 변경.
- CSS `.result-name[data-state="empty"]` 추가 → 빈 상태에서 폰트 크기 28~48px, ash 색으로 축소(거대한 boxing 자체를 회피).
- 부가: `renderAll` 에서 `lastPickedId === null` 이면 result card를 빈 상태로 되돌림(이전엔 reset 후에도 winner 텍스트가 잔존).

## B2 — 트랜지션 중 색 캡처 회피
- `.btn-primary` 의 background/color/border 트랜지션을 200ms → 60ms 로 단축.
- e2e screenshot 시점이 disabled→enabled 직후라도 60ms 안에 정상 색으로 안착.
- 호버 효과(border-color) 는 그대로(.2s) — 사용자 인지에 영향 없음.

## 영향 범위
- 기능 변경 없음. 기존 e2e 9개는 그대로 통과해야 함.
- 추가 회귀 가능성: 결과 후 reset 시 stage 가 비워지는 것이 정상 동작이지만, 만약 사용자가 reset 직전 winner 를 잠시 더 보고 싶다면 UX 손실. → 의도된 동작이므로 OK.
