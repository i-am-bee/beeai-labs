# Contributing

Maestro is an open-source project committed to bringing LLM agents to people of all backgrounds. This page describes how you can join the Maestro community in this goal.

## Before you start

If you are new to Maestro contributing, we recommend you do the following before diving into the code:

- Read [Code of Conduct](./CODE_OF_CONDUCT.md).

## Style and lint

Maestro uses the following tools to meet code quality standards and ensure a unified code style across the codebase:

We use the following libs to check the Python code: 
- [Black](https://black.readthedocs.io/) - Code Formatter
- [Ruff](https://beta.ruff.rs/docs/) - Fast Python linter

 Simple [scripts for Poetry](tools/scripts.py)) are included to help you to review your changes and commit them.

## Issues and pull requests

We use GitHub pull requests to accept contributions.

While not required, opening a new issue about the bug you're fixing or the feature you're working on before you open a pull request is important in starting a discussion with the community about your work. The issue gives us a place to talk about the idea and how we can work together to implement it in the code. It also lets the community know what you're working on, and if you need help, you can reference the issue when discussing it with other community and team members.

If you've written some code but need help finishing it, want to get initial feedback on it before finishing it, or want to share it and discuss it prior to completing the implementation, you can open a Draft pull request and prepend the title with the [WIP] tag (for Work In Progress). This will indicate to reviewers that the code in the PR isn't in its final state and will change. It also means we will only merge the commit once it is finished. You or a reviewer can remove the [WIP] tag when the code is ready to be thoroughly reviewed for merging.

## Choose an issue to work on

Maestro uses the following labels to help non-maintainers find issues best suited to their interests and experience level:

- [good first issue](https://github.com/i-am-bee/bee-hive/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) - these issues are typically the simplest available to work on, ideal for newcomers. They should already be fully scoped, with a straightforward approach outlined in the descriptions.
- [help wanted](https://github.com/i-am-bee/bee-hive/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) - these issues are generally more complex than good first issues. They typically cover work that core maintainers don't currently have the capacity to implement and may require more investigation/discussion. These are great options for experienced contributors looking for something more challenging.

## Set up a development environment

To start contributing to Maestro, follow these steps to set up your development environment:

1. **Set up Python environment:** We recommend using Python 3.12 or higher. First, ensure you have Python installed:

```bash
python --version
```

2. **Activate a virtual environment:** Activate a new virtual environment:

```bash
poetry shell
```

3. **Install dependencies:** Install all project dependencies:

```bash
poetry install
```

4. **Setup environmental variables:** Make a copy of `.env.example` file in the repository's root and name it `.env`. Uncomment and update the parameters in the `.env` as needed.

5. **Follow Conventional Commit Messages:** We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) to structure our commit messages. Please use the following format:

```
<type>(<scope>): <subject>
```

- Type: feat, fix, chore, docs, style, refactor, perf, test, etc.
- Scope: The area of the codebase your changes affect (optional). The allowed values are: adapters, agents, llms, tools, cache, emitter, internals, logger, memory, serializer, infra, deps, instrumentation
- Subject: A short description of the changes (required)

_Example:_

```
feat(llm): add streaming support for watsonx adapter

Ref: #15
```

6. **Run Linters/Formatters:** Ensure your changes meet code quality standards:

     - lint: use the next command run Black and Ruff:

```bash
poetry run lint
```
  

7. **Run Tests:** Ensure your changes pass all tests:

```bash
# Run unit tests
pytest tests/unit
# Run integration tests
pytest tests/integration
# Run E2E tests
pytest tests/e2e
```

6. **Commit:**  

     - commit: use the following command to sign-off your commit with `-s` and generate the commit.

```bash
poetry run commit "<type>(<scope>): <subject>"
```

By following these steps, you'll be all set to contribute to our project! If you encounter any issues during the setup process, please feel free to open an issue.

## Legal

The following sections detail important legal information that should be viewed prior to contribution.

### License and Copyright

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)

If you would like to see the detailed LICENSE click [here](/LICENSE).

### Developer Certificate of Origin (DCO)

We have tried to make it as easy as possible to make contributions. This applies to how we handle the legal aspects of contribution. We use the same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://developercertificate.org/) - that the Linux® Kernel [community](https://docs.kernel.org/process/submitting-patches.html#sign-your-work-the-developer-s-certificate-of-origin) uses to manage code contributions.

We ask that when submitting a patch for review, the developer must include a sign-off statement in the commit message. If you set your `user.name` and `user.email` in your `git config` file, you can sign your commit automatically by using the following command:

```bash
git commit -s
```

The following example includes a `Signed-off-by:` line, which indicates that the submitter has accepted the DCO:

```text
Signed-off-by: John Doe <john.doe@example.com>
```

We automatically verify that all commit messages contain a `Signed-off-by:` line with your email address.

#### Useful tools for doing DCO signoffs

There are a number of tools that make it easier for developers to manage DCO signoffs.

- DCO command line tool, which lets you do a single signoff for an entire repo ( <https://github.com/coderanger/dco> )
- GitHub UI integrations for adding the signoff automatically ( <https://github.com/scottrigby/dco-gh-ui> )
- Chrome - <https://chrome.google.com/webstore/detail/dco-github-ui/onhgmjhnaeipfgacbglaphlmllkpoijo>
- Firefox - <https://addons.mozilla.org/en-US/firefox/addon/scott-rigby/?src=search>
