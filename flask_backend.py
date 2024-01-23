import os
import json
from sys import set_asyncgen_hooks
import time
import tiktoken

from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from flask import Flask, request, jsonify, stream_with_context
from llama_index.query_engine import CustomQueryEngine
from llama_index.retrievers import BaseRetriever
from llama_index.response_synthesizers import (
    get_response_synthesizer,
    BaseSynthesizer,
)
from llama_index.llms import ChatMessage, MessageRole, OpenAI
from llama_index.prompts import PromptTemplate
from llama_index import StorageContext, load_index_from_storage
from llama_index.memory import BaseMemory
from llama_index.llms.generic_utils import messages_to_history_str
from llama_index.chat_engine.types import BaseChatEngine
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import insert, create_engine, String, text, Integer
from llama_index import ServiceContext, SQLDatabase
from llama_index.query_engine import PGVectorSQLQueryEngine
from llama_index.indices.struct_store.sql_retriever import BaseSQLParser
from llama_index.retrievers import SQLRetriever

os.environ['OPENAI_API_KEY'] = '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'

engine = create_engine("postgresql+psycopg2://postgres:mysecurepassword@rmgserver.nethost.co.il:5432/postgres")

sql_database = SQLDatabase(engine, include_tables=["sec_text_chunk"])

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

with open("categories.json","r") as f:
    categories = json.load(f)

text_to_sql_tmpl = PromptTemplate("""\

You can order the results by a relevant column to return the most \
interesting examples in the database.

In the Technical Specs section below, list out the technical specifications the product that the customer is looking for should have.
When you list out the technical specs do it like you are creating some sord of an id for the item you list out what it has for example:
Total length: 762 mm
Carved top
Body: Mahogany
Neck: Mahogany

The form above will be the form in which you list out the specs
This should be done based on the customer request you will have to infer what the product he wants should have

In the summery summeraize the chat and the question, the most important thing is what product the customer is interested in.

Pay attention to use only the column names that you can see in the schema \
description. Be careful to not query for columns that do not exist. \
Pay attention to which column is in which table. Also, qualify column names \
with the table name when needed. 

IMPORTANT NOTE: you can use specialized pgvector syntax (`<->`) to do nearest \
neighbors/semantic search to a given vector from an embeddings column in the table. \
The embeddings value for a given row typically represents the semantic meaning of that row. \
The vector represents an embedding representation \
of the question, given below. Do NOT fill in the vector values directly, but rather specify a \
`[query_vector]` placeholder. For instance, some select statement examples below \
(the name of the embeddings column is `embedding_description` and `embedding_name` in the examples i will use "embedding" just for demonstration perperces):
SELECT * FROM items ORDER BY embedding <-> '[query_vector]' LIMIT 5;
SELECT * FROM items WHERE id != 1 ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1) LIMIT 5;
SELECT * FROM items WHERE embedding <-> '[query_vector]' < 5;

you are selecting from "sec_text_chunk"

You are required to use the following format, \
each taking one line:

SQLQuery: SQL Query to run
Summery: Summery here
Technical Specs: Technical Specs here

Only use tables listed below.
{schema}

Chat History:
{chat_history}

Question: {query_str}
SQLQuery: \
""")

categories_and_sub = ""
for category in categories:
    subs = ""
    for sub_category in categories[category]:
        subs += "sub categories - " + sub_category + "\n"

    subs = f"""
category: {category} 
{subs}"""
    categories_and_sub += subs + "\n"

table_desc = f"""\
This table represents products. Each row contains the following columns:

id: id of row
name: name of the product
category: category of the product
sub_category: sub category of the product
price: price of the product
description: product's description
embedding_description: the embeddings representing the description 
embedding_name: the embeddings representing the name

{categories_and_sub}

For most queries you should perform semantic search against the `embedding` column values, since \
that encodes the meaning of the text.

"""

context_query_kwargs = {"sec_text_chunk": table_desc}

final_answer_template = PromptTemplate("""\
Given a summery of conversation (between Human and Assistant) and a follow up question from the user
You are an assistant you help customers choose products using the given context (use only what is relevent) 
your output should be nicely phrased
ask the customer questions to figure out what he needs
in your questions behave a little bit like a salesman and try and figure out exactly what the customer is looking for
in your questions lead the customer to the right product for him

<Chat Summery>
{chat_summery}

<context>
{context}

<Follow Up Question>
{question}

"""
)

