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

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


@pytest.mark.asyncio
async def test_root_agent_description_and_image_flow():
    """Verifies root_agent generates description first, generates image via subagent, and outputs both."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="app")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="app")

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Generate a scenery description and visual artwork for Kyoto, Japan during golden hour sunset.")]
    )

    events = []
    async for event in runner.run_async(
        new_message=message,
        user_id="test_user",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    ):
        events.append(event)

    full_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_text += part.text + "\n"

    # Verify both description elements and public GCS image URL are present in output
    assert "https://storage.googleapis.com/scenery-describer-images-31b0418c/" in full_text
    assert len(full_text.strip()) > 100
