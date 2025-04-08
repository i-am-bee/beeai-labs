import io, sys, asyncio, subprocess, os, psutil

import streamlit as st
import streamlit.web.cli as st_cli

from streamlit import runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx

from streamlit_workflow_ui import StreamlitWorkflowUI

from cli.common import Console, parse_yaml, read_file

# TODO: refactor

sys_stdout = sys.stdout

global workflow_instance
global thread

def deploy_agents_workflow_streamlit(agents_file, workflow_file):
    workflow_yaml = parse_yaml(workflow_file)
    
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

    ui = StreamlitWorkflowUI(agents_file, workflow_file, workflow_yaml[0]['spec']['template']['prompt'], 'Maestro workflow')
    ui.setup_ui()


if __name__ == '__main__':
    if runtime.exists():
        ctx = get_script_run_ctx()
        deploy_agents_workflow_streamlit(sys.argv[1], sys.argv[2])
        add_script_run_ctx(psutil.Process(os.getpid()), ctx)
    else:
        sys.exit(st_cli.main())
