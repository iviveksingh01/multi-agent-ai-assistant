import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json
import html
from datetime import datetime
from urllib.parse import urlparse

from src.AgenticAI.UserInterface.StreamlitUI.loadUI import get_history

GREETINGS = {"hello", "hi", "hey", "hello!"}

TRAVEL_STEP_LABELS = {
    "orchestrator": "🗺️ Orchestrator planned the itinerary structure",
    "llm_call": "✍️ Writer drafted a section",
    "evaluator": "🧪 Evaluator ran quality checks",
    "in_human": "👀 Review step applied feedback",
    "synthesizer": "📦 Synthesizer assembled the final plan",
}


def _now():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


# ----------------------------------------------------------------------------
# Rendering helpers (used for both live answers and chat history)
# ----------------------------------------------------------------------------

def _parse_tool_payload(content):
    data = content
    if isinstance(content, str):
        try:
            data = json.loads(content)
        except Exception:
            return {"raw": content}
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        data = data["results"]
    if isinstance(data, list) and data and all(isinstance(d, dict) for d in data):
        return {"sources": [
            {
                "title": d.get("title") or d.get("url") or "Source",
                "url": d.get("url", ""),
                "snippet": str(d.get("content") or d.get("snippet") or "")[:300],
            }
            for d in data
        ]}
    return {"raw": data if isinstance(data, str) else json.dumps(data, indent=2, default=str)}


