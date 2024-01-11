import streamlit as st
from lib import get_selected, get_all


def admin_page(select, navigate_to):
    st.sidebar.button("Back to Chat", key='back_btn', on_click=lambda: navigate_to('chat'))
    st.sidebar.write("# Conversations")
    
    conversations = get_all()
    last_id = ''
    
    for conv in conversations:
        conversation_id = conv['_id']
        if last_id == '':
            last_id = conversation_id
        first_message_text = conv['messages'][0]['text']
        id = st.session_state.selected_conversation if st.session_state.selected_conversation else last_id
        if conversation_id == id:
            st.sidebar.markdown(f"<p>{first_message_text}</p>", unsafe_allow_html=True)
        else:
            button_clicked = st.sidebar.button(first_message_text, key=f"{conversation_id}", on_click=lambda cid=conversation_id: select(cid))
            
            if button_clicked:
                st.session_state.selected_conversation = conversation_id

    
    conv = get_selected(st.session_state.selected_conversation if st.session_state.selected_conversation else last_id)
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
    
    st.write("### Enter your message:")
    st.markdown(f"<p>{conv['messages'][0]['text']}</p>", unsafe_allow_html=True)


    st.write("### Response")
    st.markdown(f"<p>{conv['messages'][1]['text']}</p>", unsafe_allow_html=True)

    st.write("### Gpt Generated Search")
    st.write(conv['prompts']['search_prompt'])
    st.markdown(f"<p>{conv['prompts']['search_prompt']}</p>", unsafe_allow_html=True)
    
    try:
        conv['user_actions']
        st.write("## Feedback")
        st.markdown(f"<p>{conv['user_actions']['feedback_text']}</p>", unsafe_allow_html=True)
        st.write(conv['user_actions']['feedback_text'])
        st.write(f"# The Feedback Is From - {conv['user_actions']['sender']}")
    except Exception as e:
        st.write("## No Feedback")