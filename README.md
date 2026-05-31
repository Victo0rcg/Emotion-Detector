# EmotionCam Web

**Real-time facial emotion recognition powered by DeepFace and Flask**

EmotionCam Web is a mobile-first web application that detects human emotions from live camera input. Users capture a photo with a single tap, and the system automatically analyzes facial expressions using deep learning, displays the result with a confidence score, and persists each analysis for later review.

---

## Overview

Understanding human emotions from facial expressions is a fundamental problem in artificial intelligence, with applications in human–computer interaction, accessibility, education, and user experience research. Manual interpretation of emotions is subjective and does not scale; automated systems can provide consistent, data-driven insights in real time.

EmotionCam Web addresses this challenge by delivering a practical, browser-based emotion recognition tool. The application combines computer vision, deep learning, and a lightweight web stack to let users interact with an AI model through their device camera—without installing native software. The interface is designed for mobile devices and is fully localized in Spanish, making it suitable for demonstrations, academic evaluation, and portfolio presentation.

---

## Features

- **Live camera preview** with front-facing camera support
- **One-tap capture and analysis** — capture, upload, and analyze in a single action
- **DeepFace emotion recognition** with dominant emotion detection
- **Confidence score visualization** with progress bar and contextual hints
- **Spanish-language interface** (UI, errors, and result labels)
- **Emotion history page** — chronological log of past analyses
- **Statistics page** — emotion distribution with counts and percentages
- **SQLite persistence** for analysis records
- **Mobile-first responsive design** optimized for iPhone Safari
- **Secure file upload handling** with validation and size limits
- **Graceful error handling** for missing faces, camera issues, and network failures

---

## Artificial Intelligence Component

### DeepFace

