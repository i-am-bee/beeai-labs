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

class Mermaid:
    # kind: sequenceDiagram or flowchart
    # orientation: TD (top down), 
    #              RL (right left) 
    #              when kind is flowchart    
    def __init__(self, workflow, kind="sequenceDiagram", orientation="TD"):
        self.workflow = workflow
        self.kind = kind
        self.orientation = orientation
    
    # generates a mermaid markdown representation of the workflow
    def to_markdown(self) -> str:
        sb, markdown = "", ""
        if self.kind == "sequenceDiagram":
            markdown = self.__to_sequenceDiagram(sb)
        elif self.kind == "flowchart":
            markdown = self.__to_flowchart(sb, self.orientation)
        else:
            raise RuntimeError(f"Invalid Mermaid kind: {kind}")
        return markdown

    # private methods
    
    # returns a markdown of the workflow as a mermaid sequence diagram
    # 
    # sequenceDiagram
    # participant agent1
    # participant agent2
    #
    # agent1->>agent2: step1
    # agent2->>agent3: step2
    # agent2-->>agent1: step3
    # agent1->>agent3: step4
    #
    # See mermaid sequence diagram documentation: 
    # https://mermaid.js.org/syntax/sequenceDiagram.html
    def __to_sequenceDiagram(self, sb):
        sb += "sequenceDiagram\n"
        for agent in self.workflow['spec']['template']['agents']:
            agent = agent.replace("-", "_")
            sb += f"participant {agent}\n"
        steps, i = self.workflow['spec']['template']['steps'], 0
        for step in steps:
            if step.get('agent'):
                agentL = step.get('agent').replace("-", "_")
            agentR = None
            # figure out agentR
            if i < (len(steps) - 1) and steps[i+1].get('agent'):
                agentR = steps[i+1].get('agent').replace("-", "_")
            if agentR:
                sb += f"{agentL}->>{agentR}: {step['name']}\n"
            else:
                sb += f"{agentL}->>{agentL}: {step['name']}\n"
            # if step has condition then add additional links
            if step.get('condition'):
                for condition in step['condition']:
                    condition_expr = ''
                    if condition.get('case'):
                        condition_expr, do_expr = condition['case'], condition['do']
                        if condition.get('default'):
                            condition_expr = 'default'
                            do_expr = condition['default']
                        sb += f"{agentL}->>{agentR}: {do_expr} {condition_expr}\n"
                    elif condition.get('if'):
                        if_expr, then_expr, else_expr = condition['if'], condition['then'], ''
                        if condition.get('else'):
                            else_expr = condition['else']
                        sb += f"{agentL}->>{agentR}: {if_expr}\n"
                        sb += f"alt if True\n"
                        sb += f"  {agentL}->>{agentR}: {then_expr}\n"
                        if condition.get('else'):
                            sb += f"else is False\n"
                            sb += f"  {agentR}->>{agentL}: {else_expr}\n"
                        sb += f"end\n"
            i = i + 1
        return sb

    # returns a markdown of the workflow as a mermaid sequence diagram
    # 
    # flowchart LR
    # agemt1-- step1 -->agent2
    # agemt2-- step2 -->agent3
    # agemt3-- step3 -->agent3
    #
    # See mermaid sequence diagram documentation: 
    # https://mermaid.js.org/syntax/flowchart.html
    def __to_flowchart(self, sb, orientation):
        sb += f"flowchart {orientation}\n"
        steps, i = self.workflow['spec']['template']['steps'], 0        
        for step in steps:
            agentL = step.get('agent')
            agentR = None
            if i < (len(steps) - 1):
                agentR = steps[i+1].get('agent')
            if agentR != None:
                sb += f"{agentL}-- {step['name']} -->{agentR}\n"
            else:
                sb += f"{agentL}-- {step['name']} -->{agentL}\n"
            # if step has condition then add additional links
            if step.get('condition'):
                for condition in step['condition']:
                    # condition_expr = ''
                    # if condition.get('case'):
                    #     condition_expr do_expr = condition['case'], condition['do']
                    #     if condition['default']:
                    #         condition_expr = 'default'
                    #         do_expr = condition['default']
                    #     sb += f"{agentL}->>{agentR}: {do_expr} {condition_expr}\n"
                    if condition.get('if'):
                        if_expr = f"{condition['if']}"
                        then_expr = condition['then']
                        else_expr = condition['else']
                        step_name = step['name']
                        sb += f"{step_name} --> Condition{{\"{if_expr}\"}}\n"
                        sb += f"  Condition -- Yes --> {then_expr}\n"
                        sb += f"  Condition -- No --> {else_expr}\n"
            i = i + 1
        return sb
        
    
