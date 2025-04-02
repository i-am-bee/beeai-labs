import io, sys, asyncio, subprocess, os, psutil

import streamlit as st
import streamlit.web.cli as st_cli

from streamlit import runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx

import streamlit_mermaid as stmd

from src.workflow import Workflow
from cli.common import Console, parse_yaml, read_file
from src.workflow import Workflow
import threading
import time

# TODO: refactor

sys_stdout = sys.stdout

global workflow_instance
global thread

def start_workflow():
    global output
    output = io.StringIO()
    sys.stdout = output
    asyncio.run(workflow_instance.run())

def create_workflow(agents_yaml, workflow_yaml):
    return Workflow(agents_yaml, workflow_yaml[0])

def deploy_agents_workflow_streamlit(agents_file, workflow_file):
    agents_yaml = parse_yaml(agents_file)
    workflow_yaml = parse_yaml(workflow_file)
    workflow = create_workflow(agents_yaml, workflow_yaml)

    # Set page configuration
    st.set_page_config(
        page_title="Maestro Workflow",
        page_icon="🤖",
        layout="centered"
    )
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            { 
                "role": "assistant", 
                "content": "Welcome to Maestro workflow"
            }]

    # Page header
    st.image("images/maestro.png", width=200)
    st.title(f"Maestro workflow")

    # add line of workflow: title, agents.yaml, and workflow.yaml
    st.markdown(f"### {workflow_yaml[0]['metadata']['name']}")

    cols = st.columns(4)
    with cols[0]:
        with st.popover("agents.yaml"):
            st.markdown("## Formatted agents YAML")
            st.code(read_file(agents_file), language="yaml", line_numbers=True, wrap_lines=False, height=700)
    with cols[1]:
        with st.popover("workflow.yaml"):
            st.markdown("## Formatted workflow YAML")
            st.code(read_file(workflow_file), language="yaml", line_numbers=True, wrap_lines=False, height=700)
    
    # create workflow
    global output
    global workflow_instance
    try:
        workflow_instance = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    
    # add workflow mermaid diagram to page
    st.markdown("")
    st.markdown(f"###### _Sequence diagram of workflow_")
    mermaid_diagram = workflow_instance.to_mermaid()
    stmd.st_mermaid(mermaid_diagram)

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="🤖"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar="👤"):
                st.markdown(message["content"])

    # Function to process user input
    async def process_query(query):
        try:
            return await workflow.run()
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    prompt = st.chat_input(f"{workflow_yaml[0]['spec']['template']['prompt']}")
    if prompt:
        # recreate workflow with the new prompt
        workflow_yaml[0]["spec"]["template"]["prompt"] = prompt
        workflow_instance = Workflow(agents_yaml, workflow_yaml[0])
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            thread = threading.Thread(target=start_workflow)
            thread.start()

            # stream response
            while True:
                message = ""
                lines = output.getvalue().splitlines()
                for line in lines:
                    message = message + f"{line}\n\n"
                message_placeholder.markdown(message)
                time.sleep(1)
                if not thread.is_alive():
                    message = ""
                    lines = output.getvalue().splitlines()
                    for line in lines:
                        message = message + f"{line}\n\n"
                    message_placeholder.markdown(message)
                    break
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": message})

        # Add reset button
        def reset_conversation():
            st.session_state.conversation = None
            st.session_state.chat_history = None
            message_placeholder = st.empty()

        st.button('Reset', on_click=reset_conversation)

if __name__ == '__main__':
    if runtime.exists():
        ctx = get_script_run_ctx()
        deploy_agents_workflow_streamlit(sys.argv[1], sys.argv[2])
        add_script_run_ctx(psutil.Process(os.getpid()), ctx)
    else:
        sys.exit(st_cli.main())
