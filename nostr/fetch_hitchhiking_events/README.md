From [hitchhiking-data-standard](https://github.com/Hitchwiki/hitchhiking-data-standard/tree/main/nostr/fetch_hitchhiking_events).

# fetch_hitchhiking_events

Node.js / TypeScript script that fetches hitchhiking-ride events from Nostr
relays and writes them to `rides.json` and `rides.csv` in this directory. Both
output files are gitignored; see [`example_rides.json`](./example_rides.json)
for a sample of the `rides.json` format.

Doing the relay round-trip in TypeScript is simpler than in Python, which is why
this is a separate Node script.

For an example of a single raw Nostr ride event, see the
[Example Nostr event](../README.md#example-nostr-event) section in the `nostr/`
README ([`nostr.json`](../nostr.json)). To learn how the underlying data
standard is structured and why it exists, see the
[README](../../README.md).

## Setup

Requires **Node.js ≥ 18**.

```bash
cd nostr/fetch_hitchhiking_events
npm install
cp example.env .env   # then edit .env
```

## Configuration

The script is configured entirely through environment variables. See
[`example.env`](./example.env) for the full list. The `.env` file next to this
script is loaded automatically (via `dotenv`). `dotenv` never overrides an
already-set variable, so you can also pass variables inline on the command line.

| Variable          | Required | Description |
|-------------------|----------|-------------|
| `RELAYS`          | yes      | JSON array of relay websocket URLs, e.g. `["wss://relay.maps.hitchwiki.org"]` |
| `NOSTR_EVENT_KIND`| yes      | Nostr event kind for rides (`36820`) |
| `SINCE`           | no       | Only fetch rides created at/after this time. ISO date (`2026-01-01`), ISO datetime (`2026-01-01T00:00:00Z`), or a Unix timestamp in seconds. Defaults to the full history. |
| `PUBKEYS`         | no       | JSON array of author public keys (hex). Only rides signed by these keys are fetched. Defaults to all authors. |
| `SOURCE`          | no       | Only keep rides whose `source` is this value. Defaults to all sources. |

## Running

Build the TypeScript and run the compiled output:

```bash
npx tsc
node dist/index.js
```

The `.env` file is picked up automatically.

## Example: fetch only the latest rides from maps.hitchwiki.org

To fetch **only rides created after a given date** and **only those published by
a specific app** (e.g. `maps.hitchwiki.org`), set `SINCE` and `SOURCE`.

Either put them in `.env`:

```env
RELAYS=["wss://relay.maps.hitchwiki.org"]
NOSTR_EVENT_KIND=36820
SINCE=2026-01-01
SOURCE=maps.hitchwiki.org
```

```bash
node dist/index.js
```

…or pass them inline for a one-off run (inline variables override the `.env`):

```bash
RELAYS='["wss://relay.maps.hitchwiki.org"]' NOSTR_EVENT_KIND=36820 \
  SINCE=2026-01-01 SOURCE=maps.hitchwiki.org \
  node dist/index.js
```

How the filters work — server-side filters are applied by the relays first, so
only trusted, recent events ever reach us; the client-side `SOURCE` filter then
narrows what remains:

- **`PUBKEYS`** *(server-side)* is sent to the relays as the Nostr `authors`
  filter, so the relays only return events signed by these public keys. Use it
  as an allow-list of trusted submitters — events from anyone else are dropped
  before they reach the script. The hex public keys of known trusted submitters
  (and the sources they publish for) are listed in the
  [`nostr/` README](../README.md).
- **`SINCE`** *(server-side)* is sent to the relays as the Nostr `since` filter,
  so the relays only return events from that point onward.
- **`SOURCE`** *(client-side)* is applied after fetching, because relays cannot
  filter on event content. A ride's origin app is stored in the JSON `content`
  field under `source`; the `d` tag (prefixed `<source>-...`) is used as a
  fallback when content is missing.

Expected log output looks roughly like:

```
Using relays: [ 'wss://relay.maps.hitchwiki.org' ]
Fetching Nostr event kind (this can take a while): 36820
Fetching rides created since: 2026-01-01T00:00:00.000Z
Keeping only rides from source: maps.hitchwiki.org
...
123 unique posts fetched across 1 relays
87 posts remain after filtering by source "maps.hitchwiki.org"
JSON written to .../rides.json
CSV written to .../rides.csv
```
