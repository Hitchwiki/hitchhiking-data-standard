- [x] Approved


| Tag         | Importance   | Type      | Description                                                                 | Enum | Example |
|-------------|--------------|-----------|-----------------------------------------------------------------------------|------|---------|
| vehicle_destination | optional  | location  | Final destination of the vehicle ride (or of any other `mode_of_transportation`). Can be further than the hitchhiking ride. |      |{latitude:52.5580333, longitude:11.2675331, is_exact: true}         |
| reasons     | optional  | list[string]    | Claimed purpose or reasons of the ride by the `occupants`. | holiday, commute, business, recreational    | [commute]         |
