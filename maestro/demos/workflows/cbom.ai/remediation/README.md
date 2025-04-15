# QSC Remediation

The demo consists of three agents:

| Agent | Purpose | In | Out | Tools | Notes |
| -- | -- | -- | -- | -- | -- |
|Finder|Parse CBOM to look for specific QSC issues to fix|CBOM|JSON findings|-|The mastercard CBOM from sonarqube scan is used|
|Fixer|Fix code to make it safer|JSON findings|git email patch|fixer||
|Patcher|Fix code to make it safer|git email patch|URL to PR|patcher||

The Agents will together take a CBOM scan of a github repository, and by the end will have raised a pull request against
the repo with a suggested fix.

## Prereqs

* Python 3.13
* `pip install -r requirements.txt -U`
* Agents are written to use the *BAM* runtime with *meta-llama/llama-3-1-70b-instruct* (see example config below)

## Executor image

This demo requires the following tools to be available within the executor environment:

* git
* gh (GitHub cli)

### Building the image (optional)

The standard executor image does not contain tools like 'gh' and 'git'

Update the executor/Dockerfile to install additional packages

```patch
diff --git a/executor/Dockerfile b/executor/Dockerfile
index 4f45222..5f3265b 100644
--- a/executor/Dockerfile
+++ b/executor/Dockerfile
@@ -42,8 +42,6 @@ RUN apk add --no-cache gcc musl-dev linux-headers make g++ clang-dev python3 pyt

 FROM docker.io/alpine:${ALPINE_VERSION} AS runtime
 RUN apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing \
-    git \
-    github-cli \
     bash \
     coreutils \
     ffmpeg \
```

Then build. In my case I tag as follows since I push to quay.io

```bash
podman build -t quay.io/planetf1/bee-code-executor:20241117a executor
podman push quay.io/planetf1/bee-code-executor:20241117a
```

### Using the executor image (mandatory)

Update `bee-code-interpreter.yaml` in bee-stack to use the image you built above (or my prebuilt one)

Look for the variable **APP_EXECUTOR_IMAGE** and update the value to the correct value for your newly created image. For example in the above build
it would be updated to `quay.io/planetf1/bee-code-executor:20241117a`.

## Running the demo

### Command Line

* Ensure the bee framework configuration is set appropriately. See an example later in this document.
  * This should also be sourced into your current shell as the demo code requires it.
* Start the bee agent framework as normal. Allow time (~1 minute) for the code executor to start
* Launch a run-through of 3 sequenced agent with `./remediation_demo.py`

### User Interface

* Manually cleanup any old CBOM-AI Agents and tools using the bee UI
* Set `BEE_KEEP=1`in the environment, and run the full demo through once. 
* You can now use the bee UI to interact in the same way
  * Some cut/paste of file contents may be needed

## Debugging

* Agents can be run individually within the bee framework via:
  * `agents/run_finder.py`
  * `agents/run_fixer.py`
  * `agents/run_patcher.py`
  
* Tools can also be run directly via:
  * `tools/tool_fixer.py`
  * `tools/tool_patcher.py`

### Executor

To debug the executor, use `podman ps` or similar to find the container running k3s ie

```shell
% podman ps -f name=bee-stack-bee-code-interpreter-k3s-1                                                                                                                                                                      <<<
CONTAINER ID  IMAGE                               COMMAND               CREATED        STATUS                  PORTS                     NAMES
50cb9892519e  docker.io/rancher/k3s:v1.30.5-k3s1  server --tls-san ...  7 minutes ago  Up 7 minutes (healthy)  0.0.0.0:50051->30051/tcp  bee-stack-bee-code-interpreter-k3s-1
```

Then use `kubectl` to watch the logs ie

```shell
podman exec -it 50cb9892519e kubectl logs -f code-interpreter
[INFO] [00000000-0000-0000-0000-000000000000] grpc_server: Registering servicer CodeInterpreterServicer
[INFO] [00000000-0000-0000-0000-000000000000] kubernetes_code_executor: Extending executor pod queue to target length 1, current queue length: 0, already spawning: 0, to spawn: 1
INFO:     Started server process [1]
INFO:     Waiting for application startup.
[INFO] [00000000-0000-0000-0000-000000000000] grpc_server: Starting server on insecure port 0.0.0.0:50051
[INFO] [00000000-0000-0000-0000-000000000000] kubectl: kubectl get pod code-interpreter --output=json
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Some errors may appear here which might help debugging

### Demoing if one agent is misbehaving

* Export the environment variable 'BEE_NOCHAIN'(to any value) to use pre-defined intermediate files, in case one agent is misbehaving

### Example Bee Stack configuration

This is an example `.env` used for launching the bee stack:

```bash
LLM_BACKEND=bam
EMBEDDING_BACKEND=bam
BEE_API=http://localhost:4000
BEE_API_KEY=sk-proj-testkey
DEFER_PYDANTIC_BUILD=false
BAM_API_KEY=pak-<redacted>
GENAPI_KEY=pak-<redacted>>
GH_TOKEN=github_pat_<redacted>>

export LLM_BACKEND
export EMBEDDING_BACKEND
export BEE_API
export BEE_API_KEY
export DEFER_PYDANTIC_BUILD
export BAM_API_KEY
export GENAPI_KEY
export GH_TOKEN
```

## Todos / Caveats

* Very little error checking
* Code needs refactoring

## Learnings

* Can be hard to debug tools
* tools must only have a single function
* the text tools return can result in the executor hitting JSON parse errors
* Hard to predict when a tool will get passed a file name vs file content
* Use of files between agent calls is not reliable
* May need to install more content in the executor
