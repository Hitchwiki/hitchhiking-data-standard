```json
{
    "destination": {
            "type": "location",
            "description": "Possible destination of this ride."
        },
    "reason": {
            "type": "string",
            "description": "The reason that the ride was declined.",
            "enum": ["wrong_direction", "too_short", "too_long", "safety_concerns"]
        },
}
```