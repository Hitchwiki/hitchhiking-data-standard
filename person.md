```json
{"origin": {
    "city": {
            "type": "string",
            "description": "The city where the person lives in or any other administrative unit smaller than country-level."
        },
    "country": {
            "type": "string",
            "description": "Country where the person lives primarily.",
            "enum": "ISO 3166-1 alpha-2 2-digit country codes"
        }
},
"year_of_birth": {
        "type": "float",
        "description": "Latitude of a spot in decimal degrees"
    },
"gender": {
        "type": "float",
        "description": "Gender of the person",
        "enum": ["male", "female" "non_binary", "prefer_not_to_say"]
    }
}
```

nickname: string
{socials: {trustroots: url, hitchwiki: url, bewelcome: url, ...}}
