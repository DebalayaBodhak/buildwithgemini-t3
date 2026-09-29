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

from app.sub_agents.gogle_media_generator_agent.tools import (
    generate_scenery_image,
    generate_scenery_video,
)

gogle_media_generator_agent = Agent(
    name="gogle_media_generator_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Scenery Media & Image/Video Generator Specialist Agent. Your primary goal is to take a scenery description "
        "and generate a breathtaking, highly artistic fine-art visual masterpiece or short video. "
        "Call `generate_scenery_image` for image generation, or `generate_scenery_video` when a short video is requested."
    ),
    description=(
        "Specialist agent that receives a scenery description and uses the gemini-3.1-flash-lite-image or gemini-omni-flash-preview model "
        "to create artistic visual artwork or short scenery videos, save ADK artifacts, and upload to Cloud Storage."
    ),
    tools=[generate_scenery_image, generate_scenery_video],
)
