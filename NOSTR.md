# Nostr Keys

| Nostr Key           | Value Type             | Required? | Purpose & Notes                                           
|---------------|------------------------|-----------|------------------------------------------------------------|
| `kind`           | Int    | Yes  | `36820` |       
| `created_at`           | Int   | Yes   | unix timestamp in seconds     
| `content`           | String   | Yes   | A json object as string using the tags from `STANDARD.md`. At least the `required` tags have to be present and not-null. For tags where no information is given for a ride simply leave the tag out (do not use null values). |
| `pubkey`           | String    | Yes   | 32-bytes lowercase hex-encoded public key of the event creator. See [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md). |              
| `id`           | String    | Yes   | 32-bytes lowercase hex-encoded sha256 of the serialized event data. See [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md). |              
| `sig`           | String    | Yes   | 64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the "id" field. See [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md). |              



# Tag Structure
Use the following Nostr-specific tags that make interacting with the Nostr events easier.

| Tag           | Value Type             | Required? | Purpose & Notes                                            | NIP-99 Standard? |
|---------------|------------------------|-----------|------------------------------------------------------------|-----------------|
| `d`           | String (UUID rec.)     | Yes   | Unique identifier for the specific ride. Prevents duplicates, enables updates/deletion. | Yes             |
| `g`           | String (Geohash Prefix)| Yes       | **Origin** geohash (up to length 9) for area filtering. Has to be equivalent to the loaction of the first `stop` object in the `stops` field in `content` (the starting location). | Yes    
| `published_at`           | String (UNIX timestamp) | Yes       | The timestamp (in unix seconds – converted to string) of the first version of this ride that was published as a Nostr event. If a `source` application directly posts events to Nostr this is equivalent to the time in `submission_time` field in `content`. | Yes           |
| `expiration`           | int| No       | If you are still testing and playing around with Nostr events set this to `0`. Otherwise this tag is not needed. | -             |


# Example Nostr event

See [nostr.json](nostr.json).
