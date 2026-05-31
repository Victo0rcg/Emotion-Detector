(function () {
    "use strict";

    const video = document.getElementById("camera-preview");
    const canvas = document.getElementById("capture-canvas");
    const captureBtn = document.getElementById("capture-btn");
    const statusEl = document.getElementById("camera-status");

    const resultEmpty = document.getElementById("result-empty");
    const resultLoading = document.getElementById("result-loading");
    const resultSuccess = document.getElementById("result-success");
    const resultError = document.getElementById("result-error");
    const resultErrorMessage = document.getElementById("result-error-message");
    const resultEmotionCard = document.getElementById("result-emotion-card");
    const emotionIcon = document.getElementById("emotion-icon");
    const emotionLabel = document.getElementById("emotion-label");
    const emotionSummary = document.getElementById("emotion-summary");
    const emotionConfidence = document.getElementById("emotion-confidence");
    const confidenceBar = document.getElementById("confidence-bar");
    const confidenceHint = document.getElementById("confidence-hint");

    const EMOTION_PRESENTATION = {
        angry: {
            label: "Enojado",
            summary: "Señales fuertes de enojo o frustración.",
            icon: "😠",
            tone: "angry",
        },
        disgust: {
            label: "Asco",
            summary: "La expresión sugiere asco o desagrado.",
            icon: "🤢",
            tone: "disgust",
        },
        fear: {
            label: "Miedo",
            summary: "La expresión sugiere miedo o ansiedad.",
            icon: "😨",
            tone: "fear",
        },
        happy: {
            label: "Feliz",
            summary: "Pareces feliz y positivo.",
            icon: "😊",
            tone: "happy",
        },
        sad: {
            label: "Triste",
            summary: "La expresión sugiere tristeza o bajo ánimo.",
            icon: "😢",
            tone: "sad",
        },
        surprise: {
            label: "Sorprendido",
            summary: "La expresión sugiere sorpresa o asombro.",
            icon: "😲",
            tone: "surprise",
        },
        neutral: {
            label: "Neutral",
            summary: "Expresión calmada y equilibrada, sin emoción marcada.",
            icon: "😐",
            tone: "neutral",
        },
    };

    const FRIENDLY_ERRORS = {
        "No se detectó ningún rostro en la imagen.":
            "No encontramos un rostro. Mira a la cámara, mejora la iluminación e inténtalo de nuevo.",
        "No se proporcionó ningún nombre de archivo.":
            "Algo salió mal al preparar tu foto. Captura de nuevo e inténtalo otra vez.",
        "Imagen no encontrada o nombre de archivo no válido.":
            "No se encontró tu foto. Captura de nuevo e inténtalo otra vez.",
        "Imagen no encontrada.":
            "No se encontró tu foto. Captura de nuevo e inténtalo otra vez.",
        "Error al analizar la emoción.":
            "El análisis falló inesperadamente. Espera un momento e inténtalo de nuevo.",
        "Error al subir la imagen.":
            "Error al subir la imagen. Comprueba tu conexión e inténtalo de nuevo.",
        "Error en el análisis.":
            "Error en el análisis. Por favor, inténtalo de nuevo.",
    };

    let stream = null;
    let isProcessing = false;

    function setStatus(message) {
        statusEl.textContent = message;
    }

    function parseResponseJson(response) {
        return response.text().then(function (text) {
            if (!text) {
                return {};
            }
            try {
                return JSON.parse(text);
            } catch (error) {
                if (response.status === 413) {
                    throw new Error("La imagen es demasiado grande.");
                }
                throw new Error("Error en el análisis.");
            }
        });
    }

    function getEmotionPresentation(emotion) {
        const key = (emotion || "").toLowerCase();
        if (EMOTION_PRESENTATION[key]) {
            return EMOTION_PRESENTATION[key];
        }
        const fallbackLabel =
            key.charAt(0).toUpperCase() + key.slice(1) || "Desconocida";
        return {
            label: fallbackLabel,
            summary: "Emoción dominante detectada por el modelo.",
            icon: "🙂",
            tone: "neutral",
        };
    }

    function getFriendlyError(message) {
        return FRIENDLY_ERRORS[message] || message || "Algo salió mal. Por favor, inténtalo de nuevo.";
    }

    function getConfidenceHint(confidence) {
        if (confidence >= 80) {
            return "Alta confianza: el modelo está bastante seguro de este resultado.";
        }
        if (confidence >= 50) {
            return "Confianza moderada: la iluminación o el ángulo pueden afectar la precisión.";
        }
        return "Baja confianza: prueba con una foto más clara y de frente.";
    }

    // Normalize UTC timestamp strings for cross-browser compatibility
    function normalizeUtcString(s) {
        if (!s) return s;
        var str = String(s).replace(/\+00:00$/, "Z");
        if (!/[Zz]$/.test(str) && !/[+-]\d{2}:\d{2}$/.test(str)) {
            str = str + "Z";
        }
        return str;
    }

    function hideAllResultStates() {
        resultEmpty.classList.add("d-none");
        resultLoading.classList.add("d-none");
        resultSuccess.classList.add("d-none");
        resultError.classList.add("d-none");
    }

    function showResultEmpty() {
        hideAllResultStates();
        resultErrorMessage.textContent = "";
        resultEmpty.classList.remove("d-none");
    }

    function showResultLoading() {
        hideAllResultStates();
        resultLoading.classList.remove("d-none");
    }

    function showResult(emotion, confidence) {
        hideAllResultStates();

        const presentation = getEmotionPresentation(emotion);
        const safeConfidence = Math.max(0, Math.min(100, Number(confidence) || 0));

        resultEmotionCard.className =
            "card result-emotion-card border-2 shadow-sm tone-" + presentation.tone;
        emotionIcon.textContent = presentation.icon;
        emotionLabel.textContent = presentation.label;
        emotionSummary.textContent = presentation.summary;
        emotionConfidence.textContent = String(Math.round(safeConfidence));
        confidenceBar.style.width = safeConfidence + "%";
        confidenceBar.setAttribute("aria-valuenow", String(Math.round(safeConfidence)));
        confidenceBar.textContent = Math.round(safeConfidence) + "%";
        confidenceBar.className =
            "progress-bar progress-bar-striped tone-bar-" + presentation.tone;
        confidenceHint.textContent = getConfidenceHint(safeConfidence);

        resultSuccess.classList.remove("d-none");
    }

    function showResultError(message) {
        hideAllResultStates();
        resultErrorMessage.textContent = getFriendlyError(message);
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
            setStatus("Cámara no compatible con este navegador.");
            return;
        }

        if (!window.isSecureContext) {
            setStatus("La cámara requiere una conexión segura (HTTPS o localhost).");
            return;
        }

        stopCamera();
        captureBtn.disabled = true;

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
                setStatus("Permiso de cámara denegado. Permite el acceso y recarga la página.");
            } else if (error.name === "NotFoundError") {
                setStatus("No se encontró ninguna cámara en este dispositivo.");
            } else {
                setStatus("No se pudo iniciar la cámara. Inténtalo de nuevo.");
            }
        }
    }

    function captureFrameToCanvas() {
        if (!video.videoWidth || !video.videoHeight) {
            throw new Error("La cámara aún no está lista. Espera un momento e inténtalo de nuevo.");
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
    }

    function canvasToBlob() {
        return new Promise(function (resolve, reject) {
            canvas.toBlob(
                function (blob) {
                    if (!blob) {
                        reject(new Error("No se pudo preparar la imagen para subir."));
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
                return parseResponseJson(response).then(function (data) {
                    if (!response.ok || !data.success) {
                        throw new Error(data.error || "Error al subir la imagen.");
                    }
                    return data.filename;
                });
            });
        });
    }

    function requestAnalysis(filename) {
        var deviceId = window.getEmotionCamDeviceId();
        return fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: filename, device_id: deviceId }),
        }).then(function (response) {
            return parseResponseJson(response).then(function (data) {
                if (!response.ok) {
                    throw new Error(data.error || "Error en el análisis.");
                }
                return data;
            });
        });
    }

    function captureAndAnalyze() {
        if (isProcessing) {
            return;
        }

        try {
            captureFrameToCanvas();
        } catch (error) {
            setStatus(error.message);
            return;
        }

        isProcessing = true;
        captureBtn.disabled = true;
        showResultLoading();
        setStatus("Analizando...");

        uploadImage()
            .then(function (filename) {
                return requestAnalysis(filename);
            })
            .then(function (data) {
                showResult(data.emotion, data.confidence);
                setStatus("Análisis completado.");
            })
            .catch(function (error) {
                showResultError(error.message);
                setStatus("");
            })
            .finally(function () {
                isProcessing = false;
                captureBtn.disabled = false;
            });
    }

    captureBtn.addEventListener("click", captureAndAnalyze);

    window.addEventListener("pagehide", stopCamera);

    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            startCamera();
        }
    });

    document.addEventListener("DOMContentLoaded", startCamera);
})();
