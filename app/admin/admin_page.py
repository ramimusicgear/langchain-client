import streamlit as st

from db import get_selected

from .admin_sidebar import admin_sidebar

def admin_page(cookie_manager):

    admin_sidebar(cookie_manager)
    selected_id = None
    if st.session_state.selected_conversation:
        selected_id = st.session_state.selected_conversation 
    else:
        if len(st.session_state.conversations) != 0:
            st.session_state.conversations[0].get("_id", None)

    conv = get_selected(
        selected_id,
        st.session_state.selected_db_collection,
        st.session_state.jwt
    )
    if conv is None:
        st.write("### Please select a conversation")
    else:
        toggle_button = st.checkbox("Show Model Instruction")
        if toggle_button:
            # Model Instruction
            st.write("### Model Instruction")
            st.write("#### Template:")
            st.markdown(
                f"<p>{conv['prompts']['template_prompt']}</p>", unsafe_allow_html=True
            )

            st.write("#### Prompt Refinement:")
            st.markdown(
                f"<p>{conv['prompts']['search_prompt']}</p>", unsafe_allow_html=True
            )

        # Chat Interface
        st.title("Chat Interface")
        for idx, msg in enumerate(conv["messages"]):
            # st.markdown(f'<p><strong>{"client: " if idx % 2 == 0 else "bot: "}</strong>{msg['text']}</p>', unsafe_allow_html=True)
            st.markdown(
                f"<p><strong>{'client: ' if idx % 2 == 0 else 'bot: '}</strong>{msg['text']}</p>",
                unsafe_allow_html=True,
            )
        try:
            conv["category"] = (
                f"{conv['category']} - "
                if conv["category"] != ""
                else "Backend didn't provide the categories"
            )
            st.write("## categories")
            st.markdown(
                f"<p><strong>{conv['category']}{conv['subcategory']}</strong></p>",
                unsafe_allow_html=True,
            )

        except Exception as e:
            pass

        try:
            conv["price"]
            formatted_number = "{:.2f}".format(conv["price"])
            st.write("## Price")
            st.markdown(
                f"<p><strong>{formatted_number} $</strong></p>", unsafe_allow_html=True
            )
        except Exception as e:
            pass

        with_feedback = False
        try:
            conv["user_actions"]
            st.write("## Feedback")
            with_feedback = True
        except Exception as e:
            st.write("## No Feedback")
            with_feedback = False
        if with_feedback:
            try:
                conv["user_actions"]["price"]
                st.write("##### Rate pricing match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['price']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['price']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate product match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['product']['rating']}</p>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"<p>{conv['user_actions']['product']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate demands match")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['demands']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['demands']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Rate phrasing")
                st.markdown(
                    f"<p>Rate: {conv['user_actions']['phraise']['rating']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p>{conv['user_actions']['phraise']['reason']}</p>",
                    unsafe_allow_html=True,
                )

                st.write("##### Do you have anything else you would like to add?")
                st.markdown(
                    f"<p>{conv['user_actions']['other']}</p>", unsafe_allow_html=True
                )

                st.write(f"### The Feedback Is From - {conv['user_actions']['name']}")
            except Exception as e:
                try:
                    conv["user_actions"]["feedback_text"]
                    st.write("##### Feedback Text")
                    st.markdown(
                        f"<p>{conv['user_actions']['feedback_text']}</p>",
                        unsafe_allow_html=True,
                    )

                    st.write(
                        f"### The Feedback Is From - {conv['user_actions']['sender']}"
                    )
                except Exception as e:
                    pass

            if st.session_state.selected_db_collection == "chats-test":
                collection = "Test"
            if st.session_state.selected_db_collection == "chats-dev":
                collection = "Development"
            if st.session_state.selected_db_collection == "chats":
                collection = "Production"
            
            st.markdown(
                f"<p>Collection: <strong>{collection}</strong></p>", unsafe_allow_html=True
            )