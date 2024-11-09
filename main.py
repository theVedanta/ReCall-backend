from fastapi import FastAPI, Request
from mongo import mongoDB
import os
import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
user_id = ObjectId("672ef39dfaad60aaca25070f")


def get_user():
    try:
        object_id = user_id
        print(object_id)
        return mongoDB.users.find_one({"_id": object_id}, {"_id": 0})
    except InvalidId:
        raise HTTPException(status_code=400, message="Invalid user ID format")


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/get-user")
def return_user():
    user = get_user()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/create-user")
async def create_user(request: Request):
    data = await request.json()
    name = data.get("name")
    email = data.get("email")
    broadcastList = data.get("broadcastList")

    try:
        mongoDB.users.insert_one(
            {"name": name, "email": email, "broadcastList": broadcastList}
        )
        return {"message": "User created successfully"}
    except Exception as e:
        print(e)
        return {"error": "User not created"}


@app.post("/add-relation")
async def add_relation(request: Request):
    data = await request.json()
    new_relation = data.get("relation")

    user = get_user()
    relations = user.get("relations", [])
    relations.append(new_relation)

    user = get_user()
    broadcastList = user.get("broadcastList", [])
    for relation in relations:
        (
            broadcastList.append(relation["email"])
            if relation["email"] not in broadcastList
            else None
        )

    try:
        mongoDB.users.update_one(
            {"_id": user_id},
            {"$set": {"relations": relations, "broadcastList": broadcastList}},
        )
        return {"message": "Relation & Broadcast email added successfully"}
    except Exception as e:
        print(e)
        return {"error": "Relation not added"}


@app.post("/count")
async def add_count(request: Request):
    data = await request.json()
    relation_id = data.get("relation_id")

    user = get_user()
    relations = user.get("relations", [])
    newRelations = []

    for relation in relations:
        if relation["id"] == relation_id:
            count = relation.get("count")
            if count:
                count["value"] += 1
                count["last"] = datetime.datetime.now()
            else:
                count = {
                    "value": 1,
                    "first": datetime.datetime.now(),
                    "last": datetime.datetime.now(),
                }

            relation["count"] = count
        newRelations.append(relation)

    try:
        mongoDB.users.update_one(
            {"_id": user_id}, {"$set": {"relations": newRelations}}
        )
        return {"message": "Message added successfully"}
    except Exception as e:
        print(e)
        return {"error": "Message not added"}


@app.post("/message/add")
async def add_message(request: Request):
    data = await request.json()
    message = data.get("message")
    relation_id = data.get("relation_id")

    user = get_user()
    relations = user.get("relations", [])
    newRelations = []

    for relation in relations:
        if relation["id"] == relation_id:
            messages = relation.get("messages", [])
            messages.append(message)
            relation["messages"] = messages
        newRelations.append(relation)

    try:
        mongoDB.users.update_one(
            {"_id": user_id}, {"$set": {"relations": newRelations}}
        )
        return {"message": "Message added successfully"}
    except Exception as e:
        print(e)
        return {"error": "Message not added"}


# Reminders ------------------------------------------------------------------------------------------


@app.post("/reminder/add")
async def add_user_reminder(request: Request):
    data = await request.json()
    reminder_time = data.get("time")
    message = data.get("message")

    try:
        reminder_time_obj = datetime.strptime(reminder_time, "%H:%M").time()
        # Generate new reminder ID
        user = get_user()
        existing_reminders = user.get("reminders", [])
        new_id = len(existing_reminders) + 1

        new_reminder = {"id": new_id, "time": reminder_time, "message": message}

        mongoDB.users.update_one(
            {"_id": user_id}, {"$push": {"reminders": new_reminder}}
        )

        return {"message": f"Reminder set for {reminder_time} - '{message}'"}
    except ValueError:
        return {"error": "Invalid time format. Please use HH:MM in 24-hour format."}
    except Exception as e:
        print(e)
        return {"error": "Failed to add reminder"}


@app.get("/reminder/get")
async def get_user_reminders():
    try:
        user = get_user()
        if not user:
            return {"error": "User not found"}

        reminders = user.get("reminders", [])
        return {"reminders": reminders}
    except Exception as e:
        print(e)
        return {"error": "Failed to retrieve reminders"}


@app.delete("/reminder/delete")
async def delete_user_reminder(reminder_id: int):
    try:
        result = mongoDB.users.update_one(
            {"_id": user_id}, {"$pull": {"reminders": {"id": reminder_id}}}
        )

        if result.modified_count > 0:
            return {"message": f"Deleted reminder with ID {reminder_id}"}
        return {"error": "Reminder not found"}
    except Exception as e:
        print(e)
        return {"error": "Failed to delete reminder"}


@app.get("/check-reminder")
async def check_user_reminders():
    try:
        user = get_user()
        if not user:
            return {"error": "User not found"}

        now = datetime.datetime.now().time().replace(second=0, microsecond=0)
        current_time = now.strftime("%H:%M")

        # Find reminders due at current time
        reminders = user.get("reminders", [])
        due_reminders = [r for r in reminders if r["time"] == current_time]

        if due_reminders:
            # Remove due reminders
            # mongoDB.users.update_one(
            #     {"_id": user_id},
            #     {"$pull": {"reminders": {"time": current_time}}}
            # )

            return {
                "notifications": [
                    f"Reminder: {reminder['message']} at {reminder['time']}"
                    for reminder in due_reminders
                ]
            }

        return {"notifications": []}
    except Exception as e:
        print(e)
        return {"error": "Failed to check reminders"}


if __name__ == "__main__":
    import uvicorn

    prod = os.getenv("PY_ENV") == "production"
    host = "0.0.0.0" if prod else "localhost"

    uvicorn.run("main:app", host=host, port=8000, reload=(False if prod else True))
