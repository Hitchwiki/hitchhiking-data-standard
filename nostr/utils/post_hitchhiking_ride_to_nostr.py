# From https://github.com/Hitchwiki/hitchhiking-data-standard/blob/main/nostr/utils/post_hitchhiking_ride_to_nostr.py
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
                [
                    "expiration",
                    str(unix_timestamp_now + 3600),
                ],  # Expiration time set to 1 hours from now
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

    def close(self):
        self.relay_manager.close_all_relay_connections()
