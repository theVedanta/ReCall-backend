from deepface import DeepFace
import numpy as np
import faiss
import cv2
import uuid

id_database = {}

# Generate an embedding from the first image to determine dimensionality
# first_embedding_obj = DeepFace.represent(img_path="img1.jpg")
# embedding_dim = len(first_embedding_obj[0]["embedding"])
embedding_dim = 4096


def create_embedding(img_path):
    embedding_objs = DeepFace.represent(img_path=img_path)
    embedding = np.array(embedding_objs[0]["embedding"], dtype="float32").reshape(1, -1)

    return embedding


# Create the FAISS index once with the correct dimensionality
index = faiss.IndexFlatL2(embedding_dim)


def update_database(id_database, index):
    id = str(uuid.uuid4())
    id_database[index.ntotal - 1] = id

    print(f"Total embeddings in FAISS index: {index.ntotal}")

    return id


def add_person_to_index(img_path, index):
    # Generate the embedding for the current image
    embedding = create_embedding(img_path)

    # Add the embedding to the FAISS index
    index.add(embedding)

    # Map the current index position to the person ID
    person_id = update_database(id_database, index)

    print(f"Added person with ID: {person_id}")


# Loop through images and add embeddings to the index
for i in range(1, 3):
    add_person_to_index(f"imgs/img{i}.jpg", index)

embedding = create_embedding("imgs/sundar.jpeg")
k = 1  # Number of closest matches

distances, indices = index.search(embedding, k)
print("Person:", id_database[indices[0][0]], "\nScore:", 1 / (1 + distances[0][0]))

"""
----------------------------------------------------------------------------------------------------------------------------------------
"""


def recognize_face_in_frame(frame, index):
    try:
        # Analyze the frame with DeepFace, find the face and get the embedding
        embedding = create_embedding(frame)

        k = 1  # Number of closest matches
        distances, indices = index.search(embedding, k)

        if 1 / (1 + distances[0][0]) > 0.4:  # Adjust threshold as needed
            person_id = id_database.get(indices[0][0])
            if person_id:
                print(f"Recognized: {person_id}, Score: {1/(1+distances[0][0])}")
            else:
                print("High score, but Unknown Face Detected without id!")
                add_person_to_index("temp_frame.jpg", index)
        else:
            print("Unknown Face Detected with low score!")
            add_person_to_index("temp_frame.jpg", index)

    except Exception as e:
        print(f"Error during face recognition: {e}")
        pass  # Handle the exception gracefully (e.g., skip the frame)


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
