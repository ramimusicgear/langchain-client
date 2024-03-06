import time
from ..utills import chats


def insert_first_message(chat_document):
    retry = 0
    inserted_id = None
    while True:
        try:
            # Insert the document into the 'chats' collection
            insert_result = chats.insert_one(chat_document)
            # Get the _id of the inserted document
            inserted_id = insert_result.inserted_id
            break
        except Exception as e:
            if retry > 3:
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)
    return inserted_id
