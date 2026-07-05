# Power Automate Desktop Flow

## Flow name

`Reserve Save My Seat Parking`

## Input variables

| Variable | Type | Example |
| --- | --- | --- |
| `PortalUrl` | Text | `https://savemyseat.atkinsrealis.com/` |
| `PreferredRegion` | Text | `APAC` |
| `PreferredLocation` | Text | `Pune` |
| `VehicleNumber` | Text | `5822` |
| `ParkingDuration` | Text | `All Day` |
| `SlotListCsv` | Text | `301,302,303,304,305,306,307,308,309,310,311,312` |
| `MaxRetryCount` | Number | `3` |
| `ElementTimeoutSeconds` | Number | `20` |

## Output variables

| Variable | Meaning |
| --- | --- |
| `BookingStatus` | `Success`, `NoSlot`, or `Failed` |
| `BookedSlot` | Reserved slot number |
| `ResultMessage` | Human-readable result |
| `ConfirmationText` | Booking confirmation text from the page |
| `ScreenshotPath` | Saved screenshot file path |

## Credentials

Create a PAD credential entry and load it at runtime:

- `SaveMySeatUsername`
- `SaveMySeatPassword`

Do not store these values as plain text in the flow.

## Implementation steps

### 1. Initialize variables

- Split `SlotListCsv` into a list variable `SlotList`
- Set:
  - `BookingStatus = Failed`
  - `BookedSlot =`
  - `ResultMessage = Flow started`
  - `ConfirmationText =`

### 2. Launch browser

Use **Launch new Microsoft Edge** or **Launch new Chrome**:

- URL: `%PortalUrl%`
- Wait for page to load
- Store browser instance in `Browser`

### 3. Sign in

Use captured web elements for:

- username/email textbox
- password textbox
- sign-in button

Actions:

1. Populate username from credential vault
2. Populate password from credential vault
3. Click sign-in
4. Wait for page content to load

### 4. Click Continue

- Wait for **Continue** button
- Click **Continue**
- Wait until next page is loaded

### 5. Ensure APAC is selected

1. Read the selected value from the region dropdown
2. If selected value is not `%PreferredRegion%`:
   - Select `%PreferredRegion%`
   - Wait for page update
3. Click **Reserve Parking**

### 6. Open a new parking request

- Wait for **New Parking Request**
- Click it
- Wait until the request form is available

### 7. Fill the request form

1. Select `%PreferredLocation%` from location dropdown
2. Set vehicle textbox to `%VehicleNumber%`
3. Select `%ParkingDuration%` such as **All Day**

### 8. Select first available slot from 301 to 312

Use a **For each** loop over `SlotList`.

For each `CurrentSlot`:

1. Find the slot row/tile matching `%CurrentSlot%`
2. Read the availability text for that slot
3. If availability equals `Available`:
   - Click the slot
   - Set `BookedSlot = %CurrentSlot%`
   - Set `BookingStatus = Success`
   - Set `ResultMessage = Slot booked`
   - Exit loop

After the loop:

- If `BookedSlot` is empty:
  - Set `BookingStatus = NoSlot`
  - Set `ResultMessage = No slot available between 301 and 312`
  - Take screenshot
  - End flow

### 9. Submit booking

If `BookingStatus = Success`:

1. Click **Book**, **Submit**, or **Confirm**
2. Wait for confirmation page/message
3. Extract confirmation text
4. Take screenshot of confirmation
5. Set `ResultMessage = Booking completed successfully`

### 10. Reliability controls

Wrap major sections with retry logic:

- Launch/sign-in
- Continue page
- Reserve Parking page
- New Parking Request page
- Final submit

Recommended pattern:

1. Use a numeric variable `RetryCounter`
2. Retry up to `%MaxRetryCount%`
3. On failure:
   - refresh page or reopen the browser only when required
   - wait a few seconds
   - try again

Use **Wait for web page content** or **Wait for element** after each critical action.

### 11. Error handling

In the flow’s error path:

1. Set `BookingStatus = Failed`
2. Set `ResultMessage` to the failing step
3. Take screenshot
4. Close browser if open
5. Return outputs to the cloud flow

## Selector guidance

Capture stable selectors for these elements:

- sign-in username field
- sign-in password field
- sign-in button
- Continue button
- APAC region dropdown
- Reserve Parking button
- New Parking Request button
- Pune location dropdown
- vehicle textbox
- All Day option
- slot tile/row
- slot availability label
- final submit button
- confirmation message

Prefer:

1. element IDs
2. stable automation attributes
3. unique names

Avoid selectors based only on position when possible.

## Suggested local screenshot folder

Use a timestamped file under a folder such as:

`C:\PowerAutomate\Parking\Screenshots`
