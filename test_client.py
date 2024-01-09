import os
import time
import requests
import mysql.connector
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

password = os.environ.get("PASSWORD")
host = os.environ.get('HOST')
user = os.environ.get('USER')
database = os.environ.get('DB')
SERVER_URL = os.environ.get('SERVER_URL')

st.title('Chat Interface')

user_input = st.text_input('Enter your message:')

if st.button('Send'):
	data = {'user_input': user_input}
	response = requests.post(f'{SERVER_URL}/process', json=data, verify=False)
	res=''
	response_query=''
	query_time=''
	if response.status_code == 200:
		result = response.json()
		st.write("### response")
		res = result.get('response', '')
		st.write(res)
		st.write("### Gpt Generated search")
		response_query = result.get('response_query', '')
		st.write(response_query)
		st.write("### time took to generate")
		query_time = str(result.get('query_time', ''))
		st.write(query_time + " seconds")
	else:
		st.error('Failed to get a response from the server.')
	while True:
		try:
			mydb = mysql.connector.connect(
				host=host,
				user=user,
				password=password,
				database=database
			)
			mycursor = mydb.cursor()
			sql = "INSERT INTO llamaindex_data (query_time, response_query, response) VALUES (%s, %s, %s)"
			val = (query_time, response_query, res)
			mycursor.execute(sql, val)
			mydb.commit()
			break
		except Exception as e:
			time.sleep(1)
