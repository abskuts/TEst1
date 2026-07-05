# Save My Seat Power Automate Workflow

This repository now documents a **Power Automate** solution for booking parking daily at **12:00 PM** on `https://savemyseat.atkinsrealis.com/`.

## Workflow overview

The implementation is split into two flows:

1. **Scheduled cloud flow**
   - Runs every day at 12:00 PM
   - Invokes a desktop flow
   - Sends success/failure notification
   - Logs the outcome

2. **Power Automate Desktop (PAD) flow**
   - Opens the Save My Seat site
   - Signs in with stored credentials
   - Clicks **Continue**
   - Ensures **APAC** is selected
   - Clicks **Reserve Parking**
   - Clicks **New Parking Request**
   - Selects **Pune**
   - Sets vehicle number to **5822**
   - Selects **All Day**
   - Books the first available slot from **301** to **312**
   - Captures confirmation details and screenshot

## Files

| File | Purpose |
| --- | --- |
| `/home/runner/work/TEst1/TEst1/docs/power-automate/cloud-flow.md` | Scheduled cloud flow design |
| `/home/runner/work/TEst1/TEst1/docs/power-automate/desktop-flow.md` | PAD step-by-step implementation |
| `/home/runner/work/TEst1/TEst1/docs/power-automate/workflow-manifest.json` | Variables, selectors, constants, outputs |

## Key settings

- Portal URL: `https://savemyseat.atkinsrealis.com/`
- Region: `APAC`
- Location: `Pune`
- Vehicle number: `5822`
- Parking type: `All Day`
- Slot order: `301` through `312`

## Security

- Do not hardcode credentials in the desktop flow.
- Store credentials in **Power Automate Desktop credential vault** or secure inputs/connections.
- Keep browser selectors in PAD tied to stable element attributes where possible.

## Recommended implementation order

1. Build the PAD flow from `desktop-flow.md`
2. Capture and update real selectors in `workflow-manifest.json`
3. Create the scheduled cloud flow from `cloud-flow.md`
4. Run one manual test
5. Enable the daily 12:00 PM schedule
