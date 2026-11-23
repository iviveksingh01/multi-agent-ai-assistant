import streamlit as st
import json
from src.AgenticAI.UserInterface.StreamlitUI.loadUI import (
    LoadStreamlitUI, get_history, get_meta, get_readiness, IMPLEMENTED_USECASES,
)
from src.AgenticAI.LLM.groqllm import GroqLLM
from src.AgenticAI.UserInterface.StreamlitUI.display_result import DisplayResultStreamlit, render_history
from src.AgenticAI.Graph.graph_builder import GraphBuilder


def load_langgraph_agentic_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.
    """

    # Load UI

    load_ui = LoadStreamlitUI()
    user_input = load_ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    usecase = user_input.get('selected_usecase')
    ready, reason = get_readiness(user_input)

    # Text input for user message (chat input is always pinned to the bottom)
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe
    else:
        typed = st.chat_input(get_meta(usecase)["placeholder"] if ready else reason.replace("**", ""),
                              disabled=not ready)
        user_message = typed or st.session_state.pop("pending_prompt", None)

    # Conversation so far / welcome screen
    if get_history(usecase):
        render_history(usecase)
        if not ready:
            st.info(reason)
    elif not user_message:
        load_ui.render_welcome(usecase, ready, reason)

    if user_message:
        if not ready:
            st.warning(reason)
            return
        try:
            obj_llm_config = GroqLLM(user_control_input=user_input)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Error: Failed to load the LLM model.")
                return

            if not usecase:
                st.error("Error: Use case not selected.")
                return


            graph_builder = GraphBuilder(model=model)
            try:
                graph = graph_builder.setup_graph(usecase=usecase)
                DisplayResultStreamlit(usecase=usecase, graph=graph, user_message=user_message).display_result_on_ui()
            except Exception as e:
                st.error(f"Something went wrong while running the agent: {e}")
                return
        except Exception as e:
            st.error(f"Error occurred: {e}")
            return
