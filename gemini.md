# CogniBridge — Speech Storyboard

## What We're Building
A real-time app where speech is converted into illustrations + simple subtitles.
When someone speaks, the listener sees an illustration of what was said — 
no reading required. Designed for children who can't read, deaf children, 
children with cognitive disabilities, and cross-generational communication.

## This is a Mistral AI Hackathon Project
Mistral API must be the CORE intelligence. Gemini is used ONLY for image generation.
- Mistral = the brain (understands speech, translates, creates scene descriptions)
- Gemini = the hand (draws the illustration from Mistral's description)
- ElevenLabs = ears and mouth (STT and TTS)

## Tech Stack (DO NOT CHANGE)
- Backend: Python 3.11+ / FastAPI / WebSocket
- Frontend: Single HTML file, vanilla JS, vanilla CSS. NO frameworks. NO npm.
- APIs:
  - Mistral Agents API — cognitive translation + scene prompt generation + emotion + guide
  - Google Gemini API (gemini-2.5-flash-image or gemini-3.1-flash-image-preview) — image generation
  - ElevenLabs Scribe v2 — STT
  - ElevenLabs Flash v2.5 — TTS
- OS: Windows 11, PowerShell terminal

## Architecture
### Image Generation
- **PRIMARY: Gemini 2.5 Flash Image** (`gemini-2.5-flash-image`) via `generate_content()`
  - Speed: ~8s per image
  - Advantage: Returns text + image in single call
  - Config: `response_modalities=['TEXT', 'IMAGE']`
- **FALLBACK: Imagen 4.0 Fast** (`imagen-4.0-fast-generate-001`) via `generate_images()`
  - Speed: ~7.7s per image
  - Image only, no text
- **REMOVED**: Mistral built-in (too slow, rate-limited, ~12s)
- **REMOVED**: `gemini-3.1-flash-image-preview` (18s, too slow)

### Timing Budget (per utterance)
- **Instant Layer (< 2s)**: Emoji + translated text + emotion + guide (Mistral Agent JSON)
- **Async Layer (~ 8s)**: Illustration added to storyboard (Gemini/Imagen)
- *User speaks next sentence during async wait → natural pacing.*

### Logic Flow
1. Speaker talks into mic
2. ElevenLabs Scribe v2 STT (speech → text, ~150ms)
3. Mistral Agent "SceneTranslator" ← ★ CORE of the hackathon
   - Returns JSON:
     ```json
     {
       "translated": "Simple Japanese for children",
       "emotion": "happy/sad/tired/fun/neutral",
       "emoji": "🍅👴🌞",
       "scene_prompt": "English prompt for image generation",
       "guide": "Conversation advice for the listener"
     }
     ```
4. Two parallel paths:
   - **[INSTANT - 0 sec]** Send emoji + translated + emotion + guide → frontend via WebSocket
     - Frontend shows stage animations (0.0s to 0.5s)
   - **[ASYNC - 8 sec]** Send `scene_prompt` → Gemini/Imagen API → illustration
     - Frontend: illustration fades into storyboard panel

## Rules
- ALWAYS use PowerShell-compatible commands (not bash/linux)
- NEVER add npm, node, React, or any JS framework
- NEVER rewrite entire files — make targeted edits only
- Keep frontend in ONE index.html file (inline CSS + JS)
- All API keys are in .env at project root — use python-dotenv
- Before making changes, show me the plan and wait for approval
- When generating code, add brief Japanese comments for key sections
- Test files go in backend/ with prefix test_

## Existing Working Components
- backend/test_mistral.py — Agent creation + conversation working
- backend/test_multimodal_bench.py — 8s image generation verified
- backend/main.py — Basic FastAPI health endpoint working
- .env — MISTRAL_API_KEY, ELEVENLABS_API_KEY, GEMINI_API_KEY

## Agent IDs
- GrandpaToChild: ag_019ca22cdac672aca58444df7da1d1a3
- ChildToGrandpa: [TBD]
- SceneTranslator (combined): [TBD — will replace separate agents]

## Key Dependencies
- mistralai (installed)
- fastapi, uvicorn, websockets, httpx, python-dotenv (installed)
- google-genai, Pillow (installed)

## Image Generation Notes
- Mistral's built-in image_generation: ~12 sec. DO NOT USE for real-time.
- Gemini 2.5 Flash Image: 8s. USE THIS via `generate_content`.
- Imagen 4.0 Fast: 7.7s. Use as FALLBACK.
- Python SDK: google-genai
- App MUST work even if image generation fails — emoji + subtitle is the minimum

## Debug Rules (ALWAYS FOLLOW)
- After ANY code change, check terminal output for errors
- After ANY frontend change, check browser DevTools console (F12)
- When fixing bugs, add print() / console.log() FIRST to find the issue
- Never remove existing print() statements during this hackathon
- After every fix, test by restarting server and refreshing browser
- The mic button must work UNLIMITED times (not just once)
- WebSocket must stay open for the entire session
