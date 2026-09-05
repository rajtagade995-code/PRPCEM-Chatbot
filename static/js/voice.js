/**
 * PRPCEM College Assistant - Voice Module
 * Speech-to-Text (STT) and Text-to-Speech (TTS) using browser Web Speech API only.
 * No external AI API. No audio data stored on server.
 */

(function () {
  const DEFAULT_SETTINGS = {
    voiceInputEnabled: true,
    autoReadAnswers: false,
    language: 'en-IN',
    speed: 1.0
  };

  let voiceSettings = loadVoiceSettings();
  let recognition = null;
  let isListening = false;
  let currentUtterance = null;
  let currentSpeakBtn = null;

  function loadVoiceSettings() {
    try {
      const saved = localStorage.getItem('prpcem_voice_settings');
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : { ...DEFAULT_SETTINGS };
    } catch (e) {
      return { ...DEFAULT_SETTINGS };
    }
  }

  function saveVoiceSettings(settings) {
    voiceSettings = { ...voiceSettings, ...settings };
    localStorage.setItem('prpcem_voice_settings', JSON.stringify(voiceSettings));
  }

  const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
  const isSTTSupported = !!SpeechRecognitionAPI;

  function initSpeechRecognition() {
    if (!isSTTSupported) return null;
    recognition = new SpeechRecognitionAPI();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = voiceSettings.language || 'en-IN';

    recognition.onstart = () => { isListening = true; setMicState('listening'); };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      const chatInput = document.getElementById('chatInput');
      if (chatInput) {
        chatInput.value = transcript;
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) sendBtn.disabled = !transcript.trim();
      }
      if (event.results[event.results.length - 1].isFinal) {
        isListening = false;
        setMicState('idle');
      }
    };

    recognition.onerror = (event) => {
      isListening = false;
      setMicState('idle');
      handleSpeechError(event.error);
    };

    recognition.onend = () => { isListening = false; setMicState('idle'); };
    return recognition;
  }

  function startListening() {
    if (!isSTTSupported) {
      showVoiceError('Speech-to-text is not supported in this browser. Please use Chrome or Edge.');
      return;
    }
    if (!voiceSettings.voiceInputEnabled) return;
    if (isListening) { stopListening(); return; }
    try {
      if (!recognition) recognition = initSpeechRecognition();
      recognition.lang = voiceSettings.language || 'en-IN';
      recognition.start();
      setMicState('listening');
    } catch (e) {
      setMicState('idle');
      showVoiceError('Could not start voice recognition. Please try again.');
    }
  }

  function stopListening() {
    if (recognition && isListening) recognition.stop();
    isListening = false;
    setMicState('idle');
  }

  function handleSpeechError(error) {
    const messages = {
      'not-allowed': 'Microphone permission is required. Please allow microphone access in your browser settings.',
      'permission-denied': 'Microphone permission denied. Please allow access to use voice input.',
      'no-speech': 'No speech detected. Please speak clearly into your microphone.',
      'audio-capture': 'No microphone found. Please connect a microphone.',
      'network': 'Network error during voice recognition.',
      'aborted': 'Voice recognition was stopped.',
    };
    const msg = messages[error] || ('Voice recognition error: ' + error);
    if (error !== 'aborted') showVoiceError(msg);
  }

  const isTTSSupported = !!window.speechSynthesis;

  function cleanTextForSpeech(text) {
    text = text.replace(/https?:\/\/[^\s]+/g, '');
    text = text.replace(/\*\*(.*?)\*\*/g, '');
    text = text.replace(/\*(.*?)\*/g, '');
    text = text.replace(/<[^>]+>/g, '');
    text = text.replace(/^[•\-\*]\s+/gm, '');
    text = text.replace(/^\d+\.\s+/gm, '');
    text = text.replace(/source:.*$/gim, '');
    text = text.replace(/view source.*/gi, '');
    text = text.replace(/\n{2,}/g, '. ');
    text = text.replace(/\n/g, '. ');
    text = text.replace(/\.\s*\.\s*\./g, '.');
    return text.replace(/\s+/g, ' ').trim();
  }

  function selectVoice(lang) {
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return null;
    return voices.find(v => v.lang === lang)
      || voices.find(v => v.lang.startsWith(lang.split('-')[0]))
      || voices.find(v => v.lang.startsWith('en'))
      || voices[0];
  }

  function speakAnswer(text, speakBtn) {
    if (!isTTSSupported) return;
    stopSpeaking();
    const cleaned = cleanTextForSpeech(text);
    if (!cleaned) return;

    currentUtterance = new SpeechSynthesisUtterance(cleaned);
    currentSpeakBtn = speakBtn;
    currentUtterance.rate = parseFloat(voiceSettings.speed) || 1.0;
    currentUtterance.lang = voiceSettings.language || 'en-IN';

    const setVoiceAndSpeak = () => {
      const voice = selectVoice(currentUtterance.lang);
      if (voice) currentUtterance.voice = voice;
      currentUtterance.onstart = () => {
        if (speakBtn) { speakBtn.innerHTML = '⏹'; speakBtn.title = 'Stop speaking'; speakBtn.setAttribute('aria-label', 'Stop speaking'); }
      };
      currentUtterance.onend = () => {
        currentUtterance = null; currentSpeakBtn = null;
        if (speakBtn) { speakBtn.innerHTML = '🔊'; speakBtn.title = 'Read answer aloud'; speakBtn.setAttribute('aria-label', 'Read answer aloud'); }
      };
      currentUtterance.onerror = () => {
        currentUtterance = null; currentSpeakBtn = null;
        if (speakBtn) { speakBtn.innerHTML = '🔊'; speakBtn.title = 'Read answer aloud'; }
      };
      window.speechSynthesis.speak(currentUtterance);
    };

    const voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) {
      window.speechSynthesis.addEventListener('voiceschanged', setVoiceAndSpeak, { once: true });
    } else {
      setVoiceAndSpeak();
    }
  }

  function stopSpeaking() {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (currentSpeakBtn) {
      currentSpeakBtn.innerHTML = '🔊';
      currentSpeakBtn.title = 'Read answer aloud';
      currentSpeakBtn.setAttribute('aria-label', 'Read answer aloud');
    }
    currentUtterance = null;
    currentSpeakBtn = null;
  }

  function setMicState(state) {
    const micBtn = document.getElementById('micBtn');
    if (!micBtn) return;
    micBtn.dataset.state = state;
    if (state === 'listening') {
      micBtn.innerHTML = '<span class="mic-pulse">🔴</span>';
      micBtn.title = 'Stop listening'; micBtn.setAttribute('aria-label', 'Stop voice input');
      micBtn.classList.add('mic-active');
    } else {
      micBtn.innerHTML = '🎤';
      micBtn.title = 'Start voice input'; micBtn.setAttribute('aria-label', 'Start voice input');
      micBtn.classList.remove('mic-active');
    }
  }

  function showVoiceError(msg) {
    let toast = document.getElementById('voiceErrorToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'voiceErrorToast';
      toast.style.cssText = 'position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:#ef4444;color:white;padding:10px 18px;border-radius:8px;font-size:0.85rem;z-index:9999;max-width:380px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 4500);
  }

  function renderVoiceSettingsModal() {
    let modal = document.getElementById('voiceSettingsModal');
    if (modal) { modal.classList.add('show'); syncVoiceSettingsUI(); return; }

    modal = document.createElement('div');
    modal.id = 'voiceSettingsModal';
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div class="modal-box" style="max-width:420px;">
        <div class="modal-head"><h3>🎤 Voice Settings</h3><button id="closeVoiceSettingsBtn" class="btn-icon" style="border:none;">✕</button></div>
        <div class="modal-content">
          <div style="margin-bottom:14px;"><label style="display:flex;align-items:center;gap:10px;cursor:pointer;font-weight:500;"><input type="checkbox" id="vsSpeechInput" style="width:18px;height:18px;"> Voice Input (Microphone)</label></div>
          <div style="margin-bottom:14px;"><label style="display:flex;align-items:center;gap:10px;cursor:pointer;font-weight:500;"><input type="checkbox" id="vsAutoRead" style="width:18px;height:18px;"> Auto-read answers (Text-to-Speech)</label></div>
          <div style="margin-bottom:14px;"><label style="display:block;font-weight:500;margin-bottom:6px;">Language</label>
            <select id="vsLanguage" style="width:100%;padding:8px;border-radius:6px;background:var(--bg-secondary,#1e2533);color:var(--text-primary,#fff);border:1px solid var(--border-color,#333);">
              <option value="en-IN">English (India)</option><option value="hi-IN">Hindi (हिंदी)</option><option value="mr-IN">Marathi (मराठी)</option>
            </select></div>
          <div style="margin-bottom:14px;"><label style="display:block;font-weight:500;margin-bottom:6px;">Speech Speed</label>
            <select id="vsSpeed" style="width:100%;padding:8px;border-radius:6px;background:var(--bg-secondary,#1e2533);color:var(--text-primary,#fff);border:1px solid var(--border-color,#333);">
              <option value="0.75">0.75x (Slow)</option><option value="1.0">1.0x (Normal)</option><option value="1.25">1.25x (Fast)</option><option value="1.5">1.5x (Very Fast)</option>
            </select></div>
        </div>
        <div class="modal-actions"><button id="saveVoiceSettingsBtn" class="btn btn-primary">Save Settings</button><button id="cancelVoiceSettingsBtn" class="btn btn-secondary">Cancel</button></div>
      </div>`;

    document.body.appendChild(modal);
    syncVoiceSettingsUI();

    document.getElementById('closeVoiceSettingsBtn').addEventListener('click', () => modal.classList.remove('show'));
    document.getElementById('cancelVoiceSettingsBtn').addEventListener('click', () => modal.classList.remove('show'));
    document.getElementById('saveVoiceSettingsBtn').addEventListener('click', () => {
      saveVoiceSettings({
        voiceInputEnabled: document.getElementById('vsSpeechInput').checked,
        autoReadAnswers: document.getElementById('vsAutoRead').checked,
        language: document.getElementById('vsLanguage').value,
        speed: parseFloat(document.getElementById('vsSpeed').value)
      });
      modal.classList.remove('show');
      if (recognition) recognition.lang = voiceSettings.language;
      updateMicButtonVisibility();
    });

    requestAnimationFrame(() => modal.classList.add('show'));
  }

  function syncVoiceSettingsUI() {
    const map = { vsSpeechInput: 'voiceInputEnabled', vsAutoRead: 'autoReadAnswers' };
    Object.entries(map).forEach(([id, key]) => { const el = document.getElementById(id); if (el) el.checked = voiceSettings[key]; });
    const vsLang = document.getElementById('vsLanguage'); if (vsLang) vsLang.value = voiceSettings.language;
    const vsSpd = document.getElementById('vsSpeed'); if (vsSpd) vsSpd.value = String(voiceSettings.speed);
  }

  function updateMicButtonVisibility() {
    const micBtn = document.getElementById('micBtn');
    if (!micBtn) return;
    micBtn.style.display = (!isSTTSupported || !voiceSettings.voiceInputEnabled) ? 'none' : 'inline-flex';
  }

  function attachSpeakerBtn(messageBubble, answerText) {
    if (!isTTSSupported) return;
    const speakBtn = document.createElement('button');
    speakBtn.className = 'speak-btn';
    speakBtn.innerHTML = '🔊';
    speakBtn.title = 'Read answer aloud';
    speakBtn.setAttribute('aria-label', 'Read answer aloud');
    speakBtn.style.cssText = 'background:none;border:none;cursor:pointer;font-size:1rem;padding:4px 8px;border-radius:6px;opacity:0.7;transition:opacity 0.2s;min-width:44px;min-height:44px;display:inline-flex;align-items:center;justify-content:center;';
    speakBtn.addEventListener('mouseover', () => speakBtn.style.opacity = '1');
    speakBtn.addEventListener('mouseout', () => speakBtn.style.opacity = '0.7');
    speakBtn.addEventListener('click', () => {
      if (window.speechSynthesis && window.speechSynthesis.speaking) {
        const wasCurrent = (currentSpeakBtn === speakBtn);
        stopSpeaking();
        if (wasCurrent) return;
      }
      speakAnswer(answerText, speakBtn);
    });
    const sourceBadge = messageBubble.querySelector('.source-badge-box');
    if (sourceBadge) sourceBadge.parentNode.insertBefore(speakBtn, sourceBadge.nextSibling);
    else messageBubble.appendChild(speakBtn);
    if (voiceSettings.autoReadAnswers) speakAnswer(answerText, speakBtn);
  }

  window.addEventListener('beforeunload', stopSpeaking);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopSpeaking(); });

  window.VoiceModule = {
    init: function () { if (isSTTSupported) initSpeechRecognition(); updateMicButtonVisibility(); },
    startListening, stopListening, stopSpeaking, speakAnswer,
    attachSpeakerBtn, openVoiceSettings: renderVoiceSettingsModal,
    getSettings: () => ({ ...voiceSettings }), isListening: () => isListening,
    isSTTSupported, isTTSSupported
  };
})();
