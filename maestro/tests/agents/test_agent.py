#!/usr/bin/env python3

# Copyright © 2025 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from src.agents.agent import Agent

class TestAgentEmojis(unittest.TestCase):

    def _create_agent(self, framework: str) -> Agent:
        agent_dict = {
            'metadata': {'name': f'{framework}_test_agent'},
            'spec': {
                'framework': framework,
                'model': 'test_model',          # Placeholder value
                'description': 'test desc',     # Placeholder value
                'instructions': 'test instr',   # Placeholder value
            }
        }
        return Agent(agent_dict)

    def test_emoji_outputs(self):
        test_cases = {
            # Known frameworks from Agent.EMOJIS
            'beeai': '🐝',
            'crewai': '👥',
            'openai': '🔓',
            'mock': '🤖',
            'remote': '💸',
            # Unknown framework should return the default
            'some_new_framework': '⚙️',
            'another_unknown': '⚙️',
            # Edge case: empty string framework name
            '': '⚙️',
        }

        for framework, expected_emoji in test_cases.items():
            with self.subTest(framework=framework):
                agent = self._create_agent(framework)
                actual_emoji = agent.emoji()

                self.assertEqual(actual_emoji, expected_emoji,
                                f"Emoji for framework '{framework}' should be '{expected_emoji}' but got '{actual_emoji}'")

if __name__ == '__main__':
    unittest.main()