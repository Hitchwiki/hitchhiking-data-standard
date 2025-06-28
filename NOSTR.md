| Nostr Key           | Value Type             | Required? | Purpose & Notes                                           
|---------------|------------------------|-----------|------------------------------------------------------------|
| `kind`           | Int    | Yes  | . |       
| `created_at`           | .    | Yes   | Has to be equivalent to the time in `submission_time` tag. |              
| `content`           | String   | Yes   | Has to be equal to `comment` tag value. |
| `pubkey`           | .    | Yes   | . |              
| `id`           | .    | Yes   | . |              
| `sec`           | .    | Yes   | . |              



**Tag Structure:**
Use all tags from `STANDARD.md` and the following Nostr-specific tags that make interacting with the Nostr events easier.

| Tag           | Value Type             | Required? | Purpose & Notes                                            | NIP-99 Standard? |
|---------------|------------------------|-----------|------------------------------------------------------------|-----------------|
| `d`           | String (UUID rec.)     | Yes   | Unique identifier for the specific ride listing/request. Prevents duplicates, enables updates/deletion. | Yes             |
| `g`           | String (Geohash Prefix)| Yes       | Cascading **origin** geohash (rec. up to len 6) for area filtering. Has to be equivalent to the loaction of the first `stop` object in the `stops` tag (the starting location). | Yes             |



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
