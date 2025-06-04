- [ ] Approved


| Tag        | Importance   | Type    | Description                                                                 | Enum | Example |
|------------|--------------|---------|-----------------------------------------------------------------------------|------|---------|
| location   | recommended   | location   | The location of the stop.                                       |      |         |
| arrival_time  | recommended  | string (RFC 9557)   | Date, time and an optional time zone when the hitchhiker arrived at the location in [RFC 9557](https://www.rfc-editor.org/rfc/rfc9557.html) format.                                     |      |         |
| departure_time   | recommended  | string (RFC 9557) | Date, time and an optional time zone when the hitchhiker left from the location in [RFC 9557](https://www.rfc-editor.org/rfc/rfc9557.html) format. |      |         |
| waiting_time_minutes   | recommended  | int | The waiting time at the location in minutes. If `arrival_time` and `departure_time` are given, this must be the difference between the two. Can also be given, if the other two are not given. |      |         |
