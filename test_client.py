import os
import time
import json
import requests
import streamlit as st

import urllib3

import pymongo
from bson import ObjectId
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVER_URL = os.environ.get('SERVER_URL')
MONGODB_URL = os.environ.get("MONGODB_URL")

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client['llamaindex']  # Replace with your database name
chats = db['chats']
ip = ''
try:
    response = requests.get('https://api.ipify.org?format=json')
    ip_data = response.json()
    ip = ip_data['ip']
except requests.RequestException as e:
    st.error("refresh please")


st.title('Model Instruction')
template = st.text_input('Enter Model Instruction: ')
search_prompt = st.text_input('Enter Model Instruction for prompt refinement: ')

st.title('Chat Interface')
user_input = st.text_input('Enter your message:')

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


if st.button('Send', key='send_button'):
	start_time = datetime.now()
	data = {'user_input': user_input,'template': template, 'search_prompt':search_prompt}
	res = requests.post(f'{SERVER_URL}/process', json=data, verify=False)

	if res.status_code == 200:
		result = res.json()
		context = result.get("context","")
		print()
		print(context)
		print()
		response = result.get('response', '')
		response_query = result.get('response_query', '')
		query_time = result.get('query_time', '')
		st.write("### context")
		st.write(json.dumps(context))
		st.write("### response")
		st.write(response)
		st.write("### Gpt Generated search")
		st.write(response_query)
		st.write("### time took to generate")
		st.write(f"{query_time} seconds")
		inserted_id = ''
		while True:
			try:
				chat_document = {
					"_id": ObjectId(),  # Generates a unique Object ID
					"user_ip": ip,  # Example IP address
					"user_device": "Desktop",  # Example device type
					"category": "General",
					"subcategory": "Example",
					"start_time": datetime.now(),
					"end_time": datetime.now(),
					"messages": [
						{
							"timestamp": datetime.now(),
							"sender": f"user - {str(ip)}",
							"text": user_input
						},
						{
							"timestamp": datetime.now(),
							"sender": "bot",
							"text": response
						}
					],
					"prompts": {
						"template_prompt": template,
						"search_prompt": search_prompt,
						"response_query": response_query
					},
					"product_references": [
						{
							"name": "Example Product",
							"description": "This is an example product description.",
							"price": 19.99,
							"category": "Electronics"
						}
					]
				}

				# Insert the document into the 'chats' collection
				insert_result = chats.insert_one(chat_document)
				# Get the _id of the inserted document
				inserted_id = insert_result.inserted_id

				break
			except Exception as e:
				time.sleep(1)

		st.write("## Feedback")
		new_feedback_text = st.text_input('Enter Your Feedback: ')
		if st.button('Send Feedback', key='send_feedback_button'):
			try:
				# Create 'user_actions' with 'feedback_text'
				new_values = {"user_actions": {"feedback_text": new_feedback_text}}
				# Perform the update
				update_result = chats.update_one({"_id": inserted_id}, {"$set": new_values})

				# Check if the update was successful
				if update_result.modified_count > 0:
					st.write("Document updated successfully.")
				else:
					st.error("No document was updated.")
			except Exception as e:
				st.error("No document was updated.")
				st.error(str(e))

	else:
		st.error('Failed to get a response from the server.')
