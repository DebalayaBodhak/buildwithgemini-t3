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

from app.agent import root_agent
from app.sub_agents.google_geo_agent import (
    find_nearby_places,
    geocode_address,
    google_geo_agent,
)


def test_geocode_address_fallback() -> None:
    res = geocode_address("Kyoto")
    assert "Geocoding result" in res
    assert "Latitude" in res


def test_find_nearby_places_execution() -> None:
    res = find_nearby_places("San Francisco", "park", 1000)
    assert ("GOOGLE_MAPS_API_KEY" in res or "Nearby" in res or "No nearby" in res)


def test_google_geo_sub_agent_configured_on_root() -> None:
    sub_names = [s.name for s in root_agent.sub_agents]
    assert "google_geo_agent" in sub_names
    assert google_geo_agent in root_agent.sub_agents
