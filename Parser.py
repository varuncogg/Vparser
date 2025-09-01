#!/usr/bin/env python3
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Constants for your target
STATE_LABEL    = "Bihar"
DISTRICT_LABEL = "West Champaran"
AC_LABEL       = "Valmikinagar"
TARGET_URL     = "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR/roll.html"
OUTPUT_ZIP     = "valmikinagar.zip"

def download_valmikinagar(output_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True, slow_mo=50)
        context = browser.new_context(
            accept_downloads=True,
            user_agent=(
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        try:
            # 1. Go to page & wait for network to idle
            page.goto(TARGET_URL, wait_until="networkidle", timeout=120_000)
            page.wait_for_timeout(2_000)

            # 2. Handle cookie‐consent if it appears
            for sel in ["button:has-text('Accept')", "button:has-text('OK')"]:
                if page.locator(sel).first.is_visible(timeout=2_000):
                    page.click(sel)
                    page.wait_for_timeout(2_000)
                    break

            # 3. Select State
            page.wait_for_selector("select#selectStateAdd", timeout=20_000)
            page.select_option("select#selectStateAdd", label=STATE_LABEL)
            page.wait_for_timeout(2_000)

            # 4. Select District
            page.wait_for_selector("select#selectDistrictAdd option:not([value=''])", timeout=20_000)
            page.select_option("select#selectDistrictAdd", label=DISTRICT_LABEL)
            page.wait_for_timeout(2_000)

            # 5. Select Assembly-Constituency
            page.wait_for_selector("select#selectACAdd option:not([value=''])", timeout=20_000)
            page.select_option("select#selectACAdd", label=AC_LABEL)
            page.wait_for_timeout(2_000)

            # 6. Wait for Download link and trigger download
            page.wait_for_selector("table#tblResult a:has-text('Download')", timeout=30_000)
            with page.expect_download(timeout=60_000) as download_info:
                page.click("table#tblResult a:has-text('Download')")
            download = download_info.value
            download.save_as(str(output_path))

            print(f"✅ Download succeeded: {output_path.resolve()}")

        except PlaywrightTimeoutError as tie:
            # Dump a screenshot to help you see what’s going on
            snap = "debug-failure.png"
            page.screenshot(path=snap, full_page=True)
            print(f"❌ Timeout or missing selector: {tie}", file=sys.stderr)
            print(f"🔍 See screenshot: {snap}", file=sys.stderr)
            sys.exit(1)

        except Exception as exc:
            print(f"❌ Unexpected error: {exc}", file=sys.stderr)
            sys.exit(1)

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    out_file = Path(OUTPUT_ZIP)
    download_valmikinagar(out_file)
