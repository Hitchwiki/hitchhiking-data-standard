
```json
{
"start": {
            "type": "location",
            "description": "Starting point of the hitchhiking ride."
        },
"destination": {
            "type": "location",
            "description": "Destination of the hitchhiking ride."
        },
"star_rating": {
            "type": "int",
            "description": "Very subjective rating of the spot where the ride started.",
            "enum" [1, 2, 3, 4, 5]
        },
"waiting_time_minutes": {
            "type": "int",
            "description": "Positive integer indicating the timespan from when rides were first solicited until the hitchhiker got their ride."
        },
"comment": {
            "type": "string",
            "description": "Any free-form comment about the starting location, destination or the entire ride."
        },
"start_time": {
            "type": "string",
            "format": "date-time",
            "description": "Date and time when the ride started from `start` in ... format. The time-zone of `start` is assumed."
        },
"arrival_time": {
            "type": "string",
            "format": "date-time",
            "description": "Date and time when the ride ended in `destination` in ... format. The time-zone of `destination` is assumed."
        },
"signal": {
            "type": "signal",
            "description": "Information about the method used to get the ride"
        },

"gift": {
            "type": "list[gift]",
            "description": "Possible gift that the hitchhiker received from the passengers."
        },
"hitchhikers": {
            "type": "list[person]",
            "description": "Most often a description of a solo-hitchhiker but also caters for couples or groups of hitchhikers."
        },
"passengers": {
            "type": "list[passenger]",
            "description": "List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver."
        },
"vehicle": {
            "type": "list[passenger]",
            "description": "List of passengers in the vehicle not including the hitchhiker, putting specific emphasize on the driver."
        },
"ride": {
            "type": "ride",
            "description": "Information about the ride of the car beyond the hitchhiker's ride."
        },
"declined_rides": {
            "type": "list[decline_ride]",
            "description": "Information about rides that were offered to the hitchhiker but that were declined by the hitchhiker."
        }
}

```
