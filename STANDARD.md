- [ ] Approved


| Tag                  | Importance   | Type                | Description                                                                                                         | Enum           | Example |
|----------------------|--------------|---------------------|---------------------------------------------------------------------------------------------------------------------|----------------|---------|
| origin                | required  | location            | Starting location of the hitchhiking ride.                                                                             |                |
| destination          | recommended  | location            | Destination of the hitchhiking ride.                                                                                |                |
| star_rating          | recommended  | int                 | Very subjective rating of the spot where the ride started.                                                          | 1, 2, 3, 4, 5  |
| waiting_time_minutes | recommended  | int                 | Positive integer indicating the timespan from when rides were first solicited until the hitchhiker got their ride.  |                |
| comment              | optional  | string              | Any free-form comment about the starting location, destination or the entire ride. Preferrably in English language.                                 |                |
| departure_time           | recommended  | string (Unix TS Secs)  | Departure time when the ride started from `origin` in UTC timestamp (seconds) format.                |                |
| origin_tz           | recommended  | string (IANA TZ ID)  |  IANA Timezone ID of the origin (e.g., "America/New_York") for accurate local time display. Required if `departure_time` is present.              |                |
| arrival_time         | optional  | string (Unix TS Secs)  | Arrival time when the ride ended in `destination` in UTC timestamp (seconds) format.|                |
| destination_tz           | recommended  | string (IANA TZ ID)  |  IANA Timezone ID of the destination (e.g., "America/New_York") for accurate local time display. Required if `arrival_time` is present.          |                |
| signal               | optional  | signal              | Information about the method used to get the ride                                                                   |                |
| gifts                 | optional  | list[gift]          | Possible gift that the hitchhiker received from the passengers.                                                     |                |
| hitchhikers          | required  | list[person]        | Most often a description of a solo-hitchhiker but also caters for couples or groups of hitchhikers. To convey not more than the number of hitchhikers use empty `person` objects.                |                |
| passengers           | optional  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| mode_of_transportation              | optional  | mode_of_transportation    | Information about the vehicle that was used for the ride. In rarer cases this could be a plane or boat as well.           |                |
| ride                 | optional  | ride                | Information about the ride of the car beyond the hitchhiker's ride.                                                 |                |
| declined_rides       | optional  | list[decline_ride]  | Information about rides that were offered to the hitchhiker but that were declined by the them.                     |                |
| source       | required  | string  | Source of this record by URL of the application. Or "private" if the records stem from an independently and individually collected source.               |                |
| reasons       | option  | list[string]  | Reason of the hitchhiking ride.        | commute, holiday, sport, no_money, safe_money, exchange, adventure, fun, social_contact, ecological_reasons             |
