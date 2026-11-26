import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr

from csv_to_standard import convert, main, row_to_record

CSV = """Lat,Lon,To lat,To lon,When,Waited,Stars,Notes,How,Car
48.1,11.5,47.8,13.0,2024-05-01T14:30,25,4,good spot,thumb;sign,car
not-a-number,11.5,,,,,,,,
52.5,13.4,,,,,6,,,
50.0,8.0,,,,,,,,truck
"""

MAPPING = {
    "start_lat": "Lat", "start_lon": "Lon", "end_lat": "To lat", "end_lon": "To lon",
    "departure_time": "When", "wait_minutes": "Waited", "rating": "Stars",
    "comment": "Notes", "signal": "How", "vehicle": "Car",
}


class CsvToStandardTest(unittest.TestCase):
    def rows(self):
        return csv.DictReader(io.StringIO(CSV))

    def test_full_row_maps_every_field(self):
        records, _ = convert(self.rows(), "my-notebook", "odbl", MAPPING, "till")
        r = records[0].model_dump(exclude_none=True)
        self.assertEqual(r["stops"][0]["location"], {"latitude": 48.1, "longitude": 11.5, "is_exact": True})
        self.assertEqual(r["stops"][0]["waiting_duration"], "PT25M")
        self.assertEqual(r["stops"][0]["departure_time"], "2024-05-01T14:30")
        self.assertEqual(r["stops"][1]["location"]["is_exact"], False)
        self.assertEqual(r["signals"], [{"methods": ["thumb", "sign"]}])
        self.assertEqual(r["mode_of_transportation"], {"kind": "car"})
        self.assertEqual(r["hitchhikers"], [{"nickname": "till"}])
        self.assertEqual((r["rating"], r["comment"], r["source"], r["license"]), (4, "good spot", "my-notebook", "odbl"))

    def test_bad_rows_are_reported_with_line_numbers_and_skipped(self):
        records, errors = convert(self.rows(), "s", "odbl", MAPPING)
        self.assertEqual(len(records), 2)
        self.assertEqual([line for line, _ in errors], [3, 4])  # bad latitude, rating 6

    def test_minimal_row_is_anonymous_and_has_no_empty_fields(self):
        r = row_to_record({"start_lat": "50", "start_lon": "8"}, "s", "odbl").model_dump(exclude_none=True)
        self.assertEqual(r["hitchhikers"], [{"nickname": "Anonymous"}])
        self.assertEqual(set(r), {"version", "stops", "hitchhikers", "source", "license"})

    def test_unknown_signal_is_rejected(self):
        with self.assertRaises(Exception):
            row_to_record({"start_lat": "50", "start_lon": "8", "signal": "dance"}, "s", "odbl")

    def test_cli_writes_json_lines(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "in.csv"), os.path.join(d, "out.jsonl")
            with open(src, "w") as fh:
                fh.write(CSV)
            args = [src, "--source", "s", "--license", "odbl", "--out", out]
            for name, col in MAPPING.items():
                args += ["--column", f"{name}={col}"]
            with redirect_stderr(io.StringIO()) as err:
                self.assertEqual(main(args), 0)
            lines = open(out).read().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[1])["mode_of_transportation"], {"kind": "truck"})
            self.assertIn("2 records written, 2 rows skipped", err.getvalue())


if __name__ == "__main__":
    unittest.main()
