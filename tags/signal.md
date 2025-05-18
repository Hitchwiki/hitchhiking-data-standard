can have different forms depending on how the ride was caught


| Tag                  | Importance   | Type    | Description                                                                                                   | Enum                | Example |
|----------------------|--------------|---------|---------------------------------------------------------------------------------------------------------------|---------------------|---------|
| signal               | recommended  | float   | Latitude of a spot in decimal degrees                                                                         | ["thumb", "waving"] |         |
| vehicles_per_minute  | recommended  | int     | Positive integer. How many vehicles passed by approximately per minute?                                       |                     |         |
| asking               | recommended  | string  | How/ What for was asked?                                                                                      |                     |         |
| total_solicited      | recommended  | int     | Positive integer. How many vehicles were asked for a ride before getting a ride or stopping the search.       |                     |         |



| Tag                     | Importance   | Type    | Description                                                                                                                      | Enum | Example |
|-------------------------|--------------|---------|----------------------------------------------------------------------------------------------------------------------------------|------|---------|
| invitation_circumstances| recommended  | string  | Implies that the hitchhiker was invited for the ride. Give more detailed information about the circumstances of the invitation.   |      |         |



| Tag                        | Importance   | Type    | Description                                                                                                                        | Enum | Example |
|----------------------------|--------------|---------|------------------------------------------------------------------------------------------------------------------------------------|------|---------|
| pre_arranging_circumstances| recommended  | string  | Implies that the ride was arranged in advance but still spontaneously e.g. through someone that the hitchhiker just got to know on their trip. |      |         |
