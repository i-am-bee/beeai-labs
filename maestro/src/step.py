#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import dotenv
import asyncio

dotenv.load_dotenv()

def eval_expression(expression, prompt):
    local = {}
    local["input"] = prompt
    result = eval(expression, local)
    return result

class Step:
    def __init__(self, step):
        self.step_name = step["name"]
        self.step_agent = step.get("agent")
        self.step_input = step.get("input")
        self.step_condition = step.get("condition")
        self.step_parallel = step.get("parallel")
        self.step_loop = step.get("loop")

    async def run(self, prompt):
        output = {"prompt": prompt}
        if self.step_agent:
            prompt = await self.step_agent.run(prompt)
            output["prompt"] = prompt
        if self.step_input:
            prompt = self.input(prompt)
            output["prompt"] = prompt
        if self.step_condition:
            next = self.evaluate_condition(prompt)
            output["next"] = next
        if self.step_parallel:
            prompt = await self.parallel(prompt)
            output["prompt"] = prompt
        if self.step_loop:
            prompt = await self.loop(prompt)
            output["prompt"] = prompt
        return output

    def evaluate_condition(self, prompt):
        if self.step_condition[0].get("if"):
            return self.process_if(prompt)
        else:
            return self.process_case(prompt)

    def process_if(self, prompt):
        expression = self.step_condition[0].get("if")
        if eval_expression(expression, prompt):
            return self.step_condition[0].get("then")
        else:
            return self.step_condition[0].get("else")

    def process_case(self, prompt):
        default = ""
        for condition in self.step_condition:
            expression = condition.get("case")
            if expression:
                if eval_expression(expression, prompt):
                    return condition.get("do")
            else:
                default = condition.get("do")
        return default

    def input(self, prompt):
        user_prompt = self.step_input.get("prompt").replace("{prompt}", str(prompt))
        template = self.step_input.get("template")
        if "{CONNECTOR}" in template: return prompt
        response = input(user_prompt) 
        formatted_response = template.replace("{prompt}", prompt).replace("{response}", response)
        return formatted_response

    async def parallel(self, prompt):
        #results = await asyncio.gather(*[asyncio.create_task(agent.run(prompt)) for agent in self.step_parallel])
        waits = []
        for agent in self.step_parallel:
            waits.append(asyncio.create_task(agent.run(prompt)))
        results = []
        for wait in waits:
            results.append(await wait)
        return str(results)

    async def loop(self, prompt):
        until = self.step_loop.get ("until")
        agent = self.step_loop.get("agent")
        while True:
            prompt = await agent.run(prompt)
            if eval_expression(until, prompt):
                return prompt
