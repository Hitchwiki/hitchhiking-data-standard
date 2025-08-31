This model to create and validation python objects that follow the hitchhiking data standard can be handy for your application. You can get it like this:

```py
import requests

url = "https://raw.githubusercontent.com/Hitchwiki/hitchhiking-data-standard/refs/heads/main/python/hitchhiking_data_standard_pydantic_model.py"
response = requests.get(url)

with open("hitchhiking_data_standard_pydantic_model.py", "w") as f:
    f.write(response.text)

from data_standard_pydantic_model import Hitchhiker, HitchhikingRecord, Location, Signal, Stop
```