```json
{"gift": {
    "kind": {
            "type": "string",
            "description": "Country where the person lives primarily.",
            "enum": ["money", "food", "goods"]
        },
    "description": {
            "type": "string",
            "description": "Further description of the give received."
        },
    "value": {
        "type": "float",
        "description": "Positive decimal number. What is the estimated/ exact value of the gift received?"
        },
    "currency": {
        "type": "string",
        "description": "Currency code."
        }
    }
}
```