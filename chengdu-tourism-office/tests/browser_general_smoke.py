"""Read-only visual smoke check of the live multi-purpose company UI."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE = "http://127.0.0.1:8765"
OUT = Path(__file__).resolve().parents[1] / "output" / "ui-qa"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
        )
        for width, height, label in [(1512, 982, "desktop"), (390, 844, "mobile")]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(BASE, wait_until="networkidle")
            page.wait_for_selector('body[data-ready="true"]')
            for view in ["assistant", "people", "organization", "skills", "activity", "files", "connections", "settings"]:
                if view != "assistant":
                    page.locator(f'[data-view="{view}"]').first.evaluate("element => element.click()")
                page.locator("#view-" + view).wait_for(state="visible")
                page.screenshot(path=str(OUT / f"{label}-{view}.png"), full_page=True)
                extent = page.evaluate("({scroll: document.documentElement.scrollWidth, viewport: innerWidth})")
                results.append({"viewport": label, "view": view, "horizontal_overflow_px": max(0, extent["scroll"] - extent["viewport"]), "page_errors": list(errors)})
            if label == "desktop":
                conversations = page.request.get(BASE + "/api/conversations").json()
                sample = next((c for c in conversations if "draft PowerPoint proposal" in c["title"]), None)
                if sample:
                    page.evaluate("id => openConversation(id)", sample["id"])
                    page.locator(".message-table-wrap table").first.wait_for(state="visible")
                    page.locator('.message-text a[href^="/api/files/"]').first.wait_for(state="visible")
                    page.screenshot(path=str(OUT / "desktop-chat-result.png"), full_page=True)
                    results.append({"viewport": label, "view": "chat-result", "tables": page.locator(".message-table-wrap table").count(), "file_links": page.locator('.message-text a[href^="/api/files/"]').count(), "page_errors": list(errors)})
            page.close()
        browser.close()
    print(json.dumps(results, indent=2))
    if any(r.get("horizontal_overflow_px", 0) > 3 or r["page_errors"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
