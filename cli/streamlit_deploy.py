# Copyright © 2025 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Streamlit deployment module for Maestro workflow UI."""

import sys
import os
import psutil

import streamlit as st
import streamlit.web.cli as st_cli

from streamlit import runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx

from cli.common import parse_yaml

from streamlit_workflow_ui import StreamlitWorkflowUI

sys_stdout = sys.stdout

def deploy_agents_workflow_streamlit(agents_file, workflow_file):
    """Deploy and run a Maestro workflow using Streamlit UI.
    
    Args:
        agents_file (str): Path to the agents configuration file
        workflow_file (str): Path to the workflow configuration file
    """
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
    st.title("Maestro workflow")

    ui = StreamlitWorkflowUI(agents_file, workflow_file, workflow_yaml[0]['spec']['template']['prompt'], 'Maestro workflow')
    ui.setup_ui()

if __name__ == '__main__':
    if runtime.exists():
        ctx = get_script_run_ctx()
        deploy_agents_workflow_streamlit(sys.argv[1], sys.argv[2])
        add_script_run_ctx(psutil.Process(os.getpid()), ctx)
    else:
        sys.exit(st_cli.main())
