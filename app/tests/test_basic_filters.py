import pytest

def filter_by_basic_filters(at):
   
    # on test collection
    at.sidebar.button("change_database_collection_btn").click().run()
    at.sidebar.selectbox("change_database_collection_selectbox").select("Test").run()
    at.sidebar.button("submit_collection_btn").click().run(timeout=10)
    
    word = "Message 1"
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
    
    # check for Keys
    at.sidebar.button("filter_conversations_btn").click().run()
    at.sidebar.multiselect("categories_multiselect").select("Keys").run()
    at.sidebar.button("submit_basic_filters_btn").click().run(timeout=10)
    assert at.session_state.filters and "Keys" in at.session_state.filters["categories"]
    assert not(
        all(
            chat["category"] == "Guitars & Basses"
            for chat in at.session_state.conversations
        )
    )
    assert (
        all(
            chat["category"] == "Keys"
            for chat in at.session_state.conversations
        )
    )

    # check for Electric Guitars
    at.sidebar.button("filter_conversations_btn").click().run()
    at.sidebar.multiselect("categories_multiselect").select("Guitars & Basses").run()
    at.sidebar.multiselect("subcategories_multiselect").select("Electric Guitars").run()
    at.sidebar.button("submit_basic_filters_btn").click().run(timeout=10)
    assert at.session_state.filters and "Electric Guitars" in at.session_state.filters["subcategories"]
    assert all(
        (
            chat["subcategory"] == "Electric Guitars"
            and chat["category"] != "Keys"
        )
        for chat in at.session_state.conversations
    )

    # check for Electric Guitars backend version 0.0.2
    at.sidebar.button("filter_conversations_btn").click().run()
    at.sidebar.multiselect("versions_multiselect").select("0.0.2").run()
    at.sidebar.multiselect("subcategories_multiselect").select("Electric Guitars").run()
    at.sidebar.button("submit_basic_filters_btn").click().run(timeout=10)
    assert at.session_state.filters and "Electric Guitars" in at.session_state.filters["subcategories"]
    assert at.session_state.filters and "0.0.2" in at.session_state.filters["backend_versions"]
    assert all(
        (
            chat["subcategory"] == "Electric Guitars" and chat["backend_version"] == "0.0.2"
            and chat["category"] != "Keys"
        )
        for chat in at.session_state.conversations
    )


    # after reset

    at.sidebar.button("filter_conversations_btn").click().run()
    at.sidebar.button("no_filters_btn").click().run(timeout=10)

    # check for backend version 0.0.3
    at.sidebar.button("filter_conversations_btn").click().run()
    at.sidebar.multiselect("versions_multiselect").select("0.0.3").run()
    at.sidebar.button("submit_basic_filters_btn").click().run(timeout=10)
    assert at.session_state.filters and "Electric Guitars" not in at.session_state.filters["subcategories"]
    assert at.session_state.filters and "0.0.3" in at.session_state.filters["backend_versions"]
    assert all(
        chat["backend_version"] == "0.0.3"
        for chat in at.session_state.conversations
    )
    at.sidebar.button("change_database_collection_btn").click().run()