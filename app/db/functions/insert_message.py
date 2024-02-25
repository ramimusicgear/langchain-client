import time
from ..utills import chats


def insert_message(
    document_id,
    new_message,
    category=None,
    subcategory=None,
    backend_version=None,
    price=0,
):
    retry = 0
    while True:
        try:
            if new_message["sender"] != "bot":
                update_result = chats.update_one(
                    {"_id": document_id}, {"$push": {"messages": new_message}}
                )
            else:
                if backend_version == "0.0.1":
                    mutation = {
                        "$push": {"messages": new_message},
                        "$set": {
                            "backend_version": backend_version,
                        }
                    }
                else:
                    mutation = {
                        "$push": {"messages": new_message},
                        "$inc": {"price": price},
                        "$set": {
                            "category": category,
                            "subcategory": subcategory,
                            "backend_version": backend_version,
                        },
                    }
                    
                update_result = chats.update_one(
                    {"_id": document_id},
                    mutation                    
                )
                
            # Check if the update was successful
            if update_result.modified_count > 0:
                break
            else:
                if retry > 3:
                    print(f"[Modified Error]: {document_id}")
                    time.sleep(10)
                retry += 1
                time.sleep(1)
        except Exception as e:
            if retry > 3:
                print(f"[Modified Error]: {document_id}")
                print(str(e))
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)
