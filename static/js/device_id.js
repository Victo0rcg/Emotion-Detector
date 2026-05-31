(function () {
    "use strict";

    const STORAGE_KEY = "emotion_device_id";
    const COOKIE_NAME = "emotion_device_id";
    const COOKIE_TTL_DAYS = 365;

    function generateDeviceId() {
        if (typeof crypto === "undefined" || typeof crypto.randomUUID !== "function") {
            throw new Error("crypto.randomUUID() is required to generate the device identifier.");
        }
        return crypto.randomUUID();
    }

    function getDeviceIdFromLocalStorage() {
        try {
            return window.localStorage.getItem(STORAGE_KEY);
        } catch (error) {
            return null;
        }
    }

    function setDeviceIdInLocalStorage(deviceId) {
        try {
            window.localStorage.setItem(STORAGE_KEY, deviceId);
        } catch (error) {
            console.warn("Unable to write device identifier to localStorage.", error);
        }
    }

    function getDeviceIdFromCookie() {
        const cookieString = document.cookie || "";
        const name = COOKIE_NAME + "=";
        const parts = cookieString.split(";");

        for (let part of parts) {
            part = part.trim();
            if (part.indexOf(name) === 0) {
                return decodeURIComponent(part.substring(name.length));
            }
        }
        return null;
    }

    function setDeviceIdCookie(deviceId) {
        const expires = new Date();
        expires.setDate(expires.getDate() + COOKIE_TTL_DAYS);
        var cookie = COOKIE_NAME + "=" + encodeURIComponent(deviceId) +
            "; path=/; expires=" + expires.toUTCString() +
            "; SameSite=Lax";
        // Only set Secure when the page is served over HTTPS
        if (window && window.location && window.location.protocol === 'https:') {
            cookie += "; Secure";
        }
        document.cookie = cookie;
    }

    function getOrCreateDeviceId() {
        const hadCookie = Boolean(getDeviceIdFromCookie());
        let deviceId = getDeviceIdFromLocalStorage();

        if (!deviceId) {
            deviceId = getDeviceIdFromCookie();
            if (deviceId) {
                setDeviceIdInLocalStorage(deviceId);
            }
        }

        if (!deviceId) {
            deviceId = generateDeviceId();
            setDeviceIdInLocalStorage(deviceId);
        }

        setDeviceIdCookie(deviceId);

        if (!hadCookie && !sessionStorage.getItem("emotion_device_id_reload_done")) {
            sessionStorage.setItem("emotion_device_id_reload_done", "1");
            window.location.reload();
        }

        return deviceId;
    }

    window.getEmotionCamDeviceId = getOrCreateDeviceId;

    getOrCreateDeviceId();
})();
