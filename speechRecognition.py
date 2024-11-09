import speech_recognition as sr
from typing import Annotated
import google.generativeai as genai
from pydantic import BaseModel, Field
import time

genai.configure(api_key="AIzaSyCB4ZoigxxVFRfe7JUKnioCTxjoTTMAtKU")

Relation = Annotated[
    str,
    Field(min_length=1, max_length=1, description="A description of the relationship between two people having a conversation. For example, 'friends', 'colleagues', 'family', etc. Feel also just say 'acquaintances' if you don't know the relationship. Keep this in third person use they/them pronouns. talk about it in the past tense. ")
]

class Summary(BaseModel):
    Relationship: str
    convo_summary: str


input = """Analyze the following conversation between two persons, 
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

now, the following is what you need to analyse and return a response for:"""



def get_gemini_repsonse(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input, generation_config=genai.GenerationConfig(
        response_mime_type="application/json", response_schema=Summary, max_output_tokens=100,
    ), )
    return response.text

summary = ""
r = sr.Recognizer()
is_recording = False
current=time.time()
while True:
    if is_recording:
        summary = ""
    if time.time()-current>10:
        break
    try:
        with sr.Microphone() as source:
            r.energy_threshold = 300
            audio = r.listen(source)
            text = r.recognize_google(audio)
            text = text.lower()
            summary += text
            print(f"You said: {text}")
    except sr.RequestError as e:
        print("Error connecting to the recognition service; {0}".format(e))
    except sr.UnknownValueError:
        pass


final = input+summary
print(final)
print(get_gemini_repsonse(final))
