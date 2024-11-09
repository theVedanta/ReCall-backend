from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import StreamingResponse
from mongo import mongoDB
import os

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
