# EmotionCam Web
## Final Project – Artificial Intelligence Applied to Mobile Applications

EmotionCam Web is a mobile-first web application that detects facial emotions from a photo captured with the device camera. It is built with Flask and uses a pre-trained deep learning model for emotion recognition, so the project stays focused on the Artificial Intelligence component while remaining feasible within a short delivery window.

The application is optimized for iPhone Safari and other mobile browsers. Desktop support is provided through the same responsive interface, without creating a separate desktop version.

---

# 1. Project Goal

Develop a functional AI-powered web application that:

- captures an image from the user’s camera,
- detects the dominant facial emotion,
- displays the result immediately,
- stores the analysis in a local database,
- shows history and basic statistics,
- can be deployed online if time allows.

The main objective is not to train a custom model, but to integrate a reliable pre-trained emotion recognition model into a working application.

---

# 2. AI Focus

This project is centered on computer vision and deep learning.

## AI Tasks Used in the System

- Facial detection
- Emotion classification
- Pre-trained CNN inference
- Result interpretation and storage

## Emotions Detected

The system is expected to classify common facial emotions such as:

- Happy
- Sad
- Angry
- Neutral
- Surprise
- Fear
- Disgust

The exact set depends on the pre-trained model used by the selected AI library.

## AI Implementation Strategy

To keep development fast and reliable, the project uses a pre-trained emotion recognition model instead of building and training a custom neural network.

This approach is appropriate because:

- it reduces implementation time,
- it avoids the need for datasets,
- it avoids training complexity,
- it still demonstrates real AI usage,
- it is more stable for a live demo.

---

# 3. Technology Stack

## Backend

- Python 3.11+
- Flask

## AI / Computer Vision

- DeepFace
- OpenCV
- TensorFlow

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Storage

- SQLite

## Optional Deployment

- Render
- Railway

---

# 4. Application Scope

## Included in the MVP

- Mobile-friendly web interface
- Camera access from browser
- Photo capture
- Emotion detection using AI
- Emotion result display
- Confidence display
- History storage in SQLite
- History page
- Statistics page

## Optional Extra Feature

- Public deployment with a shareable URL

## Not Included

- Custom CNN training
- User accounts
- Authentication
- Cloud database
- Multi-user analytics
- Real-time video processing on every frame
- Separate desktop design

---

# 5. System Architecture

```text
Mobile Browser / Desktop Browser
           ↓
        Flask App
           ↓
   Emotion Analysis Service
           ↓
      SQLite Database
```

## Architecture Explanation

### Browser Layer

The user opens the application in Safari, Chrome, or another modern browser.

### Flask Layer

Flask handles routes, uploads, rendering, and result delivery.

### AI Layer

The emotion analysis service loads the pre-trained model and returns the dominant emotion.

### Persistence Layer

SQLite stores each detected emotion with timestamp and confidence.

---

# 6. Project Structure

```text
emotioncam-web/
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── instance/
│   └── emotions.db
├── uploads/
├── templates/
│   ├── index.html
│   ├── history.html
│   └── stats.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── camera.js
├── services/
│   └── emotion_service.py
└── database/
    └── db.py
```

---

# 7. Functional Requirements

## FR-01 Camera Access

The system must allow the user to open the device camera from the browser.

## FR-02 Image Capture

The system must allow the user to capture a photo.

## FR-03 Emotion Detection

The system must analyze the captured image and identify the dominant emotion.

## FR-04 Confidence Output

The system must display a confidence value or equivalent probability indicator returned by the model.

## FR-05 Result Display

The system must show the detected emotion in the interface.

## FR-06 Persistence

The system must store each analysis in SQLite.

## FR-07 History

The system must display previous emotion detections.

## FR-08 Statistics

The system must calculate and display the frequency of detected emotions.

## FR-09 Responsive Design

The system must work as a single mobile-first interface that scales correctly on desktop browsers.

---

# 8. Non-Functional Requirements

## Usability

The interface must be simple, readable, and suitable for a live demo.

## Compatibility

The application should run correctly on:

- iPhone Safari
- Android Chrome
- Desktop browsers through responsive layout

## Performance

Emotion detection should complete in a reasonable time for demonstration purposes.

## Reliability

The system should handle missing faces or invalid uploads gracefully.

## Maintainability

The project should remain simple, modular, and easy to explain.

---

# 9. Database Specification

