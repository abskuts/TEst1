# Scheduled Cloud Flow

## Flow name

`Parking Booking Scheduler`

## Trigger

- **Type:** Scheduled cloud flow
- **Frequency:** Day
- **Interval:** 1
- **Time:** 12:00 PM
- **Time zone:** Set to your local time zone before enabling the flow

## Required connections

- Power Automate Desktop / machine runtime
- Outlook or Teams for notification

## Inputs passed to desktop flow

Pass these values into the desktop flow:

| Input | Value |
| --- | --- |
| `PortalUrl` | `https://savemyseat.atkinsrealis.com/` |
| `PreferredRegion` | `APAC` |
| `PreferredLocation` | `Pune` |
| `VehicleNumber` | `5822` |
| `ParkingDuration` | `All Day` |
| `SlotListCsv` | `301,302,303,304,305,306,307,308,309,310,311,312` |
| `MaxRetryCount` | `3` |
| `ElementTimeoutSeconds` | `20` |

## Actions

1. **Recurrence**
   - Daily at 12:00 PM

2. **Initialize variable – RunTimestamp**
   - Type: String
   - Value: current timestamp

3. **Run a desktop flow**
   - Machine: target Windows machine or machine group
   - Flow: `Reserve Save My Seat Parking`
   - Inputs: use the values above
   - Capture outputs:
     - `BookingStatus`
     - `BookedSlot`
     - `ResultMessage`
     - `ConfirmationText`
     - `ScreenshotPath`

4. **Condition – booking succeeded**
   - Success when `BookingStatus` equals `Success`

5. **If success**
   - Send email or Teams message with:
     - run timestamp
     - booked slot
     - confirmation text
     - screenshot path

6. **If no slot**
   - Send email or Teams message with:
     - run timestamp
     - `No slot available`
     - screenshot path if present

7. **If failed**
   - Send email or Teams message with:
     - run timestamp
     - failure message
     - screenshot path if present

## Suggested notification subject

- Success: `Parking booked successfully - @{BookedSlot}`
- No slot: `Parking booking not completed - no slot available`
- Failure: `Parking booking failed`

## Logging recommendation

If you want a simple audit trail, append one record per run to Excel, SharePoint, or Dataverse with:

- Timestamp
- Status
- Slot
- Message
- Screenshot path

## Manual test checklist

Before enabling the schedule:

1. Run the cloud flow manually
2. Verify desktop flow starts on the target machine
3. Verify notification is sent
4. Verify the output values are populated
5. Enable daily schedule only after the manual test passes
