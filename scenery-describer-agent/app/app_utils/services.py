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

"""Process-wide ADK session/artifact services shared by every serving surface.

Registered under ``shared://`` so the ADK web routes, the A2A path, and the
reasoning_engine adapter share one instance: a session created on any surface
is visible to the others.
"""

from __future__ import annotations

import functools
import json
import os

from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.cli.service_registry import get_service_registry
from google.adk.cli.utils.service_factory import (
    create_memory_service_from_options,
    create_session_service_from_options,
)

SESSION_SERVICE_URI = "shared://session"
ARTIFACT_SERVICE_URI = "shared://artifact"
MEMORY_SERVICE_URI = "shared://memory"

_AGENT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def _get_memory_bank_info() -> tuple[str, str | None]:
    metadata_path = os.path.join(_AGENT_DIR, "deployment_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
                if runtime_id := metadata.get("remote_agent_runtime_id"):
                    parts = runtime_id.split("/")
                    if len(parts) >= 6 and parts[2] == "locations":
                        return parts[5], parts[3]
                    return runtime_id.split("/")[-1], None
        except Exception:
            pass
    return "9105403235287433216", "us-east4"


def _resolve_location(loc: str | None) -> str:
    if not loc or loc == "global":
        return "us-east4"
    return loc


@functools.cache
def get_session_service():
    """Process-wide session service shared across every serving surface."""
    if uri := os.environ.get("SESSION_SERVICE_URI"):
        return create_session_service_from_options(
            base_dir=_AGENT_DIR, session_service_uri=uri
        )
    if agent_engine_id := os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID"):
        from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService

        location = _resolve_location(
            os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_LOCATION")
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
        )
        return VertexAiSessionService(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=location,
            agent_engine_id=agent_engine_id,
        )
    from google.adk.sessions.in_memory_session_service import InMemorySessionService

    return InMemorySessionService()


@functools.cache
def get_memory_service():
    """Process-wide memory service shared across every serving surface."""
    if uri := os.environ.get("MEMORY_SERVICE_URI"):
        return create_memory_service_from_options(
            base_dir=_AGENT_DIR, memory_service_uri=uri
        )
    if agent_engine_id := os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID"):
        from google.adk.memory import VertexAiMemoryBankService

        location = _resolve_location(
            os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_LOCATION")
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
        )
        return VertexAiMemoryBankService(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=location,
            agent_engine_id=agent_engine_id,
        )
    from google.adk.memory import VertexAiMemoryBankService

    memory_bank_id, meta_location = _get_memory_bank_info()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        try:
            import google.auth
            _, project = google.auth.default()
        except Exception:
            project = "qwiklabs-gcp-01-f6dc147b3e3d"
    location = _resolve_location(
        os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_LOCATION")
        or meta_location
        or os.environ.get("GOOGLE_CLOUD_LOCATION")
    )
    return VertexAiMemoryBankService(
        project=project,
        location=location,
        agent_engine_id=memory_bank_id,
    )


@functools.cache
def get_artifact_service():
    """Process-wide artifact service: GCS when a bucket is set, else in-memory."""
    if bucket := os.environ.get("LOGS_BUCKET_NAME"):
        return GcsArtifactService(bucket_name=bucket)
    return InMemoryArtifactService()


_registry = get_service_registry()
_registry.register_session_service("shared", lambda uri, **kw: get_session_service())
_registry.register_artifact_service("shared", lambda uri, **kw: get_artifact_service())
_registry.register_memory_service("shared", lambda uri, **kw: get_memory_service())
