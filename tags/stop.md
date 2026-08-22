- [x] Approved


| Tag        | Importance   | Type    | Description                                                                 | Enum | Example |
|------------|--------------|---------|-----------------------------------------------------------------------------|------|---------|
| location   | recommended   | location   | The location of the stop.                                       |      |{latitude:52.4680333, longitude:13.2675331, is_exact: false}         |
| arrival_time  | recommended  | string (RFC 9557)   | Date, time and an optional time zone when the hitchhiker arrived at the location in [RFC 9557](https://www.rfc-editor.org/rfc/rfc9557.html) format.                                     |      |1996-12-19T16:39:57-08:00[America/Los_Angeles]         |
| departure_time   | recommended  | string (RFC 9557) | Date, time and an optional time zone when the hitchhiker left from the location in [RFC 9557](https://www.rfc-editor.org/rfc/rfc9557.html) format. |      |1996-12-19T17:39:57-08:00[America/Los_Angeles]         |
| waiting_duration   | recommended  | string | The waiting duration at the location in ISO 8601 duration format (usually minutes). If `arrival_time` and `departure_time` are given, this must be the exact difference between the two, as a consquence it is then assumed to be accurate. Can also be given, if the other two are not given - then it is assumed to be an estimation. |      |PT50M         |
| label   | optional  | string | Short free-text name for what this stop was. Most useful on an intermediate stop (any item that is neither the first nor the last in `stops`), where a bare coordinate does not say why the detour happened -- e.g. a driver took a hitchhiker to an onsen, a viewpoint, or their grandparents' house before continuing. Not restricted to intermediate stops: a labelled origin or destination ("a friend's place") is equally valid. |      |onsen         |
