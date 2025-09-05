# From https://github.com/Hitchwiki/hitchhiking-data-standard/blob/main/nostr/publish_past_rides.py
"""
An example of how to take a present dataset of hitchhiking rides,
transform it into the defined standard and to post it to Nostr so that others can access it.
"""

import sys
import os
import wget

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

### Load your dataset of past hitchhiking rides

url = "https://hitchmap.com/dump.sqlite"
filename = "dump.sqlite"
if os.path.exists(filename):
    os.remove(filename)
filename = wget.download(url)
fn = "dump.sqlite"
points = pd.read_sql("select * from points where not banned", sqlite3.connect(fn))
points["datetime"] = points["datetime"].astype("datetime64[ns]")

### Clean your dataset from issues that your are already aware of
### This prevents that others have to do it when fetching these rides

points.loc[points["datetime"] < "2000-01-01", "datetime"] = None

points["ride_datetime"] = points["ride_datetime"].replace("0224-10-31T21:30", None)
points["ride_datetime"] = points["ride_datetime"].replace("0025-03-07T08:00", None)
points["ride_datetime"] = points["ride_datetime"].replace("1014-11-04T14:30", None)
points["ride_datetime"] = points["ride_datetime"].replace("0202-04-03T18:50", None)

points["ride_datetime"] = points["ride_datetime"].astype("datetime64[ns]")

### This is a unique step that is performed here where we post all rides from 20 years of rides

# assume that during the lifershalte time the timestamps where not always set
# thus attribute this part of the dataset to the lifershalte
no_date = points[points["datetime"].isna()]
with_date = points[~points["datetime"].isna()]

lift = pd.concat([no_date, with_date[with_date["datetime"] < "2010-08-11"]])

wiki = with_date[
    (with_date["datetime"] >= "2010-08-11") & (with_date["datetime"] < "2022-10-13")
]

hitchmap = with_date[with_date["datetime"] >= "2022-10-13"]

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
            waiting_duration=f"{int(row['wait'])}M" if pd.notna(row["wait"]) else None,
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

    signals = [map_signal(row["signal"])] if row["signal"] else None
    if signals is not None and len(signals) == 1 and pd.notna(row["wait"]):
        signals = [Signal(methods=["sign"], duration=f"{row['wait']}M")]

    record = HitchhikingRecord(
        version="0.0.0",
        stops=stops,
        rating=rating_formula(row["rating"]),
        hitchhikers=[
            Hitchhiker(
                nickname=row["nickname"] if pd.notna(row["nickname"]) else "Anonymous"
            )
        ],
        comment=row["comment"],
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

for _, row in tqdm(lift.iterrows(), total=len(lift)):
    hitchhiking_records.append(
        create_record_from_row(
            row,
            source="liftershalte.info",
            license="cc-by-sa-4.0",
        )
    )

for _, row in tqdm(wiki.iterrows(), total=len(wiki)):
    hitchhiking_records.append(
        create_record_from_row(
            row,
            source="hitchwiki.org",
            license="cc-by-sa-4.0",
        )
    )

for _, row in tqdm(hitchmap.iterrows(), total=len(hitchmap)):
    hitchhiking_records.append(
        create_record_from_row(
            row,
            source="hitchmap.com",
            license="odbl",
        )
    )

### Post your records to the Nostr protocol to publish them

poster = HitchhikingDataStandardToNostrPoster()
for record in hitchhiking_records[-100:]:
    poster.post(ride_record=record)

poster.close()
