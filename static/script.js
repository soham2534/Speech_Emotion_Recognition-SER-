let mediaRecorder;
let audioChunks = [];
let recordedBlob = null;
let selectedFile = null;

// Start Recording
document.getElementById("startRecording").addEventListener("click", async () => {
    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = []; // Reset chunks for new recording

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: "audio/wav" });
        let audioUrl = URL.createObjectURL(recordedBlob);
        document.getElementById("audioPlayback").src = audioUrl;
        
        activateUploadButton();
    };

    mediaRecorder.start();
    document.getElementById("startRecording").disabled = true;
    document.getElementById("stopRecording").disabled = false;
});

// Stop Recording
document.getElementById("stopRecording").addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
    }
    document.getElementById("startRecording").disabled = false;
    document.getElementById("stopRecording").disabled = true;
});

// Select File
document.getElementById("audioFile").addEventListener("change", (event) => {
    selectedFile = event.target.files[0];
    activateUploadButton();
});

// Activate Upload Button
function activateUploadButton() {
    let uploadBtn = document.getElementById("uploadButton");
    uploadBtn.disabled = false;
    uploadBtn.classList.add("upload-active");
}

// Upload Audio
document.getElementById("uploadButton").addEventListener("click", () => {
    let formData = new FormData();

    if (recordedBlob) {
        formData.append("file", recordedBlob, "recording.wav");
        formData.append("type", "recorded");
    } else if (selectedFile) {
        formData.append("file", selectedFile);
        formData.append("type", "uploaded");
    } else {
        alert("No audio selected or recorded!");
        return;
    }

    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Prediction response:", data);
        let resultElement = document.getElementById("result");

        if (data.emotion) {
            let confidenceText = data.confidence ? ` (${data.confidence.toFixed(2)}% confidence)` : "";
            resultElement.innerText = `🎭 Predicted Emotion: ${data.emotion}${confidenceText}`;
        } else {
            resultElement.innerText = "⚠️ Error: No emotion detected!";
        }

        resetUploadButton();
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("result").innerText = "⚠️ Error processing the request!";
    });

    // Reset selected file after upload
    document.getElementById("audioFile").value = "";
    selectedFile = null;
});

// Reset Upload Button
function resetUploadButton() {
    let uploadBtn = document.getElementById("uploadButton");
    uploadBtn.disabled = true;
    uploadBtn.classList.remove("upload-active");
}

// User Signup
document.getElementById("signupForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    
    let email = document.getElementById("signupEmail").value;
    let password = document.getElementById("signupPassword").value;
    
    fetch('/signup', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            window.location.href = "/login";
        }
    })
    .catch(error => console.error("Signup Error:", error));
});

// User Login
document.getElementById("loginForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    
    let email = document.getElementById("loginEmail").value;
    let password = document.getElementById("loginPassword").value;
    
    fetch('/login', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            window.location.href = "/";
        }
    })
    .catch(error => console.error("Login Error:", error));
});
