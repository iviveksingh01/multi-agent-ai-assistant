import streamlit as st
import os
import html
from datetime import date
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.AgenticAI.UserInterface.UIconfigFile import Config
from src.AgenticAI.UserInterface.StreamlitUI.styles import CUSTOM_CSS


# Use cases that have a graph wired up in GraphBuilder.setup_graph
IMPLEMENTED_USECASES = {"Basic Chatbot", "Chatbot with Tools", "Travel Planner"}

USECASE_META = {
    "Basic Chatbot": {
        "icon": "💬",
        "tagline": "A fast, general-purpose conversational assistant powered by your selected Groq model.",
        "welcome": "How can I help you today?",
        "placeholder": "Ask me anything…",
        "flow": ["Your message", "LLM", "Answer"],
        "suggestions": [
            "Explain LangGraph in simple terms",
            "Write a professional email asking for a project update",
            "Give me 5 ideas for a weekend side project",
            "Summarize the pros and cons of microservices",
        ],
    },
    "Chatbot with Tools": {
        "icon": "🔎",
        "tagline": "Answers grounded in live web search results via Tavily.",
        "welcome": "What would you like me to look up?",
        "placeholder": "Ask about anything current — I'll search the web…",
        "flow": ["Your question", "Agent decides", "Web search", "Grounded answer"],
        "suggestions": [
            "What are the latest developments in AI agents this week?",
            "Compare the newest open-source LLMs",
            "What's the weather like in Bengaluru today?",
            "Top tech news headlines today",
        ],
    },
    "Travel Planner": {
        "icon": "🧭",
        "tagline": "A multi-agent workflow that plans, drafts, quality-checks and assembles a complete itinerary.",
        "welcome": "Where are we heading next?",
        "placeholder": "Describe your trip — destination, days, budget, interests…",
        "flow": ["Orchestrator", "Section writers", "Evaluator", "Review", "Synthesizer"],
        "suggestions": [
            "5-day trip to Japan in spring on a mid-range budget",
            "Romantic 3-day weekend getaway in Goa",
            "10 days backpacking across Italy",
            "Family trip to Dubai for 4 days with kids",
        ],
    },
}

OTHER_ICONS = {
    "Start-up Idea Validator": "🚀", "Blog Post Generator": "✍️", "Coding Peer Reviews": "🧑‍💻",
    "AI News": "📰", "Customer Support": "🎧", "Personal Finance Advisor": "💰", "AI Tutor": "🎓",
    "AI Research Assistant": "🔬", "AI Therapist": "🌿", "Recipe Generator": "🍳",
    "AI Personal Assistant": "🗂️",
}


def get_meta(usecase):
    if usecase in USECASE_META:
        return USECASE_META[usecase]
    return {
        "icon": OTHER_ICONS.get(usecase, "🧩"),
        "tagline": "This agent is on the roadmap and isn't wired up yet.",
        "welcome": "Coming soon",
        "placeholder": "This agent isn't available yet",
        "flow": [],
        "suggestions": [],
    }


def history_key(usecase):
    return f"chat_history::{usecase}"


def get_history(usecase):
    key = history_key(usecase)
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def get_readiness(user_controls):
    """Returns (is_ready, reason) for the current sidebar configuration."""
    usecase = user_controls.get("selected_usecase")
    if usecase not in IMPLEMENTED_USECASES:
        return False, f"**{usecase}** is coming soon. Pick an available agent from the sidebar to start chatting."
    if user_controls.get("selected_llm") == "Groq" and not (
        user_controls.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    ):
        return False, "Add your **Groq API key** in the sidebar to start chatting."
    if usecase == "Chatbot with Tools" and not (
        user_controls.get("TAVILY_API_KEY") or os.environ.get("TAVILY_API_KEY")
    ):
        return False, "Add your **Tavily API key** in the sidebar to enable web search."
    return True, ""


def _queue_prompt(prompt):
    st.session_state["pending_prompt"] = prompt


def _clear_history(usecase):
    st.session_state[history_key(usecase)] = []


