let socket;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket received:", data.type);

        if (data.type === 'instant') {
            createPageCard(data);
        } else if (data.type === 'image') {
            updateCardImage(data.card_id, data.image_base64);
        }

        if (data.type === 'instant' && data.guide) {
            let guideContent = data.guide;
            const match = guideContent.match(/「[^」]+」/);
            if (match) {
                guideContent = match[0];
            }
            if (guideContent.length > 25) {
                guideContent = guideContent.substring(0, 24) + '…」';
            }
            const guideTextEl = document.getElementById('guideText');
            const guideBar = document.getElementById('globalGuideBar');
            if (guideTextEl) guideTextEl.textContent = guideContent;
            if (guideBar) {
                guideBar.style.display = 'block';
                const guideLabel = document.querySelector('#globalGuideBar div:first-child');
                if (guideLabel) {
                    guideLabel.textContent = (typeof currentLang !== 'undefined' && currentLang === 'en') ? 'Try saying:' : 'こう いってみよう！';
                }
            }
        }
    };

    socket.onclose = () => {
        console.log("WebSocket closed. Reconnecting...");
        setTimeout(initWebSocket, 2000);
    };
}

initWebSocket();

function showLoadingStage(stage) {
    let loader = document.getElementById('activeLoader');
    const storyContainer = document.getElementById('storyContainer');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'activeLoader';
        loader.style.cssText = 'text-align:center; padding:40px 20px; animation: fadeInUp 0.4s ease-out;';
        if (storyContainer) storyContainer.appendChild(loader);
    }

    const lang = typeof currentLang !== 'undefined' ? currentLang : 'ja';

    if (stage === 'listening') {
        const msg = lang === 'en' ? 'Listening to Grandpa...' : 'おじいちゃんの おはなしを きいてるよ...';
        loader.innerHTML = `<div style="font-size:48px; margin-bottom:16px;">👂</div>
            <div style="font-size:20px; font-family:Zen Maru Gothic,sans-serif; opacity:0.7;">${msg}</div>`;
    } else if (stage === 'thinking') {
        const msg = lang === 'en' ? 'Thinking about the story...' : 'おはなしを まとめてるよ...';
        loader.innerHTML = `<div style="font-size:48px; margin-bottom:16px;">💭</div>
            <div style="font-size:20px; font-family:Zen Maru Gothic,sans-serif; opacity:0.7;">${msg}</div>`;
    } else if (stage === 'drawing') {
        const msg = lang === 'en' ? 'Drawing a picture...' : 'えを かいてるよ...';
        loader.innerHTML = `<div style="font-size:48px; margin-bottom:16px;">🎨</div>
            <div style="font-size:20px; font-family:Zen Maru Gothic,sans-serif; opacity:0.7;">${msg}</div>`;
    }

    loader.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function removeLoader() {
    const loader = document.getElementById('activeLoader');
    if (loader) loader.remove();
}

function createPageCard(data) {
    removeLoader();
    console.log("Creating new card with ID:", data.card_id);

    const storyContainer = document.getElementById('storyContainer');
    if (!storyContainer) return;

    const card = document.createElement('div');
    card.className = 'page-card';
    card.id = `card-${data.card_id}`;

    const emojiRow = document.createElement('div');
    emojiRow.style.cssText = 'text-align:center; font-size:48px; min-height:60px;';

    const emojiStr = String(data.emoji || '');
    const emojis = emojiStr.match(/\p{Emoji_Presentation}|\p{Emoji}\uFE0F/gu) || [];
    emojis.forEach((em, index) => {
        const span = document.createElement('span');
        span.textContent = em;
        span.style.cssText = `
            display: inline-block;
            opacity: 0;
            transform: scale(0) translateY(20px);
            animation: emojiPop 0.5s ease-out forwards;
            animation-delay: ${index * 0.3}s;
            margin: 0 4px;
        `;
        emojiRow.appendChild(span);
    });
    card.appendChild(emojiRow);

    const imgContainer = document.createElement('div');
    imgContainer.className = 'card-image-container';
    const placeholder = document.createElement('div');
    placeholder.className = 'image-placeholder';
    placeholder.id = `placeholder-${data.card_id}`;
    placeholder.innerHTML = '<div style="text-align:center; padding:60px 20px;">' +
        '<div style="font-size:48px; animation: emojiPop 0.5s ease-out;">🎨</div>' +
        '<div style="font-size:16px; font-family:Zen Maru Gothic,sans-serif; opacity:0.6; margin-top:12px;">えを かいてるよ...</div>' +
        '</div>';

    const img = document.createElement('img');
    img.className = 'story-image';
    img.id = `img-${data.card_id}`;
    imgContainer.appendChild(placeholder);
    imgContainer.appendChild(img);
    card.appendChild(imgContainer);

    const translatedRow = document.createElement('div');
    translatedRow.className = 'translated-display';
    translatedRow.textContent = data.translated || '...';
    card.appendChild(translatedRow);

    const footerRow = document.createElement('div');
    footerRow.className = 'card-footer-small';
    const orig = document.createElement('div');
    orig.className = 'original-text';
    orig.textContent = '🗣️ ' + (data.original || 'おじいちゃんの おはなし');
    const emotionBadge = document.createElement('div');
    emotionBadge.className = 'emotion-display';
    emotionBadge.textContent = data.emotion || '...';
    footerRow.appendChild(orig);
    footerRow.appendChild(emotionBadge);
    card.appendChild(footerRow);

    storyContainer.appendChild(card);

    setTimeout(() => {
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

function updateCardImage(cardId, imageBase64) {
    console.log("Updating image for card:", cardId);
    const placeholder = document.getElementById(`placeholder-${cardId}`);
    const imgEl = document.getElementById(`img-${cardId}`);

    if (placeholder && imgEl) {
        placeholder.style.display = 'none';

        imgEl.src = `data:image/png;base64,${imageBase64}`;

        imgEl.onload = () => {
            imgEl.classList.add('loaded');
            setTimeout(() => {
                const cardElement = document.getElementById(`card-${cardId}`);
                if (cardElement) {
                    cardElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 300);
        };
    } else {
        console.error("Card or image elements not found for ID:", cardId);
    }
}
