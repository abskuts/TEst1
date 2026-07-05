"""
Parking Slot Auto-Booker
Runs daily at 12:00 PM and books the first available 4-wheeler slot (301-312)
for location "Pune", vehicle number 5822.

Configuration via environment variables (see .env.example):
  PARKING_URL      - Full URL of the "Save My Seat" login page
  PARKING_USERNAME - Login username / email
  PARKING_PASSWORD - Login password
"""

import os
import time
import logging
import schedule
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

PARKING_URL = os.environ.get("PARKING_URL", "")
USERNAME = os.environ.get("PARKING_USERNAME", "")
PASSWORD = os.environ.get("PARKING_PASSWORD", "")
VEHICLE_NUMBER = "5822"
TARGET_SLOTS = [str(i) for i in range(301, 313)]  # 301 to 312 inclusive


def book_parking() -> None:
    log.info("Starting parking booking at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if not PARKING_URL:
        log.error("PARKING_URL is not set. Please configure it in .env")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # ── Step 1: Navigate to login page ────────────────────────────────
            log.info("Navigating to %s", PARKING_URL)
            page.goto(PARKING_URL, wait_until="networkidle")

            # ── Step 2: Login (if login form is present) ──────────────────────
            if page.locator("input[type='password']").count() > 0:
                log.info("Login form detected — entering credentials")
                username_field = page.locator("input[type='email'], input[type='text']").first
                username_field.fill(USERNAME)
                page.locator("input[type='password']").fill(PASSWORD)
                page.locator("button[type='submit'], input[type='submit']").click()
                page.wait_for_load_state("networkidle")

            # ── Step 3: Click the "Continue" button ───────────────────────────
            log.info("Looking for Continue button")
            continue_btn = page.get_by_role("button", name="Continue").or_(
                page.get_by_text("Continue", exact=True)
            )
            continue_btn.wait_for(timeout=15_000)
            continue_btn.click()
            page.wait_for_load_state("networkidle")

            # ── Step 4: Select "APAC" from the region/group dropdown ──────────
            log.info("Checking region dropdown for APAC")
            region_dropdown = page.locator("select").first
            current_value = region_dropdown.input_value()
            if "APAC" not in current_value:
                log.info("Selecting APAC in dropdown (current: %s)", current_value)
                region_dropdown.select_option(label="APAC")
                page.wait_for_load_state("networkidle")
            else:
                log.info("APAC is already selected")

            # ── Step 5: Click "Reserve Parking" ──────────────────────────────
            log.info("Clicking Reserve Parking")
            reserve_btn = page.get_by_role("button", name="Reserve Parking").or_(
                page.get_by_text("Reserve Parking", exact=True)
            )
            reserve_btn.wait_for(timeout=15_000)
            reserve_btn.click()
            page.wait_for_load_state("networkidle")

            # ── Step 6: Click "New Parking Request" ───────────────────────────
            log.info("Clicking New Parking Request")
            new_req_btn = page.get_by_role("button", name="New Parking Request").or_(
                page.get_by_text("New Parking Request", exact=True)
            )
            new_req_btn.wait_for(timeout=15_000)
            new_req_btn.click()
            page.wait_for_load_state("networkidle")

            # ── Step 7: Select "Pune" from location dropdown ──────────────────
            log.info("Selecting Pune as location")
            location_dropdown = page.locator("select").filter(
                has_text=lambda t: "Pune" in (page.locator("select").all_inner_texts() or [])
            )
            # Fallback: iterate all selects to find the one containing "Pune"
            all_selects = page.locator("select").all()
            pune_select = None
            for sel in all_selects:
                options = sel.locator("option").all_inner_texts()
                if any("Pune" in opt for opt in options):
                    pune_select = sel
                    break
            if pune_select is None:
                log.error("Could not find a dropdown containing 'Pune'")
                return
            pune_select.select_option(label="Pune")
            page.wait_for_load_state("networkidle")

            # ── Step 8: Fill in vehicle number ───────────────────────────────
            log.info("Entering vehicle number %s", VEHICLE_NUMBER)
            vehicle_field = page.locator(
                "input[name*='vehicle'], input[placeholder*='vehicle'], input[id*='vehicle']"
            ).first
            vehicle_field.fill(VEHICLE_NUMBER)

            # ── Step 9: Select "All Day" slot ─────────────────────────────────
            log.info("Looking for All Day option")
            all_day = page.get_by_label("All Day").or_(
                page.get_by_text("All Day", exact=True)
            )
            if all_day.count() > 0:
                all_day.first.click()

            # ── Step 10: Find and book first available slot 301-312 ───────────
            log.info("Searching for available slots 301-312")
            booked = False
            for slot_num in TARGET_SLOTS:
                # Look for an element representing the slot that is "Available"
                slot_el = page.locator(
                    f"[data-slot='{slot_num}'], "
                    f"td:has-text('{slot_num}'), "
                    f"div:has-text('{slot_num}'), "
                    f"button:has-text('{slot_num}')"
                ).filter(has_text="Available")

                if slot_el.count() == 0:
                    # Try a broader match: slot label/button whose parent shows Available
                    slot_el = page.locator(f"text={slot_num}").locator(
                        "xpath=ancestor::tr | xpath=ancestor::div[contains(@class,'slot')]"
                    ).filter(has_text="Available")

                if slot_el.count() > 0:
                    log.info("Slot %s is available — clicking it", slot_num)
                    slot_el.first.click()
                    booked = True
                    break

            if not booked:
                log.warning("No available slots found between 301 and 312")
                return

            # ── Step 11: Submit / Confirm booking ─────────────────────────────
            log.info("Submitting booking")
            submit_btn = page.get_by_role("button", name="Book").or_(
                page.get_by_role("button", name="Confirm").or_(
                    page.get_by_role("button", name="Submit")
                )
            )
            if submit_btn.count() > 0:
                submit_btn.first.click()
                page.wait_for_load_state("networkidle")

            log.info("Booking completed successfully")

        except PlaywrightTimeoutError as exc:
            log.error("Timed out waiting for a page element: %s", exc)
        except Exception as exc:
            log.exception("Unexpected error during booking: %s", exc)
        finally:
            context.close()
            browser.close()


def main() -> None:
    log.info("Parking bot started — scheduling daily booking at 12:00 PM")
    schedule.every().day.at("12:00").do(book_parking)

    # Run once immediately if --now flag is passed (useful for testing)
    import sys
    if "--now" in sys.argv:
        log.info("--now flag detected, running booking immediately")
        book_parking()
        return

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
