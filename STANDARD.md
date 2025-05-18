| Tag                  | Importance   | Type                | Description                                                                                                         | Enum           | Example |
|----------------------|--------------|---------------------|---------------------------------------------------------------------------------------------------------------------|----------------|---------|
| start                | recommended  | location            | Starting point of the hitchhiking ride.                                                                             |                |
| destination          | recommended  | location            | Destination of the hitchhiking ride.                                                                                |                |
| star_rating          | recommended  | int                 | Very subjective rating of the spot where the ride started.                                                          | 1, 2, 3, 4, 5  |
| waiting_time_minutes | recommended  | int                 | Positive integer indicating the timespan from when rides were first solicited until the hitchhiker got their ride.  |                |
| comment              | recommended  | string              | Any free-form comment about the starting location, destination or the entire ride.                                  |                |
| start_time           | recommended  | string (date-time)  | Date and time when the ride started from `start` in ... format. The time-zone of `start` is assumed.                |                |
| arrival_time         | recommended  | string (date-time)  | Date and time when the ride ended in `destination` in ... format. The time-zone of `destination` is assumed.        |                |
| signal               | recommended  | signal              | Information about the method used to get the ride                                                                   |                |
| gift                 | recommended  | list[gift]          | Possible gift that the hitchhiker received from the passengers.                                                     |                |
| hitchhikers          | recommended  | list[person]        | Most often a description of a solo-hitchhiker but also caters for couples or groups of hitchhikers.                 |                |
| passengers           | recommended  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| vehicle              | recommended  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| ride                 | recommended  | ride                | Information about the ride of the car beyond the hitchhiker's ride.                                                 |                |
| declined_rides       | recommended  | list[decline_ride]  | Information about rides that were offered to the hitchhiker but that were declined by the them.                     |                |
