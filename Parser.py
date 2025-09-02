#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
import os
import time

TARGET_URL = "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR/roll.html"
AC_LABEL = "VALMIKINAGAR"  # Change to match the row text exactly
OUTPUT_ZIP = "valmikinagar.zip"

PROGRESS_INTERVAL = 30  # seconds between progress logs/screenshots
MAX_WAIT = 60 * 60       # 1 hour max wait
SCREENSHOT_DIR = Path("screenshots")

def download_zip(output_path: Path):
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            print(f"🌐 Opening {TARGET_URL}")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=120_000)

            # # Wait for the table and the correct row
            # selector = f"tr:has-text('{AC_LABEL}') button:has-text('Download')"
            # page.wait_for_selector(selector, timeout=180_000)

            # print(f"📥 Clicking download for {AC_LABEL}...")
            # with page.expect_download(timeout=MAX_WAIT * 1000) as download_info:
            #     page.click(selector)
            try:
                # start listening for a download
                with page.expect_download(timeout=120_000) as dl_info:
                    # this triggers the JS click-handler you wrote
                    page.click("button.btn-download")
                download = dl_info.value
                path = Path(download.path())
                temp_path = download.path()
                print("✅ Saved to", path.resolve())
            except TimeoutError:
                print("❌ Download never started or timed out")

            # download = download_info.value
            # temp_path = download.path()

            # Monitor file size until stable
            last_size = -1
            stable_count = 0
            start_time = time.time()
            iteration = 0

            while True:
                iteration += 1
                screenshot_path = SCREENSHOT_DIR / f"progress_{iteration}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)

                if os.path.exists(temp_path):
                    size = os.path.getsize(temp_path)
                    print(f"⏳ Downloading... {size / (1024*1024):.2f} MB")
                    if size == last_size:
                        stable_count += 1
                    else:
                        stable_count = 0
                    last_size = size

                    # If size hasn't changed for 3 intervals, assume complete
                    if stable_count >= 3:
                        break
                else:
                    print("Waiting for file to appear...")

                if time.time() - start_time > MAX_WAIT:
                    raise TimeoutError("Download timed out.")

                time.sleep(PROGRESS_INTERVAL)

            # Save final file
            download.save_as(str(output_path))
            print(f"✅ Download complete: {output_path.resolve()}")

            # Final screenshot
            page.screenshot(path=str(SCREENSHOT_DIR / "final_success.png"), full_page=True)

        except TimeoutError as e:
            page.screenshot(path=str(SCREENSHOT_DIR / "debug_failure.png"), full_page=True)
            print(f"❌ Timeout: {e}")
            print(f"📸 Failure screenshot saved in {SCREENSHOT_DIR}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    download_zip(Path(OUTPUT_ZIP))
