# CBOM demo (partial)

This part of the demo covers the remediation flow, as based on our earlier cbom.ai demo

The sequence is:

* `cbom_finder` : extracts some changes to work on from the supplied cbom
  * currently the CBOM is encoded verbatim in the workflow, when merged this should come from the previous workflow step.
* `cbom_fixer` : creates a patchfile with the required fix
* `cbom_patcher` : takes a patchfile & creates a github pull request

## Dependencies

## BeeAI stack

### Executor image

This demo requires the following tools to be available within the executor environment:

* git
* gh (GitHub cli)

#### Building the image (optional)

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
podman build -t quay.io/planetf1/bee-code-executor:20250410 executor
podman push quay.io/planetf1/bee-code-executor:20250410
```

#### Using the executor image (mandatory)

Update `bee-code-interpreter.yaml` in bee-stack to use the image you built above (or my prebuilt one)

Look for the variable **APP_EXECUTOR_IMAGE** and update the value to the correct value for your newly created image. For example in the above build
it would be updated to `quay.io/planetf1/bee-code-executor:20250410`.

### Environment

Ensure the following environment variables are set:

```shell
BEE_API=http://localhost:4000
BEE_API_KEY=sk-proj-testkey
DEFER_PYDANTIC_BUILD=false
```

### github tokens

Replace the string `__TOKEN__` in `demos/workflows/cbom.ai/agents_fromcbom.yaml` with a valid token
for access to https://github.com/Mastercard/client-encryption-java. This needs write access to the repository:
  
### Ollama setup

To avoid having to edit and redeploy the agents, they both use a model name of 'cbom:latest'

to create this model do this with your favoured model:

```
ollama run granite3.3:8b
/save cbom:latest
^D
```

## Running the demo

1. Create the agents

  ```bash
  maestro create /Users/jonesn/AI/maestro/demos/workflows/cbom.ai/agents_fromcbom.yaml 
  ```

1. Create the tools:
  
* copy the python code from the 'code' attribute in the agent & create in the bee UI accordingly as
  * cbom_fixer.py
  * cbom_patcher.py

1. Associate the tools with the agents

* edit the agents previously created to activate the required tools 

1. run the workflow

  ```bash
  maestro run /Users/jonesn/AI/maestro/demos/workflows/cbom.ai/agents_fromcbom.yaml /Users/jonesn/AI/maestro/demos/workflows/cbom.ai/workflow_fromcbom.yaml
  ```

## Limitations

* Dependent on the now-deprecated bee-stack
* manual steps needed to configure agent

