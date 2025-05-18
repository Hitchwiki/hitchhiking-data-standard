- [ ] Approved


can have different forms depending on how the ride was caught





| Tag                  | Importance   | Type    | Description                                                                                                   | Enum                | Example |
|----------------------|--------------|---------|---------------------------------------------------------------------------------------------------------------|---------------------|---------|
| signal               | required  | float   | The method used to signal that one is looking for a hitchhiking ride.                                                                         | thumb, waving |         |
| vehicles_per_minute  | recommended  | int     | Positive integer. How many vehicles passed by approximately per minute?                                       |                     |         |

| Tag                  | Importance   | Type    | Description                                                                                                   | Enum                | Example |
|----------------------|--------------|---------|---------------------------------------------------------------------------------------------------------------|---------------------|---------|
| asking               | recommended  | string  | How/ What for was asked?                                                                                      |                     |         |
| total_solicited      | recommended  | int     | Positive integer. How many vehicles were asked for a ride before getting a ride or stopping the search.       |                     |         |



| Tag                     | Importance   | Type    | Description                                                                                                                      | Enum | Example |
|-------------------------|--------------|---------|----------------------------------------------------------------------------------------------------------------------------------|------|---------|
| invitation_circumstances| required  | string  | Implies that the hitchhiker was invited for the ride. Give more detailed information about the circumstances of the invitation.   |      |         |



| Tag                        | Importance   | Type    | Description                                                                                                                        | Enum | Example |
|----------------------------|--------------|---------|------------------------------------------------------------------------------------------------------------------------------------|------|---------|
| pre_arranging_circumstances| required  | string  | Implies that the ride was arranged in advance but still spontaneously e.g. through someone that the hitchhiker just got to know on their trip. |      |         |
