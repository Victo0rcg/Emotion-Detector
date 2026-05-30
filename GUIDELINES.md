# EmotionCam Web
## Final Project – Artificial Intelligence Applied to Mobile Applications

---

# Project Overview

## Project Name

**EmotionCam Web**

## Description

EmotionCam Web is a mobile-friendly web application capable of detecting human facial emotions using Artificial Intelligence techniques. Users can capture a photo through their device camera, analyze the image using a pre-trained emotion recognition model, store results, and visualize emotional history and statistics.

The application is developed as a responsive web application using Flask, allowing it to run on smartphones, tablets, and desktop browsers without requiring installation from an app store.

---

# Project Objectives

## General Objective

Develop a functional mobile-oriented web application that integrates Artificial Intelligence techniques for real-time facial emotion recognition.

## Specific Objectives

- Capture images using the device camera.
- Detect and classify facial emotions using a pre-trained AI model.
- Store emotion analysis results locally.
- Display historical emotion records.
- Generate basic emotional statistics.
- Deploy the application online for public access.

---

# Artificial Intelligence Techniques

The project implements the following AI techniques:

## Computer Vision

Used for image acquisition and facial processing.

## Facial Detection

Face localization before emotion analysis.

## Deep Learning (CNN)

Emotion classification is performed using a pre-trained Convolutional Neural Network through the DeepFace framework.

---

# Technology Stack

## Backend

- Flask
- Python 3.11+

## Artificial Intelligence

- DeepFace
- TensorFlow
- OpenCV

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Database

- SQLite

## Deployment

- Render
- Railway (optional alternative)

---

# System Architecture

```text
Browser
    ↓
Flask Routes
    ↓
Emotion Service
    ↓
SQLite Database
```

---

# Project Structure

```text
emotioncam/

│
├── app.py
│
├── services/
│   └── emotion_service.py
│
├── database/
│   └── db.py
│
├── templates/
│   ├── index.html
│   ├── history.html
│   └── stats.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── camera.js
│
├── uploads/
│
├── instance/
│   └── emotions.db
│
├── requirements.txt
│
└── README.md
```

---

# Functional Requirements

## FR-01 Camera Access

The system shall allow the user to access the device camera.

### Inputs

- User grants camera permission.

### Outputs

- Live camera preview.

---

## FR-02 Image Capture

The system shall allow the user to capture a photo.

### Inputs

- Capture button.

### Outputs

- Stored image file.

---

## FR-03 Emotion Analysis

The system shall analyze the captured image and determine the dominant emotion.

### Inputs

- Captured image.

### Outputs

- Emotion label.
- Confidence percentage.

Example:

```text
Emotion: Happy
Confidence: 87%
```

---

## FR-04 Result Storage

The system shall store all analyses in a database.

Stored fields:

- Date
- Time
- Emotion
- Confidence

---

## FR-05 Emotion History

The system shall display previously recorded analyses.

Example:

```text
May 30 10:05 PM
Happy

May 30 10:03 PM
Neutral

May 30 09:58 PM
Sad
```

---

## FR-06 Emotion Statistics

The system shall generate statistical summaries from stored records.

Example:

```text
Happy: 60%
Neutral: 25%
Sad: 15%
```

---

# Non-Functional Requirements

## Performance

Emotion analysis should complete within a few seconds.

## Usability

The interface should be mobile-friendly and intuitive.

## Compatibility

The application should work on:

- iPhone (Safari)
- Android (Chrome)
- Desktop browsers

## Reliability

The application should gracefully handle invalid images or missing faces.

---

# Database Design

## Table: emotions

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    emotion TEXT,
    confidence REAL
);
```

---

# API Design

## Route: Home

### GET /

Displays the main interface.

---

## Route: Analyze Emotion

### POST /analyze

Receives an image and returns analysis results.

### Response

```json
{
  "emotion": "happy",
  "confidence": 87
}
```

---

## Route: History

### GET /history

Displays all stored analyses.

---

## Route: Statistics

### GET /stats

Displays emotion frequency statistics.

---

# User Interface Design

## Home Screen

```text
--------------------------------
EmotionCam

