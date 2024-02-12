import streamlit as st
from datetime import datetime

from db import get_selected, get_feedback_sender_names, get_all_filtered


def get_card_color(user_actions):
    backend_version = user_actions.get("backend_version", "0")
    if backend_version == "0":
        return "white"  # default to light gray if no match

    overall_rate = user_actions.get("overall_rate", "0")

    colors = {
        "good": "#90ee90",  # light green
        "okay": "#ffcc99",  # light orange
        "bad": "#ff9999",  # light red
        "0": "#d3d3d3",  # light gray
    }

    return colors.get(overall_rate, "#d3d3d3")  # default to light gray if no match


def admin_page(
    navigate_to, select, show_hide_filters, change_filtes, change_active_tab
):
    st.sidebar.button(
        "Back to Chat", key="back_btn", on_click=lambda: navigate_to("chat")
    )
    st.sidebar.write("# Conversations")

    # Filter Button
    st.sidebar.button("Filter Conversations", on_click=show_hide_filters)

    # Popup for Filtering
    if st.session_state.get("show_filter_popup", False):
        with st.sidebar:
            with st.expander("Filter Options", expanded=True):
                filters = {}
                print()
                # categories, sub_categories, backend_versions, feedback_sender_names = get_data()
                # Define the tab titles
                tab_titles = ["Filtering", "Feedback Filtering"]

                # Render tabs in the sidebar and assign callbacks to manage active tab state
                tabs = st.sidebar.tabs(tab_titles)

                # Depending on the active tab stored in session state, display content for that tab
                with tabs[0]:
                    change_active_tab(tab_titles[0])
                    if st.session_state.active_tab == tab_titles[0]:
                        with st.container(border=True):
                            # Category Selection

                            # Define the categories and sub-categories
                            categories = {
                                "Guitars & Basses": [
                                    "Electric Guitars",
                                    "Acoustic Guitars",
                                    "Classical Guitars",
                                    "Electric Basses",
                                    "Acoustic & Semi-Acoustic Basses",
                                    "Ukuleles",
                                    "Guitar/Bass Accessories",
                                    "Bluegrass Instruments",
                                    "Strings",
                                    "Guitar & Bass Spare Parts",
                                    "Pickups",
                                    "Travel Guitars",
                                    "Misc. Stringed Instruments",
                                    "Electric Guitar Amps",
                                    "Bass Amps",
                                    "Guitar & Bass Effects",
                                    "Acoustic Guitar Amps",
                                ],
                                "Keys": [
                                    "Keyboards",
                                    "Keyboard Amps",
                                    "Synthesizers",
                                    "Piano Accessories",
                                    "MIDI Master Keyboards",
                                    "Stage Pianos",
                                    "Digital Pianos",
                                    "Electric Organs",
                                    "Classical Organs",
                                ],
                            }
                            # Multi-select widget for categories
                            selected_categories = st.multiselect(
                                "Select Categories",
                                options=list(categories.keys()),
                                key="categories_select",
                            )

                            # Add filter options here

                            # Display subcategories based on the selected categories
                            subcategories_options = [
                                subcategory
                                for category in selected_categories
                                for subcategory in categories[category]
                            ]
                            selected_subcategories = st.multiselect(
                                "Select Subcategories:",
                                options=subcategories_options,
                                key="subcategories_select_in_form",
                            )

                            # backend version Selection
                            backend_versions = [
                                "0.1.1",
                                "0.1.2",
                            ]  # Update with actual backend version
                            selected_backend_version = st.multiselect(
                                "Select backend version", backend_versions
                            )
                            # Free Text Search
                            search_text = st.text_input("Search Text")
                            # Date Range Selection
                            # date_range = st.slider('Select Date Range', value=(min_date, max_date))  # Set min_date and max_date
                            # Submit Filtering Button
                            # if f.form_submit_button("No Filters"):
                            #     st.session_state.show_filter_popup = False
                            filters["categories"] = selected_categories
                            filters["subcategories"] = selected_subcategories
                            print(filters)
                            print()
                            filte = {
                                "categories": selected_categories,
                                "subcategories": selected_subcategories,
                                # "free_text_inside_the_messages": free_text_inside_the_messages,
                                # "date_range": date_range,
                                # "backend_version": backend_version,
                                # "reviewer_name": reviewer_name,
                                # "free_text_inside_the_user_actions": free_text_inside_the_user_actions,
                                # "overall_rating": overall_rating,
                                # "price_rating": price_rating,
                                # "product_rating": product_rating,
                                # "demands_rating": demands_rating,
                                # "phraise_rating": phraise_rating,
                            }
                            st.button(
                                "Submit",
                                key="submit_filters_btn",
                                on_click=lambda: change_filtes(filters),
                            )
                            button_clicked = st.button(
                                "No Filters",
                                key="no_filters_btn",
                                on_click=show_hide_filters,
                            )

                with tabs[1]:
                    change_active_tab(tab_titles[1])
                    if st.session_state.active_tab == tab_titles[1]:
                        feedback_sender_names = get_feedback_sender_names()
                        with st.container(border=True):
                            with_or_without = st.selectbox(
                                "With/Without Feedback",
                                [
                                    "All Chats",
                                    "Only Chats With Feedback",
                                    "Only Chats Without Feedback",
                                ],
                            )

                            # Update with actual sender names
                            selected_senders = st.multiselect(
                                "Select Sender’s Name", feedback_sender_names
                            )
                            # Free Text Search in Review
                            review_search_text = st.text_input("Search Text in Reviews")
                            # Rating Selections
                            price_match_rating = st.multiselect(
                                "Price Match Rating", ["Good", "Okay", "Bad"]
                            )
                            product_match_rating = st.multiselect(
                                "Product Match Rating", ["Good", "Okay", "Bad"]
                            )
                            recommendation_match_rating = st.multiselect(
                                "Recommendation Match Rating", ["Good", "Okay", "Bad"]
                            )
                            chat_phrasing_rating = st.multiselect(
                                "Chat Phrasing Rating", ["Good", "Okay", "Bad"]
                            )
                            # Submit Advanced Filtering Button
                            filters["feedback"] = with_or_without
                            filters["reviewer_name"] = selected_senders
                            print(filters)
                            print()
                            st.button(
                                "Submit",
                                key="feedback_submit_filters_btn",
                                on_click=lambda: change_filtes(filters),
                            )

    conversations, total_prices = get_all_filtered(st.session_state.filters)
    last_id = ""
    dates = []
    if st.session_state.filters != None:
        st.sidebar.markdown(
            f"<p>Total Conversations: {len(conversations)}</p>", unsafe_allow_html=True
        )

    for conv in conversations:
        conversation_id = conv["_id"]
        first_message_text = (
            conv["messages"][0]["text"] if conv["messages"] else "No messages"
        )
        card_color = get_card_color(conv.get("user_actions", {}))

        if last_id == "":
            last_id = conversation_id

        id = (
            st.session_state.selected_conversation
            if st.session_state.selected_conversation
            else last_id
        )
        d = str(conv["start_time"]).split()[0]

        if d not in dates:
            # st.sidebar.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
            # TODO: show the total price of all chats on the date
            total_price = total_prices.get(d, 0)  # Get total price for the date
            if total_price == 0:
                st.sidebar.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
            else:
                formatted_number = "{:.2f}".format(total_price)
                st.sidebar.markdown(
                    f"<p>Date: {d}, Total Price: {formatted_number} $</p>",
                    unsafe_allow_html=True,
                )
            dates.append(d)
        if conversation_id == id:
            st.sidebar.markdown(
                f"<p><strong>Selected Chat: </strong>{first_message_text}</p>",
                unsafe_allow_html=True,
            )
        else:
            # button_style = f"style='background-color:{card_color}; width:100%; margin-bottom:5px;'"
            # button_html = f"<button type='button' {button_style}>{first_message_text}</button>"
            # st.sidebar.markdown(button_html, unsafe_allow_html=True)
            #     on_click=lambda cid=conversation_id: select(cid),

            button_clicked = st.sidebar.button(
                first_message_text,
                key=f"{conversation_id}_btn",
                on_click=lambda cid=conversation_id: select(str(cid)),
            )
            if button_clicked:
                st.session_state.selected_conversation = conversation_id

    # print(f"selected: {st.session_state.selected_conversation}")
    conv = get_selected(
        st.session_state.selected_conversation
        if st.session_state.selected_conversation
        else last_id
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
