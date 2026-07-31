# From https://github.com/Hitchwiki/hitchhiking-data-standard/blob/main/nostr/publish_past_rides.py
#
# Copyright (C) 2025-2026 Till Wenke
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Incremental import of hitchmap.com rides into the Nostr relay.

Unlike 2026_05_25_publish_hitchmap_with_nicknames.py this script takes the nicknames
directly from https://hitchmap.com/dump.sqlite instead of a side-loaded CSV:
a point either carries a free-text `points.nickname` (anonymous submission) or a
`points.user_id` pointing at an account whose nickname is `user.username`. Usernames of
all accounts are published, not just the ones that set `make_public`.

Only rides submitted *after* the most recent hitchmap.com ride already in the relay
are published, so the script can be re-run to catch up without creating duplicates.

Ran via: sudo .venv/bin/python3 2026_07_29_publish_hitchmap_with_nicknames.py to write readonly db.
Can only do this when on the same server as the relay for very large imports.
Pass --dry-run to see what would be published without touching the relay database.
"""

import sys
import os
import argparse

import sqlite3
import pandas as pd
from tqdm import tqdm

sys.path.append("../python")

from utils.post_hitchhiking_ride_to_nostr import HitchhikingDataStandardToNostrPoster
from hitchhiking_data_standard_pydantic_model import (
    Hitchhiker,
    HitchhikingRecord,
    Location,
    Signal,
    Stop,
)

DUMP_URL = "https://hitchmap.com/dump.sqlite"
DUMP_FILE = "dump.sqlite"
RELAY_DB = "/var/www/relay.maps.hitchwiki.org/data/nostr.db"
SOURCE = "hitchmap.com"
LICENSE = "odbl"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="build the records and print a summary, but do not write to the relay database",
)
parser.add_argument(
    "--since",
    default=None,
    help="override the cutoff (e.g. 2026-05-25T04:35:42) instead of reading it from the relay",
)
parser.add_argument("--relay-db", default=RELAY_DB, help=f"relay SQLite file (default: {RELAY_DB})")
parser.add_argument("--batch-size", type=int, default=50)
args = parser.parse_args()


### Find out how far the relay already is, so that we only publish what is missing

def latest_hitchmap_submission_time(relay_db: str) -> pd.Timestamp | None:
    """Submission time of the most recent hitchmap.com ride that the relay already holds."""
    conn = sqlite3.connect(f"file:{relay_db}?mode=ro", uri=True)
    try:
        (latest,) = conn.execute(
            """SELECT max(json_extract(json_extract(content, '$.content'), '$.submission_time'))
               FROM event
               WHERE kind = 36820
                 AND json_extract(json_extract(content, '$.content'), '$.source') = ?""",
            (SOURCE,),
        ).fetchone()
    finally:
        conn.close()

    return pd.to_datetime(latest) if latest else None


if args.since:
    cutoff = pd.to_datetime(args.since)
    print(f"Using cutoff given on the command line: {cutoff}")
else:
    cutoff = latest_hitchmap_submission_time(args.relay_db)
    if cutoff is None:
        sys.exit(
            f"No {SOURCE} rides found in {args.relay_db} - "
            "refusing to guess a cutoff, pass --since explicitly to publish anyway."
        )
    print(f"Latest {SOURCE} ride in the relay was submitted at {cutoff}")


### Load the current hitchmap dump

import wget  # noqa: E402  (imported late so that --help stays fast)

if os.path.exists(DUMP_FILE):
    os.remove(DUMP_FILE)
filename = wget.download(DUMP_URL, DUMP_FILE)
print()

conn = sqlite3.connect(DUMP_FILE)
points = pd.read_sql("select * from points where not banned", conn)
points["datetime"] = pd.to_datetime(points["datetime"], errors="coerce")

# Every account contributes its username as the nickname of the rides it submitted.
users = pd.read_sql("select id, username from user", conn)
user_id_to_username = dict(zip(users["id"], users["username"]))
conn.close()


### Clean your dataset from issues that your are already aware of
### This prevents that others have to do it when fetching these rides

points.loc[points["datetime"] < "2000-01-01", "datetime"] = None

points["ride_datetime"] = points["ride_datetime"].replace("0224-10-31T21:30", None)
points["ride_datetime"] = points["ride_datetime"].replace("0025-03-07T08:00", None)
points["ride_datetime"] = points["ride_datetime"].replace("1014-11-04T14:30", None)
points["ride_datetime"] = points["ride_datetime"].replace("0202-04-03T18:50", None)

points["ride_datetime"] = pd.to_datetime(points["ride_datetime"], errors="coerce")


### Keep only the rides that were submitted after the relay's newest hitchmap ride
### Rides without a submission time cannot be placed relative to the cutoff, so they are skipped

# `submission_time` is published truncated to whole seconds, so the cutoff read back from the
# relay has no sub-second part. Compare at the same precision, otherwise the ride sitting exactly
# on the cutoff second is republished on every run (its fractional datetime is always > cutoff).
hitchmap = points[
    points["datetime"].notna() & (points["datetime"].dt.floor("s") > cutoff)
].copy()

print(f"{len(hitchmap)} rides submitted after {cutoff} (out of {len(points)} in the dump)")


### Resolve the nickname of a ride: the username of the (public) account that submitted it,
### otherwise the free-text nickname stored on the point itself, otherwise anonymous


def resolve_nickname(row: pd.Series) -> str:
    if pd.notna(row["user_id"]):
        username = user_id_to_username.get(row["user_id"])
        if username and str(username).strip():
            return str(username).strip()
        # Should not happen: every account in the dump has a username
        return "Anonymous"

    nickname = row["nickname"]
    if pd.notna(nickname) and str(nickname).strip():
        return str(nickname).strip()

    return "Anonymous"


hitchmap["nickname"] = hitchmap.apply(resolve_nickname, axis=1)

print(
    f"Nicknames: {(hitchmap['nickname'] != 'Anonymous').sum()} named, "
    f"{(hitchmap['nickname'] == 'Anonymous').sum()} anonymous"
)


### Define functions that create the objects demanded by this standard from the possibly unique data that is used in your dataset


def map_signal(signal: str) -> Signal:
    if not signal:
        return None

    if signal == "sign":
        return Signal(
            methods=["sign"],
        )
    elif signal == "thumb":
        return Signal(
            methods=["thumb"],
        )
    elif signal == "ask":
        return Signal(
            methods=["asking"],
        )
    elif signal == "ask-sign":
        return Signal(
            methods=["asking", "sign"],
        )
    else:
        return None


### Define one function that takes single rides from your dataset and builds objects that follow this standard from them


def create_record_from_row(
    row: pd.Series, source: str, license: str, rating_formula=lambda x: x
) -> HitchhikingRecord:
    stops = [
        Stop(
            location=Location(latitude=row["lat"], longitude=row["lon"], is_exact=True),
            arrival_time=None,
            departure_time=(row["ride_datetime"]).strftime("%Y-%m-%dT%H:%M:%S")
            if pd.notna(row["ride_datetime"])
            else None,
            waiting_duration=f"PT{int(row['wait'])}M" if pd.notna(row["wait"]) else None,
        ),
    ]
    if pd.notna(row["dest_lat"]) and pd.notna(row["dest_lon"]):
        stops.append(
            Stop(
                location=Location(
                    latitude=row["dest_lat"], longitude=row["dest_lon"], is_exact=False
                )
            )
        )

    signal = map_signal(row["signal"])
    if signal is not None and pd.notna(row["wait"]):
        signal = Signal(methods=signal.methods, duration=f"PT{int(row['wait'])}M")
    signals = [signal] if signal is not None else None

    record = HitchhikingRecord(
        version="0.0.0",
        stops=stops,
        rating=rating_formula(int(row["rating"])) if pd.notna(row["rating"]) else None,
        hitchhikers=[Hitchhiker(nickname=row["nickname"])],
        comment=row["comment"] if pd.notna(row["comment"]) else None,
        signals=signals,
        occupants=None,
        mode_of_transportation=None,
        ride=None,
        declined_rides=None,
        source=source,
        license=license,
        submission_time=row["datetime"].strftime("%Y-%m-%dT%H:%M:%S")
        if pd.notna(row["datetime"])
        else None,
    )

    return record


### Collect the records that are now in the desired format

hitchhiking_records = []

for _, row in tqdm(hitchmap.iterrows(), total=len(hitchmap)):
    hitchhiking_records.append(
        create_record_from_row(
            row,
            source=SOURCE,
            license=LICENSE,
        )
    )

### Post your records to the Nostr protocol to publish them

print(f"Total records to publish: {len(hitchhiking_records)}")

if not hitchhiking_records:
    sys.exit("Nothing to publish - the relay is up to date.")

if args.dry_run:
    print("Dry run - not writing to the relay database. First record:")
    print(hitchhiking_records[0].model_dump_json(exclude_none=True, by_alias=True, indent=2))
    sys.exit(0)

poster = HitchhikingDataStandardToNostrPoster()

# Use batch processing for much faster publishing
# Adjust batch_size based on your relay capacity (100-500 works well)
poster.post_batch_to_db(
    ride_records=hitchhiking_records,
    db_path=args.relay_db,
    batch_size=args.batch_size,
)

poster.close()
