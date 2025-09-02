#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

TARGET_URL = "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR/roll.html"
STATE_LABEL = "Bihar"
DISTRICT_LABEL = "West Champaran"
AC_LABEL = "Valmikinagar"
OUTPUT_ZIP = "valmikinagar.zip"

def download_valmikinagar_zip(output_path: Path):
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
            page.goto(TARGET_URL, wait_until="networkidle", timeout=120_000)
            page.wait_for_timeout(3000)

            # Handle cookie banner if present
            for sel in ["button:has-text('Accept')", "button:has-text('OK')"]:
                if page.locator(sel).first.is_visible(timeout=2000):
                    page.click(sel)
                    page.wait_for_timeout(1000)
                    break

            # Select State
            
            page.selectpage.wait_for_selector("select#selectStateAdd", state="attached", timeout=300_000)
            page.select_option("select#selectStateAdd", label=STATE_LABEL)
            page.wait_for_timeout(2000)

            # Select District
            page.wait_for_selector("select#selectDistrictAdd option:not([value=''])", timeout=200_000)
            page.select_option("select#selectDistrictAdd", label=DISTRICT_LABEL)
            page.wait_for_timeout(2000)

            # Select AC
            page.wait_for_selector("select#selectACAdd option:not([value=''])", timeout=200_000)
            page.select_option("select#selectACAdd", label=AC_LABEL)
            page.wait_for_timeout(2000)

            # Wait for download link
            page.wait_for_selector("table#tblResult a:has-text('Download')", timeout=300_000)
            with page.expect_download(timeout=60_000) as download_info:
                page.click("table#tblResult a:has-text('Download')")
            download = download_info.value
            download.save_as(str(output_path))

            print(f"✅ Downloaded: {output_path.resolve()}")

        except TimeoutError as e:
            page.screenshot(path="debug_failure.png", full_page=True)
            print(f"❌ Timeout: {e}")
            print("📸 Screenshot saved as debug_failure.png")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    download_valmikinagar_zip(Path(OUTPUT_ZIP))
