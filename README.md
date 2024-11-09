# ReCall.AI

**ReCall.AI** is an innovative application designed to assist dementia patients in improving their quality of life and maintaining stronger connections with their caregivers and family members. The app leverages advanced technologies, including OpenCV, DeepFace, speech recognition, and geolocation tracking, to offer features such as recognition of close relations, conversation recording, medication reminders, and location tracking for safety. Additionally, it helps doctors by collecting valuable data for diagnosis.

## Key Features

### 1. **Facial Recognition for Close Relations**
   - Using **OpenCV** and **DeepFace**, ReCall.AI recognizes faces of family members and close relations. When a patient encounters a familiar face, the app identifies the person and provides relevant information, including their name and details about previous conversations.

### 2. **Speech Recognition and Reminders**
   - The app incorporates **speech recognition** to capture conversations and store them for future reference. This can help patients recall past interactions.
   - It also generates and sets **daily reminders** for important tasks such as:
     - Taking medication
     - Drinking water
     - Eating meals
     - Any other customizable tasks to support the patient's daily routine.

### 3. **Location Tracking and Caregiver Notifications**
   - ReCall.AI tracks the patient's **geolocation** to ensure their safety.
   - The app sends **notifications to caregivers** if the patient exits a predefined safe radius. This feature helps ensure that patients don't wander off and provides peace of mind to caregivers.

### 4. **Data Collection for Doctors**
   - ReCall.AI collects crucial data during interactions and daily activities. This data is stored securely and can be shared with doctors to assist in diagnosing and monitoring the patient’s condition.
   - By analyzing patterns in speech, activities, and location, healthcare providers gain valuable insights into the patient's well-being and progression.

## How It Works

### **Facial Recognition:**
   - The app uses the **DeepFace** library, which is integrated with **OpenCV** to analyze and compare facial features. When the patient is interacting with someone, the app identifies the face and presents relevant details, such as the person’s name and previous interactions. This feature helps the patient recall familiar faces, which is crucial in managing dementia-related memory loss.

### **Speech Recognition and Reminders:**
   - The app listens to the patient's voice and captures audio. Using advanced **speech recognition** algorithms, ReCall.AI transcribes the conversation into text and stores it.
   - Additionally, the app can create and set voice-activated reminders. For example, the patient can ask the app to remind them to take their medication at a specific time, or the app can automatically prompt reminders for important tasks.

### **Location Tracking:**
   - ReCall.AI uses **GPS tracking** to monitor the patient's location in real-time.
   - Caregivers can set a geofence, and if the patient moves outside of the safe zone, the app will notify the caregiver immediately, ensuring that the patient stays within a safe environment.

### **Data Collection and Doctor Support:**
   - All interactions, location data, and reminders are stored securely within the app. This data can be shared with healthcare providers, providing insights into the patient's daily activities and behaviors.
   - The collected data helps doctors better understand the patient’s needs, track their progression, and make informed decisions about their care.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ReCall.AI.git
   cd ReCall.AI
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure to have OpenCV and DeepFace set up on your environment:

   ```bash
   pip install opencv-python deepface
   ```

4. Set up Speech Recognition (ensure you have a working microphone):

   ```bash
   pip install SpeechRecognition
   ```

5. Install geolocation tracking library:

   ```bash
   pip install geopy
   ```

6. Set up and configure any external APIs or databases as necessary for data storage and doctor support.

## Usage

1. **Launch the app**:
   - Run the app through your Python environment by executing:

     ```bash
     python app.py
     ```

2. **Set up patient profile**:
   - Once the app is running, set up the patient’s profile with their relevant information and set reminders for daily tasks.

3. **Facial Recognition Setup**:
   - Upload images of family members and caregivers for facial recognition. These images will be stored in the app for future reference.

4. **Configure Geolocation**:
   - Set the safe radius for location tracking in the app settings. The app will notify caregivers when the patient moves beyond this radius.

5. **Speech Recognition & Reminders**:
   - Use voice commands to set reminders for medication and other important tasks. The app will capture conversations and store them for future reference.

## Data Privacy and Security

ReCall.AI takes the privacy and security of the patient’s data very seriously:
- All data collected (including facial images, conversations, and geolocation data) is stored securely.
- Data shared with doctors is encrypted and handled in compliance with privacy regulations.
- The app follows best practices for user data protection, ensuring that sensitive information is never exposed.

## Future Improvements

- **Enhanced AI**: Future versions of ReCall.AI may include more advanced AI models to improve recognition and better understand the patient's emotional state.
- **Integration with Wearables**: Integration with wearable devices to monitor heart rate, sleep patterns, and physical activity for a more comprehensive view of the patient’s health.
- **Expanded Reminder Features**: More customizable reminders for the patient's comfort and ease of use.
- **Multi-User Support**: Allow caregivers to manage multiple patients within the same app.

## Contributing

We welcome contributions to **ReCall.AI**. If you'd like to contribute, please fork the repository and submit a pull request. For any issues or feature requests, please create an issue in the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Thank you for using **ReCall.AI**! We hope it can make a difference in the lives of dementia patients and their caregivers.
