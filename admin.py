import streamlit as st
from db import get_selected, get_all

def admin_page(navigate_to, select):
    st.sidebar.button("Back to Chat", key='back_btn', on_click=lambda: navigate_to('chat'))
    st.sidebar.write("# Conversations")
    
    conversations, total_prices = get_all()
    last_id = ''
    dates = []
    for conv in conversations:
        conversation_id = str(conv['_id'])
        if last_id == '':
            last_id = conversation_id
        first_message_text = conv['messages'][0]['text']
        id = st.session_state.selected_conversation if st.session_state.selected_conversation else last_id
        d = str(conv['start_time']).split()[0]
        if d not in dates: 
            # st.sidebar.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
            # TODO: show the total price of all chats on the date
            total_price = total_prices.get(d, 0)  # Get total price for the date
            if total_price == 0:
                st.sidebar.markdown(f"<p>Date: {d}</p>", unsafe_allow_html=True)
            else:
                formatted_number = "{:.2f}".format(total_price)
                st.sidebar.markdown(f"<p>Date: {d}, Total Price: {formatted_number} $</p>", unsafe_allow_html=True)
            dates.append(d)
        if conversation_id == id:
            st.sidebar.markdown(f"<p><strong>Selected Chat: </strong>{first_message_text}</p>", unsafe_allow_html=True)
        else:
            try:
                if conv['user_actions']:
                    first_message_text = f"with feedback: " + first_message_text
            except Exception as e:
                pass
            button_clicked = st.sidebar.button(first_message_text, key=f"{conversation_id}_btn", on_click=lambda cid=conversation_id: select(cid))
            if button_clicked:
                st.session_state.selected_conversation = conversation_id

    # print(f"selected: {st.session_state.selected_conversation}")
    conv = get_selected(st.session_state.selected_conversation if st.session_state.selected_conversation else last_id)
    if conv is None:
        st.write("### Please select a conversation")
    else:
        toggle_button = st.checkbox("Show Model Instruction")
        if toggle_button:
            # Model Instruction
            st.write("### Model Instruction")
            st.write("#### Template:")
            st.markdown(f"<p>{conv['prompts']['template_prompt']}</p>", unsafe_allow_html=True)

            st.write("#### Prompt Refinement:")
            st.markdown(f"<p>{conv['prompts']['search_prompt']}</p>", unsafe_allow_html=True)

        # Chat Interface
        st.title('Chat Interface')
        for idx, msg in enumerate(conv['messages']):
            # st.markdown(f'<p><strong>{"client: " if idx % 2 == 0 else "bot: "}</strong>{msg['text']}</p>', unsafe_allow_html=True)
            st.markdown(f"<p><strong>{'client: ' if idx % 2 == 0 else 'bot: '}</strong>{msg['text']}</p>", unsafe_allow_html=True)

        try:
            conv['price']
            formatted_number = "{:.2f}".format(conv['price'])
            st.write("## Price")
            st.markdown(f"<p><strong>{formatted_number} $</strong></p>", unsafe_allow_html=True)
        except Exception as e:
            pass

        with_feedback = False
        try:
            conv['user_actions']
            st.write("## Feedback")
            with_feedback = True
        except Exception as e:
            st.write("## No Feedback")
            with_feedback = False
        if with_feedback:
            try:
                conv['user_actions']['price']
                st.write("##### Rate pricing match")
                st.markdown(f"<p>Rate: {conv['user_actions']['price']['rating']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{conv['user_actions']['price']['reason']}</p>", unsafe_allow_html=True)
                
                st.write("##### Rate product match")
                st.markdown(f"<p>Rate: {conv['user_actions']['product']['rating']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{conv['user_actions']['product']['reason']}</p>", unsafe_allow_html=True)
                
                st.write("##### Rate demands match")
                st.markdown(f"<p>Rate: {conv['user_actions']['demands']['rating']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{conv['user_actions']['demands']['reason']}</p>", unsafe_allow_html=True)
                
                st.write("##### Rate phrasing")
                st.markdown(f"<p>Rate: {conv['user_actions']['phraise']['rating']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{conv['user_actions']['phraise']['reason']}</p>", unsafe_allow_html=True)
                
                st.write("##### Do you have anything else you would like to add?")
                st.markdown(f"<p>{conv['user_actions']['other']}</p>", unsafe_allow_html=True)
                
                st.write(f"### The Feedback Is From - {conv['user_actions']['name']}")
            except Exception as e:
                try:
                    conv['user_actions']['feedback_text']
                    st.write("##### Feedback Text")
                    st.markdown(f"<p>{conv['user_actions']['feedback_text']}</p>", unsafe_allow_html=True)
                    
                    st.write(f"### The Feedback Is From - {conv['user_actions']['sender']}")
                except Exception as e:
                    pass
                
