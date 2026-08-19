- [x] Approved


| Tag         | Importance   | Type      | Description                                                                 | Enum | Example |
|-------------|--------------|-----------|-----------------------------------------------------------------------------|------|---------|
| vehicle_destination | optional  | location  | Final destination of the vehicle ride (or of any other `mode_of_transportation`). Can be further than the hitchhiking ride. |      |{latitude:52.5580333, longitude:11.2675331, is_exact: true}         |
| reasons     | optional  | list[string]    | Claimed purpose or reasons of the ride by the `occupants`. | holiday, commute, business, recreational, errands   | [commute]         |
| expected_payment | `[amount, currency]`   | optional       | Payment demanded by the driver/occupants for this ride, if any. Presence of this field means payment was demanded; omit it if none was asked, regardless of whether it was actually paid. `currency` uses ISO 4217 or common crypto codes (BTC, SATS), same as `gift.md`'s `price`. `amount` is a positive decimal number. |             | `["10", "EUR"]` |
