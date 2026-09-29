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

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.app_utils.time_tools import calculate_time_difference
from app.sub_agents.google_geo_agent.tools import find_nearby_places, geocode_address

google_geo_agent = Agent(
    name="google_geo_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Google Geo & Places Specialist Agent. You specialize in converting street addresses "
        "or place names to precise coordinates using the Google Maps Geocoding API (`geocode_address`), "
        "discovering nearby points of interest using the Google Places API (New) (`find_nearby_places`), "
        "and calculating time differences between locations using `calculate_time_difference`."
    ),
    description=(
        "Specialist agent that converts addresses to coordinates, finds nearby points of interest, "
        "and calculates time differences between locations."
    ),
    tools=[geocode_address, find_nearby_places, calculate_time_difference],
)
