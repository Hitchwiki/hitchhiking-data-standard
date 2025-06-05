- [ ] Approved


can have different forms depending on how the ride was caught





| Tag                  | Importance   | Type    | Description                                                                                                   | Enum                | Examples |
|----------------------|--------------|---------|---------------------------------------------------------------------------------------------------------------|---------------------|---------|
| methods               | required  | list[string]   | The methods used to signal that one is looking for a hitchhiking ride. Multiple methods can be used simultaneously.                                                                        | thumb, waving, sign, asking |[thumb, sign]         |
| sign_content               | optional  | string   | Only if `sign` is included in `methods`. What was written on the sign?                                                                         |  |Straßburg - Strasbourg          |
| sign_languages               | optional  | list[string (ISO 639-3)]   | Only if `sign` is included in `methods`. The languages used on the sign? Using ISO 639-3 (Three-letter codes for all known languages). If the `sign_content` was written so it is suitable for the local language, only listing the local language here is sufficient.                                                                         |  |[deu, fra]         |
| asking_content               | optional  | string   | Only if `asking` is included in `methods`. How/ What for was asked?                                                                        |  | Are you driving towards Strasbourg?          |
| asking_languages               | optional  | list[string (ISO 639-3)]   | Only if `asking` is included in `methods`. The languages used while asking? Using ISO 639-3 (Three-letter codes for all known languages).                                                                       |  |[eng]         |
| vehicles_per_minute  | optional  | float     | Positive floating point number. How many vehicles were approached passively per minute? For classical thumbing this would be the frequency of cars passing by.                                       |                     |5.0 [5 vehicles per minute] / 0.01 [one vehicle every 100 minutes]        |
| total_solicited      | optional  | int     | Only if `asking` is included in `methods`. Positive integer. How many vehicles were actively asked for a ride before getting a ride or stopping the search.       |                     |10         |



| Tag                     | Importance   | Type    | Description                                                                                                                      | Enum | Example |
|-------------------------|--------------|---------|----------------------------------------------------------------------------------------------------------------------------------|------|---------|
| invitation_circumstances| required  | string  | Implies that the hitchhiker was invited for the ride. Give more detailed information about the circumstances of the invitation.   |      |         |



| Tag                        | Importance   | Type    | Description                                                                                                                        | Enum | Example |
|----------------------------|--------------|---------|------------------------------------------------------------------------------------------------------------------------------------|------|---------|
| pre_arranging_circumstances| required  | string  | Implies that the ride was arranged in advance but still spontaneously e.g. through someone that the hitchhiker just got to know on their trip. |      |         |
