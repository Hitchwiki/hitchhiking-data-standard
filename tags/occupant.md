- [x] Approved


inherits from [`person`](https://github.com/Hitchwiki/hitchhiking_data_standard/blob/main/tags/person.md)

| Tag                         | Importance   | Type     | Description                                                                                   | Enum | Example |
|-----------------------------|--------------|----------|-----------------------------------------------------------------------------------------------|------|---------|
| reason_to_pick_up | optional  | string   | The reason the hitchhiker(s) are picked up, identified by asking the occupant that picked them up specifically. Use this tag if this occupant had the power to decided for picking up the hitchhiker. If the occupant did not want to pick up the hitchhiker but was overruled by another occupant set this to `opposed`. If the occupant had no say in whether or not to pick up the hitchhiker to not use this tag.| `is_hitchhiker`, `was_hitchhiker`, `social_exchange`, `cultural_exchange`, `environmental`, `wanted_driver`, `curiosity`, `hospitality_norm` (Cultural or personal values around helping strangers.). `elevated_mood` (The driver was in an unusually good mood or feeling generous.), `nonthreatening_appearance`, `sympathy` (The driver felt pity or concern for the hitchhiker e.g., due to weather or appearance), `safety_concern` (The driver believed the hitchhiker might be in danger e.g., harsh weather, isolated location.), `opposed`    | [was_hitchhiker, environmental, sympathy]        |
