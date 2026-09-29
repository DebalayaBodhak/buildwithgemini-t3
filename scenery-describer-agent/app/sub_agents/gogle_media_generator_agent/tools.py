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

import uuid

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded project ID and public Cloud Storage bucket as required
PROJECT_ID = "qwiklabs-gcp-01-f6dc147b3e3d"
BUCKET_NAME = "scenery-describer-images-31b0418c"


async def generate_scenery_image(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates visual artwork or a photograph capturing scenery, weather, lighting, and landscape details.

    Args:
        prompt: Detailed description of the scenery, lighting, weather conditions, time of day, and aesthetic style.

    Returns:
        A dictionary containing the generation status, public Cloud Storage image URL, and artifact filename.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    artistic_prompt = (
        f"A magnificent fine-art masterpiece painting, highly artistic, painterly, and evocative visual artwork. "
        f"Vivid color palette, dramatic atmospheric lighting, aesthetic composition, rich texture. "
        f"Scenery: {prompt}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=artistic_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate image via gemini-3.1-flash-lite-image: {e!s}",
        }

    image_bytes = None
    mime_type = "image/jpeg"

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break
                if image_bytes:
                    break

    if not image_bytes:
        return {
            "status": "error",
            "message": "No image data was returned by the gemini-3.1-flash-lite-image model.",
        }

    ext = "png" if "png" in mime_type.lower() else "jpg"
    filename = f"scenery_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact for ADK / Playground panel
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    try:
        await tool_context.save_artifact(filename=filename, artifact=image_part)
    except Exception as e:
        # Log error but proceed to Cloud Storage upload
        print(f"Warning: tool_context.save_artifact failed: {e}")

    # 2. Upload image bytes directly to public Cloud Storage bucket
    try:
        gcs_client = storage.Client(project=PROJECT_ID)
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        return {
            "status": "error",
            "message": f"Saved artifact, but failed to upload image to Cloud Storage bucket '{BUCKET_NAME}': {e!s}",
            "artifact_filename": filename,
        }

    return {
        "status": "success",
        "message": "Successfully generated scenery artwork and uploaded to Cloud Storage bucket.",
        "image_url": public_url,
        "artifact_filename": filename,
    }


async def generate_scenery_video(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates a short video depicting an atmospheric scenery moment, weather, landscape, or cinematic view.

    Args:
        prompt: Detailed description of the scenery, motion, atmospheric lighting, weather conditions, or landscape.

    Returns:
        A dictionary containing the generation status, public Cloud Storage video URL, and artifact filename.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    artistic_prompt = (
        f"A breathtaking short video capturing scenic landscape, atmospheric motion, and dramatic lighting. "
        f"Scenery: {prompt}"
    )

    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=[{"type": "text", "text": artistic_prompt}],
        )
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate video via gemini-omni-flash-preview: {e!s}",
        }

    video_bytes = None
    mime_type = "video/mp4"

    if hasattr(interaction, "steps") and interaction.steps:
        for step in interaction.steps:
            if getattr(step, "type", "") == "model_output" and getattr(step, "content", None):
                for item in step.content:
                    item_type = getattr(item, "type", "")
                    item_mime = getattr(item, "mime_type", "")
                    if item_type == "video" or "video" in item_mime.lower():
                        data = getattr(item, "data", None)
                        if data:
                            if isinstance(data, str):
                                import base64
                                video_bytes = base64.b64decode(data)
                            elif isinstance(data, bytes):
                                video_bytes = data
                            if item_mime:
                                mime_type = item_mime
                            break
                if video_bytes:
                    break

    if not video_bytes:
        return {
            "status": "error",
            "message": "No video data was returned by the gemini-omni-flash-preview model.",
        }

    ext = "mp4"
    filename = f"scenery_video_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact for ADK / Playground panel
    video_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    try:
        await tool_context.save_artifact(filename=filename, artifact=video_part)
    except Exception as e:
        print(f"Warning: tool_context.save_artifact failed for video: {e}")

    # 2. Upload video bytes directly to public Cloud Storage bucket
    try:
        gcs_client = storage.Client(project=PROJECT_ID)
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        return {
            "status": "error",
            "message": f"Saved artifact, but failed to upload video to Cloud Storage bucket '{BUCKET_NAME}': {e!s}",
            "artifact_filename": filename,
        }

    return {
        "status": "success",
        "message": "Successfully generated scenery video and uploaded to Cloud Storage bucket.",
        "video_url": public_url,
        "artifact_filename": filename,
    }

