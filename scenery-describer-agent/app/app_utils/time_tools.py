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
from zoneinfo import ZoneInfo

from app.app_utils.geocoding import geocode_location


def calculate_time_difference(location1: str, location2: str) -> str:
    """Calculates the time difference (in hours and minutes) between two cities or locations.

    Args:
        location1: The first location name (e.g. "Tokyo", "London", "New York").
        location2: The second location name (e.g. "Paris", "San Francisco", "Sydney").

    Returns:
        A formatted string detailing current local times in both locations and the exact time difference.
    """
    geo1 = geocode_location(location1)
    if not geo1 or "timezone" not in geo1:
        return f"Could not determine timezone or location info for: '{location1}'."

    geo2 = geocode_location(location2)
    if not geo2 or "timezone" not in geo2:
        return f"Could not determine timezone or location info for: '{location2}'."

    try:
        tz1_name = geo1["timezone"]
        tz2_name = geo2["timezone"]
        tz1 = ZoneInfo(tz1_name)
        tz2 = ZoneInfo(tz2_name)

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now1 = now_utc.astimezone(tz1)
        now2 = now_utc.astimezone(tz2)

        offset1_minutes = now1.utcoffset().total_seconds() / 60
        offset2_minutes = now2.utcoffset().total_seconds() / 60

        diff_minutes = offset1_minutes - offset2_minutes
        abs_diff_minutes = abs(diff_minutes)
        diff_hours = abs_diff_minutes / 60

        hours_part = int(diff_hours)
        mins_part = int(round((diff_hours - hours_part) * 60))

        if mins_part == 60:
            hours_part += 1
            mins_part = 0

        time_diff_str = (
            f"{hours_part} hour(s)"
            if mins_part == 0
            else f"{hours_part} hour(s) and {mins_part} minute(s)"
        )

        name1 = geo1.get("name", location1)
        country1 = geo1.get("country", "")
        loc1_label = f"{name1}, {country1}".strip(", ")

        name2 = geo2.get("name", location2)
        country2 = geo2.get("country", "")
        loc2_label = f"{name2}, {country2}".strip(", ")

        if diff_minutes > 0:
            rel_str = f"{loc1_label} is {time_diff_str} ahead of {loc2_label}."
        elif diff_minutes < 0:
            rel_str = f"{loc1_label} is {time_diff_str} behind {loc2_label}."
        else:
            rel_str = f"{loc1_label} and {loc2_label} have the same time offset."

        return (
            f"Time Difference Analysis:\n"
            f"- Current time in {loc1_label} ({tz1_name}): {now1.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"- Current time in {loc2_label} ({tz2_name}): {now2.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"- Time Difference: {rel_str}"
        )
    except Exception as e:
        return f"Error calculating time difference between '{location1}' and '{location2}': {e!s}"
