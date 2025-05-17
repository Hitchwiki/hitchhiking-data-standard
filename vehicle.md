```json
{
    "class": {
            "type": "float",
            "description": "Latitude of a spot in decimal degrees",
            "enum": [
                "car",
                "bus",
                "van",
                "truck",
                "motorbike",
                "scooter",
                "taxi",
                "horse-cart",
                "train",
                "camper",
                "tractor",
                "plane",
                "ferry",
                "boat"
            ],
        },
    "model": {
            "type": "string",
            "description": "More specific model of the vehicle."
        },
    "license_plate_country": {
            "type": "string",
            "description": "Country from the license plate of the car.",
            "enum": "ISO 3166-1 alpha-2 2-digit country codes"
        }
}
```