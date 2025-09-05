"""
An example of how to take a ride that was just recorded
e.g. on a hitchhiking application with opinionated fields that were collected by the application,
transform it into the defined standard and to post it to Nostr so that others can access it.
"""

import sys

import pandas as pd

sys.path.append("../python")

from utils.post_hitchhiking_ride_to_nostr import HitchhikingDataStandardToNostrPoster
from hitchhiking_data_standard_pydantic_model import (
    Hitchhiker,
    HitchhikingRecord,
    Location,
    Signal,
    Stop,
)

CUSTOM_HITCHHIKING_RIDE_OBJECT = {
    "rate": "3",
    "coords": "12.34,56.78,90.12,34.56",
    "datetime_ride": "2025-08-31T12:00:00",
    "wait": "5",
    "signal": "thumb",
    "nickname": "Alice",
    "comment": "Pretty easy",
}

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
### Again, here the function is a bit special because we are dealing with multiple datasets actually


def create_record_from_custom_object(
    custom_object: dict, source: str, license: str
) -> HitchhikingRecord:
    """Caters for setup of hitchmap.com on 2025/08/31."""
    lat, lon, dest_lat, dest_lon = map(float, custom_object["coords"].split(","))

    stops = [
        Stop(
            location=Location(
                latitude=lat,
                longitude=lon,
                is_exact=True,
            ),
            arrival_time=None,
            departure_time=pd.to_datetime(custom_object["datetime_ride"]).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            if pd.notna(custom_object["datetime_ride"])
            else None,
            waiting_duration=f"{int(custom_object['wait'])}M"
            if pd.notna(custom_object["wait"])
            else None,
        ),
    ]
    if pd.notna(dest_lat) and pd.notna(dest_lon):
        stops.append(
            Stop(
                location=Location(
                    latitude=dest_lat,
                    longitude=dest_lon,
                    is_exact=False,
                )
            )
        )

    signals = [map_signal(custom_object["signal"])] if custom_object["signal"] else None
    if signals is not None and len(signals) == 1 and pd.notna(custom_object["wait"]):
        signals = [
            Signal(methods=signals[0].methods, duration=f"{custom_object['wait']}M")
        ]

    now = pd.Timestamp.now()

    record = HitchhikingRecord(
        version="0.0.0",
        stops=stops,
        rating=int(custom_object["rate"]),
        hitchhikers=[
            Hitchhiker(
                nickname=custom_object["nickname"]
                if pd.notna(custom_object["nickname"])
                else "Anonymous"
            )
        ],
        comment=None if custom_object["comment"] == "" else custom_object["comment"],
        signals=signals,
        occupants=None,
        mode_of_transportation=None,
        ride=None,
        declined_rides=None,
        source=source,
        license=license,
        submission_time=now.strftime("%Y-%m-%dT%H:%M:%S"),
    )

    return record


### Post your record to the Nostr protocol to publish them

poster = HitchhikingDataStandardToNostrPoster()
record = create_record_from_custom_object(
    CUSTOM_HITCHHIKING_RIDE_OBJECT, source="hitchmap.com", license="odbl"
)
poster.post(ride_record=record)
poster.close()
