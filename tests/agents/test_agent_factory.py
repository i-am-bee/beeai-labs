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

import os, unittest

from typing import Callable

from unittest import TestCase

from src.agents.agent_factory import AgentFramework, AgentFactory

class TestAgentFramework(TestCase):    
    def test_frameworks(self):        
        self.assertTrue(AgentFramework.BEEAI is not None)
        self.assertTrue(AgentFramework.CREWAI is not None)
        self.assertTrue(AgentFramework.OPENAI is not None)
        self.assertTrue(AgentFramework.MOCK is not None)
        self.assertTrue(AgentFramework.REMOTE is not None)


class TestAgentFactory(TestCase):    
    def test_create_agents(self):
        self.assertTrue(isinstance(AgentFactory.create_agent(AgentFramework.BEEAI), Callable))
        self.assertTrue(isinstance(AgentFactory.create_agent(AgentFramework.CREWAI), Callable))
        self.assertTrue(isinstance(AgentFactory.create_agent(AgentFramework.OPENAI), Callable))
        self.assertTrue(isinstance(AgentFactory.create_agent(AgentFramework.MOCK), Callable))
        self.assertTrue(isinstance(AgentFactory.create_agent(AgentFramework.REMOTE), Callable))

    def test_get_factory(self):
        self.assertTrue(AgentFactory.get_factory(AgentFramework.BEEAI) is not None)
        self.assertTrue(AgentFactory.get_factory(AgentFramework.CREWAI) is not None)
        self.assertTrue(AgentFactory.get_factory(AgentFramework.OPENAI) is not None)
        self.assertTrue(AgentFactory.get_factory(AgentFramework.MOCK) is not None)
        self.assertTrue(AgentFactory.get_factory(AgentFramework.REMOTE) is not None)

if __name__ == '__main__':
    unittest.main()