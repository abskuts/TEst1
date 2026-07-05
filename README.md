# Parking Slot Auto-Booker

Automatically books a 4-wheeler parking slot (301–312) every day at **12:00 PM** on the "Save My Seat" portal.

## What the bot does

1. Navigates to the parking portal login page and logs in.
2. Clicks the **Continue** button on the welcome screen.
3. Checks the region dropdown — selects **APAC** if it is not already selected.
4. Clicks **Reserve Parking**.
5. Clicks **New Parking Request**.
6. Selects **Pune** as the location.
7. Sets the vehicle number to **5822**.
8. Selects the **All Day** slot option.
9. Picks the **first available slot between 301 and 312** and books it.
10. Submits/confirms the booking.

## Requirements

- Python 3.10+
- Google Chrome (installed automatically by Playwright)

## Setup

```bash
# 1. Clone the repo and enter it
git clone https://github.com/abskuts/TEst1.git
cd TEst1

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install the Playwright browser
playwright install chromium

# 5. Configure credentials
cp .env.example .env
# Edit .env and fill in PARKING_URL, PARKING_USERNAME, PARKING_PASSWORD
```

## Configuration (`.env`)

| Variable           | Description                                    |
|--------------------|------------------------------------------------|
| `PARKING_URL`      | Full URL of the "Save My Seat" login page      |
| `PARKING_USERNAME` | Your login email / username                    |
| `PARKING_PASSWORD` | Your login password                            |

## Running

### Scheduled (runs every day at 12:00 PM)

```bash
python parking_bot.py
```

Keep this process running (e.g. in a `screen`/`tmux` session, or as a systemd service).

### Run once immediately (for testing)

```bash
python parking_bot.py --now
```

## Logs

The bot logs all steps to stdout with timestamps. Redirect to a file if needed:

```bash
python parking_bot.py >> parking.log 2>&1 &
```

## Notes

- The bot runs in **headless** mode (no visible browser window).
- If the slot-selector elements on the page use different HTML attributes than expected, you may need to adjust the selectors in `parking_bot.py` (Step 10 in `book_parking()`).
- Slots 301–312 are tried **in order**; the first available one is booked.
