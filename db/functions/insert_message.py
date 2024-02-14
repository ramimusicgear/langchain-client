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
                print(category)
                print(subcategory)
                update_result = chats.update_one(
                    {"_id": document_id},
                    {
                        "$push": {"messages": new_message},
                        "$inc": {"price": price},
                        "$set": {
                            "category": category,
                            "subcategory": subcategory,
                            "backend_version": backend_version,
                        },
                    },
                )
            # Check if the update was successful
            if update_result.modified_count > 0:
                break
            else:
                if retry > 3:
                    print("error, to fix click on reset button")
                    time.sleep(10)
                retry += 1
                time.sleep(1)
        except Exception as e:
            if retry > 3:
                print("error, to fix click on reset button")
                print(str(e))
                print(str(e))
                time.sleep(10)
            retry += 1
            time.sleep(1)
