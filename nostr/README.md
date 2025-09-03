

To mitigate data duplication and data being injected into "our" ecosystem from outside actors we collect people (identified by their npub) and the organization/ application (`source`) which they publish hitchhiking rides for here. Thus in case the data gets compromised filtering by the following should yield data from trustworthy sources again.

| npub         | sources            | Who is responsible?|                                    
|---------------|------------------------|---|
| `d17ff51bfc32d49217e8cb5bfa558a5a78e6cbe3ea4d947acbc7f11ca5c5dbd5` | liftershalte.info, hitchmap.com, hitchwiki.org | @tillwenke |

# Examples

`publish_past_rides.py` ... shows an example of how to take a present dataset of hitchhiking rides, transform it into the defined standard and to post it to Nostr so that others can access it. You might have to adapt a few things for your own dataset. You might have to adapt a few more things to do this in another language than python.

`publish_ride.py` ... shows an example of how to take a ride that was just recorded e.g. on a hitchhiking application with opinionated fields that were collected by the application, transform it into the defined standard and to post it to Nostr so that others can access it.

To get started with those script you need to set up the python evironment as follows:

```shell
cp example.env .env
# set env vars in .env
# using python 3.12
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You and other people have published their hitchhiking rides using the Nostr protocol, thus you can access this common collection of rides.

`fetch_hitchhiking_events/` ... shows how this can be done.

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

| Tag           | Value Type             | Required? | Purpose & Notes                                            |
|---------------|------------------------|-----------|------------------------------------------------------------|
| `d`           | String (UUID recommended)     | Yes   | Unique identifier for the specific ride. Prevents duplicates, enables updates/deletion. By posting a new event with the same d tag its content can be changed - the older version of the event may be discarded by relays. Each application posting hitchhiking events can come up with their own schema, it is recommended to use "`source`-`version 4 UUID`". |
| `g`           | String (Geohash Prefix)| Yes       | Cascading **origin** geohash (at least of length 10) for area filtering. This means there will be multiple g tags, one for each precision level that the geohash provides. Has to be equivalent to the loaction of the first `stop` object in the `stops` field in `content` (the starting location). |
| `published_at`           | String (UNIX timestamp) | Yes       | The timestamp (in unix seconds – converted to string) of the first version of this ride that was published as a Nostr event. If a `source` application directly posts events to Nostr this is equivalent to the time in `submission_time` field in `content`. If the ride was recorded well before it was published as a Nostr event, then `submission_time` must be earlier than `published_at`. |
| `expiration`           | int| No       | If you are still testing and playing around with Nostr events set this to `0`. Otherwise this tag is not needed. |


# Example Nostr event

See [nostr.json](nostr.json).
