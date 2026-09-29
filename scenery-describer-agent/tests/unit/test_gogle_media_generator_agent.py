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

import urllib.request
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.adk.tools import ToolContext

from app.sub_agents.gogle_media_generator_agent import (
    generate_scenery_image,
    generate_scenery_video,
    gogle_media_generator_agent,
)


@pytest.mark.asyncio
async def test_generate_scenery_image_end_to_end():
    """Tests image generation, artifact saving, and public GCS upload."""
    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.save_artifact = AsyncMock(return_value=1)

    prompt = "A breathtaking sunset over misty mountains in blue hour lighting"
    res = await generate_scenery_image(prompt=prompt, tool_context=mock_tool_context)

    assert res["status"] == "success"
    assert "image_url" in res
    assert res["image_url"].startswith("https://storage.googleapis.com/scenery-describer-images-31b0418c/")

    # Verify save_artifact was called
    mock_tool_context.save_artifact.assert_called_once()
    call_args = mock_tool_context.save_artifact.call_args
    assert "scenery_" in call_args.kwargs["filename"]
    assert call_args.kwargs["artifact"].inline_data is not None

    # Verify public URL is reachable via HTTP HEAD
    req = urllib.request.Request(res["image_url"], method="HEAD")
    with urllib.request.urlopen(req) as http_res:
        assert http_res.status == 200
        assert "image/" in http_res.headers.get("Content-Type", "")


@pytest.mark.asyncio
async def test_generate_scenery_video_end_to_end():
    """Tests video generation with gemini-omni-flash-preview, artifact saving, and public GCS upload."""
    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.save_artifact = AsyncMock(return_value=1)

    prompt = "Ocean waves crashing on rocky cliffs at sunset with cinematic lighting"
    res = await generate_scenery_video(prompt=prompt, tool_context=mock_tool_context)

    assert res["status"] == "success"
    assert "video_url" in res
    assert res["video_url"].startswith("https://storage.googleapis.com/scenery-describer-images-31b0418c/")

    # Verify save_artifact was called
    mock_tool_context.save_artifact.assert_called_once()
    call_args = mock_tool_context.save_artifact.call_args
    assert "scenery_video_" in call_args.kwargs["filename"]
    assert call_args.kwargs["artifact"].inline_data is not None

    # Verify public URL is reachable via HTTP HEAD
    req = urllib.request.Request(res["video_url"], method="HEAD")
    with urllib.request.urlopen(req) as http_res:
        assert http_res.status == 200
        assert "video/" in http_res.headers.get("Content-Type", "")


def test_agent_structure():
    """Verifies gogle_media_generator_agent declaration and tool binding."""
    assert gogle_media_generator_agent.name == "gogle_media_generator_agent"
    tool_names = [t.__name__ for t in gogle_media_generator_agent.tools]
    assert "generate_scenery_image" in tool_names
    assert "generate_scenery_video" in tool_names

