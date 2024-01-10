import os
import time
import bson
import requests
import streamlit as st

import pymongo
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

SERVER_URL = os.environ.get('SERVER_URL')
MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
# client = pymongo.MongoClient(MONGODB_URL)
# db = client['llamaindex']  # Replace with your database name
# chats = db['chats']


st.title('Chat Interface')


user_input = st.text_input('Enter your message:')

template = st.text_input('Enter Model Instruction: ')
search_prompt = st.text_input('Enter Model Instruction for prompt refinement: ')

if not template:
	template = "You are an assistant you help customers choose products using the given context (use only what is relevent) your output should be nicely phrased:"

if not search_prompt:
	search_prompt = """
	Using the Following question 
	create a prompt which will be searched in the vector dataset
    the prompt will help find the optimal search results for the given queston
    you can alter the question to get more fitting products
	"""

st.sidebar.write("### template")
st.sidebar.write(template)
st.sidebar.write("### search prompt")
st.sidebar.write(search_prompt)


if st.button('Send'):
	start_time = datetime.now()
	data = {'user_input': user_input,'template': template, 'search_prompt':search_prompt}
	response = requests.post(f'{SERVER_URL}/process', json=data)

	if response.status_code == 200:
		result = response.json()
		context = result.get("context","")
		st.write("### response")
		st.write(result.get('response', ''))
		st.write("### Gpt Generated search")
		st.write(result.get('response_query', ''))
		st.write("### time took to generate")
		st.write(f"{result.get('query_time', '')} seconds")
		while True:
			try:
				chat_document = {
					"_id": bson.ObjectId(),  # Unique identifier for the chat
					# "category": ,  # Category or identification of the chat
					# "subcategory": ,  # Subategory or identification of the chat
					"start_time": start_time,  # Start time of the conversation
					"end_time": datetime.now(), 
					"messages":[]
				}
				# chats.insert_one(chat_document)
				break
			except Exception as e:
				time.sleep(1)

	else:
		st.error('Failed to get a response from the server.')
