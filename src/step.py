#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import dotenv
import asyncio

dotenv.load_dotenv()

def eval_expression(expression, prompt):
    """
    Evaluate an expression with a given prompt.

    Args:
        expression (str): The expression to evaluate.
        prompt (str): The input prompt.

    Returns:
        The result of evaluating the expression.
    """
    local = {}
    local["input"] = prompt
    result = eval(expression, local)
    return result

class Step:
    """
    A class representing a step in a workflow.

    Attributes:
        step_name (str): The name of the step.
        step_agent (Agent): The agent to be used for this step.
        step_input (dict): The input to be provided for this step.
        step_condition (list): The conditions to be evaluated for this step.
        step_parallel (list): The agents to be run in parallel for this step.
        step_loop (dict): The loop configuration for this step.

    Methods:
        run(prompt): Runs the step with the given prompt and returns the output.
    """
    def __init__(self, step):
        self.step_name = step["name"]
        self.step_agent = step.get("agent")
        self.step_input = step.get("input")
        self.step_condition = step.get("condition")
        self.step_parallel = step.get("parallel")
        self.step_loop = step.get("loop")

    async def run(self, prompt):
        """
        Runs the step with the given prompt and returns the output.

        Args:
            prompt (str): The prompt to be used for this step.

        Returns:
            dict: The output of the step.
        """
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
        """
        Evaluate the condition based on the prompt.

        Parameters:
            prompt (str): The input prompt for evaluating the condition.

        Returns:
            str: The result of evaluating the condition.
        """
        if self.step_condition[0].get("if"):
            return self.process_if(prompt)
        else:
            return self.process_case(prompt)

    def process_if(self, prompt):
        """
        Process the 'if' condition in a step.

        Parameters:
            prompt (str): The input prompt for the code generation.

        Returns:
            str: The 'then' or 'else' block based on the evaluation of the 'if' condition.
        """
        expression = self.step_condition[0].get("if")
        if eval_expression(expression, prompt):
            return self.step_condition[0].get("then")
        else:
            return self.step_condition[0].get("else")

    def process_case(self, prompt):
        """
        Process the case based on the given prompt.

        Args:
            prompt (str): The input prompt for processing the case.

        Returns:
            str: The result of processing the case based on the prompt.
        """
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
        """
        This function takes a prompt as input and returns a formatted response based on the template provided.

        Parameters:
            prompt (str): The input prompt to be used in the response.

        Returns:
            str: The formatted response based on the template provided.
        """
        user_prompt = self.step_input.get("prompt").replace("{prompt}", str(prompt))
        template = self.step_input.get("template")
        if "{CONNECTOR}" in template: return prompt
        response = input(user_prompt) 
        formatted_response = template.replace("{prompt}", prompt).replace("{response}", response)
        return formatted_response

    async def parallel(self, prompt):
        """
        This function runs multiple agents in parallel and returns the results as a string.

        Args:
            prompt (str): The input prompt for the agents to run.

        Returns:
            str: The results of running the agents in parallel as a string.
        """
        #results = await asyncio.gather(*[asyncio.create_task(agent.run(prompt)) for agent in self.step_parallel])
        waits = []
        for agent in self.step_parallel:
            waits.append(asyncio.create_task(agent.run(prompt)))
        results = []
        for wait in waits:
            results.append(await wait)
        return str(results)

    async def loop(self, prompt):
        """
        This function is a loop that runs an agent on a given prompt until a certain condition is met.

        Parameters:
            prompt (str): The initial prompt for the agent to run.

        Returns:
            str: The final prompt after the loop has completed.
        """
        until = self.step_loop.get ("until")
        agent = self.step_loop.get("agent")
        while True:
            prompt = await agent.run(prompt)
            if eval_expression(until, prompt):
                return prompt
