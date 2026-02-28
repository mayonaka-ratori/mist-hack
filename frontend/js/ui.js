let currentLang = 'ja';

function toggleLanguage() {
    currentLang = currentLang === 'ja' ? 'en' : 'ja';

    if (typeof recognition !== 'undefined' && recognition) {
        recognition.lang = currentLang === 'en' ? 'en-US' : 'ja-JP';
        console.log('[LANG] Speech recognition set to:', recognition.lang);
    }

    const btn = document.getElementById('langToggle');
    if (currentLang === 'en') {
        btn.textContent = '🇬🇧 → 🇯🇵';
        btn.style.background = 'rgba(100,149,237,0.3)';
        btn.style.borderColor = 'rgba(100,149,237,0.5)';
        document.querySelector('#headerBar a').textContent = '📚 History';
        document.getElementById('endSessionBtn').textContent = 'End 📖';
    } else {
        btn.textContent = '🇯🇵 → 🇬🇧';
        btn.style.background = 'rgba(255,107,138,0.3)';
        btn.style.borderColor = 'rgba(255,107,138,0.5)';
        document.querySelector('#headerBar a').textContent = '📚 まえの おはなし';
        document.getElementById('endSessionBtn').textContent = 'おわり 📖';
    }
    if (typeof socket !== 'undefined' && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'set_language', language: currentLang }));
    }
}

async function saveConversation() {
    const btn = document.getElementById('endSessionBtn');
    const res = await fetch('/save-conversation', { method: 'POST' });
    const result = await res.json();
    if (result.status === 'saved') {
        const msg = currentLang === 'en' ? 'Story saved! 📚' : 'ほぞん したよ！ 📚';
        btn.textContent = msg;
        btn.style.background = 'rgba(100,200,100,0.3)';
        setTimeout(() => {
            document.getElementById('storyContainer').innerHTML = '';
            const guideBar = document.getElementById('globalGuideBar');
            if (guideBar) guideBar.style.display = 'none';
            btn.textContent = currentLang === 'en' ? 'End 📖' : 'おわり 📖';
            btn.style.background = 'rgba(255,255,255,0.1)';
        }, 2000);
    } else if (result.status === 'empty') {
        btn.textContent = currentLang === 'en' ? 'Please speak' : 'おはなし してね';
        setTimeout(() => { btn.textContent = currentLang === 'en' ? 'End 📖' : 'おわり 📖'; }, 1500);
    }
}

function scrollToBottom() {
    const storyContainer = document.getElementById('storyContainer');
    if (storyContainer) {
        storyContainer.scrollTo({
            top: storyContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
}
