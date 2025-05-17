can have different forms depending on how the ride was caught

{sign_to: string, vehicles_per_minute: int} |
```json
{
    "signal": {
            "type": "float",
            "description": "Latitude of a spot in decimal degrees",
            "enum": ["thumb", "waving"]
        },
    "vehicles_per_minute": {
            "type": "int",
            "description": "Positive integer. How many vehicles passed by approximatelly per minute?"
        }
}

{
    "asking": {
            "type": "string",
            "description": "How/ What for was asked?"
        },
    "total_solicited": {
            "type": "int",
            "description": "Positive integer. How many vehicles were asked for a ride before getting a ride or stopping the search."
        }
}

{"invitation_circumstances": {
            "type": "string",
            "description": "Implies that the hitchhiker was invited for the ride. Give more detailed information about the circumstances of the invitation."
        }
}

{"pre_arranging_circumstances": {
            "type": "string",
            "description": "Implies that the ride was arranged in advance but still spontaneously e.g. through someone that the hitchhiker just got to know on their trip."
        }
}
```