## Table: emotions

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    emotion TEXT NOT NULL,
    confidence REAL
);
```

## Stored Data

- ID
- timestamp
- detected emotion
- confidence score

---

# 10. API and Route Specification

## GET /

Shows the main application interface.

## POST /analyze

Receives an image, sends it to the emotion model, and returns the result.

## GET /history

Displays stored emotion analysis records.

## GET /stats

Displays the statistics summary of stored emotions.

---

# 11. User Interface Specification

## Main Screen

The main screen should include:

- title
- camera preview or capture section
- capture button
- analyze button
- emotion result
- confidence value
- link to history
- link to statistics

## History Screen

The history screen should show:

- date
- time
- detected emotion
- confidence

## Statistics Screen

The statistics screen should show:

- emotion counts
- emotion percentages
- simple visual summary if time allows

## Design Strategy

The interface is intentionally mobile-first.

On desktop, the same interface should appear centered and responsive, without a separate desktop redesign.

---

# 12. Development Roadmap in Correct Order

## Step 1 — Validate the AI Model

### Goal

Confirm that the selected AI library can successfully detect emotions.

### Output

A working emotion prediction from a local image file.

---

## Step 2 — Create the Flask Skeleton

### Goal

Have a minimal app that serves one page.

### Output

A working local server at:

```text
http://localhost:5000
```

---

## Step 3 — Build the Main Interface

### Goal

Show the camera section, buttons, and result area.

### Output

A usable interface that looks correct on a phone screen.

---

## Step 4 — Add Camera Capture

### Goal

Let the user take a photo from the mobile browser.

### Output

A captured image ready to be sent to the backend.

---

## Step 5 — Connect Image Upload to Flask

### Goal

Transfer the photo from the frontend to the backend.

### Output

The backend receives and saves the uploaded image.

---

## Step 6 — Integrate Emotion Detection

### Goal

Analyze the image and extract the dominant emotion.

### Output

A returned emotion label and confidence value.

---

## Step 7 — Display the Result in the UI

### Goal

Make the AI result visible and understandable to the user.

### Output

Emotion and confidence appear on the main page.

---

## Step 8 — Add SQLite Persistence

### Goal

Keep a record of all analyses.

### Output

Each result is written into `emotions.db`.

---

## Step 9 — Build the History Page

### Goal

Let the user see past results.

### Output

A history page with timestamps and emotions.

---

## Step 10 — Build the Statistics Page

### Goal

Show the distribution of detected emotions.

### Output

A statistics view with counts or percentages.

---

## Step 11 — Polish the Interface

### Goal

Make the app presentable for evaluation.

### Output

A clean and stable mobile-first interface.

---

## Step 12 — Test and Deploy

### Goal

Prepare the final version for live demonstration.

### Output

A public URL or a stable local deployment.

---

# 13. Development Strategy

## Recommended Implementation Style

Use a Minimum Viable Product (MVP) approach:

- build the smallest working version first,
- test constantly,
- avoid unnecessary features,
- prioritize reliability over complexity.

## Recommended Modeling Strategy

Use a pre-trained model.

Do not train a custom neural network.

## Recommended Interface Strategy

Use a single-screen mobile interface.

Do not create separate desktop screens.

## Recommended Deployment Strategy

Deploy only after the local version is stable.

---

# 14. Testing Plan

## Test 1 — Server Startup

The Flask server must start without errors.

## Test 2 — Camera Access

The browser must request and receive camera permission.

## Test 3 — Image Capture

The captured image must be sent to Flask correctly.

## Test 4 — Emotion Detection

The AI module must return a valid emotion.

## Test 5 — Database Storage

The result must be saved in SQLite.

## Test 6 — History Display

The history page must show saved records.

## Test 7 — Statistics Display

The statistics page must summarize the stored data.

## Test 8 — Mobile Usability

The application must remain readable and functional on a phone screen.

---

# 15. Deployment Plan

## Option A — Local Demo

Run Flask locally and open the application from the iPhone using the laptop's network IP.

## Option B — Public Deployment

Deploy the app on a hosting platform such as Render.

## Deployment Goal

Make the application accessible through a shareable URL.

Example:

```text
https://emotioncam.onrender.com
```

Deployment is optional but strongly recommended as an extra feature if time permits.

---

# 16. Expected Demo Flow

1. Open the application on the phone browser.
2. Allow camera access.
3. Capture a photo.
4. Run emotion analysis.
5. Show the detected emotion.
6. Open the history page.
7. Open the statistics page.
8. Explain the AI model, Flask backend, SQLite storage, and responsive web architecture.

---

# 17. Deliverables

## Source Code

Complete project repository.

## Technical Documentation

Must include:

- objectives
- architecture
- AI techniques used
- screenshots
- implementation details
- results

## Demonstration Video

A short video showing the application working.

## Final Presentation

Slides summarizing:

- problem
- solution
- technologies
- AI components
- results

---

# 18. Final Notes

This project is intentionally designed to be achievable within a short development window while still satisfying the Artificial Intelligence requirements of the course.

Priority order:

1. Working emotion recognition
2. Mobile-friendly interface
3. Reliable storage
4. History visualization
5. Statistics visualization
6. Optional deployment

The final product should be stable, demonstrable, and easy to explain during evaluation.