class CustomParser(BaseSQLParser):
    """PGVector SQL Parser."""

    def __init__(self,embed_model):
        """Initialize params."""
        self._embed_model = embed_model

    def parse_response_to_sql(self, response, query):
        """Parse response to SQL."""
        sql_vector_start = response.find("Technical Specs:")
        pg_vector = ""
        if sql_vector_start  != -1:
            pg_vector = response[sql_vector_start :]
            # TODO: move to removeprefix after Python 3.9+
            if pg_vector.startswith("Technical Specs:"):
                pg_vector = pg_vector[len("Technical Specs:") :]

        print()
        print(pg_vector.strip())
        print()

        sql_query_start = response.find("SQLQuery:")
        if sql_query_start != -1:
            response = response[sql_query_start:]
            if response.startswith("SQLQuery:"):
                response = response[len("SQLQuery:") :]
        sql_result_start = response.find("Summery:")
        if sql_result_start != -1:
            response = response[:sql_result_start]

        print(response)

        # this gets you the sql string with [query_vector] placeholders
        raw_sql_str = response.strip().strip("```").strip()
        if pg_vector != "":
            query_embedding = self._embed_model.get_query_embedding(pg_vector)
        else:
            query_embedding = self._embed_model.get_query_embedding(query)
        query_embedding_str = str(query_embedding)
        return raw_sql_str.replace("[query_vector]", query_embedding_str),pg_vector

# class CustomSqlRetriver(NLSQLRetriever):
# 	def _load_sql_parser(self, sql_parser_mode , service_context):
# 		return CustomParser(service_context.embed_model)


row_dict = [
	"id",
	"name",
	"category",
	"sub_category",
	"price",
	"description"]
# TODO: Check if this works and add the pgvector sql retriver to actually use this one and check if all of this works
# from llama_index.query_engine import PGVectorSQLQueryEngine
inp_pricing_per_token = 0.00003
out_pricing_per_token = 0.00006
encoding = tiktoken.encoding_for_model('gpt-4')
class CustomSqlRetriver:
    def __init__(self,sql_database,llm,embeded_model,template,scheme,final_template):
        self.sql_retriever = SQLRetriever(sql_database, return_raw=True)
        self.llm = llm
        self.parser = CustomParser(embed_model)
        self.template = template
        self.scheme = scheme
        self.final_template = final_template

    def custom_query(self,query,chat_history):
        chat_history = messages_to_history_str(chat_history)
        inp = self.template.format(schema=self.scheme,chat_history=chat_history,query_str=query)
        num_inp_tokens = len(encoding.encode(inp))
        response = str(self.llm.complete(inp))

        num_out_tokens = len(encoding.encode(response))
        summery_start = response.find("Summery:")
        summery = response
        if summery_start != -1:
            summery = summery[summery_start:]
            if summery.startswith("Summery:"):
                summery = summery[len("Summery:") :]
        sql_result_start = summery.find("Technical Specs:")
        if sql_result_start != -1:
            summery = summery[:sql_result_start]

        sql_query,pg_vector = self.parser.parse_response_to_sql(response,query)

        retrieved_nodes, metadata = self.sql_retriever.retrieve_with_metadata(sql_query)
        results = metadata['result']
        fixed_results = ""
        for r in results:
            fixed_r = ""
            for i,name in enumerate(row_dict):
                fixed_r += f"{name} - {r[i]}" + "\n"
            fixed_results += fixed_r + '\n\n'

        inp_final = self.final_template.format(chat_summery=summery,context=fixed_results,question=query)
        num_inp_tokens += len(encoding.encode(inp_final))
        final_answer = str(self.llm.complete(inp_final))
        num_out_tokens += len(encoding.encode(final_answer))

        price = num_inp_tokens*inp_pricing_per_token + num_out_tokens*out_pricing_per_token
        return final_answer,pg_vector,price


llm = OpenAI(model="gpt-4")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
chat_engine = CustomSqlRetriver(sql_database=sql_database,llm=llm,embeded_model=embed_model,template=text_to_sql_tmpl,scheme=context_query_kwargs,final_template=final_answer_template)



app = Flask(__name__)
@app.route('/process', methods=['POST'])
def process_text():
	data = request.json
	user_input = data.get('user_input', '')  # Get user input from the client
	history = data.get('history','')
	custom_chat_history = []
	for item in history:
		if item['role'] == "user":
			custom_chat_history.append(ChatMessage(role=MessageRole.USER,content=item['content']))
		if item['role'] == "assistant":
			custom_chat_history.append(ChatMessage(role=MessageRole.ASSISTANT,content=item['content']))
		
	response,response_query,price = chat_engine.custom_query(user_input,custom_chat_history)

	return jsonify({'response': response,'response_query':response_query,'price':price})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
