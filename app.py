"""Streamlit entry point for the LLM Chat-bot project."""

import streamlit as st

from config.settings import APP_NAME, DEFAULT_MODEL, MODEL_CONFIGS
from prompts.preset_prompts import PRESET_PROMPTS
from services.chat_service import ChatService


@st.cache_resource
def get_chat_service() -> ChatService:
    """Create one chat service instance for the Streamlit process."""
    return ChatService()


def clean_username(username: str) -> str:
    """Normalize the sidebar username."""
    return username.strip() or "demo_user"


def conversation_label(conversation) -> str:
    """Build a compact label for the history selector."""
    return f"{conversation['title']} | {conversation['model_name']} | {conversation['role_name']}"


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon=":speech_balloon:", layout="wide")

    service = get_chat_service()

    with st.sidebar:
        st.header("Chat Settings")
        username = clean_username(st.text_input("Username", value="demo_user"))

        if st.session_state.get("active_username") != username:
            st.session_state.active_username = username
            st.session_state.current_conversation_id = None

        conversations = service.list_conversations(username)
        if not conversations:
            st.session_state.current_conversation_id = service.create_conversation(
                username=username,
                model_name=DEFAULT_MODEL,
                role_name="普通助手",
            )
            conversations = service.list_conversations(username)

        conversation_ids = [row["id"] for row in conversations]
        current_id = st.session_state.get("current_conversation_id")
        if current_id not in conversation_ids:
            current_id = conversation_ids[0]
            st.session_state.current_conversation_id = current_id

        current_conversation = service.get_conversation(username, current_id)
        if current_conversation is None:
            st.session_state.current_conversation_id = None
            st.rerun()

        model_names = list(MODEL_CONFIGS.keys())
        role_names = list(PRESET_PROMPTS.keys())
        current_model = current_conversation["model_name"]
        current_role = current_conversation["role_name"]

        model_choice = st.selectbox(
            "Model",
            options=model_names,
            index=model_names.index(current_model)
            if current_model in model_names
            else model_names.index(DEFAULT_MODEL),
        )
        role_choice = st.selectbox(
            "Role",
            options=role_names,
            index=role_names.index(current_role) if current_role in role_names else 0,
        )

        if model_choice != current_model or role_choice != current_role:
            service.update_settings(current_id, model_choice, role_choice)
            st.rerun()

        if st.button("New conversation", use_container_width=True):
            st.session_state.current_conversation_id = service.create_conversation(
                username=username,
                model_name=model_choice,
                role_name=role_choice,
            )
            st.rerun()

        st.divider()
        st.subheader("History")
        selected_conversation_id = st.selectbox(
            "Conversations",
            options=conversation_ids,
            index=conversation_ids.index(current_id),
            format_func=lambda item_id: conversation_label(
                next(row for row in conversations if row["id"] == item_id)
            ),
            label_visibility="collapsed",
        )
        if selected_conversation_id != current_id:
            st.session_state.current_conversation_id = selected_conversation_id
            st.rerun()

        st.divider()
        st.subheader("Title")
        new_title = st.text_input("Conversation title", value=current_conversation["title"])
        if st.button("Rename", use_container_width=True):
            service.rename_conversation(current_id, new_title)
            st.rerun()

    current_id = st.session_state.current_conversation_id
    current_conversation = service.get_conversation(username, current_id)
    messages = service.get_messages(current_id)

    st.title(current_conversation["title"])
    st.caption(
        f"User: {username} | Model: {current_conversation['model_name']} | Role: {current_conversation['role_name']}"
    )

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask anything...")
    if user_message:
        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_reply = ""
            for chunk in service.send_message_stream(username, current_id, user_message):
                full_reply += chunk
                placeholder.markdown(full_reply)

        st.rerun()


if __name__ == "__main__":
    main()
