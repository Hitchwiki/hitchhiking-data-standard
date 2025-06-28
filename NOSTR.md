| Nostr Key           | Value Type             | Required? | Purpose & Notes                                           
|---------------|------------------------|-----------|------------------------------------------------------------|
| `kind`           | Int    | Yes  | . |       
| `created_at`           | .    | Yes   | . |              
| `content`           | String   | Yes   | Has to be equal to `comment` tag value. |
| `pubkey`           | .    | Yes   | . |              
| `id`           | .    | Yes   | . |              
| `sec`           | .    | Yes   | . |              



**Tag Structure:**

| Tag           | Value Type             | Required? | Purpose & Notes                                            | NIP-99 Standard? |
|---------------|------------------------|-----------|------------------------------------------------------------|-----------------|
| `d`           | String (UUID rec.)     | Yes   | Unique identifier for the specific ride listing/request. Prevents duplicates, enables updates/deletion. | Yes             |
| `g`           | String (Geohash Prefix)| Yes       | Cascading **origin** geohash (rec. up to len 6) for area filtering. | Yes             |



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
