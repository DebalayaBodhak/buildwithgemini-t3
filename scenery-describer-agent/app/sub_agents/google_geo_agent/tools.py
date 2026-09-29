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


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic coordinates using Google Maps Geocoding API.

    Args:
        address: The street address or place name to geocode (e.g. "1600 Amphitheatre Pkwy, Mountain View, CA").

    Returns:
        A formatted string with the key fields: address, formatted address, and coordinates (latitude, longitude).
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        # Fallback to free geocoding helper if key is not configured yet
        geo = geocode_location(address)
        if geo:
            return (
                f"Geocoding result for '{address}':\n"
                f"- Name/Address: {geo.get('name', address)}, {geo.get('country', '')}\n"
                f"- Location: Latitude {geo.get('latitude')}, Longitude {geo.get('longitude')}"
            )
        return f"GOOGLE_MAPS_API_KEY is not configured and fallback geocoding failed for '{address}'."

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={urllib.parse.quote(api_key)}"
    req = urllib.request.Request(url, headers={"User-Agent": "GoogleGeoAgent/1.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            status = data.get("status")
            if status == "OK" and data.get("results"):
                first = data["results"][0]
                formatted_address = first.get("formatted_address", address)
                loc = first.get("geometry", {}).get("location", {})
                lat, lng = loc.get("lat"), loc.get("lng")
                return (
                    f"Geocoding result for '{address}':\n"
                    f"- Name/Address: {formatted_address}\n"
                    f"- Location: Latitude {lat}, Longitude {lng}"
                )
            return f"Geocoding API returned status '{status}' for address '{address}'."
    except Exception as e:
        return f"Error calling Google Maps Geocoding API for '{address}': {e!s}"


def find_nearby_places(location: str, place_type: str = "tourist_attraction", radius: int = 5000) -> str:
    """Finds nearby places of a given type around a location using Google Places API (New).

    Args:
        location: City, address, or location name (e.g. "Kyoto", "San Francisco").
        place_type: Type of place to search for (e.g. "tourist_attraction", "park", "restaurant", "museum").
        radius: Search radius in meters (default 5000).

    Returns:
        A string listing nearby places with key fields: name, address, and location coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")

    # Resolve coordinates
    geo = geocode_location(location)
    if not geo:
        return f"Could not determine coordinates for location '{location}'."

    lat, lng = geo.get("latitude"), geo.get("longitude")

    if not api_key or api_key == "PASTE_KEY_HERE":
        return (
            f"GOOGLE_MAPS_API_KEY environment variable is not configured. "
            f"Coordinates resolved for '{location}': Lat {lat}, Lng {lng}. Please set a valid GOOGLE_MAPS_API_KEY in .env."
        )

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng,
                },
                "radius": radius,
            }
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            places = data.get("places", [])
            if not places:
                return f"No nearby places of type '{place_type}' found around {location}."

            results = [f"Nearby '{place_type}' places around {location}:"]
            for idx, p in enumerate(places, 1):
                name = p.get("displayName", {}).get("text", "N/A")
                address = p.get("formattedAddress", "N/A")
                loc = p.get("location", {})
                plat, plng = loc.get("latitude", "N/A"), loc.get("longitude", "N/A")
                results.append(
                    f"{idx}. Name: {name}\n"
                    f"   Address: {address}\n"
                    f"   Location: Latitude {plat}, Longitude {plng}"
                )
            return "\n".join(results)
    except Exception as e:
        return f"Error calling Places API (New) for '{location}': {e!s}"
