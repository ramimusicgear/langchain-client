import streamlit as st
import requests

SERVER_URL = 'https://82.80.25.207:5000'  # Replace with your server's URL

st.title('Chat Interface')

user_input = st.text_input('Enter your message:')

if st.button('Send'):
	data = {'user_input': user_input}
	response = requests.post(f'{SERVER_URL}/process', json=data)

	if response.status_code == 200:
		result = response.json()
		st.write("### response")
		st.write(result.get('response', ''))
		st.write("### Gpt Generated search")
		st.write(result.get('response_query', ''))
		st.write("### time took to generate")
		st.write(result.get('query_time ', '') + " seconds")
	else:
		st.error('Failed to get a response from the server.')
