import os, sys, traceback, psutil

import streamlit as st
import streamlit.web.cli as st_cli

from streamlit import runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx

from streamlit_workflow_ui import StreamlitWorkflowUI

from cli.common import Console, parse_yaml, read_file

def deploy_meta_agents_streamlit(prompt_text_file):
    prompt = "Enter your maestro meta-agents prompt here"
    try:
        prompt = read_file(prompt_text_file)
    except Exception as e:
        Console.error(f"Unable to read prompt text file: {prompt_text_file} error: {str(e)}")

    # Set page configuration
    st.set_page_config(
        page_title="Maestro Meta-Agents Workflow",
        page_icon="🤖",
        layout="centered"
    )

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to Maestro meta-agents workflow"}
        ]

    # Page header
    st.image("images/maestro.png", width=200)
    st.title(f"Maestro Meta-Agents workflows")

    # Set tabs for: Meta-Agents agents and workflow workflows and the generated workflow
    agents_tab, workflow_tab, generated_workflow_tab = st.tabs(["Agents", "Workflow", "Generated"])

    with agents_tab:
        st.header("Meta-agents 🤖 -> agents.yaml")
        ma_agents_workflow_ui = StreamlitWorkflowUI('src/agents/meta_agent/agents.yaml', 'src/agents/meta_agent/workflow_agent.yaml', prompt, 'Maestro meta-agents agents workflow')
        ma_agents_workflow_ui.setup_ui()
    
    with workflow_tab:
        st.header("Meta-agents 🤖 -> workflow.yaml")
        ma_workflow_workflow_ui = StreamlitWorkflowUI('src/agents/meta_agent/agents.yaml', 'src/agents/meta_agent/workflow_workflow.yaml', prompt, 'Maestro meta-agents workflow')
        ma_workflow_workflow_ui.setup_ui()

    with generated_workflow_tab:
        st.header("Meta-agents generated ⌇ -> Workflow")
        agent_file = st.file_uploader("Choose agents.yaml", key='agents.yaml')
        workflow_file = st.file_uploader("Choose agents.yaml", key='workflow.yaml')

        if agent_file is not None and workflow_file is not None:
            ma_gent_workflow_workflow_ui = StreamlitWorkflowUI(agent_file.getvalue().decode("utf-8"), workflow_file.getvalue().decode("utf-8"), '', 'Maestro meta-agents generated workflow')
            ma_gent_workflow_workflow_ui.setup_ui()

if __name__ == '__main__':
    if runtime.exists():
        ctx = get_script_run_ctx()
        deploy_meta_agents_streamlit(sys.argv[1])
        add_script_run_ctx(psutil.Process(os.getpid()), ctx)
    else:
        sys.exit(st_cli.main())
