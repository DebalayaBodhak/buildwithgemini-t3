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

"""Seed script to populate initial scenic moments into Firestore.

Important: Project ID is hardcoded as a string for Agent Platform compatibility.
"""

import datetime
from google.cloud import firestore

# Hardcode project ID string as required
PROJECT_ID = "qwiklabs-gcp-01-f6dc147b3e3d"
COLLECTION_NAME = "scenic_moments"

SEED_MOMENTS = [
    {
        "title": "Golden Gate Fog & Sunset",
        "location": "San Francisco, CA",
        "weather": "60°F, Foggy & Breezy",
        "time_of_day": "Sunset",
        "description": "Low-hanging mist rolls over the crimson towers of the Golden Gate Bridge as golden hour sunlight pierces through the marine layer, casting a warm ethereal glow over the Pacific waves.",
        "style_tags": ["cinematic", "dramatic", "cozy"],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "title": "Kyoto Bamboo Grove in Autumn Rain",
        "location": "Kyoto, Japan",
        "weather": "58°F, Gentle Rain",
        "time_of_day": "Morning",
        "description": "Soft rain whispers through tall emerald bamboo stalks in Arashiyama. Damp stone pathways reflect amber lanterns, and autumn foliage creates a peaceful, serene atmosphere.",
        "style_tags": ["peaceful", "moody", "serene"],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "title": "Yosemite Valley Morning Mist",
        "location": "Yosemite National Park, CA",
        "weather": "45°F, Crisp & Clear",
        "time_of_day": "Dawn",
        "description": "First light hits Half Dome as river mist floats above dew-covered granite meadows. The air is sharp and fragrant with pine, and the cliff faces glow in soft rose-pink hue.",
        "style_tags": ["majestic", "dramatic", "nature"],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "title": "Santorini Sunset Over Caldera",
        "location": "Santorini, Greece",
        "weather": "74°F, Clear & Calm",
        "time_of_day": "Golden Hour",
        "description": "Whitewashed cliffside villas and blue domes reflect rich magenta and violet hues as the Mediterranean sun dips beneath the sea horizon.",
        "style_tags": ["vibrant", "warm", "romantic"],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]


def seed_firestore():
    """Seeds initial scenic moments into the Firestore collection."""
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)
    print(f"Seeding '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")

    for item in SEED_MOMENTS:
        doc_ref = collection.document()
        doc_ref.set(item)
        print(f"  Added document ID: {doc_ref.id} | Title: {item['title']}")

    print(f"Successfully seeded {len(SEED_MOMENTS)} items into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed_firestore()
