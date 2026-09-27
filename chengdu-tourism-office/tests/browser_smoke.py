"""Interactive local smoke check; no live AI or email calls, settings restored."""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get("ATLAS_TEST_URL", "http://127.0.0.1:8765")
OUT = Path(os.environ.get("TEMP", ".")) / "atlas-browser-review"
OUT.mkdir(exist_ok=True)
RESULTS: list[dict] = []


def main():
    with sync_playwright() as engine:
        browser = engine.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
        )
        context = browser.new_context(viewport={"width": 1512, "height": 982})
        baseline = context.request.get(BASE + "/api/settings").json()
        config = context.request.get(BASE + "/api/config").json()
        if config.get("ai_configured"):
            raise RuntimeError("Live AI key is configured; this check only runs in local mode.")
        errors = []
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script("""Object.defineProperty(window, 'speechSynthesis', {value: {
            speaking: false, getVoices() { return []; }, cancel() { this.speaking = false; },
            speak(utterance) { this.speaking = true; window.testSpeech = utterance; utterance.onstart?.(); }
        }});""")

        def screenshot(name):
            page.screenshot(path=str(OUT / (name + ".png")), full_page=True)

        def check(name, fn):
            try:
                fn()
                RESULTS.append({"check": name, "status": "passed"})
            except Exception as error:
                RESULTS.append({"check": name, "status": "failed", "error": str(error)})
                screenshot("failure-" + name)

        def navigate(view):
            page.locator(".main-nav [data-view='" + view + "'], .sidebar-footer [data-view='" + view + "']").click()
            expect(page.locator("#view-" + view)).to_be_visible()

        def send(message, mode="ask"):
            page.locator("#chat-mode").select_option(mode)
            page.locator("#chat-input").fill(message)
            with page.expect_response(lambda response: response.url.endswith("/api/chat") and response.request.method == "POST", timeout=60000) as response:
                page.locator("#send-message").click()
            result = response.value.json()
            assert response.value.ok, result
            expect(page.locator("#chat-input")).to_be_enabled(timeout=60000)
            expect(page.locator(".message.assistant").last).to_be_visible()
            return result

        def review(action, comment=None):
            page.locator("#view-assistant [data-review='" + action + "']").click()
            if comment:
                page.locator("#review-comment").fill(comment)
                with page.expect_response(lambda response: response.url.endswith("/api/review"), timeout=60000) as response:
                    page.locator("#review-submit").click()
                result = response.value.json()
                assert response.value.ok, result
                expect(page.locator("#review-dialog")).not_to_be_visible()
                return result
            page.wait_for_function("document.querySelector('#notice').textContent.includes('Decision recorded')")
            return None

        conversation_id = None
        try:
            page.goto(BASE)
            expect(page.locator("body")).to_have_attribute("data-ready", "true")
            expect(page.locator(".welcome h1")).to_have_text("What can we take care of?")
            page.wait_for_function("document.querySelector('#companion-panel img')?.naturalWidth > 0")
            screenshot("01-desktop-welcome")
            RESULTS.append({"check": "welcome-history", "status": "passed", "history_items": page.locator(".history-item").count()})

            def voice_check():
                page.locator("#hear-intro").click()
                expect(page.locator("#companion-panel .atlas-avatar")).to_have_attribute("data-state", "speaking")
                page.locator("#voice-stop").click()
                expect(page.locator("#companion-panel .atlas-avatar")).to_have_attribute("data-state", "idle")
            check("avatar-speaking-state", voice_check)

            def settings_check():
                navigate("settings")
                page.locator("[name='autonomy_mode'][value='proposal_first']").check()
                page.locator("[name='execute_plan']").check()
                page.locator("[name='generate_reports']").check()
                page.locator("[name='send_email']").uncheck()
                page.locator("[name='max_auto_quote_cny']").fill("210000")
                page.locator("[name='allowed_recipients']").fill("")
                with page.expect_response(lambda r: r.url.endswith("/api/settings") and r.request.method == "POST") as response:
                    page.locator("#settings-form button[type='submit']").click()
                assert response.value.ok, response.value.text()
                current = context.request.get(BASE + "/api/settings").json()
                assert current["max_auto_quote_cny"] == 210000 and not current["send_email"]
                expect(page.locator(".setup-code")).to_contain_text("OPENAI_API_KEY=")
                expect(page.locator("#api-key-input")).to_be_visible()
                screenshot("02-settings")
            check("settings-persistence", settings_check)

            def people_check():
                navigate("people")
                assert page.locator(".staff-card").count() >= 6
                first_name = page.locator(".staff-card h3").first.inner_text()
                page.locator("#people-search").fill(first_name)
                expect(page.locator(".staff-card")).to_have_count(1)
                page.locator(".staff-card [data-edit]").click()
                expect(page.locator("#staff-dialog")).to_be_visible()
                expect(page.locator("#staff-name")).to_have_value(first_name)
                page.locator("#staff-dialog [data-close='staff-dialog']").first.click()
                page.locator("#people-search").fill("")
                screenshot("03-people")
                page.locator("[data-people-tab='network']").click()
                assert page.locator(".network-node").count() >= 6
                page.locator("[data-network='follows']").click()
                assert page.locator(".network-edge.follows").count() > 0
                screenshot("04-relationship-map")
            check("people-directory-network", people_check)

            def organization_check():
                navigate("organization")
                chart = page.locator("#view-organization")
                expect(chart.locator(".org-overview")).to_be_visible()
                assert chart.locator(".network-node").count() >= 6
                assert chart.locator(".network-edge.reports_to").count() >= 5
                chart.locator("[data-org-node='ops_manager']").first.click()
                expect(chart.locator(".org-inspector h3")).to_contain_text("He")
                chart.locator("#org-search-organization").fill("finance")
                matching = chart.locator(".network-node:not(.dimmed)").count()
                assert matching >= 1, {"matching_nodes": matching, "query": page.evaluate("state.orgQuery"), "expected": page.evaluate("state.company.people.filter(p => (p.name + ' ' + p.role).toLowerCase().includes('finance')).map(p => p.name)")}
                follows = chart.locator("[data-network='follows']")
                if follows.get_attribute("aria-pressed") != "true":
                    follows.click()
                assert chart.locator(".network-edge.follows").count() > 0
                chart.locator("#org-zoom-organization").evaluate("el => { el.value = '1.2'; el.dispatchEvent(new Event('input', { bubbles: true })); }")
                screenshot("04a-org-chart")
            check("organization-graph", organization_check)

            def workflow_check():
                nonlocal conversation_id
                navigate("assistant")
                result = send("Browser smoke RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage tour from 2026-10-25, budget CNY 200000.", "delegate")
                conversation_id = result["conversation"]["id"]
                assert result["conversation"]["proposal"]["status"] == "pending_review", result["conversation"]["proposal"]
                expect(page.locator(".case-card")).to_be_visible()
                expect(page.locator("[data-review='approve']")).to_be_visible()
                screenshot("05-proposal")
                page.reload()
                expect(page.locator(".message.assistant").last).to_be_visible()
                expect(page.locator(".history-item.active")).to_have_count(1)
                assert page.evaluate("localStorage.getItem('atlasConversation')") == conversation_id
            check("workflow-history-reload", workflow_check)

            def work_check():
                navigate("work")
                page.locator("#view-work .segmented [data-work='options']").click()
                assert page.locator(".option-card").count() >= 3
                screenshot("06-options")
                page.locator("#view-work .segmented [data-work='schedule']").click()
                assert page.locator(".day-card").count() >= 3
                page.locator("#view-work .segmented [data-work='tasks']").click()
                assert page.locator(".task-card").count() >= 6
                assert page.locator("[data-complete]:enabled").count() == 0, "Task controls must wait for proposal approval."
                screenshot("07-tasks")
            check("work-tabs", work_check)

            def reviews_check():
                navigate("assistant")
                result = review("request_changes", "Keep this as a test proposal; confirm the schedule and revise the option explanation.")
                assert result["conversation"]["proposal"]["status"] == "changes_requested"
                review("resubmit", "Schedule checked; the option explanation and pacing are confirmed.")
                expect(page.locator("[data-review='approve']")).to_be_visible(timeout=60000)
                result = review("escalate", "Test escalation: the client wants a manager to confirm the pacing.")
                assert result["conversation"]["proposal"]["status"] == "escalated"
                expect(page.locator(".manager-note")).to_be_visible()
                result = review("resolve", "Manager reviewed the plan and confirms the current pacing is suitable.")
                assert result["conversation"]["proposal"]["status"] == "ready_to_resubmit"
                expect(page.locator("[data-review='resubmit']")).to_be_visible()
                review("resubmit", "Manager guidance has been incorporated; resubmit the current plan.")
                expect(page.locator("[data-review='approve']")).to_be_visible(timeout=60000)
                with page.expect_response(lambda response: response.url.endswith("/api/review"), timeout=60000) as response:
                    page.locator("[data-review='approve']").click()
                result = response.value.json()
                assert response.value.ok, result
                assert result["conversation"]["proposal"]["status"] in ("approved", "completed"), result["conversation"]["proposal"]
                screenshot("08-review-complete")
            check("reviews-comments-escalation-approval", reviews_check)

            def colleague_check():
                navigate("assistant")
                page.locator("#chat-target").select_option("finance_manager")
                result = send("Please explain the quote, financial checks and your role in this request.")
                answer = result["conversation"]["messages"][-1]
                assert answer["person_id"] == "finance_manager", answer
                expect(page.locator(".companion-name")).not_to_have_text("Atlas")
                screenshot("09-colleague-chat")
            check("colleague-chat", colleague_check)

            def reports_check():
                navigate("reports")
                assert page.locator(".download-card").count() == 3
                for link in page.locator(".download-card").all():
                    response = context.request.get(BASE + link.get_attribute("href"))
                    assert response.ok, response.status
                    assert len(response.body()) > 100
                page.locator("#case-search").fill("Chengdu")
                page.locator("#search-cases").click()
                expect(page.locator(".search-result").first).to_be_visible()
            check("reports-download-search", reports_check)

            def workspace_check():
                navigate("skills")
                expect(page.locator(".skill-card").first).to_be_visible()
                assert page.locator(".skill-card").count() >= 9
                for view in ("activity", "files", "connections"):
                    navigate(view)
                    expect(page.locator("#view-" + view + " .loading-state")).to_have_count(0)
                    expect(page.locator("#view-" + view)).not_to_contain_text("Could not load this page")
                RESULTS.append({"check": "portrait-loaded", "status": "passed"})
            check("workspace-library-connections", workspace_check)

            def mobile_check():
                page.set_viewport_size({"width": 390, "height": 844})
                page.goto(BASE)
                expect(page.locator("body")).to_have_attribute("data-ready", "true")
                expect(page.locator("#chat-input")).to_be_visible()
                page.locator("#menu-toggle").click()
                expect(page.locator("#sidebar")).to_have_class("sidebar open")
                page.locator(".main-nav [data-view='people']").click()
                expect(page.locator("#view-people")).to_be_visible()
                screenshot("10-mobile-people")
                page.locator("#menu-toggle").click()
                page.locator(".main-nav [data-view='organization']").click()
                expect(page.locator("#view-organization .org-inspector")).to_be_visible()
                page.wait_for_timeout(250)  # Let the mobile navigation slide fully out before the screenshot.
                screenshot("10a-mobile-org-chart")
                page.locator("#menu-toggle").click()
                page.locator(".main-nav [data-view='assistant']").click()
                screenshot("11-mobile-chat")
                width = page.evaluate("({page:document.documentElement.scrollWidth,viewport:innerWidth})")
                assert width["page"] <= width["viewport"] + 1, width
            check("mobile-navigation-layout", mobile_check)
        finally:
            restored = context.request.post(BASE + "/api/settings", data=baseline)
            RESULTS.append({"check": "restore-settings", "status": "passed" if restored.ok else "failed"})
            RESULTS.append({"check": "javascript-errors", "status": "passed" if not errors else "failed", "errors": errors})
            print(json.dumps({"results": RESULTS, "screenshots": str(OUT), "conversation_id": conversation_id}, indent=2))
            browser.close()
        if any(result["status"] == "failed" for result in RESULTS):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
