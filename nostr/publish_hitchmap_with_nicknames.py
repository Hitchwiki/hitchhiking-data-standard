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
Rides that hitchmap.com stores more than once, and rides the relay already holds, are
dropped as well - see "Drop duplicates" below.

The dump is verified before it is used and the relay database before and after it is
written to; see "Load the current hitchmap dump" and "Check the relay database over".
Exit codes: 0 published, 1 nothing to publish, 2 no usable dump, 3 relay database not
writable or batch did not land intact.

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
###
### The download is not always complete: on 2026-08-12 wget produced a 19 MB file holding nothing
### but the `points` table, and the run died on `select ... from user` after having already decided
### its cutoff. A truncated dump is therefore verified before it replaces the previous one, and a
### failed download is retried rather than taken at face value.

import wget  # noqa: E402  (imported late so that --help stays fast)

DUMP_MIN_BYTES = 40 * 1024 * 1024  # the real dump is ~60 MB and only grows
DUMP_MIN_POINTS = 60_000  # 79k as of 2026-08-12; a floor, not an expectation
DUMP_REQUIRED_TABLES = ("points", "user")
DUMP_REQUIRED_COLUMNS = (
    "id", "lat", "lon", "rating", "wait", "nickname", "comment", "datetime",
    "banned", "dest_lat", "dest_lon", "signal", "ride_datetime", "user_id",
)
DOWNLOAD_ATTEMPTS = 3

EXIT_NOTHING_TO_PUBLISH = 1  # kept distinct: this is the normal no-op outcome
EXIT_BROKEN_DUMP = 2
EXIT_BROKEN_WRITE = 3


