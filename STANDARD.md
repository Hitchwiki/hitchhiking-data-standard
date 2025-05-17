
```json
{
start: location,
destination: location,
star_rating: int [1,5]
waiting_time_minutes: +int
comment: string
date: date
start_time: time
arrival_time: time
signal:
{sign_to: string, vehicles_per_minute: int} |
{signal: "thumb" | "waving" | ..., vehicles_per_minute: int} |
{asking: string, total_solicited: int} |
{invited: bool, while_doing: string} |
{pre_arranged: bool, through: string}
gift: {money: {value: +float, currency: EUR, USD, ...}} | {food: string} | {goods: string}
hitchhikers: list[person] 
passengers: list[passenger] {age: age, origin: {city: string, country: GER, US, FR, ...}, driver: bool, reason_to_pick_up_or_reject: string}
vehicle: {type: {class: car| bus| van | truck | bus | motorbike | scooter | taxi | horse-cart | train | camper | tractor | plane | ferry | boat | ..., model: string}, license_plate_country: GER, US, FR, ...}
ride: {destination: location, purpose: string}
declined_rides: list[location]
source: url | string
}

```
