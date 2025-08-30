# Nostr Keys

| Nostr Key           | Value Type             | Required? | Purpose & Notes                                           
|---------------|------------------------|-----------|------------------------------------------------------------|
| `kind`           | Int    | Yes  | `36820` |       
| `created_at`           | .    | Yes   | Has to be equivalent to the time in `submission_time` tag. |              
| `content`           | String   | Yes   | A json objects using the tags from `STANDARD.md`. At least the `required` tags have to be present and not-null. For tags where no information is given for a ride simply leave the tag out (do not use null values). |
| `pubkey`           | .    | Yes   | . |              
| `id`           | .    | Yes   | . |              
| `sec`           | .    | Yes   | . |              



# Tag Structure
Use the following Nostr-specific tags that make interacting with the Nostr events easier.

| Tag           | Value Type             | Required? | Purpose & Notes                                            | NIP-99 Standard? |
|---------------|------------------------|-----------|------------------------------------------------------------|-----------------|
| `d`           | String (UUID rec.)     | Yes   | Unique identifier for the specific ride listing/request. Prevents duplicates, enables updates/deletion. | Yes             |
| `g`           | String (Geohash Prefix)| Yes       | **Origin** geohash (up to length 6) for area filtering. Has to be equivalent to the loaction of the first `stop` object in the `stops` field in `content` (the starting location). | Yes             |

# Example Nostr event

```json
{
  "kind": ...,
  "created_at": 1715000000, // Timestamp of THIS event object
  "content": "comment",
  "tags": [
    ["d", "hitchmap-12345"], // Unique ID
    ["g", "g"], ["g", "gc"], ["g", "gcp"], ["g", "gcpv"], ["g", "gcpvj"], ["g", "gcpvj0"], // Origin geohash
    ["title", "..."],
    ["published_at", "..."], // Timestamp of first publication
  ],
  "pubkey": "...",
  "id": "...", // ID of this specific event
  "sig": "..."
}
```
