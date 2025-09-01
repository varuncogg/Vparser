#!/usr/bin/env python3

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def download_valmikinagar(output_path: Path):
    with sync_playwright() as p:
        # Launch Chrome; on CI ubuntu-latest Chrome is pre-installed
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # Navigate and wait for links
            page.goto(
                "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR/roll.html",
                timeout=60_000
            )
            page.wait_for_selector("a:has-text('Download')", timeout=30_000)

            # Grab the first Download link (Valmikinagar)
            download_link = page.locator("a:has-text('Download')").first

            # Trigger the download
            with page.expect_download() as download_info:
                download_link.click()
            download = download_info.value

            # Save to desired filename
            download.save_as(str(output_path))
            print(f"✅ Download succeeded: {output_path.resolve()}")

        except PlaywrightTimeoutError:
            print("❌ Timed out waiting for download link or download.", file=sys.stderr)
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
