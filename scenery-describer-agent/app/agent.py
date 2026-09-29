# ruff: noqa
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

import datetime
import json
import os
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback
from app.app_utils.geocoding import geocode_location
from app.sub_agents.air_quality_agent import air_quality_agent, get_air_quality
from app.sub_agents.gogle_media_generator_agent import gogle_media_generator_agent
from app.sub_agents.google_geo_agent import find_nearby_places, geocode_address, google_geo_agent

_geocode_location = geocode_location


WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_live_weather(location: str) -> str:
    """Fetches real-time live weather conditions, temperature, and wind speed for any location.

    Args:
        location: City or place name (e.g. "San Francisco", "Kyoto", "Paris").

    Returns:
        A string describing the current weather conditions, temperature, daytime/nighttime status, and wind speed.
    """
    geo = geocode_location(location)
    if not geo:
        return f"Could not find coordinates for location: '{location}'."

    lat, lon = geo["latitude"], geo["longitude"]
    name = geo.get("name", location)
    country = geo.get("country", "")

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
    req = urllib.request.Request(url, headers={"User-Agent": "SceneryAgent/1.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            curr = data.get("current_weather", {})
            temp_c = curr.get("temperature", 0.0)
            temp_f = round((temp_c * 9 / 5) + 32, 1)
            code = curr.get("weathercode", 0)
            condition = WMO_WEATHER_CODES.get(code, "Variable weather")
            is_day = "Daytime" if curr.get("is_day") == 1 else "Nighttime"
            wind_speed = curr.get("windspeed", 0.0)

            return (
                f"Live weather for {name}, {country}: {temp_c}°C ({temp_f}°F), {condition}. "
                f"Period: {is_day}. Wind speed: {wind_speed} km/h."
            )
    except Exception as e:
        return f"Error fetching live weather for {location}: {str(e)}"


def get_weather(query: str) -> str:
    """Alias for get_live_weather to fetch real weather conditions for a location."""
    return get_live_weather(query)


def get_sun_times(location: str) -> str:
    """Fetches exact sunrise, sunset, and golden/blue hour lighting windows for a location.

    Args:
        location: City or place name (e.g. "San Francisco", "Kyoto", "Reykjavik").

    Returns:
        A string with exact sunrise, sunset, and estimated golden/blue hour windows in the local timezone.
    """
    geo = geocode_location(location)
    if not geo:
        return f"Could not find coordinates for location: '{location}'."

    lat, lon = geo["latitude"], geo["longitude"]
    name = geo.get("name", location)
    country = geo.get("country", "")
    tz_name = geo.get("timezone", "UTC")

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=sunrise,sunset&timezone=auto"
    req = urllib.request.Request(url, headers={"User-Agent": "SceneryAgent/1.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            daily = data.get("daily", {})
            sunrises = daily.get("sunrise", [])
            sunsets = daily.get("sunset", [])

            if not sunrises or not sunsets:
                return f"Could not determine solar times for {location}."

            sunrise_time = sunrises[0].split("T")[-1]
            sunset_time = sunsets[0].split("T")[-1]

            return (
                f"Solar schedule for {name}, {country} (Timezone: {tz_name}):\n"
                f"- Sunrise: {sunrise_time}\n"
                f"- Sunset: {sunset_time}\n"
                f"- Morning Golden Hour: ~{sunrise_time} to 1 hr post-sunrise\n"
                f"- Evening Golden Hour: ~1 hr pre-sunset to {sunset_time}\n"
                f"- Evening Blue Hour: ~{sunset_time} to 30 mins post-sunset"
            )
    except Exception as e:
        return f"Error fetching solar timing for {location}: {str(e)}"


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    geo = geocode_location(query)
    if geo and "timezone" in geo:
        tz = ZoneInfo(geo["timezone"])
        now = datetime.datetime.now(tz)
        return f"The current local time for {geo['name']} is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    return f"Sorry, could not find timezone information for {query}."


from app.app_utils.time_tools import calculate_time_difference
from app.firestore_tools import (
    list_scenic_moments,
    save_scenic_moment,
    search_scenic_moments_by_location,
)
from app.sub_agents.gogle_media_generator_agent import (
    generate_scenery_image,
    generate_scenery_video,
)

code_executor = AgentEngineSandboxCodeExecutor()

async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Memory service is not available in this context/runner
        pass
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Scenery Describer Agent, a master poet and fine-art visual orchestrator. "
        "CRITICAL MANDATE: For EVERY user request, you MUST ALWAYS provide BOTH an atmospheric, detailed description "
        "AND a generated fine-art visual artwork image in the frontend. "
        "You craft deeply poetic, vivid scenery descriptions grounded in real-time weather, solar lighting times, "
        "air quality, time differences, and local geographical context. "
        "You remember all frequent questions, user preferences, explicit instructions, and key details from past conversations."
    ),
    workflow_description=(
        "Follow this workflow for EVERY turn:\n"
        "1. Gather necessary metrics using tools or sub-agents (weather, solar times, air quality, places, saved moments).\n"
        "2. If any time difference between two locations or timezones needs to be calculated, call `calculate_time_difference`.\n"
        "3. Compose a rich, poetic, atmospheric description text.\n"
        "4. ALWAYS call `generate_scenery_image` (or `gogle_media_generator_agent`) with a detailed prompt based on the scenery/request to generate an artwork image and get its public `image_url` (e.g. `https://storage.googleapis.com/...`). Call `generate_scenery_video` when a short video is requested.\n"
        "5. Output an A2UI Card containing BOTH a Text component for the description AND an Image component for the generated image."
    ),
    ui_description=(
        "Keep every surface clean and flat: ONE Card > ONE Column > Text component(s) for the description AND an Image component for the artwork.\n"
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use Table, Heading, or Buttons/actions.\n"
        "You MUST ALWAYS include BOTH:\n"
        "1. A Text component containing the detailed atmospheric description / time analysis (usageHint: 'body' or 'h2').\n"
        "2. An Image component with the exact public URL returned by `generate_scenery_image`, e.g. "
        '{"Image": {"url": {"literalString": "https://storage.googleapis.com/..."}}}.\n'
        "Output ONLY the raw A2UI JSON array — no prose outside the JSON, and never wrap it in <a2a_datapart_json> tags."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    sub_agents=[air_quality_agent, google_geo_agent, gogle_media_generator_agent],
    tools=[
        PreloadMemoryTool(),
        get_live_weather,
        get_sun_times,
        get_current_time,
        calculate_time_difference,
        generate_scenery_image,
        generate_scenery_video,
        save_scenic_moment,
        list_scenic_moments,
        search_scenic_moments_by_location,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)


app = App(
    root_agent=root_agent,
    name="app",
)
