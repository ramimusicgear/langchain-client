import pytest

def filter_by_simple_filters(at):
   
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
