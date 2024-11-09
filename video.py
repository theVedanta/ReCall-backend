from deepface import DeepFace
import numpy as np
import faiss
from faiss import write_index
import cv2
import uuid
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()


def upload_to_imgur(img_path):
    try:
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {os.getenv('IMGUR_CLIENT_ID')}"}

        # Read image file and encode as base64
        with open(img_path, "rb") as file:
            data = file.read()
            base64_data = base64.b64encode(data)

        # Upload image to Imgur and get URL
        response = requests.post(url, headers=headers, data={"image": base64_data})
        url = response.json()["data"]["link"]

        return url
    except Exception as e:
        print(f"Error uploading to Imgur: {e}")
        return None


id_database = {}

# Generate an embedding from the first image to determine dimensionality
# first_embedding_obj = DeepFace.represent(img_path="img1.jpg")
# embedding_dim = len(first_embedding_obj[0]["embedding"])
embedding_dim = 4096


def create_embedding(img_path):
    embedding_objs = DeepFace.represent(img_path=img_path)
    embedding = np.array(embedding_objs[0]["embedding"], dtype="float32").reshape(1, -1)

    return embedding


# Create the FAISS index
index = faiss.IndexFlatL2(embedding_dim)


def update_database(id_database, index):
    id = str(uuid.uuid4())
    id_database[index.ntotal - 1] = id

    print(f"Total embeddings in FAISS index: {index.ntotal}")

    return id


def add_person_to_index(img_path, index):
    embedding = create_embedding(img_path)
    index.add(embedding)
    person_id = update_database(id_database, index)
    url = upload_to_imgur(img_path)
    
    print(url)

    write_index(index, f"faiss_index")

    print(f"Added person with ID: {person_id}")


"""
SAMPLING --------------------------------------------------------------------------------------------------------------------------------
"""
# Loop through images and add embeddings to the index
for i in range(1, 3):
    add_person_to_index(f"imgs/img{i}.jpg", index)

embedding = create_embedding("imgs/sundar.jpeg")
k = 1  # Number of closest matches

distances, indices = index.search(embedding, k)
print("Person:", id_database[indices[0][0]], "\nScore:", 1/(1+distances[0][0]))

"""
----------------------------------------------------------------------------------------------------------------------------------------
"""


def recognize_face_in_frame(frame, index):
    try:
        embedding = create_embedding(frame)

        k = 1
        distances, indices = index.search(embedding, k)
        score = 1/(1+distances[0][0])

        if score > 0.4:
            person_id = id_database.get(indices[0][0])
            if person_id:
                print(f"Recognized: {person_id}, Score: {score}")
            else:
                print("High score, but Unknown Face Detected without id!")
                add_person_to_index("temp_frame.jpg", index)
        else:
            print("Unknown Face Detected with low score!")
            add_person_to_index("temp_frame.jpg", index)

    except Exception as e:
        print(f"Error during face recognition: {e}")
        pass


# Video stream setup
video_capture = cv2.VideoCapture(
    0
)  # Use 0 for default webcam or provide video file path

if not video_capture.isOpened():
    print(video_capture)
    print("Error opening video capture device")
    exit()

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Convert frame to image file
    cv2.imwrite("temp_frame.jpg", frame)

    # Perform face recognition
    recognize_face_in_frame("temp_frame.jpg", index)

    # Display the resulting frame
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


video_capture.release()
cv2.destroyAllWindows()
