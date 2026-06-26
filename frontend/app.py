"""
Streamlit chat UI for the Procurement Agent API.

Run the API first:
    uvicorn main:app --reload

Then start this app:
    streamlit run app.py
"""

import os
import uuid

import httpx
import streamlit as st

DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def init_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_agent" not in st.session_state:
        st.session_state.active_agent = "orchestrator"
    if "bootstrapped" not in st.session_state:
        st.session_state.bootstrapped = False


def check_health(api_url: str) -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{api_url.rstrip('/')}/health")
            resp.raise_for_status()
            return True, resp.json().get("status", "ok")
    except Exception as exc:
        return False, str(exc)


def send_chat(api_url: str, session_id: str, message: str) -> dict:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{api_url.rstrip('/')}/chat",
            json={"session_id": session_id, "message": message},
        )
        if resp.status_code == 400:
            raise ValueError(resp.json().get("detail", "Bad request"))
        resp.raise_for_status()
        return resp.json()


def reset_session(api_url: str, session_id: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(f"{api_url.rstrip('/')}/reset/{session_id}")
        resp.raise_for_status()


def append_assistant_turn(reply: str, active_agent: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.active_agent = active_agent


def bootstrap_conversation(api_url: str) -> None:
    """Send the initial 'start' message, matching the CLI entry point."""
    try:
        data = send_chat(api_url, st.session_state.session_id, "start")
        append_assistant_turn(data["reply"], data["active_agent"])
        st.session_state.bootstrapped = True
    except Exception as exc:
        st.error(f"Could not start conversation: {exc}")


def handle_user_message(api_url: str, user_text: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_text})
    try:
        with st.spinner("Thinking…"):
            data = send_chat(api_url, st.session_state.session_id, user_text)
        append_assistant_turn(data["reply"], data["active_agent"])
    except Exception as exc:
        st.session_state.messages.pop()
        st.error(f"Request failed: {exc}")


def render_sidebar(api_url: str) -> str:
    with st.sidebar:
        st.title("Settings")
        api_url_input = st.text_input("API URL", value=api_url, help="Base URL of the FastAPI server")

        healthy, detail = check_health(api_url_input)
        if healthy:
            st.success("API connected")
        else:
            st.error("API unreachable")
            st.caption(detail)

        st.divider()
        st.caption("Session")
        st.code(st.session_state.session_id, language=None)
        st.caption(f"Active agent: **{st.session_state.active_agent}**")

        if st.button("New conversation", use_container_width=True):
            try:
                reset_session(api_url_input, st.session_state.session_id)
            except Exception:
                pass
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.active_agent = "orchestrator"
            st.session_state.bootstrapped = False
            st.rerun()

        st.divider()
        st.markdown(
            "**Agents**\n"
            "- **orchestrator** — gathers procurement details\n"
            "- **renewable** — renewal orders\n"
            "- **non_renewable** — new purchases"
        )

    return api_url_input


def main() -> None:
    st.set_page_config(
        page_title="Procurement Agent",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    api_url = render_sidebar(DEFAULT_API_URL)

    st.title("Procurement Agent")
    st.caption("Chat with the procurement assistant to place or renew orders.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.bootstrapped:
        if check_health(api_url)[0]:
            bootstrap_conversation(api_url)
            st.rerun()
        else:
            st.info("Start the API with `uvicorn main:app --reload`, then refresh this page.")

    if prompt := st.chat_input("Type your message…"):
        handle_user_message(api_url, prompt)
        st.rerun()


if __name__ == "__main__":
    main()
