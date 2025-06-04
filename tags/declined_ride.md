- [ ] Approved

| Tag         | Importance   | Type      | Description                                   | Enum                                               | Example |
|-------------|--------------|-----------|-----------------------------------------------|----------------------------------------------------|---------|
| destination | recommended  | location  | Possible destination of this ride.            |                                                    |         |
| reasons      | recommended  | list[string]    | The reasons that the offered ride was not accepted by the hitchhiker.         | `wrong_direction` (the ride would not follow the intended route and changing the route is not an option), `too_short` (the ride follows the intended route but the hitchhiker prefers to get a further ride), `too_long` (the ride follows the intended route but being dropped of at a certain desired place is not an option), `risk_concern` (the hitchhiker is concerned that the driver(s) could harm them unintentionally e.g. by drunk driving or speeding), `safety_concern` (the hitchhiker is concerned that the driver(s) could harm them intentionally |         |