def _badge(kind, text):
    return f'<span class="status {kind}">{text}</span>'


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def intialize_session(self):
        return {
            "current_step" : "requirements",
            "requirements" : "",
            "user_stories" : "",
            "po_feedback" : "",
            "generated_code" : "",
            "review_feedback" : "",
            "decision" : None
        }

    def load_streamlit_ui(self):
        st.set_page_config(
            page_title="Agentic AI Studio · " + self.config.get_page_title(),
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        st.session_state.timeframe = ''
        st.session_state.IsFetchButtonClicked = False
        st.session_state.IsSDLC = False

        with st.sidebar:
            st.markdown(
                f"""<div class="side-brand">
                        <div class="logo">🤖</div>
                        <div><div class="name">Agentic AI Studio</div>
                        <div class="sub">{html.escape(self.config.get_page_title())}</div></div>
                    </div>""",
                unsafe_allow_html=True,
            )

            #Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # ---------- Agent selection ----------
            st.markdown('<div class="side-section">Agent</div>', unsafe_allow_html=True)

            def _fmt(option):
                label = f"{get_meta(option)['icon']}  {option}"
                return label if option in IMPLEMENTED_USECASES else f"{label}  · soon"

            self.user_controls["selected_usecase"] = st.selectbox(
                "Use case", usecase_options, format_func=_fmt
            )
            usecase = self.user_controls["selected_usecase"]
            st.caption(get_meta(usecase)["tagline"])
            if usecase not in IMPLEMENTED_USECASES:
                st.markdown(_badge("soon", "Coming soon"), unsafe_allow_html=True)

            # ---------- Model ----------
            st.markdown('<div class="side-section">Model</div>', unsafe_allow_html=True)

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("LLM provider", llm_options)

            if self.user_controls["selected_llm"] == "Groq":
                #Model Selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Model", model_options)
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input(
                    "Groq API key", type="password", placeholder="gsk_…",
                    help="Your key is only kept in this browser session.",
                )

                #API key validation
                if self.user_controls["GROQ_API_KEY"]:
                    st.markdown(_badge("ok", "Groq connected"), unsafe_allow_html=True)
                else:
                    st.markdown(
                        _badge("warn", 'Key required · <a href="https://console.groq.com/keys" target="_blank">get one</a>'),
                        unsafe_allow_html=True,
                    )

            if usecase == "Chatbot with Tools":
                st.markdown('<div class="side-section">Tools</div>', unsafe_allow_html=True)
                # API key input
                self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input(
                    "Tavily API key", type="password", placeholder="tvly-…",
                    help="Used by the web-search tool.",
                )
                if self.user_controls["TAVILY_API_KEY"]:
                    os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"]

                # validation of API key
                if self.user_controls["TAVILY_API_KEY"]:
                    st.markdown(_badge("ok", "Web search enabled"), unsafe_allow_html=True)
                else:
                    st.markdown(
                        _badge("warn", 'Key required · <a href="https://app.tavily.com/home" target="_blank">get one</a>'),
                        unsafe_allow_html=True,
                    )

            if "state" not in st.session_state:
                st.session_state.state = self.intialize_session()

            # ---------- Conversation ----------
            st.markdown('<div class="side-section">Conversation</div>', unsafe_allow_html=True)
            st.caption("Each agent keeps its own chat history for this session.")
            st.button(
                "🗑️  Clear conversation", on_click=_clear_history, args=(usecase,),
                key="clear_chat",
            )

            st.markdown(
                '<div class="side-footer">Built with LangGraph · Groq · Streamlit</div>',
                unsafe_allow_html=True,
            )

        self._render_hero(usecase)
        return self.user_controls

    def _render_hero(self, usecase):
        meta = get_meta(usecase)
        model = self.user_controls.get("selected_groq_model") or self.user_controls.get("selected_llm", "")
        st.markdown(
            f"""<div class="hero">
                    <div class="hero-icon">{meta['icon']}</div>
                    <div class="hero-text">
                        <div class="hero-title">{html.escape(usecase)}</div>
                        <div class="hero-sub">{html.escape(meta['tagline'])}</div>
                    </div>
                    <div class="hero-pill">⚡ {html.escape(model)}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    def render_welcome(self, usecase, ready, reason):
        """Empty-state screen with suggested prompts."""
        meta = get_meta(usecase)
        flow_html = ""
        if meta["flow"]:
            parts = '<span class="arrow">→</span>'.join(
                f'<span class="step">{html.escape(s)}</span>' for s in meta["flow"]
            )
            flow_html = f'<div class="flow">{parts}</div>'
        st.markdown(
            f"""<div class="welcome">
                    <div class="big">{meta['icon']}</div>
                    <div class="title">{html.escape(meta['welcome'])}</div>
                    <div class="sub">{html.escape(meta['tagline'])}</div>
                    {flow_html}
                </div>""",
            unsafe_allow_html=True,
        )

        if not ready:
            st.info(reason, icon="🔑" if usecase in IMPLEMENTED_USECASES else "🛠️")

        if meta["suggestions"]:
            st.markdown('<div class="try-label">Try one of these</div>', unsafe_allow_html=True)
            cols = st.columns(2)
            for i, prompt in enumerate(meta["suggestions"]):
                with cols[i % 2]:
                    st.button(
                        prompt, key=f"suggest_{usecase}_{i}", on_click=_queue_prompt,
                        args=(prompt,), disabled=not ready,
                    )
