import pytest

def filter_by_collection(at):

    word = "Message 1"

    # at admin dahsboard:
    at.sidebar.button("change_database_collection_btn").click().run()
    at.sidebar.selectbox("change_database_collection_selectbox").select("Test").run()
    at.sidebar.button("submit_collection_btn").click().run()
    
    assert at.success[0].value == "Show chats form Test"
    assert at.session_state.selected_db_collection == "chats-test"
    assert at.session_state.conversations[0]["_id"] == at.session_state.selected_conversation
    assert (
            any(
                word.lower() in message["text"].lower()
                for chat in at.session_state.conversations
                for message in chat["messages"]
            )
        )

    at.sidebar.selectbox("change_database_collection_selectbox").select("Production").run()
    at.sidebar.button("submit_collection_btn").click().run()
    
    assert at.session_state.selected_db_collection == "chats"
    assert at.success[0].value == "Show chats form Production"
    assert at.session_state.conversations[0]["_id"] == at.session_state.selected_conversation
    assert not(
            all (
                word.lower() in message["text"].lower()
                for chat in at.session_state.conversations
                for message in chat["messages"]
            )
        )

    at.sidebar.selectbox("change_database_collection_selectbox").select("Development").run()
    at.sidebar.button("submit_collection_btn").click().run()
    
    assert at.success[0].value == "Show chats form Development"
    assert at.session_state.selected_db_collection == "chats-dev"
    assert at.session_state.conversations[0]["_id"] == at.session_state.selected_conversation
    assert not(
            all (
                word.lower() in message["text"].lower()
                for chat in at.session_state.conversations
                for message in chat["messages"]
            )
        )
    at.button[10]