def dump_defects(path: str) -> list[str]:
    """Everything wrong with the file at `path`, empty when it is a usable hitchmap dump."""
    if not os.path.exists(path):
        return ["file was not created"]

    size = os.path.getsize(path)
    if size < DUMP_MIN_BYTES:
        return [f"only {size / 1024 / 1024:.1f} MB, expected at least {DUMP_MIN_BYTES // 1024 // 1024} MB"]

    defects = []
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as error:
        return [f"cannot be opened as SQLite: {error}"]
    try:
        # quick_check skips the (much slower) index cross-checks that integrity_check does.
        (verdict,) = conn.execute("PRAGMA quick_check").fetchone()
        if verdict != "ok":
            return [f"failed SQLite quick_check: {verdict}"]

        tables = {name for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing = [t for t in DUMP_REQUIRED_TABLES if t not in tables]
        if missing:
            defects.append(f"missing table(s): {', '.join(missing)}")
        if "points" not in missing:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(points)")}
            absent = [c for c in DUMP_REQUIRED_COLUMNS if c not in columns]
            if absent:
                defects.append(f"points is missing column(s): {', '.join(absent)}")
            (count,) = conn.execute("SELECT count(*) FROM points").fetchone()
            if count < DUMP_MIN_POINTS:
                defects.append(f"only {count} points, expected at least {DUMP_MIN_POINTS}")
            (dated,) = conn.execute("SELECT count(*) FROM points WHERE datetime IS NOT NULL").fetchone()
            if not dated:
                defects.append("no point carries a submission time")
    except sqlite3.DatabaseError as error:
        defects.append(f"is not readable: {error}")
    finally:
        conn.close()
    return defects


def dump_point_count(path: str) -> int | None:
    """Points in an existing dump, for the shrink check. None when it cannot be read."""
    if not os.path.exists(path):
        return None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            (count,) = conn.execute("SELECT count(*) FROM points").fetchone()
            return count
        finally:
            conn.close()
    except sqlite3.Error:
        return None


def download_dump() -> None:
    """Fetch the dump into DUMP_FILE, leaving the previous one in place unless the new one is sound."""
    previous_count = dump_point_count(DUMP_FILE)
    partial = f"{DUMP_FILE}.part"

    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        if os.path.exists(partial):
            os.remove(partial)
        try:
            wget.download(DUMP_URL, partial)
            print()
        except Exception as error:  # noqa: BLE001 - any transport failure is just a retry
            print(f"Download attempt {attempt}/{DOWNLOAD_ATTEMPTS} failed: {error}")
            continue

        defects = dump_defects(partial)
        if defects:
            print(f"Download attempt {attempt}/{DOWNLOAD_ATTEMPTS} produced an unusable dump:")
            for defect in defects:
                print(f"  - the downloaded file {defect}")
            continue

        new_count = dump_point_count(partial)
        if previous_count and new_count and new_count < previous_count * 0.95:
            # Not fatal: bans and deletions do shrink the dump. Worth seeing in the log though.
            print(
                f"Warning: the dump shrank from {previous_count} to {new_count} points "
                "since the last run"
            )
        os.replace(partial, DUMP_FILE)
        print(f"Dump verified: {new_count} points, {os.path.getsize(DUMP_FILE) / 1024 / 1024:.1f} MB")
        return

    if os.path.exists(partial):
        os.remove(partial)
    print(
        f"Could not obtain a usable {DUMP_URL} after {DOWNLOAD_ATTEMPTS} attempts - "
        "nothing was published, the previous dump is left untouched.",
        file=sys.stderr,
    )
    sys.exit(EXIT_BROKEN_DUMP)


download_dump()

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


### Drop duplicates
###
### hitchmap.com itself stores some submissions several times over: a double-clicked or retried
### submit writes two or more `points` rows that are identical apart from their `id` and a
### sub-second difference in `datetime`. Publishing those unchanged gave the relay 119 redundant
### ride notes (removed on 2026-08-12). A ride is therefore treated as a duplicate of another when
### its whole payload - position, comment, ride time, rating, nickname - matches and the two were
### submitted within DUP_WINDOW_S of each other. The earliest submission wins.
###
### The same check runs against the rides the relay already holds, so publishing a range that
### overlaps what is stored (an explicit --since, or a cutoff that moved backwards) cannot
### re-import anything either.

DUP_WINDOW_S = 300


def normalise_time(value) -> str:
    """A timestamp in the exact form the published record carries it ('' when absent)."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return ""
    if isinstance(value, str):
        return value[:19]
    return value.strftime("%Y-%m-%dT%H:%M:%S")


def ride_key(lat, lon, comment, ride_time, rating, nickname) -> tuple:
    """Identity of a ride, ignoring the fields that differ between duplicate submissions.

    Coordinates are rounded to 7 decimals (~1 cm) so that a float round-trip through the
    published JSON cannot make the same position look like two.
    """
    return (
        None if lat is None or pd.isna(lat) else round(float(lat), 7),
        None if lon is None or pd.isna(lon) else round(float(lon), 7),
        "" if comment is None or (not isinstance(comment, str) and pd.isna(comment)) else str(comment).strip(),
        normalise_time(ride_time),
        None if rating is None or pd.isna(rating) else int(rating),
        "" if nickname is None else str(nickname).strip(),
    )


def submission_epoch(value) -> int | None:
    """Whole seconds since the epoch, matching the precision rides are published with."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    ts = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(ts) else int(ts.floor("s").timestamp())


def relay_ride_keys(relay_db: str) -> dict:
    """key -> submission epochs, for every hitchmap.com ride the relay already holds."""
    conn = sqlite3.connect(f"file:{relay_db}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            """SELECT json_extract(j, '$.stops[0].location.latitude'),
                      json_extract(j, '$.stops[0].location.longitude'),
                      json_extract(j, '$.comment'),
                      json_extract(j, '$.stops[0].departure_time'),
                      json_extract(j, '$.rating'),
                      json_extract(j, '$.hitchhikers[0].nickname'),
                      json_extract(j, '$.submission_time')
               FROM (SELECT json_extract(content, '$.content') AS j
                     FROM event WHERE kind = 36820)
               WHERE json_extract(j, '$.source') = ?""",
            (SOURCE,),
        ).fetchall()
    finally:
        conn.close()

    seen = {}
    for lat, lon, comment, ride_time, rating, nickname, submission_time in rows:
        seen.setdefault(ride_key(lat, lon, comment, ride_time, rating, nickname), []).append(
            submission_epoch(submission_time)
        )
    return seen


def is_duplicate(seen: dict, key: tuple, epoch: int | None) -> bool:
    """True when `seen` already holds this ride, submitted at about the same time."""
    for other in seen.get(key, ()):
        if other is None and epoch is None:
            return True
        if other is not None and epoch is not None and abs(other - epoch) <= DUP_WINDOW_S:
            return True
    return False


relay_rides = relay_ride_keys(args.relay_db)
print(f"{sum(len(v) for v in relay_rides.values())} {SOURCE} rides already in the relay")

# Oldest first, so that the earliest submission of a duplicated ride is the one that is kept.
batch_rides: dict = {}
kept_index, dropped_here, dropped_already_in_relay = [], 0, 0
for index, row in hitchmap.sort_values("datetime").iterrows():
    key = ride_key(
        row["lat"], row["lon"], row["comment"], row["ride_datetime"], row["rating"], row["nickname"]
    )
    epoch = submission_epoch(row["datetime"])
    if is_duplicate(relay_rides, key, epoch):
        dropped_already_in_relay += 1
        continue
    if is_duplicate(batch_rides, key, epoch):
        dropped_here += 1
        continue
    batch_rides.setdefault(key, []).append(epoch)
    kept_index.append(index)

hitchmap = hitchmap.loc[kept_index]

print(
    f"Dropped {dropped_here} rides duplicated inside the dump and "
    f"{dropped_already_in_relay} already published; {len(hitchmap)} left to publish"
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
    print("Nothing to publish - the relay is up to date.")
    sys.exit(EXIT_NOTHING_TO_PUBLISH)

if args.dry_run:
    print("Dry run - not writing to the relay database. First record:")
    print(hitchhiking_records[0].model_dump_json(exclude_none=True, by_alias=True, indent=2))
    sys.exit(0)


### Check the relay database over before and after writing to it
###
### The poster writes rows into `event` and `tag` itself instead of going through the relay
### process, and the sqlite3 CLI leaves foreign keys off, so nothing downstream would notice a
### half-written batch. Each event contributes exactly 12 tags (one `d`, ten `g`, one
### `published_at`); anything else means tags went missing or were written twice.

TAGS_PER_EVENT = 12


def relay_counts(relay_db: str) -> tuple[int, int, int]:
    """(events, tags, tags whose event is gone) in the relay database."""
    conn = sqlite3.connect(f"file:{relay_db}?mode=ro", uri=True)
    try:
        (events,) = conn.execute("SELECT count(*) FROM event").fetchone()
        (tags,) = conn.execute("SELECT count(*) FROM tag").fetchone()
        (orphans,) = conn.execute(
            "SELECT count(*) FROM tag t LEFT JOIN event e ON e.id = t.event_id WHERE e.id IS NULL"
        ).fetchone()
        return events, tags, orphans
    finally:
        conn.close()


def assert_relay_writable(relay_db: str) -> None:
    """Fail before building events if we cannot write - `data/` is owned by the container uid."""
    try:
        # Neither mode=rw nor BEGIN IMMEDIATE is enough: SQLite quietly opens an unwritable file
        # read-only and only complains once something actually writes. So write, then roll back -
        # the probe table never survives, and the relay's own rows are never touched.
        conn = sqlite3.connect(f"file:{relay_db}?mode=rw", uri=True, isolation_level=None)
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute("CREATE TABLE _import_write_probe (x)")
            finally:
                conn.execute("ROLLBACK")
        finally:
            conn.close()
    except sqlite3.Error as error:
        print(
            f"Cannot write to {relay_db}: {error}\n"
            "Run the import as root - data/ is owned by the container uid (100:100).",
            file=sys.stderr,
        )
        sys.exit(EXIT_BROKEN_WRITE)


assert_relay_writable(args.relay_db)
events_before, tags_before, orphans_before = relay_counts(args.relay_db)

poster = HitchhikingDataStandardToNostrPoster()

# Use batch processing for much faster publishing
# Adjust batch_size based on your relay capacity (100-500 works well)
poster.post_batch_to_db(
    ride_records=hitchhiking_records,
    db_path=args.relay_db,
    batch_size=args.batch_size,
)

poster.close()

events_after, tags_after, orphans_after = relay_counts(args.relay_db)
events_written = events_after - events_before
tags_written = tags_after - tags_before

print(
    f"Relay grew by {events_written} events and {tags_written} tags "
    f"(expected {len(hitchhiking_records)} and {len(hitchhiking_records) * TAGS_PER_EVENT})"
)

problems = []
if events_written != len(hitchhiking_records):
    problems.append(
        f"wrote {events_written} of {len(hitchhiking_records)} events - "
        "the log above names the records that failed"
    )
if tags_written != events_written * TAGS_PER_EVENT:
    problems.append(
        f"wrote {tags_written} tags for {events_written} events, expected "
        f"{events_written * TAGS_PER_EVENT}"
    )
if orphans_after > orphans_before:
    problems.append(f"left {orphans_after - orphans_before} tags without an event")

if problems:
    print("Relay database check failed after publishing:", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    sys.exit(EXIT_BROKEN_WRITE)

print("Relay database check passed.")
