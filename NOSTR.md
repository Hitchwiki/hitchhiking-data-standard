# Nostr Keys

| Nostr Key           | Value Type             | Required? | Purpose & Notes                                           
|---------------|------------------------|-----------|------------------------------------------------------------|
| `kind`           | Int    | Yes  | `36820` |       
| `created_at`           | .    | Yes   | Has to be equivalent to the time in `submission_time` field in `content`. |              
| `content`           | String   | Yes   | A json objects using the tags from `STANDARD.md`. At least the `required` tags have to be present and not-null. For tags where no information is given for a ride simply leave the tag out (do not use null values). |
| `pubkey`           | .    | Yes   | . |              
| `id`           | .    | Yes   | . |              
| `sec`           | .    | Yes   | . |              



# Tag Structure
Use the following Nostr-specific tags that make interacting with the Nostr events easier.

| Tag           | Value Type             | Required? | Purpose & Notes                                            | NIP-99 Standard? |
|---------------|------------------------|-----------|------------------------------------------------------------|-----------------|
| `d`           | String (UUID rec.)     | Yes   | Unique identifier for the specific ride listing/request. Prevents duplicates, enables updates/deletion. | Yes             |
| `g`           | String (Geohash Prefix)| Yes       | **Origin** geohash (up to length 9) for area filtering. Has to be equivalent to the loaction of the first `stop` object in the `stops` field in `content` (the starting location). | Yes             |

# Example Nostr event

```json
{
  "kind": 36820,
  "created_at": 1751231417, // Timestamp of THIS event object
  "content": "{
  "stops": [
    {
      "arrival_time": null,
      "departure_time": null,
      "location": {
        "is_exact": true,
        "latitude": 32.0727564373025,
        "longitude": 34.7934436798096
      },
      "waiting_duration": null
    }
  ],
  "rating": 4,
  "hitchhikers": [
    {
      "gender": null,
      "hitchhiking_since": null,
      "languages": null,
      "nickname": null,
      "origin_country": null,
      "origin_location": null,
      "reasons_to_hitchhike": null,
      "was_driver": null,
      "year_of_birth": null
    }
  ],
  "comment": null,
  "signals": null,
  "occupants": null,
  "mode_of_transportation": null,
  "ride": null,
  "declined_rides": null,
  "source": "liftershalte.info",
  "license": "cc-by-sa-4.0",
  "submission_time": null
}",
  "tags": [
    ["expiration", "0"],
    ["d", "liftershalte.info-7852e9df-ffd6-45dc-a164-b81f006254f0"], // Unique ID
    ["g", "sv8wrwxv6"], // Origin geohash
    ["title", "..."],
    ["published_at", "..."], // Timestamp of first publication
  ],
  "pubkey": "d17ff51bfc32d49217e8cb5bfa558a5a78e6cbe3ea4d947acbc7f11ca5c5dbd5",
  "id": "dae98bbe6d790463931c32f31178e691ffd1300c44e2f026c5f2933e85362da8", // ID of this specific event
  "sig": "3dfaf7a1377414634ada1e3a1277ce8ebf5ddf24e3e7985ae70ce019f43d2df7c03b7ae5225cca0a476b72a3fc2c8906c438df5afd818abdd5c1c9bc8b68dba4"
}
```
