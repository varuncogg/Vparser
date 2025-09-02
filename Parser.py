#!/usr/bin/env python3
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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

            # Optional: Wait for specific row if needed
            selector = f"tr:has-text('{AC_LABEL}') button:has-text('Download')"
            try:
                page.wait_for_selector(selector, timeout=180_000)
                print(f"📥 Clicking download for {AC_LABEL}...")
                with page.expect_download(timeout=MAX_WAIT * 1000) as download_info:
                    page.click(selector)
                download = download_info.value
            except PlaywrightTimeoutError:
                print(f"⚠️ Could not find selector for {AC_LABEL}, falling back to generic button.")
                with page.expect_download(timeout=180_000) as dl_info:
                    page.click("button.btn-download")
                download = dl_info.value

            temp_path = download.path()
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

                    if stable_count >= 3:
                        break
                else:
                    print("Waiting for file to appear...")

                if time.time() - start_time > MAX_WAIT:
                    raise PlaywrightTimeoutError("Download timed out.")

                time.sleep(PROGRESS_INTERVAL)

            download.save_as(str(output_path))
            print(f"✅ Download complete: {output_path.resolve()}")
            page.screenshot(path=str(SCREENSHOT_DIR / "final_success.png"), full_page=True)

        except PlaywrightTimeoutError as e:
            page.screenshot(path=str(SCREENSHOT_DIR / "debug_failure.png"), full_page=True)
            print(f"❌ Timeout: {e}")
            print(f"📸 Failure screenshot saved in {SCREENSHOT_DIR}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    download_zip(Path(OUTPUT_ZIP))
