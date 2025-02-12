# Summary.ai Example

A multi-agent workflow using Bee-Hive: Allows an user to specify a topic from Arxiv they want to look at, choose a number of potential papers to summarize.

## Setup

There are 2 demos in this example, which is why we are using the custom workflow in the common/src folder.

By default, in the `run_workflow_summary.py` file, in the main there is the default value of `result= sequential_workflow_for_summary(workflow_yaml)`. This is for the summary demo, which only requires 2 agents `Search Arxiv, Individual Summary` which are defined in the `agents.yaml` file.

To test the full end to end workflow w/multiple agents, you can change in the workflow file to use the function `result=sequential_workflow_for_demo(workflow_yaml)` instead of the summary, and go to `agents.yaml` to uncomment the other agent definitions.

Note, the file `run.sh` uses the custom `run_workflow.summary.py`file instead of the regular workflow to handle specific tooling and user inputs, which is already set by default so no changes are needed.

## Getting Started

* Run a local instance of the [bee-stack](https://github.com/i-am-bee/bee-stack/blob/main/README.md)

* Verify a valid llm is available to bee-stack

* Install [bee-hive](https://github.com/i-am-bee/bee-hive) dependencies: `cd ../../../bee-hive/bee-hive && poetry shell && poetry install && cd -`

* Configure environmental variables: `cp example.env .env`

* Copy `.env` to common directory: `cp .env ./../common/src`

* Set up the demo and create the agents: `./setup.sh`

* Run the workflow: `./run.sh` (to run for a different topic, change the `prompt` field in `workflow.yaml`)

### NOTE: Custom Tools Required for this Demo:

Go into the UI and make 2 tools for this demo:

1) Fetch tool:

Name: Fetch

Code:
```
import urllib.request

def fetch_arxiv_titles(topic: str, k: int = 10):
  """Fetches the k most recent article titles from arXiv on a given topic."""
  url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&sortBy=submittedDate&sortOrder=descending&max_results={k}"

  with urllib.request.urlopen(url) as response:
      data = response.read().decode()

  titles = [line.split("<title>")[1].split("</title>")[0] for line in data.split("\n") if "<title>" in line][1:k+1]
  return titles
```

2) Filtering tool:

Name: Filter

Code:
```
import urllib.request
import urllib.parse
import re
import time


def fetch_valid_arxiv_titles(titles: list):
    """
    Fetches titles that have an available abstract on ArXiv.

    Args:
        titles (list): List of paper titles.

    Returns:
        list: Titles that have an abstract.
    """
    base_url = "http://export.arxiv.org/api/query?search_query="
    valid_titles = []

    for title in titles:
        search_query = f'all:"{urllib.parse.quote(title)}"'
        url = f"{base_url}{search_query}&max_results=1"
        for attempt in range(3):  # Retry mechanism (max 3 attempts)
            try:
                with urllib.request.urlopen(url) as response:
                    data = response.read().decode()
                break  # Exit loop on successful request
            except Exception as e:
                print(f"⚠️ Attempt {attempt+1} failed for '{title}': {e}")
                time.sleep(2)  # Wait before retrying
        else:
            print(f"❌ Skipping '{title}' after 3 failed attempts.")
            continue  # Skip to the next title after max retries

        abstract_match = re.search(r"<summary>(.*?)</summary>", data, re.DOTALL)

        if abstract_match and abstract_match.group(1).strip():
            valid_titles.append(title)
        else:
            print(f"❌ No abstract found: {title}")
    return valid_titles
```