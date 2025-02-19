#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import dotenv

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

    def run(self, prompt):
        output = {"prompt": prompt}
        if self.step_agent:
            prompt = self.step_agent.run(prompt)
            output["prompt"] = prompt
        if self.step_input:
            prompt = self.input(prompt)
            output["prompt"] = prompt
        if self.step_condition:
            next = self.evaluate_condition(prompt)
            output["next"] = next
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
        response = input(user_prompt) 
        template = self.step_input.get("template")
        formatted_response = template.replace("{prompt}", prompt).replace("{response}", response)
        return formatted_response