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

    def post_batch(self, ride_records: list[HitchhikingRecord], batch_size: int = 100):
        """Post multiple records efficiently in batches"""
        if not POST_TO_RELAYS:
            print("POST_TO_RELAYS is disabled, skipping publishing")
            return

        total_records = len(ride_records)
        print(f"Publishing {total_records} records in batches of {batch_size}")
        print(f"Estimated time: ~{(total_records / batch_size * 0.2):.1f} seconds")
        
        published_count = 0
        
        for i in tqdm(range(0, total_records, batch_size), desc="Publishing batches"):
            batch = ride_records[i:i + batch_size]
            
            try:
                # Create and queue all events in the batch
                for record in batch:
                    event = self.create_event(record)
                    self.relay_manager.publish_event(event)
                
                # Send the batch
                self.relay_manager.run_sync()
                published_count += len(batch)
                
                # Process any OK notices without blocking
                processed_notices = 0
                while self.relay_manager.message_pool.has_ok_notices() and processed_notices < batch_size:
                    self.relay_manager.message_pool.get_ok_notice()
                    processed_notices += 1
                
                # Brief pause between batches to avoid overwhelming relays
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error publishing batch {i//batch_size + 1}: {e}")
                break

            if i % 100 == 0:
                print(f"Processed {i} records")
                time.sleep(60) 
        
        print(f"Successfully published {published_count}/{total_records} records")

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
