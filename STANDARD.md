- [ ] Approved


| Tag                  | Importance   | Type                | Description                                                                                                         | Enum           | Example |
|----------------------|--------------|---------------------|---------------------------------------------------------------------------------------------------------------------|----------------|---------|
| stops                | required  | list[stop]            | Starting location of the hitchhiking ride.                                                                             |                |
| star_rating          | recommended  | int                 | Very subjective rating of the spot where the ride started.                                                          | 1, 2, 3, 4, 5  |           |
| comment              | optional  | string              | Any free-form comment about the starting location, destination or the entire ride. Preferrably in English language.                                 |                |
| signals               | optional  | list[signal]            | Information about the methods used to get the ride. List them in the order that they were used.                                                                  |                |
| gifts                 | optional  | list[gift]          | Possible gift that the hitchhiker received from the passengers.                                                     |                |
| hitchhikers          | required  | list[hitchhiker]        | Most often a description of a solo-hitchhiker but also caters for couples or groups of hitchhikers. To convey not more than the number of hitchhikers use empty `person` objects.                |                |
| passengers           | optional  | list[passenger]     | List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver.           |                |
| mode_of_transportation              | optional  | mode_of_transportation    | Information about the vehicle that was used for the ride. In rarer cases this could be a plane or boat as well.           |                |
| ride                 | optional  | ride                | Information about the ride of the car beyond the hitchhiker's ride.                                                 |                |
| declined_rides       | optional  | list[decline_ride]  | Information about rides that were offered to the hitchhiker but that were declined by the them.                     |                |
| source       | required  | string  | Source of this record by URL of the application. Or "private" if the records stem from an independently and individually collected source.               |                |https://hitchwiki.org
| reasons       | optional  | list[string]  | Reason for the hitchhiking ride.        | commute, holiday, sport, financial, social_exchange, cultural_exchange, recreational, environmental             |[holiday, financial, cultural_exchange]
