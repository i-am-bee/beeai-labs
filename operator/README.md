# Maestro Operator

## How to build and run operator:

1. build images
        cd operator
        make docker-build
        make engine-docker-build
2. Create a kind cluster
        kind create cluster --config tests/integration/deploys/kind-config.yaml
3. Load images cluster
        kind load docker-image localhost/controller:latest
        kind load docker-image localhost/maestro-engine:latest
4. Install Maestro Operator
        kubectl apply -f config/crd/bases
        make deploy
5. Deploy test agents, workflow, configmap and workflowrun
        cd ..
        python deploycr.py demos/workflows/weather-checker.ai/agents.yaml
        python deploycr.py demos/workflows/weather-checker.ai/workflow.yaml
        kubectl apply -f operator/test/config/test-configmap.yaml
        kubectl apply -f operator/test/config/test-workflowrun.yaml
6. open a browser to 127.0.0.1:30051

"DRY_RUN" is set in the "operator/test/config/test-configmap.yaml".  The "BEE_API" and ""BEE_API_KEY" must be set to run with real agent.
