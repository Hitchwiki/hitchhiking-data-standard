- [ ] Approved


| Tag                   | Importance   | Type    | Description                                      | Enum                                                                                                         | Examples |
|-----------------------|--------------|---------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------|---------|
| kind                 | required  | string   | The kind of mode of transportation used. Most often a sort of vehicle but can also be something more exotic.            | car, bus, van, truck, motorbike, scooter, taxi, horse-cart, train, camper, tractor, plane, ferry, boat       |car / camper / boat         |
| make                 | optional  | string  | The brand or manufacturer of the transportation object.             |                                                                                                              |Toyota / Knaus / Boston Whaler         |
| model                 | optional  | string  | More specific model of the transportation object.              |                                                                                                              |Corolla / BOXLIFE PRO 600 / Montauk 170         |
| license_plate_country | optional  | string (ISO 3166-1 alpha-2)  | Country from the license plate of the car.       | ISO 3166-1 alpha-2 2-digit country codes                                                                     |DE / FR / US        |
| license_plate_identifier | optional  | string  | A location-based identifiers on the license plate that is present in some countries e.g. Germany (city/district), France (department), USA (state)       |                                                                    |B / 93 / Georgia        |
