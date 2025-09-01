#!/usr/bin/env python3

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def download_valmikinagar(output_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            page.goto(
                "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR/roll.html",
                wait_until="networkidle",
                timeout=60_000
            )

            # 1. Wait for the AC dropdown to populate
            page.wait_for_selector("select#selectACAdd option:not([value=''])", timeout=30_000)

            # 2. Select Valmikinagar
            page.select_option("select#selectACAdd", label="Valmikinagar")

            # 3. Wait for the table Download link to appear
            page.wait_for_selector("table#tblResult a:has-text('Download')", timeout=30_000)

            # 4. Trigger and save the download
            with page.expect_download(timeout=60_000) as dl:
                page.click("table#tblResult a:has-text('Download')")
            download = dl.value
            download.save_as(str(output_path))

            print(f"✅ Download succeeded: {output_path.resolve()}")

        except PlaywrightTimeoutError:
            print("❌ Timed out waiting for dropdown, link, or download.", file=sys.stderr)
            sys.exit(1)
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    out_file = Path("valmikinagar.zip")
    try:
        download_valmikinagar(out_file)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
