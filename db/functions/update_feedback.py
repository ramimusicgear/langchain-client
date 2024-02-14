import time
from ..utills import chats


def update_feedback(id, new_values):
    retry = 0
    while True:
        try:
            update_result = chats.update_one({"_id": id}, {"$set": new_values})
            # Check if the update was successful
            if update_result.modified_count > 0:
                break
            else:
                if retry > 3:
                    time.sleep(10)
                retry += 1
                time.sleep(1)
        except Exception as e:
            print(str(e))
            if retry > 3:
                time.sleep(10)
            retry += 1
            time.sleep(1)
