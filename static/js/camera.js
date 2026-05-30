(function () {
    "use strict";

    const video = document.getElementById("camera-preview");
    const canvas = document.getElementById("capture-canvas");
    const captureBtn = document.getElementById("capture-btn");
    const uploadBtn = document.getElementById("upload-btn");
    const analyzeBtn = document.getElementById("analyze-btn");
    const capturedSection = document.getElementById("captured-section");
    const statusEl = document.getElementById("camera-status");

    const resultEmpty = document.getElementById("result-empty");
    const resultSuccess = document.getElementById("result-success");
    const resultError = document.getElementById("result-error");
    const emotionBadge = document.getElementById("emotion-badge");
    const emotionLabel = document.getElementById("emotion-label");
    const emotionConfidence = document.getElementById("emotion-confidence");
    const confidenceBar = document.getElementById("confidence-bar");

    let stream = null;
    let hasCapturedImage = false;
    let lastUploadedFilename = null;

    function setStatus(message) {
        statusEl.textContent = message;
    }

    function formatEmotion(emotion) {
        return emotion.charAt(0).toUpperCase() + emotion.slice(1);
    }

    function clearResult() {
        resultError.classList.add("d-none");
        resultError.textContent = "";
        resultSuccess.classList.add("d-none");
        resultEmpty.classList.remove("d-none");
    }

    function showResult(emotion, confidence) {
        resultError.classList.add("d-none");
        resultEmpty.classList.add("d-none");
        resultSuccess.classList.remove("d-none");

        const label = formatEmotion(emotion);
        emotionBadge.textContent = label;
        emotionLabel.textContent = label;
        emotionConfidence.textContent = String(confidence);
        confidenceBar.style.width = confidence + "%";
        confidenceBar.setAttribute("aria-valuenow", String(confidence));
        confidenceBar.textContent = confidence + "%";
    }

    function showResultError(message) {
        resultEmpty.classList.add("d-none");
        resultSuccess.classList.add("d-none");
        resultError.textContent = message;
        resultError.classList.remove("d-none");
    }

    function stopCamera() {
        if (!stream) {
            return;
        }

        stream.getTracks().forEach(function (track) {
            track.stop();
        });
        stream = null;
        video.srcObject = null;
    }

    async function startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setStatus("Camera is not supported in this browser.");
            return;
        }

        if (!window.isSecureContext) {
            setStatus("Camera requires a secure connection (HTTPS or localhost).");
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "user",
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false,
            });

            video.srcObject = stream;

            video.addEventListener(
                "loadedmetadata",
                function onMetadataLoaded() {
                    video.removeEventListener("loadedmetadata", onMetadataLoaded);
                    captureBtn.disabled = false;
                    setStatus("");
                },
                { once: true }
            );

            await video.play();
        } catch (error) {
            stopCamera();
            captureBtn.disabled = true;

            if (error.name === "NotAllowedError") {
                setStatus("Camera permission denied. Allow access and reload.");
            } else if (error.name === "NotFoundError") {
                setStatus("No camera found on this device.");
            } else {
                setStatus("Could not start the camera. Try again.");
            }
        }
    }

    function capturePhoto() {
        if (!video.videoWidth || !video.videoHeight) {
            setStatus("Camera is not ready yet. Wait a moment and try again.");
            return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        capturedSection.hidden = false;
        hasCapturedImage = true;
        lastUploadedFilename = null;
        uploadBtn.disabled = false;
        analyzeBtn.disabled = false;
        clearResult();
        setStatus("Photo captured. Tap Upload or Analyze.");
    }

    function canvasToBlob() {
        return new Promise(function (resolve, reject) {
            canvas.toBlob(
                function (blob) {
                    if (!blob) {
                        reject(new Error("Could not prepare the image for upload."));
                        return;
                    }
                    resolve(blob);
                },
                "image/jpeg",
                0.92
            );
        });
    }

    function uploadImage() {
        return canvasToBlob().then(function (blob) {
            const formData = new FormData();
            formData.append("image", blob, "capture.jpg");

            return fetch("/upload", {
                method: "POST",
                body: formData,
            }).then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok || !data.success) {
                        throw new Error(data.error || "Upload failed.");
                    }
                    return data.filename;
                });
            });
        });
    }

    function requestAnalysis(filename) {
        return fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: filename }),
        }).then(function (response) {
            return response.json().then(function (data) {
                if (!response.ok) {
                    throw new Error(data.error || "Analysis failed.");
                }
                return data;
            });
        });
    }

    function uploadPhoto() {
        if (!hasCapturedImage || canvas.width === 0 || canvas.height === 0) {
            setStatus("Capture a photo before uploading.");
            return;
        }

        uploadBtn.disabled = true;
        setStatus("Uploading...");

        uploadImage()
            .then(function (filename) {
                lastUploadedFilename = filename;
                setStatus("Upload successful. Ready to analyze.");
            })
            .catch(function (error) {
                setStatus(error.message);
            })
            .finally(function () {
                uploadBtn.disabled = false;
            });
    }

    function analyzePhoto() {
        if (!hasCapturedImage || canvas.width === 0 || canvas.height === 0) {
            showResultError("Capture a photo before analyzing.");
            return;
        }

        analyzeBtn.disabled = true;
        uploadBtn.disabled = true;
        clearResult();
        setStatus("Analyzing...");

        const uploadPromise = lastUploadedFilename
            ? Promise.resolve(lastUploadedFilename)
            : uploadImage();

        uploadPromise
            .then(function (filename) {
                lastUploadedFilename = filename;
                return requestAnalysis(filename);
            })
            .then(function (data) {
                showResult(data.emotion, data.confidence);
                setStatus("Analysis complete.");
            })
            .catch(function (error) {
                showResultError(error.message);
                setStatus("");
            })
            .finally(function () {
                analyzeBtn.disabled = false;
                uploadBtn.disabled = false;
            });
    }

    captureBtn.addEventListener("click", capturePhoto);
    uploadBtn.addEventListener("click", uploadPhoto);
    analyzeBtn.addEventListener("click", analyzePhoto);

    window.addEventListener("pagehide", stopCamera);

    document.addEventListener("DOMContentLoaded", startCamera);
})();
