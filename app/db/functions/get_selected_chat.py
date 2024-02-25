from bson import ObjectId
from ..utills import verify_jwt_token, db


def get_selected(selected_conversation, selected_db_collection, jwt):
    payload = verify_jwt_token(jwt)
    if payload and payload["is_admin"]:
        try:
            # Convert string to ObjectId
            selected_conversation_ObjectId = ObjectId(selected_conversation)

            # Query the database with ObjectId
            conversation = db[selected_db_collection].find_one(
                {"_id": selected_conversation_ObjectId}
            )
            if conversation == None:
                conversation = db[selected_db_collection].find_one(
                    {"_id": selected_conversation}
                )
            return conversation
        except Exception as e:
            print(f"ERR1 - {str(e)}")
            try:
                # Query the database with ObjectId
                conversation = db[selected_db_collection].find_one(
                    {"_id": selected_conversation}
                )
                return conversation

            except Exception as e:
                print(f"ERR2 - {str(e)}")
                # Handle invalid ObjectId string
                return None

    return None
