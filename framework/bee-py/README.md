
> [!WARNING] 
> [PRE-Alpha] Please reach out if you want to get involved in the discussions. All feedback is welcomed

<p align="center">
    <img alt="Bee Framework logo" src="/docs/assets/Bee_Dark.svg" height="128">
    <h1 align="center">Bee Agent Framework Python</h1>
</p>

<p align="center">
  <img align="center" alt="Project Status: Alpha" src="https://img.shields.io/badge/Status-Alpha-red">
  <h4 align="center">Python implementation of the Bee Agent Framework for building, deploying, and serving powerful agentic workflows at scale.</h4>
</p>

The Bee Agent Framework Python makes it easy to build scalable agent-based workflows with your model of choice. This framework is designed to perform robustly with [IBM Granite](https://www.ibm.com/granite?adoper=255252_0_LS1) and [Llama 3.x](https://ai.meta.com/blog/meta-llama-3-1/) models. Varying level of support is currently availble for [other LLMs using LiteLLM](https://docs.litellm.ai/docs/providers). We're actively working on optimizing its performance with these popular LLMs.

Our goal is to empower Python developers to adopt the latest open-source and proprietary models with minimal changes to their current agent implementation.

## Key Features

- 🤖 **AI agents**: Use our powerful Bee agent refined for Llama 3.x and Granite 3.x, or build your own.
- 🛠️ **Tools**: Use our built-in tools or create your own in Python.
- ... more on our Roadmap

## Getting Started

### Installation

```bash
pip install ./framework/bee-py
```

### Quick Example

```python
from bee_agent import BeeAgent, LLM

agent = BeeAgent(llm=LLM())

agent.run("What is the capital of Massachusetts")
```

> **Note**: To run this example, ensure you have [ollama](https://ollama.com) installed with the [llama3.1](https://ollama.com/library/llama3.1) model downloaded.

to run other examples you can use, "python -m examples.bee_agent.[example_name]":

```bash
python -m examples.bee_agent.basic
```

## Local Development

1. Clone the repository: `git clone https://github.com/i-am-bee/bee-hive.git`
1. Change into the `./framework/bee-py` directory
1. Install dependencies: `poetry install`
1. Activate virtual environment: `poetry shell`
1. Create `.env` from `.env.example` and fill in required values


### Build the pip package

#### Build the package:

```bash
cd ./framework/bee-py
poetry build
```

#### Test the Build Locally (Recommended)

```bash
# Create a virtual environment
python -m venv test_env

source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the built package
pip install dist/bee-py-0.1.0.tar.gz
```

#### Publish to TestPyPI

```bash
# Configure Poetry:
poetry config repositories.testpypi https://test.pypi.org/legacy/
# Publish
poetry publish -r testpypi
#Test the installation
pip install --index-url https://test.pypi.org/simple/ bee-py
```

## Modules

The package provides several modules:

| Module   | Description                                           |
| -------- | ----------------------------------------------------- |
| `agents` | Base classes defining the common interface for agents |
| `llms`   | Base classes for text inference (standard or chat)    |
| `tools`  | Tools that an agent can use                           |

## Roadmap

- 👩‍💻 **Code interpreter**: Run code safely in a sandbox container.
- 💾 **Memory**: Multiple strategies to optimize token spend.
- ⏸️ **Serialization**: Handle complex agentic workflows and easily pause/resume them without losing state.
- 🔍 **Instrumentation**: Full visibility of your agent's inner workings.
- 🎛️ **Production-level** control with caching and error handling.
- 🔁 **API**: OpenAI-compatible Assistants API integration.
- Bee agent performance optimization with additional models
- Examples, tutorials, and comprehensive documentation
- Improvements to building custom agents
- Multi-agent orchestration
- Feature parity with TypeScript version

## Contributing

The Bee Agent Framework Python is an open-source project and we ❤️ contributions. Please check our [contribution guidelines](./CONTRIBUTING.md) before getting started.

### Reporting Issues

We use [GitHub Issues](https://github.com/i-am-bee/bee-hive/issues) to track public bugs. Please check existing issues before filing new ones.

### Code of Conduct

This project adheres to our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Legal Notice

All content in these repositories including code has been provided by IBM under the associated open source software license and IBM is under no obligation to provide enhancements, updates, or support. IBM developers produced this code as an open source project (not as an IBM product), and IBM makes no assertions as to the level of quality nor security, and will not be maintaining this code going forward.
