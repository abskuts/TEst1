#!/usr/bin/env python3
import argparse
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except Exception:
    class PlaywrightTimeoutError(Exception):
        pass


SLOT_MIN = 301
SLOT_MAX = 312


@dataclass
class BotConfig:
    login_url: str
    timezone: str
    headless: bool
    reserve_timeout_ms: int
    location: str
    vehicle_number: str


def _first_visible(page, selectors):
    for selector in selectors:
        locator = page.locator(selector).first
        if locator.count() and locator.is_visible():
            return locator
    return None


def _safe_click(locator):
    try:
        locator.click(timeout=3000)
        return True
    except Exception:
        return False


def parse_slot_number(text: str):
    match = re.search(r"\b(3(?:0[1-9]|1[0-2]))\b", text)
    return int(match.group(1)) if match else None


def pick_first_available_slot_text(texts):
    best = None
    for text in texts:
        text_lc = text.lower()
        if "available" not in text_lc:
            continue
        if "4" not in text_lc:
            continue
        slot = parse_slot_number(text)
        if slot is None or not (SLOT_MIN <= slot <= SLOT_MAX):
            continue
        if best is None or slot < best[0]:
            best = (slot, text)
    return best[1] if best else None


def wait_until_noon(timezone_name: str):
    tz = ZoneInfo(timezone_name)
    now = datetime.now(tz)
    target = now.replace(hour=12, minute=0, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"Waiting until {target.isoformat()} ({int(wait_seconds)}s)")
    time.sleep(wait_seconds)


def click_continue(page):
    continue_selectors = [
        "button:has-text('Continue')",
        "input[type='submit'][value*='Continue' i]",
        "[role='button']:has-text('Continue')",
    ]
    locator = _first_visible(page, continue_selectors)
    if locator:
        print("Clicking Continue")
        return _safe_click(locator)
    print("Continue button not found; proceeding")
    return False


def select_apac_and_reserve(page):
    apac_dropdown = _first_visible(
        page,
        [
            "select:has(option:has-text('APAC'))",
            "[role='combobox']",
            "select",
        ],
    )
    if apac_dropdown:
        value = apac_dropdown.input_value().strip().lower()
        if "apac" not in value:
            try:
                apac_dropdown.select_option(label="APAC")
            except Exception:
                apac_dropdown.click()
                page.get_by_text("APAC", exact=False).first.click(timeout=3000)
            print("Selected APAC")
        else:
            print("APAC already selected")

    reserve_button = _first_visible(
        page,
        [
            "button:has-text('Reserve Parking')",
            "[role='button']:has-text('Reserve Parking')",
            "button:has-text('Reserve')",
        ],
    )
    if not reserve_button:
        raise RuntimeError("Reserve Parking button not found")
    print("Clicking Reserve Parking")
    reserve_button.click(timeout=10000)


def click_new_parking_request(page):
    btn = _first_visible(
        page,
        [
            "button:has-text('New Parking Request')",
            "[role='button']:has-text('New Parking Request')",
            "a:has-text('New Parking Request')",
        ],
    )
    if not btn:
        raise RuntimeError("New Parking Request button not found")
    print("Clicking New Parking Request")
    btn.click(timeout=10000)


def choose_location(page, location: str):
    location_selector = _first_visible(
        page,
        [
            "select:has(option:has-text('Pune'))",
            "label:has-text('Location') + select",
            "select",
            "[role='combobox']",
        ],
    )
    if not location_selector:
        raise RuntimeError("Location selector not found")

    try:
        location_selector.select_option(label=location)
    except Exception:
        location_selector.click()
        page.get_by_text(location, exact=False).first.click(timeout=3000)
    print(f"Selected location: {location}")


def set_vehicle_number(page, vehicle_number: str):
    vehicle_input = _first_visible(
        page,
        [
            "input[placeholder*='Vehicle' i]",
            "input[name*='vehicle' i]",
            "input[id*='vehicle' i]",
            "input[type='text']",
        ],
    )
    if not vehicle_input:
        raise RuntimeError("Vehicle number input not found")
    vehicle_input.fill(vehicle_number)
    print(f"Updated vehicle number to: {vehicle_number}")


def _collect_candidate_slot_rows(page):
    selector = os.getenv("SLOT_ROW_SELECTOR", "tr, .slot-row, .mat-row, li")
    rows = page.locator(selector)
    return [rows.nth(i) for i in range(rows.count())]


def select_first_available_slot(page):
    rows = _collect_candidate_slot_rows(page)
    best = None
    for row in rows:
        try:
            text = row.inner_text(timeout=1000)
        except Exception:
            continue
        text_lc = text.lower()
        slot = parse_slot_number(text)
        if slot is None:
            continue
        if "available" not in text_lc:
            continue
        if "4" not in text_lc:
            continue
        if best is None or slot < best[0]:
            best = (slot, row)

    if not best:
        raise RuntimeError("No available 4-wheeler slot found from 301 to 312")

    slot, row = best
    print(f"Selecting slot {slot}")
    preferred_click_targets = [
        "button:has-text('All Day')",
        "button:has-text('Book')",
        "button:has-text('Reserve')",
        "button:has-text('Select')",
        "[role='button']:has-text('All Day')",
    ]
    for target in preferred_click_targets:
        button = row.locator(target).first
        if button.count() and button.is_visible():
            if _safe_click(button):
                return slot

    if _safe_click(row):
        return slot

    raise RuntimeError(f"Unable to click available slot {slot}")


def book_parking(config: BotConfig):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.headless)
        context = browser.new_context()
        page = context.new_page()
        print(f"Opening {config.login_url}")
        page.goto(config.login_url, wait_until="domcontentloaded", timeout=config.reserve_timeout_ms)

        click_continue(page)
        page.wait_for_timeout(1000)

        select_apac_and_reserve(page)
        page.wait_for_timeout(1000)

        click_new_parking_request(page)
        page.wait_for_timeout(1000)

        choose_location(page, config.location)
        set_vehicle_number(page, config.vehicle_number)
        slot = select_first_available_slot(page)

        print(f"Booked slot candidate: {slot}")
        browser.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Automatic parking booking bot")
    parser.add_argument("--login-url", required=True, help="Parking login URL")
    parser.add_argument("--timezone", default="Asia/Kolkata", help="Timezone for 12:00 PM schedule")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    parser.add_argument("--daily", action="store_true", help="Run every day at 12:00 PM")
    parser.add_argument("--location", default="Pune", help="Parking location value")
    parser.add_argument("--vehicle", default="5822", help="Vehicle number")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Playwright timeout in milliseconds")
    return parser.parse_args()


def main():
    args = parse_args()
    config = BotConfig(
        login_url=args.login_url,
        timezone=args.timezone,
        headless=args.headless,
        reserve_timeout_ms=args.timeout_ms,
        location=args.location,
        vehicle_number=args.vehicle,
    )

    while True:
        if args.daily:
            wait_until_noon(config.timezone)
        try:
            book_parking(config)
            print("Parking flow completed")
        except PlaywrightTimeoutError as exc:
            print(f"Timeout while booking parking: {exc}", file=sys.stderr)
        except Exception as exc:
            print(f"Parking booking failed: {exc}", file=sys.stderr)

        if not args.daily:
            break


if __name__ == "__main__":
    main()
