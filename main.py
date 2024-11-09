from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import StreamingResponse
from mongo import mongoDB
import os
import datetime

app = FastAPI()

def get_user(user_id):
    return mongoDB.users.find_one({"_id": user_id})

@app.get("/")
async def root():
    return {"message": "API is running"}


@app.post("/create-user")
async def create_user(request: Request):
    data = await request.json()
    name = data.get("name")
    email = data.get("email")
    broadcastList = data.get("broadcastList")

    try:
        mongoDB.users.insert_one({"name": name, "email": email, "broadcastList": broadcastList})
        return {"message": "User created successfully"}
    except Exception as e:
        print(e)
        return {"error": "User not created"}


@app.put("/add-to-broadcast")
async def create_user(request: Request, user_id: str):
    data = await request.json()
    new_email = data.get("email")

    user = get_user(user_id)
    broadcastList = user.get("broadcastList")
    broadcastList.append(new_email)

    try:
        mongoDB.users.update_one({"_id": user_id}, {"$set": {"broadcastList": broadcastList } })
        return {"message": "Broadcast email added successfully"}
    except Exception as e:
        print(e)
        return {"error": "Broadcast email not added"}


@app.put("/add-relation")
async def create_user(request: Request, user_id: str):
    data = await request.json()
    new_relation = data.get("relation")

    user = get_user(user_id)
    relations = user.get("relations")
    relations.append(new_relation)

    try:
        mongoDB.users.update_one({"_id": user_id}, {"$set": {"relations": relations } })
        return {"message": "Relation added successfully"}
    except Exception as e:
        print(e)
        return {"error": "Relation not added"}


@app.post("/reminder/add")
async def add_user_reminder(request: Request, user_id: str):
    data = await request.json()
    reminder_time = data.get("time")
    message = data.get("message")
    
    try:
        reminder_time_obj = datetime.strptime(reminder_time, "%H:%M").time()
        # Generate new reminder ID
        user = get_user(user_id)
        existing_reminders = user.get("reminders", [])
        new_id = len(existing_reminders) + 1
        
        new_reminder = {
            "id": new_id,
            "time": reminder_time,
            "message": message
        }
        
        mongoDB.users.update_one(
            {"_id": user_id},
            {"$push": {"reminders": new_reminder}}
        )
        
        return {"message": f"Reminder set for {reminder_time} - '{message}'"}
    except ValueError:
        return {"error": "Invalid time format. Please use HH:MM in 24-hour format."}
    except Exception as e:
        print(e)
        return {"error": "Failed to add reminder"}


@app.get("/reminder/get")
async def get_user_reminders(user_id: str):
    try:
        user = get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        reminders = user.get("reminders", [])
        return {"reminders": reminders}
    except Exception as e:
        print(e)
        return {"error": "Failed to retrieve reminders"}


@app.delete("/reminder/delete")
async def delete_user_reminder(user_id: str, reminder_id: int):
    try:
        result = mongoDB.users.update_one(
            {"_id": user_id},
            {"$pull": {"reminders": {"id": reminder_id}}}
        )
        
        if result.modified_count > 0:
            return {"message": f"Deleted reminder with ID {reminder_id}"}
        return {"error": "Reminder not found"}
    except Exception as e:
        print(e)
        return {"error": "Failed to delete reminder"}


@app.get("/check-reminder")
async def check_user_reminders(user_id: str):
    try:
        user = get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        now = datetime.now().time().replace(second=0, microsecond=0)
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


@app.post("/stream-video")
async def stream_video(video_data: bytes):
    """
    Receives the video stream from the client and sends it back as a response.
    """

    async def video_generator():
        """
        Generator function to stream the video data.
        """
        yield video_data

    return StreamingResponse(video_generator(), media_type="video/webm")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        print(data)


if __name__ == "__main__":
    import uvicorn

    prod = os.getenv("PY_ENV") == "production"
    host = "0.0.0.0" if prod else "localhost"

    uvicorn.run("main:app", host=host, port=8000, reload=(False if prod else True))
