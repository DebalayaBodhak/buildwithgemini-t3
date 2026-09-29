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
import os
import urllib.parse
import urllib.request

from app.app_utils.geocoding import geocode_location


def get_air_quality(location: str) -> str:
    """Fetches real-time air quality index (AQI), particulate metrics (PM2.5, PM10), UV index, and atmospheric clarity for a location.

    Args:
        location: City or place name (e.g. "San Francisco", "Kyoto", "Paris").

    Returns:
        A string describing air quality conditions, US AQI rating, particulate levels, and UV index.
    """
    geo = geocode_location(location)
    if not geo:
        return f"Could not find coordinates for location: '{location}'."

    lat, lon = geo["latitude"], geo["longitude"]
    name = geo.get("name", location)
    country = geo.get("country", "")

    api_key = os.environ.get("AIR_QUALITY_API_KEY") or os.environ.get("OPEN_METEO_API_KEY")
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,european_aqi,pm10,pm2_5,uv_index"
    if api_key:
        url += f"&apikey={urllib.parse.quote(api_key)}"

    req = urllib.request.Request(url, headers={"User-Agent": "SceneryAgent/1.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            curr = data.get("current", {})
            us_aqi = curr.get("us_aqi", "N/A")
            pm25 = curr.get("pm2_5", "N/A")
            pm10 = curr.get("pm10", "N/A")
            uv = curr.get("uv_index", "N/A")

            if isinstance(us_aqi, (int, float)):
                if us_aqi <= 50:
                    clarity = "Good (Clear atmospheric visibility)"
                elif us_aqi <= 100:
                    clarity = "Moderate (Acceptable air clarity)"
                elif us_aqi <= 150:
                    clarity = "Unhealthy for Sensitive Groups (Hazy atmospheric conditions)"
                else:
                    clarity = "Unhealthy / Severe Haze (Significantly reduced visibility)"
            else:
                clarity = "Unknown atmospheric clarity"

            return (
                f"Air Quality & Atmospheric Data for {name}, {country}:\n"
                f"- US AQI: {us_aqi} ({clarity})\n"
                f"- PM2.5: {pm25} µg/m³\n"
                f"- PM10: {pm10} µg/m³\n"
                f"- UV Index: {uv}"
            )
    except Exception as e:
        return f"Error fetching air quality data for {location}: {e!s}"
