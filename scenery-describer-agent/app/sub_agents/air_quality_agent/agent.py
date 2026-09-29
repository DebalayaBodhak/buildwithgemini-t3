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

from app.sub_agents.air_quality_agent.tools import get_air_quality

air_quality_agent = Agent(
    name="air_quality_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Air Quality Specialist Agent. You specialize in retrieving and interpreting "
        "atmospheric air quality (AQI, PM2.5, PM10, UV index) and atmospheric clarity conditions. "
        "Always use the `get_air_quality` tool when requested to evaluate air quality or atmospheric visibility for a location."
    ),
    description="Specialist agent that fetches and analyzes real-time air quality, AQI, dust, PM2.5, PM10, UV index, and atmospheric clarity for any location.",
    tools=[get_air_quality],
)
