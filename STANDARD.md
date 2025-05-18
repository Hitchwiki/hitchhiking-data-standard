- [ ] Approved


| Tag                  | Importance   | Type                | Description                                                                                                         | Enum           | Example |
|----------------------|--------------|---------------------|---------------------------------------------------------------------------------------------------------------------|----------------|---------|
| start                | required  | location            | Starting point of the hitchhiking ride.                                                                             |                |
| destination          | recommended  | location            | Destination of the hitchhiking ride.                                                                                |                |
| star_rating          | recommended  | int                 | Very subjective rating of the spot where the ride started.                                                          | 1, 2, 3, 4, 5  |
| waiting_time_minutes | recommended  | int                 | Positive integer indicating the timespan from when rides were first solicited until the hitchhiker got their ride.  |                |
| comment              | optional  | string              | Any free-form comment about the starting location, destination or the entire ride.                                  |                |
| start_time           | recommended  | string (date-time)  | Date and time when the ride started from `start` in ... format. The time-zone of `start` is assumed.                |                |
| arrival_time         | optional  | string (date-time)  | Date and time when the ride ended in `destination` in ... format. The time-zone of `destination` is assumed.        |                |
| signal               | optional  | signal              | Information about the method used to get the ride                                                                   |                |
| gift                 | optional  | list[gift]          | Possible gift that the hitchhiker received from the passengers.                                                     |                |
| hitchhikers          | required  | list[person]        | Most often a description of a solo-hitchhiker but also caters for couples or groups of hitchhikers. To convey not more than the number of hitchhikers use empty `person` objects.                |                |
| passengers           | optional  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| vehicle              | optional  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| ride                 | optional  | ride                | Information about the ride of the car beyond the hitchhiker's ride.                                                 |                |
| declined_rides       | optional  | list[decline_ride]  | Information about rides that were offered to the hitchhiker but that were declined by the them.                     |                |
