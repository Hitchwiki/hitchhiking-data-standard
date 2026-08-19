- [x] Approved



| Tag                | Importance   | Type    | Description                                                                 | Enum                                         | Example |
|--------------------|--------------|---------|-----------------------------------------------------------------------------|----------------------------------------------|---------|
| origin_location       | optional  | string  | The city where the person lives in or any other administrative unit smaller than country-level. |                                              |  Milano       | 
| origin_country     | optional  | string  | Country where the person lives primarily. ISO 3166-1 alpha-2 2-digit country codes                                 |      | IT         |
| year_of_birth      | optional  | int   | Year of birth of the person.                                      |                                              |2000         |
| gender             | optional  | string   | Gender of the person                                                        | male, female, non_binary, prefer_not_to_say  | prefer_not_to_say         |
| languages               | optional  | list[string (ISO 639-3)]   | The languages that the person speaks so well that they are used to communicate on a hitchhiking ride.                                                                    |  |[deu, fra]         |
| was_driver                   | optional  | boolean  | Whether the person drove the car at some point. Often this will be true for one or more of a vehicle's occupants but it can also happen that a hitchhiker drivers the car at some point.                                            |      | false        |
| image_link         | optional  | string (URI)  | Link to a profile picture of the person (e.g. a Gravatar URL, or a photo used on `source`). Lets a reader infer visual features (e.g. presenting gender, approximate age) without the person having to state them explicitly as separate fields. |      | https://gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50        |
| items              | optional  | list[item] | Animals or belongings travelling with this person that may affect a pickup, such as a dog, guitar, or bicycle. Attach an item to one person only. | | [{"name": "dog"}, {"name": "guitar"}] |
