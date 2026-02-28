const micBtn = document.getElementById('micBtn');
const recordingStatus = document.getElementById('recordingStatus');

let recognition = null;
let silenceTimer = null;
let lastSentText = '';

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = typeof currentLang !== 'undefined' ? (currentLang === 'en' ? 'en-US' : 'ja-JP') : 'ja-JP';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
        if (micBtn) micBtn.classList.add('recording');
        if (recordingStatus) recordingStatus.style.visibility = 'visible';
    };

    recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            }
        }

        if (finalTranscript && finalTranscript !== lastSentText) {
            lastSentText = finalTranscript;
            clearTimeout(silenceTimer);
            silenceTimer = setTimeout(() => {
                if (typeof socket !== 'undefined' && socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({ type: "text", content: finalTranscript, language: typeof currentLang !== 'undefined' ? currentLang : 'ja' }));
                    if (typeof showLoadingStage === 'function') {
                        showLoadingStage('listening');
                        setTimeout(() => showLoadingStage('thinking'), 1500);
                    }
                }
                console.log('Sent final transcript:', finalTranscript);
                recognition.stop();
                lastSentText = '';
            }, 4000);
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };
}

function startRecording() {
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            console.error("Recognition start error:", e);
        }
    } else {
        alert("お使いのブラウザはWeb Speech APIをサポートしていません。Chrome等を使用してください。");
    }
}

function stopRecording() {
    if (recognition) {
        recognition.stop();
    }
    if (micBtn) micBtn.classList.remove('recording');
    if (recordingStatus) recordingStatus.style.visibility = 'hidden';
}

if (micBtn) {
    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('recording')) {
            stopRecording();
        } else {
            startRecording();
        }
    });
}
