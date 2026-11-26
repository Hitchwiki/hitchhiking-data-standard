# From https://github.com/Hitchwiki/hitchhiking-data-standard/blob/main/python/csv_to_standard.py
#
# Copyright (C) 2026 Till Wenke
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
"""Turn a private spreadsheet of rides (CSV) into records that follow this standard.

Nothing is published. The output is a JSON Lines file (one validated record per
line) that stays on your machine; publishing it is a separate, deliberate step
(see ../nostr/README.md).

    python csv_to_standard.py my_rides.csv --source my-notebook --license odbl --out my_rides.jsonl

Your CSV may use its own column names; map them with --column, e.g.
``--column start_lat=Lat --column wait_minutes="Waiting (min)"``.
Recognised columns (only start_lat and start_lon are required):

    start_lat, start_lon   where you stood (decimal degrees)
    end_lat, end_lon       where the ride dropped you (optional)
    departure_time         when the ride started, e.g. 2024-05-01T14:30
    wait_minutes           how long you waited, whole minutes
    rating                 1-5
    comment                free text
    signal                 one or more of thumb, waving, sign, asking, invited,
                           prearranged, unsolicited; separate several with ";"
    vehicle                car, bus, van, truck, motorbike, ... (see KindEnum)
    nickname               who hitchhiked; falls back to --nickname, then "Anonymous"

Rows that do not validate are reported with their line number and skipped.
"""

import argparse
import csv
import json
import sys
from typing import Dict, Iterable, List, Optional, Tuple

from pydantic import ValidationError

from hitchhiking_data_standard_pydantic_model import (
    Hitchhiker,
    HitchhikingRecord,
    Location,
    ModeOfTranportation,
    Signal,
    Stop,
)

STANDARD_VERSION = "0.0.0"
COLUMNS = (
    "start_lat", "start_lon", "end_lat", "end_lon", "departure_time",
    "wait_minutes", "rating", "comment", "signal", "vehicle", "nickname",
)


def _get(row: Dict[str, str], mapping: Dict[str, str], name: str) -> Optional[str]:
    value = row.get(mapping.get(name, name))
    if value is None:
        return None
    value = value.strip()
    return value or None


def row_to_record(
    row: Dict[str, str],
    source: str,
    license: str,
    mapping: Optional[Dict[str, str]] = None,
    nickname: Optional[str] = None,
) -> HitchhikingRecord:
    """Build one HitchhikingRecord from a CSV row. Raises ValueError/ValidationError."""
    mapping = mapping or {}
    g = lambda name: _get(row, mapping, name)  # noqa: E731

    if g("start_lat") is None or g("start_lon") is None:
        raise ValueError("start_lat and start_lon are required")
    wait = g("wait_minutes")
    stops = [
        Stop(
            location=Location(latitude=float(g("start_lat")), longitude=float(g("start_lon")), is_exact=True),
            departure_time=g("departure_time"),
            waiting_duration=f"PT{int(float(wait))}M" if wait is not None else None,
        )
    ]
    if g("end_lat") is not None and g("end_lon") is not None:
        stops.append(
            Stop(location=Location(latitude=float(g("end_lat")), longitude=float(g("end_lon")), is_exact=False))
        )

    signal = g("signal")
    methods = [m.strip().lower() for m in signal.split(";") if m.strip()] if signal else []
    vehicle = g("vehicle")
    rating = g("rating")

    return HitchhikingRecord(
        version=STANDARD_VERSION,
        stops=stops,
        rating=int(float(rating)) if rating is not None else None,
        hitchhikers=[Hitchhiker(nickname=g("nickname") or nickname or "Anonymous")],
        comment=g("comment"),
        signals=[Signal(methods=methods)] if methods else None,
        mode_of_transportation=ModeOfTranportation(kind=vehicle.lower()) if vehicle else None,
        source=source,
        license=license,
    )


def convert(
    rows: Iterable[Dict[str, str]],
    source: str,
    license: str,
    mapping: Optional[Dict[str, str]] = None,
    nickname: Optional[str] = None,
) -> Tuple[List[HitchhikingRecord], List[Tuple[int, str]]]:
    """Return (records, errors); errors are (csv line number, message)."""
    records, errors = [], []
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        try:
            records.append(row_to_record(row, source, license, mapping, nickname))
        except (ValueError, ValidationError) as exc:
            errors.append((line_no, str(exc).splitlines()[0] if str(exc) else type(exc).__name__))
    return records, errors


def _parse_mapping(pairs: List[str]) -> Dict[str, str]:
    mapping = {}
    for pair in pairs:
        name, sep, column = pair.partition("=")
        if not sep or name not in COLUMNS:
            raise SystemExit(f"--column expects one of {', '.join(COLUMNS)} as NAME=YOUR_COLUMN, got {pair!r}")
        mapping[name] = column
    return mapping


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("csv", help="your rides, one per row, with a header line")
    ap.add_argument("--source", required=True, help="name of your dataset, e.g. my-notebook")
    ap.add_argument("--license", required=True, help="e.g. odbl or cc-by-sa-4.0 (or 'private')")
    ap.add_argument("--nickname", help="hitchhiker nickname when the CSV has no nickname column")
    ap.add_argument("--column", action="append", default=[], metavar="NAME=YOUR_COLUMN")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--out", help="JSON Lines output file (default: stdout)")
    args = ap.parse_args(argv)

    with open(args.csv, newline="", encoding="utf-8-sig") as fh:
        records, errors = convert(
            csv.DictReader(fh, delimiter=args.delimiter),
            args.source, args.license, _parse_mapping(args.column), args.nickname,
        )

    out = open(args.out, "w", encoding="utf-8") if args.out else sys.stdout
    try:
        for record in records:
            out.write(json.dumps(record.model_dump(exclude_none=True), ensure_ascii=False) + "\n")
    finally:
        if args.out:
            out.close()

    for line_no, message in errors:
        print(f"line {line_no}: skipped ({message})", file=sys.stderr)
    print(f"{len(records)} records written, {len(errors)} rows skipped", file=sys.stderr)
    return 1 if errors and not records else 0


if __name__ == "__main__":
    raise SystemExit(main())
