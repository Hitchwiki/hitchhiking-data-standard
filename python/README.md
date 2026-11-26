This model to create and validation python objects that follow the hitchhiking data standard can be handy for your application. You can get it like this:

```py
import requests

url = "https://raw.githubusercontent.com/Hitchwiki/hitchhiking-data-standard/refs/heads/main/python/hitchhiking_data_standard_pydantic_model.py"
response = requests.get(url)

with open("hitchhiking_data_standard_pydantic_model.py", "w") as f:
    f.write(response.text)

from data_standard_pydantic_model import Hitchhiker, HitchhikingRecord, Location, Signal, Stop
```
## Converting your own (private) ride log

If you keep your rides in a spreadsheet, `csv_to_standard.py` turns a CSV export of it into records that follow this standard. Each row is validated, and the records are written as JSON Lines. **Nothing is published:** the output file stays on your machine until you decide to share it (see `../nostr/README.md` for how to publish).

```shell
pip install -r requirements.txt
python csv_to_standard.py my_rides.csv --source my-notebook --license odbl --nickname me --out my_rides.jsonl
```

Only `start_lat` and `start_lon` are required. The other recognised columns are `end_lat`, `end_lon`, `departure_time`, `wait_minutes`, `rating`, `comment`, `signal` (e.g. `thumb;sign`), `vehicle` and `nickname`. If your spreadsheet uses different headers, map them, e.g. `--column start_lat=Lat --column wait_minutes="Waiting (min)"`. Rows that do not validate are listed with their line number and skipped, so you can fix them and run it again.
