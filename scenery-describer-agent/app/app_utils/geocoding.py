# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import urllib.parse
import urllib.request


def geocode_location(location: str):
    """Helper function to convert a location name to lat, lon, and metadata."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1"
    req = urllib.request.Request(url, headers={"User-Agent": "SceneryAgent/1.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            results = data.get("results")
            if results:
                return results[0]
    except Exception as e:
        print(f"Geocoding error for {location}: {e}")
    return None
