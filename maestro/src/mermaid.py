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
    
    def __fix_agent_name(self, name):
        return name.replace("-", "_")

    def __agent_for_step(self, step_name):
        for step in self.workflow['spec']['template']['steps']:
            if step['name'] == step_name:
                return step['agent']
        return None

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
    def __to_sequenceDiagram(self, sb) -> str:
        sb += "sequenceDiagram\n"
        for agent in self.workflow['spec']['template']['agents']:
            agent = self.__fix_agent_name(agent)
            sb += f"participant {agent}\n"
        agentL = None
        steps, i = self.workflow['spec']['template']['steps'], 0
        for step in steps:
            if step.get('agent'):
                agentL = self.__fix_agent_name(step.get('agent'))
            agentR = None
            # figure out agentR
            if i < (len(steps) - 1) and steps[i+1].get('agent'):
                agentR = self.__fix_agent_name(steps[i+1].get('agent'))
            if agentR:
                sb += f"{agentL}->>{agentR}: {step['name']}\n"
            else:
                sb += f"{agentL}->>{agentL}: {step['name']}\n"
            # if step has condition then add additional links
            if step.get('condition'):
                for condition in step['condition']:
                    sb += self.__to_sequenceDiagram_condition(agentL, agentR, condition)
            # if step has parallel execution
            if step.get('parallel'):
                sb += self.__to_sequenceDiagram_parallel(agentL, step)
            # if step has loop
            if step.get('loop'):
                sb += self.__to_sequenceDiagram_loop(agentL, step['loop'])
            i = i + 1
        # if workflow has global on event handling
        if self.workflow['spec']['template'].get('event'):
            sb += self.__to_sequenceDiagram_event(self.workflow['spec']['template']['event'])
        # if workflow has global exception then add at the end
        if self.workflow['spec']['template'].get('exception'):
            sb += self.__to_sequenceDiagram_exception(steps, self.workflow['spec']['template']['exception'])
        return sb

    # convert event to mermaid sequenceDiagram
    def __to_sequenceDiagram_event(self, event):
        name = event['name']
        cron = event['cron']
        exit = event['exit']
        sb = f"alt cron \"{cron}\"\n"
        if event.get('steps'):
            for step in event['steps']:
                sb += f"  cron->>{self.__agent_for_step(step)}: {step}\n"
        else:
            agent = event['agent']
            sb += f"  cron->>{agent}: {name}\n"
        sb += "else\n"
        sb += f"  cron->>exit: {exit}\n"
        sb += 'end\n'
        return sb

    # convert parallel to mermaid sequenceDiagram
    def __to_sequenceDiagram_parallel(self, agentL, parallelStep):
        i, sb = 0, 'par\n'
        agents = parallelStep['parallel']
        for agent in agents:
            agentR = self.__fix_agent_name(agent)
            sb += f"  {agentL}->>{agentR}: {parallelStep['name']}\n"
            if i < len(agents):
                sb += 'and\n'
            i += 1
        sb += 'end\n'
        return sb

    # convert exception to mermaid sequenceDiagram
    def __to_sequenceDiagram_exception(self, steps, exception):
        i, sb = 0, 'alt exception\n'
        for step in steps:
            if step.get('agent'):
                agentL = self.__fix_agent_name(step.get('agent'))
                sb += f"  {agentL}->>{exception['agent']}: {exception['name']}\n"
            i += 1
        sb += 'end'
        return sb

    # convert loop to mermaid sequenceDiagram
    def __to_sequenceDiagram_loop(self, agentL, loopStep):
        i, sb = 0, ''
        agentR = self.__fix_agent_name(loopStep['agent'])
        loop_name, loop_expr = 'loop', 'True'
        if loopStep.get('until'):
            loop_name = 'until'
            loop_expr = loopStep['until']
        sb += f"loop {loop_expr}\n"
        sb += f"  {agentL}-->{agentR}: {loop_name}\n"
        sb += 'end\n'
        return sb

    # convert condition section to sequenceDiagram mermaid diagram
    def __to_sequenceDiagram_condition(self, agentL, agentR, condition) -> str:            
        sb, condition_expr = '', ''
        # generate the case / do / default
        if condition.get('case'):
            condition_expr, do_expr = condition['case'], condition['do']
            if condition.get('default'):
                condition_expr = 'default'
                do_expr = condition['default']
            sb += f"{agentL}->>{agentR}: {do_expr} {condition_expr}\n"
        # generate the if / then / else
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
    def __to_flowchart(self, sb, orientation) -> str:
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
                    sb += self.__to_flowchart_condition(agentL, agentR, step, condition)
            i = i + 1
        # if workflow has global exception then add at the end
        if self.workflow['spec']['template'].get('exception'):
            sb += self.__to_flowchart_exception(steps, self.workflow['spec']['template']['exception'])
        return sb

    # convert condition section to flowchart mermaid diagram
    def __to_flowchart_condition(self, agentL, agentR, step, condition) -> str:
        sb = ''
        # generate the case / do / default
        if condition.get('case'):
            condition_expr, do_expr = condition['case'], condition['do']
            if condition.get('default'):
                condition_expr = 'default'
                do_expr = condition['default']
            sb += f"{agentL}->>{agentR}: {do_expr} {condition_expr}\n"
        # generate the if / then / else
        if condition.get('if'):
            if_expr = f"{condition['if']}"
            then_expr = condition['then']
            else_expr = condition['else']
            step_name = step['name']
            sb += f"{step_name} --> Condition{{\"{if_expr}\"}}\n"
            sb += f"  Condition -- Yes --> {then_expr}\n"
            sb += f"  Condition -- No --> {else_expr}\n"
        return sb

    # convert event to mermaid flowchart
    def __to_flowchart_event(self, event):
        name = event['name']
        cron = event['cron']
        exit = event['exit']
        sb = ''
        # TODO: complete this for flowchart
        # for step in steps:
        #     if step.get('agent'):
        #         agentL = self.__fix_agent_name(step.get('agent'))
        #         sb += f"{agentL} -->|exception| {exception['name']}{{{exception['agent']}}}\n"
        return sb

    # convert exception to mermaid flowchart
    def __to_flowchart_exception(self, steps, exception):
        sb = ''
        for step in steps:
            if step.get('agent'):
                agentL = self.__fix_agent_name(step.get('agent'))
                sb += f"{agentL} -->|exception| {exception['name']}{{{exception['agent']}}}\n"
        return sb
