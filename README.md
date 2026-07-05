# TEst1

Automates daily parking booking at **12:00 PM**.

## Setup

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Usage

Run once:

```bash
python parking_bot.py --login-url "<parking-login-url>"
```

Run daily at 12:00 PM (Asia/Kolkata by default):

```bash
python parking_bot.py --login-url "<parking-login-url>" --daily
```

Default booking behavior:
- Click **Continue** on login page (if present)
- Select **APAC** (if not already selected), then click **Reserve Parking**
- Click **New Parking Request**
- Select **Pune**
- Set vehicle number to **5822**
- Select first available **4-wheeler** slot between **301 and 312**

Optional flags:
- `--headless` run Chromium headless
- `--timezone` override timezone
- `--location` override location (default Pune)
- `--vehicle` override vehicle number (default 5822)
- `--timeout-ms` override page timeout

If your slot table uses a custom row selector, set env var `SLOT_ROW_SELECTOR`.
