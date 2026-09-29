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

"""Firestore backend tools for Scenery Describer Agent.

Collection: scenic_moments
"""

import datetime

from google.cloud import firestore

# Hardcode project ID string as required for Agent Platform deployment compatibility
PROJECT_ID = "qwiklabs-gcp-01-f6dc147b3e3d"
COLLECTION_NAME = "scenic_moments"


def get_firestore_client() -> firestore.Client:
    """Gets a Firestore client configured with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def save_scenic_moment(
    title: str,
    location: str,
    weather: str,
    time_of_day: str,
    description: str,
    style_tags: str = "cinematic",
) -> str:
    """Saves a new scenic moment description to the Firestore catalog.

    Args:
        title: Short descriptive title for the scenic moment (e.g. 'Golden Gate Fog at Sunset').
        location: City or landmark location (e.g. 'San Francisco, CA').
        weather: Weather conditions (e.g. '60°F, Foggy').
        time_of_day: Time of day or lighting period (e.g. 'Sunset', 'Golden Hour', 'Dawn').
        description: Rich, evocative atmospheric description of the scenery.
        style_tags: Comma-separated list of style tags (e.g. 'cinematic, cozy, dramatic').

    Returns:
        Confirmation message with the created moment's document ID.
    """
    db = get_firestore_client()
    tags_list = [t.strip() for t in style_tags.split(",") if t.strip()]

    moment_data = {
        "title": title,
        "location": location,
        "weather": weather,
        "time_of_day": time_of_day,
        "description": description,
        "style_tags": tags_list,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set(moment_data)
    return f"Successfully saved scenic moment '{title}' with ID: {doc_ref.id}"


def list_scenic_moments(limit: int = 10) -> str:
    """Lists saved scenic moments from the Firestore catalog.

    Args:
        limit: Maximum number of moments to retrieve (default: 10).

    Returns:
        Formatted string listing saved scenic moments.
    """
    db = get_firestore_client()
    docs = (
        db.collection(COLLECTION_NAME)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    moments = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        moments.append(data)

    if not moments:
        return "No saved scenic moments found in Firestore."

    result = [f"Found {len(moments)} saved scenic moment(s):"]
    for m in moments:
        tags_str = ", ".join(m.get("style_tags", []))
        result.append(
            f"- [{m.get('id')}] {m.get('title')} ({m.get('location')} | {m.get('weather')} | {m.get('time_of_day')})\n"
            f"  Description: {m.get('description')}\n"
            f"  Tags: {tags_str}"
        )
    return "\n\n".join(result)


def search_scenic_moments_by_location(location: str) -> str:
    """Searches for saved scenic moments in Firestore by location name.

    Args:
        location: Location name or substring to search for (e.g. 'San Francisco', 'Kyoto').

    Returns:
        Formatted string of matching scenic moments.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()

    matching = []
    loc_lower = location.lower()
    for doc in docs:
        data = doc.to_dict()
        doc_loc = data.get("location", "").lower()
        doc_title = data.get("title", "").lower()
        if loc_lower in doc_loc or loc_lower in doc_title:
            data["id"] = doc.id
            matching.append(data)

    if not matching:
        return f"No scenic moments found matching location '{location}'."

    result = [f"Found {len(matching)} scenic moment(s) for '{location}':"]
    for m in matching:
        tags_str = ", ".join(m.get("style_tags", []))
        result.append(
            f"- [{m.get('id')}] {m.get('title')} ({m.get('location')} | {m.get('weather')} | {m.get('time_of_day')})\n"
            f"  Description: {m.get('description')}\n"
            f"  Tags: {tags_str}"
        )
    return "\n\n".join(result)
