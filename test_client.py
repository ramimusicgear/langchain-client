import os
import re
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


# Initialize session state variables if they don't exist
if 'template' not in st.session_state:
	st.session_state.template = "You are an assistant you help customers choose products using the given context (use only what is relevant) your output should be nicely phrased:"

if 'search_prompt' not in st.session_state:
	st.session_state.search_prompt = """Using the Following question 
	create a prompt which will be searched in the vector dataset
	the prompt will help find the optimal search results for the given question
	you can alter the question to get more fitting products"""

if 'user_input' not in st.session_state:
	st.session_state.user_input = ''

if 'change_instruction' not in st.session_state:
	st.session_state.change_instruction = False

if 'document_id' not in st.session_state:
	st.session_state.document_id = ''


# Sidebar
st.sidebar.write("### Template")
st.sidebar.write(st.session_state.template)
st.sidebar.write("### Search Prompt")
st.sidebar.write(st.session_state.search_prompt)
if st.sidebar.button('Change Propmts', key='change_propmpts_button'):
    st.session_state.change_instruction = True

if st.session_state.change_instruction:
	st.title('Model Instruction')

	template = st.text_area('Enter Model Instruction For Template: ', 
							key='template', 
							value=st.session_state['template'], 
							height=50)

	search_prompt = st.text_area('Enter Model Instruction For Prompt Refinement: ', 
								key='search_prompt', 
								value=st.session_state['search_prompt'], 
								height=125)
							
st.title('Chat Interface')
user_input = st.text_area('Enter your message:', 
						key='user_input', 
						value=st.session_state['user_input'], 
						height=35)




# Initialize session state variables if they don't exist
if 'message_submitted' not in st.session_state:
	st.session_state.message_submitted = False

# Initialize session state variables if they don't exist
if 'feedback_submitted' not in st.session_state:
	st.session_state.feedback_submitted = False


if st.button('Send', key='send_button'):
	start_time = datetime.now()
	data = {
		'template': st.session_state.template, 
		'user_input': st.session_state.user_input,
		'search_prompt': st.session_state.search_prompt
	}
	res = requests.post(f'{SERVER_URL}/process', json=data, verify=False)

	if res.status_code != 200:
		st.error('Failed to get a response from the server.')

	result = res.json()
	context = result.get("context","")

	response = result.get('response', '')
	response_query = result.get('response_query', '')
	query_time = result.get('query_time', '')
	st.write("### response")
	st.write(response)
	st.write("### Gpt Generated search")
	st.write(response_query)
	st.write("### time took to generate")
	st.write(f"{round(query_time)} seconds")
	st.session_state.message_submitted = True

	inserted_id = ''
	references = []
	category = ''
	subcategory = ''
	
	# Join the list into a single string (if it's not already)
	context_string = ' '.join(context)
	if not context_string.startswith("{"):
		context_string = "{" + context_string
	if not context_string.endswith("}"):
		context_string += "}"
	
	def extract_json_strings(s):
		json_strings = []
		brace_count = 0
		current_json = ''

		for char in s:
			if char == '{':
				brace_count += 1
				current_json += char
			elif char == '}':
				brace_count -= 1
				current_json += char
				if brace_count == 0:
					json_strings.append(current_json)
					current_json = ''
			elif brace_count > 0:
				current_json += char

		return json_strings

	json_strings = extract_json_strings(context_string)

	# Parsing each JSON string
	parsed_json_objects = []
	for json_str in json_strings:
		try:
			p = json.loads(json_str)
			category = p["categories"][2]
			subcategory = p["categories"][3]
			references.append({
				"name": p["name"],
				"description": p["description"] ,
				"price": float(p["price"]),
				"categories": json.dumps(p["categories"])
			})
		except json.JSONDecodeError:
			print(f"Invalid JSON object: {json_str}")

	while True:
		try:
			chat_document = {
				"_id": ObjectId(),  # Generates a unique Object ID
				"user_ip": ip,  # Example IP address
				"user_device": "Desktop",  # Example device type
				"category": category,
				"subcategory": subcategory,
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
				"product_references": references
			}

			# Insert the document into the 'chats' collection
			insert_result = chats.insert_one(chat_document)
			# Get the _id of the inserted document
			inserted_id = insert_result.inserted_id
			st.session_state.document_id = inserted_id


			break
		except Exception as e:
			st.error(str(e))
			time.sleep(10)

if st.session_state['message_submitted']:
	# Initialize session state for feedback
	if 'feedback' not in st.session_state:
		st.session_state.feedback = ''

	st.write("## Feedback")

	# Use session state variable for the text input
	new_feedback_text = st.text_input('Enter Your Feedback:', key='feedback_text', value=st.session_state.feedback)

	# Update the session state when the text input changes
	st.session_state.feedback = new_feedback_text

	if st.button('Send Feedback', key='send_feedback_button'):
		try:
			# Create 'user_actions' with 'feedback_text'
			new_values = {"user_actions": {"feedback_text": new_feedback_text}}
			# Perform the update
			update_result = chats.update_one({"_id": st.session_state.document_id}, {"$set": new_values})

			# Check if the update was successful
			if update_result.modified_count > 0:
				st.write("Document updated successfully.")
			else:
				st.error("No document was updated.")
		except Exception as e:
			st.error("No document was updated.")
			st.error(str(e))