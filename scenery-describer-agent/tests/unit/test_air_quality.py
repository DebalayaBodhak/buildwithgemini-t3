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

from app.agent import root_agent
from app.sub_agents.air_quality_agent import air_quality_agent, get_air_quality


def test_get_air_quality_real_data() -> None:
    res = get_air_quality("Kyoto")
    assert "Air Quality" in res
    assert "US AQI" in res


def test_sub_agent_configured_on_root() -> None:
    assert len(root_agent.sub_agents) >= 1
    sub_names = [s.name for s in root_agent.sub_agents]
    assert "air_quality_agent" in sub_names
    assert air_quality_agent in root_agent.sub_agents