[DeepFace](https://github.com/serengil/deepface) is an open-source Python framework for facial analysis. It wraps pre-trained deep learning models (built on TensorFlow/Keras) that perform face detection and attribute inference. In this project, DeepFace is used exclusively for **emotion recognition**.

### Emotion Recognition

When an image is submitted for analysis, DeepFace detects faces in the photograph and evaluates each face against seven emotion categories:

| Emotion   | Label (ES)    |
|-----------|---------------|
| Angry     | Enojado       |
| Disgust   | Asco          |
| Fear      | Miedo         |
| Happy     | Feliz         |
| Sad       | Triste        |
| Surprise  | Sorprendido   |
| Neutral   | Neutral       |

The model returns a probability distribution across all seven classes for each detected face.

### Dominant Emotion Detection

The **dominant emotion** is the class with the highest predicted probability in DeepFace's output. The application extracts this value via `dominant_emotion` and normalizes it to a lowercase label before returning it to the client and storing it in the database.

If no face is detected in the image (`enforce_detection=True`), the service raises a dedicated error and the user receives a clear message to adjust lighting or camera angle.

### Confidence Score Generation

The confidence score corresponds to the model's predicted probability for the dominant emotion class, expressed as an integer percentage (0–100). The value is read directly from DeepFace's emotion score dictionary and clamped to a maximum of 100 to prevent display anomalies from floating-point rounding.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Bootstrap UI │  │  camera.js   │  │ MediaDevices API │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼──────────────┘
          │                 │                   │
          │    HTTP (HTML)    │   REST (JSON)     │  getUserMedia
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask Backend (app.py)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Routes  │  │  Upload  │  │ Analyze  │  │  Templates │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────────┘  │
│       │             │             │                         │
│       │             ▼             ▼                         │
│       │      ┌────────────┐  ┌─────────────────┐           │
│       │      │  uploads/  │  │ emotion_service │           │
│       │      └────────────┘  └────────┬────────┘           │
│       │                               │                     │
│       ▼                               ▼                     │
│  ┌─────────────┐              ┌──────────────┐             │
│  │  database/  │              │   DeepFace   │             │
│  │   (SQLite)  │              │  (TensorFlow)│             │
│  └─────────────┘              └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Flask Backend

The backend is built with **Flask 3.x** and exposes both server-rendered pages and JSON API endpoints. It handles image uploads, orchestrates emotion analysis, persists results, and serves the history and statistics views.

| Route      | Method | Description                          |
|------------|--------|--------------------------------------|
| `/`        | GET    | Main camera and analysis page        |
| `/history` | GET    | Emotion analysis history             |
| `/stats`   | GET    | Emotion distribution statistics      |
| `/upload`  | POST   | Receive and store captured image     |
| `/analyze` | POST   | Run DeepFace analysis on uploaded image |

### Bootstrap Frontend

The user interface uses **Bootstrap 5.3** (CDN) with custom CSS for a clean, mobile-first layout. The main page (`index.html`) provides the camera preview, capture button, and result panel. History and statistics pages share a consistent navigation bar and container width (max 480 px).

Client-side logic in `camera.js` manages camera access, frame capture via HTML5 Canvas, asynchronous upload/analysis requests, and dynamic result rendering.

### SQLite Database

Analysis results are stored in a local **SQLite** database (`instance/emotions.db`). The `emotions` table records:

| Column     | Type     | Description                    |
|------------|----------|--------------------------------|
| `id`       | INTEGER  | Primary key                    |
| `timestamp`| DATETIME | UTC timestamp of analysis      |
| `emotion`  | TEXT     | Dominant emotion label         |
| `confidence`| REAL    | Confidence score (0–100)       |

### Camera Integration

The browser **MediaDevices API** (`getUserMedia`) accesses the device camera with:

- Front-facing mode (`facingMode: "user"`)
- `playsinline` and `muted` attributes for iOS Safari compatibility
- HTTPS requirement enforced via secure context check (satisfied by ngrok or localhost)

Captured frames are drawn to a hidden canvas and exported as JPEG blobs for upload.

### DeepFace Service

The `services/emotion_service.py` module encapsulates all AI logic. It accepts a file path, invokes `DeepFace.analyze()` with `actions=["emotion"]`, extracts the dominant emotion and confidence, and returns a structured JSON-compatible dictionary. Error handling distinguishes file-not-found, no-face-detected, and general analysis failures.

---

## Application Workflow

```
User
  │
  ▼
Opens application in mobile browser (HTTPS)
  │
  ▼
Camera ──► Live preview starts via getUserMedia
  │
  ▼
Capture ──► User taps "Capturar"
  │           Frame drawn to hidden canvas
  │
  ▼
Upload ──► JPEG sent to POST /upload
  │           Saved to uploads/ with UUID filename
  │
  ▼
DeepFace Analysis ──► POST /analyze with filename
  │                     Face detection + emotion inference
  │
  ▼
Result Display ──► Emotion label, icon, summary,
  │                 confidence bar shown in Spanish
  │
  ▼
Database Storage ──► Record inserted into SQLite
                      (emotion, confidence, timestamp)
```

---

## Technologies Used

| Category            | Technology                        |
|---------------------|-----------------------------------|
| Backend framework   | Flask 3.x                         |
| AI / Deep learning  | DeepFace, TensorFlow 2.x          |
| Computer vision     | OpenCV (headless)                 |
| Database            | SQLite 3                          |
| Frontend framework  | Bootstrap 5.3                     |
| Client scripting    | Vanilla JavaScript (ES5+)         |
| Camera API          | MediaDevices / getUserMedia       |
| Image processing    | HTML5 Canvas                      |
| Language            | Python 3.12                       |
| Tunneling (mobile)  | ngrok                             |

---

## Project Structure

```
Emotion Detector/
├── app.py                  # Flask application and route definitions
├── requirements.txt        # Python dependencies
├── validate_ai.py          # Standalone DeepFace validation script
├── README.md               # Project documentation
│
├── database/
│   └── db.py               # SQLite initialization and CRUD operations
│
├── services/
│   └── emotion_service.py  # DeepFace emotion analysis service
│
├── templates/
│   ├── index.html          # Main camera and analysis page
│   ├── history.html        # Emotion history view
│   └── stats.html          # Emotion statistics view
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom mobile-first styles
│   └── js/
│       └── camera.js       # Camera, capture, and API client logic
│
├── uploads/                # Stored captured images (gitignored)
└── instance/
    └── emotions.db         # SQLite database (gitignored)
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip
- A webcam or mobile device with camera access
- (Optional) [ngrok](https://ngrok.com/) for mobile testing over HTTPS

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/emotion-detector.git
   cd emotion-detector
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   .venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** The first run will download DeepFace model weights (~100 MB). Ensure a stable internet connection.

4. **Verify the AI component (optional)**

   ```bash
   python validate_ai.py path/to/test_image.jpg
   ```

---

## Running the Project

Start the Flask development server:

```bash
python app.py
```

The application will be available at:

```
http://localhost:5000
```

Open this URL in a desktop browser for local testing. Camera access requires a secure context (HTTPS or localhost).

---

## Mobile Testing with ngrok

Mobile browsers require HTTPS for camera access. Use ngrok to expose the local server securely:

1. **Start the Flask server**

   ```bash
   python app.py
   ```

2. **Start ngrok in a separate terminal**

   ```bash
   ngrok http 5000
   ```

3. **Open the HTTPS URL** provided by ngrok (e.g., `https://abc123.ngrok-free.app`) on your iPhone or Android device using Safari or Chrome.

4. **Grant camera permission** when prompted.

5. **Pre-warm the model** by performing one test capture before a live demonstration. The first analysis may take 15–30 seconds while DeepFace loads its models.

---

## Usage Instructions

1. Open the application in a supported mobile browser (HTTPS required).
2. Allow camera access when the browser requests permission.
3. Position your face within the live camera preview.
4. Tap **Capturar** to capture and analyze your expression.
5. Wait for the analysis to complete (a loading indicator is shown).
6. Review the detected **emotion** and **confidence score**.
7. Navigate to **Historial** to view past analyses.
8. Navigate to **Estadísticas** to see emotion distribution across all sessions.

### Tips for Best Results

- Face the camera directly with adequate lighting.
- Avoid extreme angles or partial face occlusion.
- Wait for the camera preview to fully load before capturing.
- If no face is detected, adjust position and try again.

---

## Screenshots

> Replace the placeholders below with actual screenshots before publication.

### Main Page — Camera and Analysis

![Main page — live camera preview and capture button](docs/screenshots/main-page.png)

### Emotion Result

![Detected emotion with confidence score](docs/screenshots/emotion-result.png)

### History Page

![Chronological list of past emotion analyses](docs/screenshots/history-page.png)

### Statistics Page

![Emotion distribution with counts and percentages](docs/screenshots/stats-page.png)

---

## Future Improvements

- **Real-time video analysis** — continuous emotion detection without manual capture
- **Multi-face support** — analyze multiple faces in a single frame
- **User authentication** — personal history and session management
- **Model selection** — allow switching between DeepFace backend models
- **Deployment pipeline** — production hosting on Render, Railway, or similar
- **Local timezone display** — convert UTC timestamps to the user's locale
- **Image cleanup policy** — automatic removal of old uploads to manage disk usage
- **Progress indicator** — granular feedback during long model loading
- **Internationalization** — support for additional languages beyond Spanish
- **Unit and integration tests** — automated test coverage for API and service layers

---

## Academic Context

This project was developed as part of an **Artificial Intelligence course** at university level. It demonstrates the practical application of deep learning concepts—specifically computer vision and facial expression analysis—in a full-stack web application.

The project covers key AI and software engineering topics including:

- Integration of pre-trained deep learning models via DeepFace
- Face detection and multi-class emotion classification
- Confidence scoring and result interpretation
- Building a user-facing AI system with appropriate error handling
- Persisting and visualizing AI inference results
- Mobile-first design for real-world AI interaction

EmotionCam Web serves as both a functional prototype and a portfolio piece showcasing the ability to connect AI research tools with accessible, production-oriented software design.

---

## License

This project was created for academic purposes. See the repository for license details.