[ Open Camera ]

[ Capture ]

Detected Emotion:
Happy

Confidence:
87%
--------------------------------
```

---

## History Screen

```text
--------------------------------
Emotion History

Happy
Neutral
Happy
Sad
--------------------------------
```

---

## Statistics Screen

```text
--------------------------------
Emotion Statistics

Happy 50%
Neutral 30%
Sad 20%
--------------------------------
```

---

# Development Roadmap

## Phase 1 – AI Prototype

### Estimated Time

2–3 Hours

### Objective

Verify that emotion recognition works independently before integrating it into Flask.

### Tasks

- Install DeepFace.
- Install OpenCV.
- Analyze a sample image.
- Verify emotion detection.

### Success Criteria

The system correctly returns a dominant emotion.

---

## Phase 2 – Flask Setup

### Estimated Time

2 Hours

### Objective

Create the web application structure.

### Tasks

- Configure Flask project.
- Create routes.
- Create templates.

### Success Criteria

Application runs locally at:

```text
http://localhost:5000
```

---

## Phase 3 – Camera Integration

### Estimated Time

3 Hours

### Objective

Allow image capture from browser.

### Tasks

- Access device camera.
- Display live preview.
- Capture image.
- Upload image to Flask.

### Success Criteria

Captured image is successfully received by the backend.

---

## Phase 4 – Emotion Analysis Integration

### Estimated Time

3 Hours

### Objective

Connect Flask and DeepFace.

### Tasks

- Create emotion service.
- Analyze uploaded images.
- Return results to user.

### Success Criteria

Captured images return emotion predictions.

---

## Phase 5 – Database Integration

### Estimated Time

1 Hour

### Objective

Store analysis results.

### Tasks

- Create SQLite database.
- Create emotions table.
- Insert analysis records.

### Success Criteria

Every analysis is persisted.

---

## Phase 6 – History Module

### Estimated Time

1 Hour

### Objective

Display previous analyses.

### Tasks

- Query database.
- Render history page.

### Success Criteria

History page displays stored records.

---

## Phase 7 – Statistics Module

### Estimated Time

1 Hour

### Objective

Generate emotion statistics.

### Tasks

- Aggregate emotion counts.
- Calculate percentages.
- Display results.

### Success Criteria

Statistics are correctly calculated.

---

## Phase 8 – UI Improvements

### Estimated Time

30 Minutes

### Objective

Improve mobile usability.

### Tasks

- Add Bootstrap styling.
- Improve navigation.
- Optimize responsive design.

### Success Criteria

Application looks acceptable on smartphones.

---

# Deployment Plan

## Objective

Publish the application online.

## Platform

Render

## Deployment Process

```text
Local Development
        ↓
GitHub Repository
        ↓
Render Deployment
        ↓
Public URL
```

Example:

```text
https://emotioncam.onrender.com
```

---

# Testing Plan

## Test 1 – Camera Access

Expected Result:

Camera preview appears.

---

## Test 2 – Image Capture

Expected Result:

Image is uploaded successfully.

---

## Test 3 – Emotion Recognition

Expected Result:

System identifies dominant emotion.

---

## Test 4 – History Storage

Expected Result:

Analysis is stored in database.

---

## Test 5 – Statistics Generation

Expected Result:

Emotion percentages are correctly displayed.

---

# Deliverables

## Source Code

Complete project repository.

## Technical Documentation

Includes:

- Objectives
- Architecture
- AI Techniques
- Screenshots
- Results

## Demonstration Video

Duration:

3–5 minutes

Contents:

- Project overview
- Live demonstration
- Emotion analysis
- History module
- Statistics module

## Final Presentation

Slides summarizing:

- Problem
- Solution
- Technologies
- AI Components
- Results

---

# MVP Definition

The project will be considered complete if the following features work correctly:

- Camera access
- Image capture
- Emotion recognition
- Emotion display
- Database storage
- History visualization
- Statistics visualization

Deployment to a public URL is considered an additional feature that increases usability and project quality.