# SPDX-License-Identifier: Apache-2.0

import os
import base64
import traceback
import warnings

# Currently this is a dependency in poetry. Make code resilient so we 
# could make library optional
try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    logfire = None

# TODO: observability should not depend on openAI agents - partial
# function if not here (needs refactor, and adding 2nd backend to prove)
try:
    from agents import set_tracing_disabled
    AGENTS_TRACING_AVAILABLE = True
except ImportError:
    AGENTS_TRACING_AVAILABLE = False
    set_tracing_disabled = None

_langfuse_initialized = False

def setup_langfuse_tracing(print_func: callable = print) -> bool:
    """
    Sets up langFuse tracing using LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_HOST. 

    Currently instruments the openai agents library only

    Args:
        print_func (callable): Function to use for logging messages (defaults to print).

    Returns:
        bool: True if Langfuse was successfully configured, False otherwise.
    """
    global _langfuse_initialized
    if _langfuse_initialized:
        print_func("DEBUG [Observability]: Langfuse tracing already initialized.")
        return True

    if not LOGFIRE_AVAILABLE:
        print_func("DEBUG [Observability]: 'logfire' library not found. Skipping Langfuse setup.")
        return False
    
    if not AGENTS_TRACING_AVAILABLE:
        print_func("WARN [Observability]: 'agents.set_tracing_disabled' not found. Cannot control agent tracing state for Langfuse.")


    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")

    if not all([public_key, secret_key, host]):
        print_func("DEBUG [Observability]: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, or LANGFUSE_HOST not set. Skipping Langfuse setup.")
        return False

    print_func("INFO [Observability]: Found Langfuse configuration. Attempting to set up tracing...")

    if not public_key.startswith("pk-lf"):
        print_func("ERROR [Observability]: LANGFUSE_PUBLIC_KEY must start with 'pk-lf'. Aborting Langfuse setup.")
        return False
    if not secret_key.startswith("sk-lf"):
        print_func("ERROR [Observability]: LANGFUSE_SECRET_KEY must start with 'sk-lf'. Aborting Langfuse setup.")
        return False
    if not host.startswith(("http://", "https://")):
        print_func("WARN [Observability]: LANGFUSE_HOST does not look like a valid URL. Proceeding anyway.")

    # TODO: Warning seems to have no effect, so mask for now
    warnings.filterwarnings(
        "ignore",
        message="Overriding of current TracerProvider is not allowed",
        category=UserWarning,
        module="opentelemetry.trace"
    )

    try:
        # OpenTelemetry config
        auth_header = base64.b64encode(
            f"{public_key}:{secret_key}".encode()
        ).decode()
        otel_endpoint = f"{host}/api/public/otel"
        otel_headers = f"Authorization=Basic%20{auth_header}"

        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = otel_headers

        print_func(f"DEBUG [Observability]: Set OTEL_EXPORTER_OTLP_ENDPOINT to {otel_endpoint}")
        print_func(f"DEBUG [Observability]: Set OTEL_EXPORTER_OTLP_HEADERS.")

        # logfire is useful intercept->otel, but we don't actually send to logfire service
        logfire.configure(
            send_to_logfire=False,
            service_name='maestro'
        )

        # adds actual hook that intruments openai
        logfire.instrument_openai_agents()
        print_func("DEBUG [Observability]: Instrumented openai_agents with logfire.")

        # Enable openAI tracing
        if set_tracing_disabled:
            set_tracing_disabled(disabled=False)
            print_func("DEBUG [Observability]: Enabled tracing in agents library.")
        else:
            print_func("WARN [Observability]: Could not enable tracing in agents library (set_tracing_disabled not found).")

        print_func("INFO [Observability]: Langfuse tracing setup successful.")
        _langfuse_initialized = True
        return True

    except Exception as e:
        print_func(f"ERROR [Observability]: Failed during Langfuse setup: {e}")
        print_func(traceback.format_exc())
        return False
