import speech_recognition as sr
from typing import Annotated
import google.generativeai as genai
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import time
import threading
import requests
import json

# Initialize FastAPI app
app = FastAPI()

url = "https://recall-backend-5rw5.onrender.com/"

headers = {
    "Content-Type": "application/json"  # adjust as needed
}

# Configure Google Generative AI API
genai.configure(api_key="AIzaSyCB4ZoigxxVFRfe7JUKnioCTxjoTTMAtKU")

input_text = """Analyze the following conversation between two persons, 
Identify the relationship between them (e.g., friends, 
coworkers, family members, client-professional) based on the tone, topics 
discussed, and interaction style. Then, provide a concise summary of the 
conversation, highlighting the main topics, sentiments expressed, and any
 key decisions or conclusions reached by the persons.
                   

return json object with keys:
- relationship: string
- summary: string

example1: 

Hey! My weekend was fantastic I went to Paris with my family! 
The city was as beautiful as ever, with its stunning architecture and lively atmosphere. 
I invited our younger brother to join us, but unfortunately, he was caught 
up with work and couldn’t make it. My wife and kids were thrilled, 
though we explored so many iconic spots, from the Eiffel Tower to cozy 
little cafés along the Seine. Watching their excitement as they took in the 
sights was priceless. It was truly a memorable trip! How was your weekend?

{
  "relationship": "family",
  "summary": "The speaker had a fantastic weekend in Paris with their family. They visited iconic spots like the Eiffel Tower and cozy cafés along the Seine. The speaker's wife and kids were thrilled, and the speaker found the trip to be memorable."}

Now analyze the below conversation and return the relationship and summary. as a json object."""

# Define models
Relation = Annotated[
    str,
    Field(min_length=1, max_length=1, description="A description of the relationship between two people having a conversation. For example, 'friends', 'colleagues', 'family', etc. Use third person and past tense.")
]

class Summary(BaseModel):
    Relationship: str
    convo_summary: str

class RequestData(BaseModel):
    Task: str
    id: str

# Define function to interact with Google Generative AI API
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input_text, generation_config=genai.GenerationConfig(
        response_mime_type="application/json", response_schema=Summary, max_output_tokens=100,
    ))
    return response.text

# Speech recognition setup
r = sr.Recognizer()
recordings = {}  # Dictionary to track recordings by id
is_recording = False  # Global variable to track recording state
recording_event = threading.Event()  # Event to control recording state in the thread

# Function for continuous listening and speech recognition
def listen_and_recognize():
    global is_recording
    while True:
        if is_recording:
            try:
                with sr.Microphone() as source:
                    r.energy_threshold = 300
                    print("Listening...")
                    audio = r.listen(source, timeout=5)  # Listen for a maximum of 5 seconds
                    text = r.recognize_google(audio)
                    print(f"You said: {text}")
                    
                    if current_id in recordings:
                        recordings[current_id] += text.lower() + " "
            except sr.RequestError as e:
                print(f"Error connecting to the recognition service: {e}")
            except sr.UnknownValueError:
                continue
        else:
            recording_event.wait()  # Wait until is_recording is set to True

# Start the speech recognition thread
recognition_thread = threading.Thread(target=listen_and_recognize, daemon=True)
recognition_thread.start()

# FastAPI endpoint to receive POST request and trigger recording
@app.post("/trigger-recording")
async def trigger_recording(data: RequestData):
    global recordings, is_recording, recording_event, current_id

    # Handle "start" task
    if data.Task.lower() == "start_recording":
        if data.id in recordings:
            return {"message": f"Recording already in progress for id: {data.id}"}

        recordings[data.id] = ""  # Initialize recording for this id
        current_id = data.id  # Store the current id for tracking
        is_recording = True  # Set the flag to True to start recording
        recording_event.set()  # Notify the thread to start recording

        print(f"Recording started for id: {data.id}")
        return {"message": f"Recording started for id: {data.id}"}

    # Handle "stop" task
    elif data.Task.lower() == "stop_recording":
        if data.id not in recordings or not recordings[data.id]:
            return {"message": f"No recording in progress for id: {data.id}"}

        is_recording = False  # Stop the recording
        recording_event.clear()  # Notify the thread to stop recording
        print(f"Recording stopped for id: {data.id}")

        final_input = input_text + recordings[data.id]
        print("Prompt:", final_input)
        # Generate AI response and clear recording for this id
        ai_response = get_gemini_response(final_input)
        ai_response = json.loads(ai_response)
        
        payload = {
            "id": data.id,
            "relationship": ai_response['Relationship'],
            "summary": ai_response['convo_summary']
        }
        message={"message": payload}
        response = requests.post(url, json=message, headers=headers)
        if response.status_code == 200:
            print("Data sent to backend")
        else:
            print("Error sending data to backend")
        print(ai_response)
        del recordings[data.id]  # Clear recording data

        # Return the AI-generated response
        return JSONResponse(content={"id": data.id, "ai_response": ai_response})

    else:
        raise HTTPException(status_code=400, detail="Invalid task")

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)