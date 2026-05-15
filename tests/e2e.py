"""End-to-end Playwright tests for 발표 차례 룰렛.

Run via:
    python3 /home/user/1-day-1-code-project/webapp-testing/scripts/with_server.py \
        --server "python3 -m http.server 5180 --bind 127.0.0.1" --port 5180 \
        -- python3 tests/e2e.py
"""
from __future__ import annotations
import sys, json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, expect

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "tests" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)

URL = os.environ.get("APP_URL", "http://127.0.0.1:5180/")

console_errors: list[str] = []
page_errors: list[str] = []

def attach_listeners(page: Page) -> None:
    def on_console(msg):
        if msg.type == "error":
            text = msg.text
            # filter known harmless warnings if any (none yet)
            console_errors.append(text)
    page.on("console", on_console)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))


def shot(page: Page, name: str) -> None:
    page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)


def assert_eq(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"[{label}] expected {expected!r}, got {actual!r}")


def main():
    failures: list[str] = []

    def check(label, fn):
        try:
            fn()
            print(f"  PASS  {label}")
        except Exception as exc:
            failures.append(f"{label}: {exc}")
            print(f"  FAIL  {label} — {exc}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        attach_listeners(page)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")

        # Fresh state: clear localStorage and reload
        page.evaluate("localStorage.clear()")
        page.reload()
        page.wait_for_load_state("networkidle")

        # ─── Scenario 1: empty state ──────────────────────────────────────
        def s1():
            spin = page.locator("#spinBtn")
            assert spin.is_disabled(), "spin should be disabled with empty roster"
            assert "0명" in page.locator("#countChip").inner_text()
            assert "명단을 먼저" in page.locator("#resultCaption").inner_text()
        check("S1: empty state shows disabled spin + helpful caption", s1)
        shot(page, "01-empty")

        # ─── Scenario 2: enter roster via demo button ─────────────────────
        def s2():
            page.locator("#loadDemo").click()
            page.wait_for_function("document.querySelector('#countChip').textContent.includes('24')")
            assert_eq(page.locator("#countChip").inner_text(), "24명", "count chip after demo")
            assert page.locator("#spinBtn").is_enabled()
            # Roster list should have 24 rows
            rows = page.locator(".roster-row").count()
            assert rows == 24, f"expected 24 rows, got {rows}"
        check("S2: demo loads 24 students, spin enabled", s2)
        shot(page, "02-demo-loaded")

        # ─── Scenario 3: spin and reveal ──────────────────────────────────
        def s3():
            page.locator("#spinBtn").click()
            # wait for reveal
            page.wait_for_function("document.querySelector('#resultCard').classList.contains('is-revealed')", timeout=4000)
            name = page.locator("#resultName").inner_text().strip()
            assert name and name != "— · —" and "—" not in name, f"name should be revealed: {name!r}"
            stat = page.locator("#resultStat").inner_text()
            assert "오늘 1회" in stat, f"stat should show today 1: {stat!r}"
            # one chip in recent
            assert page.locator(".recent .chip").count() == 1
        check("S3: spin reveals a name, stat updates, recent chip added", s3)
        shot(page, "03-after-spin")

        # ─── Scenario 4: today-only mode auto-resets after everyone picked ─
        def s4():
            page.locator("input[name='mode'][value='today-only']").check(force=True)
            # already picked 1 person → 23 left. Spin 23 more times.
            for i in range(23):
                page.locator("#spinBtn").click()
                page.wait_for_function("document.querySelector('#resultCard').classList.contains('is-revealed')", timeout=4000)
                # quick read; sleep handled by waitForFunction
            # After 24 total picks (S3 + 23) all today >= 1.
            # Next spin: should auto-reset and pick someone.
            page.locator("#spinBtn").click()
            page.wait_for_function("document.querySelector('#resultCard').classList.contains('is-revealed')", timeout=4000)
            # Validate via window.__app.getState
            state = page.evaluate("window.__app.getState()")
            todays = [s["today"] for s in state["students"]]
            # After auto-reset+1 spin: exactly one student has today=1, others 0
            assert sum(todays) == 1, f"after auto-reset+1 spin, sum today should be 1: {todays}"
            assert max(todays) == 1
        check("S4: today-only mode auto-resets after all picked", s4)
        shot(page, "04-today-only-auto-reset")

        # ─── Scenario 5: exclude-last mode ────────────────────────────────
        def s5():
            page.locator("input[name='mode'][value='exclude-last']").check(force=True)
            prev = page.evaluate("window.__app.getState().lastPickedId")
            # spin 10x; never the same id twice in a row
            last = prev
            for _ in range(10):
                page.locator("#spinBtn").click()
                page.wait_for_function("document.querySelector('#resultCard').classList.contains('is-revealed')", timeout=4000)
                # wait until lastPickedId changes
                page.wait_for_function(f"window.__app.getState().lastPickedId !== {json.dumps(last)}", timeout=4000)
                cur = page.evaluate("window.__app.getState().lastPickedId")
                assert cur != last, "exclude-last should prevent immediate repeat"
                last = cur
        check("S5: exclude-last never picks same student twice in a row", s5)

        # ─── Scenario 6: JSON export + import roundtrip ───────────────────
        def s6():
            # Capture export via download event
            with page.expect_download() as dl_info:
                page.locator("#exportBtn").click()
            dl = dl_info.value
            tmp = ROOT / "tests" / "_export.json"
            dl.save_as(str(tmp))
            data = json.loads(tmp.read_text())
            assert isinstance(data.get("students"), list)
            assert len(data["students"]) == 24
            # Clear, then import (auto-confirm the dialog)
            page.evaluate("localStorage.clear()")
            page.reload()
            page.wait_for_load_state("networkidle")
            assert page.locator("#countChip").inner_text() == "0명"
            # Accept the confirm dialog that fires during import
            page.once("dialog", lambda d: d.accept())
            page.locator("#fileInput").set_input_files(str(tmp))
            page.wait_for_function("document.querySelector('#countChip').textContent.includes('24')", timeout=3000)
            assert page.locator("#countChip").inner_text() == "24명"
            tmp.unlink(missing_ok=True)
        check("S6: JSON export+import roundtrip preserves 24 students", s6)
        shot(page, "06-after-import")

        # ─── Scenario 7: keyboard Space triggers spin ─────────────────────
        def s7():
            page.evaluate("document.activeElement.blur()")
            # press Space anywhere outside an input
            page.locator("body").press("Space")
            page.wait_for_function("document.querySelector('#resultCard').classList.contains('is-revealed')", timeout=4000)
        check("S7: Space key on body triggers a spin", s7)
        shot(page, "07-after-space")

        # ─── Scenario 8: roster parsing edge cases ────────────────────────
        def s8():
            result = page.evaluate("""() => {
                const text = '1. 김민지\\n2) 박지호\\n  \\n3 이수아\\n김민지\\n  정도원';
                return window.__app.parseRoster(text);
            }""")
            names = [r["name"] for r in result]
            # 김민지 deduped; 정도원 included w/o number
            assert names == ['김민지','박지호','이수아','정도원'], f"unexpected: {names}"
            nums = [r["num"] for r in result]
            assert nums == [1,2,3,4], f"unexpected nums: {nums}"
        check("S8: parser handles numbers, separators, blanks, dupes", s8)

        # ─── Scenario 9: no console / page errors ─────────────────────────
        def s9():
            assert console_errors == [], f"console errors: {console_errors}"
            assert page_errors == [], f"page errors: {page_errors}"
        check("S9: no console errors, no page errors", s9)

        browser.close()

    print()
    print(f"{'='*60}")
    if failures:
        print(f"FAIL — {len(failures)} test(s) failed:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    else:
        print("All e2e checks passed.")


if __name__ == "__main__":
    main()
