import os
import time
import mysql.connector

from dotenv import load_dotenv
load_dotenv()

password = os.environ.get("PASSWORD")
host = os.environ.get('HOST')
user = os.environ.get('USER')
database = os.environ.get('DB')
mydb = mysql.connector.connect(
	host=host,
	user=user,
	password=password,
	database=database
)
mycursor = mydb.cursor()
# query_time, response_query, response
# mycursor.execute("DROP TABLE llamaindex_data")
mycursor.execute("CREATE TABLE llamaindex_data (query_time TEXT, response_query TEXT, response TEXT)")


