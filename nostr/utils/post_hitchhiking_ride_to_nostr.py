# From https://github.com/Hitchwiki/hitchhiking-data-standard/blob/main/nostr/utils/post_hitchhiking_ride_to_nostr.py
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
Class to allow posting hitchhiking rides in the standardized format to Nostr.
Especially for large bulk upload you should test this uploading procedure by running it with the expiration tag
described below, verify that all your rides are on the relays and then remove the expiration tag and re-run to upload permanently.
If you are certain that you want to permanantly publish the rides remove the expiration tag from the Nostr event.
"""

import logging
import time
import uuid
import sys
import os
import ast
import json
import sqlite3
from tqdm import tqdm

sys.path.append("../python")

from pynostr.key import PrivateKey
from pynostr.relay_manager import RelayManager
from pynostr.event import Event
import geohash2
from dotenv import load_dotenv

from hitchhiking_data_standard_pydantic_model import HitchhikingRecord

load_dotenv(".env")

NSEC = os.getenv("NSEC")
POST_TO_RELAYS = os.getenv("POST_TO_RELAYS").lower() in ("true", "1", "t")
RELAYS = ast.literal_eval(os.getenv("RELAYS"))

logger = logging.getLogger(__name__)

# relay.maps.hitchwiki.org's own config.toml caps at 5 events/sec (issue #59/#61)
# via nostr-rs-relay's token-bucket limiter, which allows only a small initial
# burst before enforcing that sustained rate. Stay safely under it.
DEFAULT_EVENTS_PER_SEC = 4.0


class HitchhikingDataStandardToNostrPoster:
    def __init__(self):
        private_key_obj = PrivateKey.from_nsec(NSEC)
        self.private_key_hex = private_key_obj.hex()
        self.pubkey_hex = private_key_obj.public_key.hex()
        self.npub = private_key_obj.public_key.bech32()
        print(f"Posting as npub {self.npub}")

        # Initialize the relay manager
        self.relay_manager = RelayManager(timeout=5)
        for relay in RELAYS:
            self.relay_manager.add_relay(relay)

        self.event_kind = 36820  # Event kind for hitchhiking notes

    def create_event(self, ride_record: HitchhikingRecord):
        content = ride_record.model_dump_json(exclude_none=True, by_alias=True)

        start_location = ride_record.stops[0].location

        unix_timestamp_now = int(time.time())

        # Create cascading geohash tags for each precision from 1 to 10
        geohash_tags = [
            [
                "g",
                geohash2.encode(
                    start_location.latitude, start_location.longitude, precision=p
                ),
            ]
            for p in range(1, 11)
        ]

        event = Event(
            kind=self.event_kind,
            created_at=unix_timestamp_now,
            content=content,
            pubkey=self.pubkey_hex,
            id=None,  # ID will be computed later
            sig=None,  # Signature will be added later
            tags=[
                ["d", f"{ride_record.source}-{uuid.uuid4()}"],
                *geohash_tags,
                ["published_at", str(unix_timestamp_now)],
            ],
        )

        event.sign(self.private_key_hex)
        return event

    def post(self, ride_record: HitchhikingRecord):
        event = self.create_event(ride_record)
        print(event.to_message())

        if POST_TO_RELAYS:
            self.relay_manager.publish_event(event)
            self.relay_manager.run_sync()

            # Wait briefly for OK notices from relays
            time.sleep(1)
            self.relay_manager.run_sync()

            confirmed = 0
            while self.relay_manager.message_pool.has_ok_notices():
                ok_notice = self.relay_manager.message_pool.get_ok_notice()
                if ok_notice.ok:
                    confirmed += 1
                else:
                    print(f"Relay {ok_notice.url} rejected event: {ok_notice.message}")

            if confirmed > 0:
                print(f"Event confirmed by {confirmed} relay(s)")
            else:
                print("Warning: No confirmation received from any relay")

    def post_batch(
        self,
        ride_records: list[HitchhikingRecord],
        batch_size: int = 100,
        events_per_sec: float = DEFAULT_EVENTS_PER_SEC,
    ):
        """Post multiple records, paced under the relay's own rate limit.

        Previously this queued a whole `batch_size` chunk of events and fired
        them at once (`run_sync()`), pausing only *between* batches -- against
        relay.maps.hitchwiki.org's real `messages_per_sec = 5` (config.toml,
        issue #59/#61) that burst blows straight through the limit, so most of
        each batch would come back rejected. Worse, the old code drained OK
        notices without ever reading `.ok`, so a run reported "published
        N/N" regardless of how many the relay actually accepted -- exactly
        the silent-loss issue #61 asks to fix. This paces one event at a time
        at `events_per_sec` (default 4, below the relay's 5/sec cap) and
        counts confirmed vs. rejected vs. unconfirmed for real, logging every
        rejection (same pattern already shipped for the live app in
        maps.hitchwiki.org's `post_hitchhiking_ride_to_nostr.py::flush()`).
        `batch_size` now only controls progress-print granularity, kept for
        backward compatibility with existing callers.
        """
        if not POST_TO_RELAYS:
            print("POST_TO_RELAYS is disabled, skipping publishing")
            return

        total_records = len(ride_records)
        interval = 1.0 / events_per_sec
        print(f"Publishing {total_records} records at ~{events_per_sec}/sec")
        print(f"Estimated time: ~{(total_records * interval):.1f} seconds")

        confirmed_count = 0
        rejected_count = 0
        unconfirmed_count = 0

        for i, record in enumerate(tqdm(ride_records, desc="Publishing")):
            start = time.monotonic()
            try:
                event = self.create_event(record)
                self.relay_manager.publish_event(event)
                self.relay_manager.run_sync()

                # Give relays a moment to answer this specific event before moving
                # on -- draining non-blockingly (the old code) risks the *next*
                # event's OK notice arriving late and being misattributed here.
                time.sleep(0.2)
                self.relay_manager.run_sync()

                got_notice = False
                while self.relay_manager.message_pool.has_ok_notices():
                    ok_notice = self.relay_manager.message_pool.get_ok_notice()
                    got_notice = True
                    if ok_notice.ok:
                        confirmed_count += 1
                    else:
                        rejected_count += 1
                        logger.warning(
                            "Relay %s rejected event: %s", ok_notice.url, ok_notice.message
                        )
                if not got_notice:
                    unconfirmed_count += 1
            except Exception as e:
                print(f"Error publishing record {i}: {e}")
                unconfirmed_count += 1

            elapsed = time.monotonic() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)

            if (i + 1) % batch_size == 0:
                print(
                    f"Processed {i + 1}/{total_records} "
                    f"({confirmed_count} confirmed, {rejected_count} rejected, "
                    f"{unconfirmed_count} unconfirmed)"
                )

        print(
            f"Done: {confirmed_count} confirmed, {rejected_count} rejected, "
            f"{unconfirmed_count} unconfirmed of {total_records} total"
        )

    def _get_expires_at(self, tags: list) -> int | None:
        for tag in tags:
            if len(tag) >= 2 and tag[0] == "expiration":
                try:
                    return int(tag[1])
                except (ValueError, IndexError):
                    pass
        return None

    def _write_event_to_db(self, event, conn: sqlite3.Connection):
        """Write a single signed pynostr Event to the relay SQLite database."""
        event_dict = event.to_dict()
        content_json = json.dumps(event_dict, separators=(',', ':'))

        event_hash = bytes.fromhex(event_dict["id"])
        author = bytes.fromhex(event_dict["pubkey"])
        first_seen = int(time.time())
        created_at = event_dict["created_at"]
        kind = event_dict["kind"]
        expires_at = self._get_expires_at(event_dict["tags"])

        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR IGNORE INTO event
               (event_hash, first_seen, created_at, expires_at, author, delegated_by, kind, hidden, content)
               VALUES (?, ?, ?, ?, ?, NULL, ?, 0, ?)""",
            (event_hash, first_seen, created_at, expires_at, author, kind, content_json),
        )
        event_row_id = cursor.lastrowid

        # Only insert tags if the event was actually inserted (not a duplicate)
        if event_row_id:
            for tag in event_dict["tags"]:
                if len(tag) < 2:
                    continue
                name = tag[0]
                value = tag[1]
                # Store binary blob in value_hex if the value is a valid hex string
                value_hex = None
                if isinstance(value, str) and len(value) % 2 == 0:
                    try:
                        value_hex = bytes.fromhex(value)
                    except ValueError:
                        pass
                cursor.execute(
                    """INSERT INTO tag (event_id, name, value, value_hex, created_at, kind)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (event_row_id, name, value, value_hex, created_at, kind),
                )

    def post_to_db(self, ride_record: HitchhikingRecord, db_path: str):
        """Create an event from a ride record and write it directly to the relay database."""
        event = self.create_event(ride_record)
        conn = sqlite3.connect(db_path)
        try:
            self._write_event_to_db(event, conn)
            conn.commit()
        finally:
            conn.close()

    def post_batch_to_db(self, ride_records: list[HitchhikingRecord], db_path: str, batch_size: int = 1000):
        """Write multiple ride records directly to the relay database in batches."""
        total = len(ride_records)
        print(f"Writing {total} records directly to database: {db_path}")
        conn = sqlite3.connect(db_path)
        written = 0
        try:
            for i in tqdm(range(0, total, batch_size), desc="Writing to DB"):
                batch = ride_records[i:i + batch_size]
                for record in batch:
                    try:
                        self._write_event_to_db(self.create_event(record), conn)
                        written += 1
                    except Exception as e:
                        print(f"Error writing record: {e}")
                conn.commit()
        finally:
            conn.close()
        print(f"Successfully wrote {written}/{total} records")

    def close(self):
        self.relay_manager.close_all_relay_connections()