def _render_tool_calls(tools):
    n_sources = sum(len(t.get("sources", [])) for t in tools)
    label = f"🔎 Searched the web · {n_sources} source{'s' if n_sources != 1 else ''}" if n_sources \
        else f"🔧 Used {len(tools)} tool call{'s' if len(tools) != 1 else ''}"
    with st.expander(label, expanded=False):
        for tool in tools:
            if tool.get("sources"):
                for s in tool["sources"]:
                    url = s["url"]
                    host = urlparse(url).netloc.replace("www.", "") if url else ""
                    st.markdown(
                        f"""<div class="src">
                                <a href="{html.escape(url, quote=True)}" target="_blank">{html.escape(s['title'])}</a>
                                <div class="host">{html.escape(host)}</div>
                                <div class="snip">{html.escape(s['snippet'])}{'…' if len(s['snippet']) >= 300 else ''}</div>
                            </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.code(str(tool.get("raw", ""))[:4000], language="json")


def _render_travel(data, key):
    if data.get("response"):
        st.markdown('<div class="notice">🚨 <b>Travel Specialist Notice</b></div>', unsafe_allow_html=True)
        st.markdown(data["response"])
        return

    sections = data.get("sections", [])
    drafts = data.get("completed_sections", [])
    passed = data.get("evaluator_passed")
    final = data.get("final_report")

    c1, c2, c3 = st.columns(3)
    c1.metric("Itinerary sections", len(sections))
    c2.metric("Drafts written", len(drafts))
    c3.metric("Quality check", "—" if passed is None else ("Passed ✅" if passed else "Needs work ❌"))

    tab_plan, tab_blueprint, tab_drafts = st.tabs(["🌟 Travel plan", "📋 Blueprint", "📄 Drafts"])

    with tab_plan:
        if final:
            plan_md = "\n\n".join(final) if isinstance(final, list) else str(final)
            st.markdown(plan_md)
            st.download_button(
                "⬇️  Download plan (.md)", plan_md, file_name="travel_plan.md",
                mime="text/markdown", key=f"dl_{key}",
            )
        else:
            st.info("No final plan was produced for this request.")

    with tab_blueprint:
        if sections:
            for i, sec in enumerate(sections, 1):
                st.markdown(f"**{i}. {sec.get('name', 'Section')}**")
                if sec.get("description"):
                    st.caption(sec["description"])
        else:
            st.caption("No blueprint available.")

    with tab_drafts:
        if drafts:
            for i, content in enumerate(drafts):
                name = sections[i]["name"] if i < len(sections) else f"Section {i + 1}"
                with st.expander(f"{i + 1}. {name}", expanded=False):
                    st.caption(f"{len(content)} characters")
                    st.markdown(content)
        else:
            st.caption("No drafts available.")


def _render_body(entry, key):
    if entry.get("kind") == "travel":
        _render_travel(entry["data"], key)
    else:
        if entry.get("tools"):
            _render_tool_calls(entry["tools"])
        st.markdown(entry.get("content", ""))
    if entry.get("time"):
        st.caption(entry["time"])


def render_entry(entry, key):
    with st.chat_message(entry["role"]):
        _render_body(entry, key)


def render_history(usecase):
    for i, entry in enumerate(get_history(usecase)):
        render_entry(entry, f"{usecase}_{i}")


# ----------------------------------------------------------------------------
# Live execution
# ----------------------------------------------------------------------------

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message
        history = get_history(usecase)
        key = f"{usecase}_{len(history) + 1}"

        user_entry = {"role": "user", "content": user_message, "time": _now()}
        render_entry(user_entry, f"{usecase}_{len(history)}")
        history.append(user_entry)

        if usecase == "Basic Chatbot":
            # Basic chatbot implementation
            with st.chat_message("assistant"):
                content = ""
                with st.spinner("Thinking…"):
                    for event in graph.stream({"messages": ("user", user_message)}):
                        for value in event.values():
                            content = value["messages"].content
                entry = {"role": "assistant", "content": content, "time": _now()}
                _render_body(entry, key)
            history.append(entry)

        elif usecase == "Chatbot with Tools":
            # Tool-enabled chatbot implementation
            with st.chat_message("assistant"):
                with st.spinner("Searching the web and reasoning…"):
                    initial_state = {"messages": [user_message]}
                    res = graph.invoke(initial_state)
                tools, answers = [], []
                for message in res["messages"]:
                    if isinstance(message, ToolMessage):
                        tools.append(_parse_tool_payload(message.content))
                    elif isinstance(message, AIMessage) and message.content:
                        answers.append(message.content)
                entry = {
                    "role": "assistant",
                    "content": "\n\n".join(answers) or "_No answer was returned._",
                    "tools": tools,
                    "time": _now(),
                }
                _render_body(entry, key)
            history.append(entry)

        elif usecase == "Travel Planner":
            initial_state = {"topic": user_message}

            # Handle greetings and non-travel queries
            if initial_state["topic"].lower().strip() in GREETINGS:
                entry = {
                    "role": "assistant",
                    "content": "👋 **Hello! I'm your AI Travel Assistant.** Let's plan your perfect trip!\n\n"
                               "Tell me a destination, how many days, your budget and what you enjoy — "
                               "e.g. *“6 days in Bali for a couple who love beaches and food.”*",
                    "time": _now(),
                }
                render_entry(entry, key)
                history.append(entry)
                return

            with st.chat_message("assistant"):
                state, drafted = None, 0
                with st.status("🌍 Crafting your perfect itinerary…", expanded=True) as status:
                    try:
                        for mode, chunk in graph.stream(initial_state, stream_mode=["updates", "values"]):
                            if mode == "values":
                                state = chunk
                                continue
                            for node in (chunk or {}):
                                if node == "llm_call":
                                    drafted += 1
                                    total = len((state or {}).get("sections", []) or [])
                                    status.write(f"✍️ Writer drafted section {drafted}" + (f" of {total}" if total else ""))
                                elif node in TRAVEL_STEP_LABELS:
                                    status.write(TRAVEL_STEP_LABELS[node])
                    except Exception:
                        status.update(label="Something went wrong while planning", state="error")
                        raise
                    status.update(label="✅ Itinerary ready", state="complete", expanded=False)

                state = state or {}
                data = {
                    "response": state.get("response"),
                    "sections": [
                        {"name": getattr(s, "name", "Section"), "description": getattr(s, "description", "")}
                        for s in state.get("sections", []) or []
                    ],
                    "completed_sections": [str(c) for c in state.get("completed_sections", []) or []],
                    "evaluator_passed": state.get("evaluator_passed"),
                    "final_report": state.get("final_report"),
                }
                entry = {"role": "assistant", "kind": "travel", "data": data, "time": _now()}
                _render_body(entry, key)
            history.append(entry)
