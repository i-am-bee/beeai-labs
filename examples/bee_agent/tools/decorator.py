from bee_agent.tools import bee_tool


@bee_tool(
    name="Calculator",
    description="Multiplies two numbers",
    input_schema={
        "type": "object",
        "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
    },
    output={"type": "number", "description": "The product of x and y"},
)
def multiply(input):
    return input["x"] * input["y"]


# Example with string output description
@bee_tool(
    name="Greeting",
    description="Creates a greeting message",
    input_schema={"type": "object", "properties": {"name": {"type": "string"}}},
    output="A personalized greeting message",
)
def greet(input):
    return f"Hello, {input['name']}!"


# Example without output schema
@bee_tool(
    name="Logger",
    description="Logs a message",
    input_schema={"type": "object", "properties": {"message": {"type": "string"}}},
)
def log_message(input):
    print(input["message"])
    return None


# Usage examples
print(
    multiply.output_schema
)  # {"type": "number", "description": "The product of x and y"}
print(
    greet.output_schema
)  # {"type": "string", "description": "A personalized greeting message"}
print(log_message.output_schema)  # {}

# Example of prompt_data() including output schema
print(multiply.prompt_data())
