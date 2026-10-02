// Sample error presets
const SAMPLES = {
  react: `TypeError: Cannot read properties of undefined (reading 'avatar')
    at UserProfileCard (UserProfile.tsx:42:25)
    at renderWithHooks (react-dom.development.js:15486:18)
    at mountIndeterminateComponent (react-dom.development.js:20103:13)
    at beginWork (react-dom.development.js:21626:16)`,
  python: `Traceback (most recent call last):
  File "~/workspace/app/services/data_cleaner.py", line 64, in normalize_dataset
    target_metric = records[10]
IndexError: list index out of range`,
  async: `UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch().
    at fetchUserPreferences (authMiddleware.js:28:11)
    at processTicksAndRejections (internal/process/task_queues.js:95:5)`,
  docker: `docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: open /var/log/app.log: permission denied: unknown.`
};

// DOM Elements
const errorInput = document.getElementById('errorInput');
const codeContextInput = document.getElementById('codeContextInput');
const codeContextWrapper = document.getElementById('codeContextWrapper');
const toggleCodeCtxBtn = document.getElementById('toggleCodeCtxBtn');
const voiceCheckbox = document.getElementById('voiceCheckbox');
const whisperBtn = document.getElementById('whisperBtn');

const idleState = document.getElementById('idleState');
const loadingState = document.getElementById('loadingState');
const diagnosisContainer = document.getElementById('diagnosisContainer');

const playPauseBtn = document.getElementById('playPauseBtn');
const playIcon = document.getElementById('playIcon');
const audioStatus = document.getElementById('audioStatus');
const simplerBtn = document.getElementById('simplerBtn');
const companionAudio = document.getElementById('companionAudio');

const empathyText = document.getElementById('empathyText');
const causeText = document.getElementById('causeText');
const actionTitle = document.getElementById('actionTitle');
const actionLocation = document.getElementById('actionLocation');
const codeSnippet = document.getElementById('codeSnippet');
const actionExplanation = document.getElementById('actionExplanation');
const copyCodeBtn = document.getElementById('copyCodeBtn');
const copyBtnText = document.getElementById('copyBtnText');
const tipText = document.getElementById('tipText');

const focusModeBtn = document.getElementById('focusModeBtn');
const focusBtnText = document.getElementById('focusBtnText');
const telemetryProvider = document.getElementById('telemetryProvider');
const telemetryLatency = document.getElementById('telemetryLatency');
const waveformCanvas = document.getElementById('waveformCanvas');
const ctx = waveformCanvas.getContext('2d');

let currentSpokenScript = "";
let isPlaying = false;
let animationFrameId = null;

// Initialize health & status badges
async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      const data = await res.json();
      const modelBadge = document.getElementById('modelBadge');
      const voiceBadge = document.getElementById('voiceBadge');
      if (modelBadge && data.gemma_model) {
        modelBadge.querySelector('.status-label').textContent = `Gemma 2 (${data.integrations.gemma})`;
      }
      if (voiceBadge) {
        voiceBadge.querySelector('.status-label').textContent = 
          data.integrations.elevenlabs === 'configured' ? 'ElevenLabs' : 'Web Speech';
      }
    }
  } catch (e) {
    console.log("Standalone mode active");
  }
}
checkHealth();

// Preset Buttons handler
document.querySelectorAll('.preset-btn, .sample-chip').forEach(btn => {
  btn.addEventListener('click', () => {
    const key = btn.dataset.sample;
    if (SAMPLES[key]) {
      errorInput.value = SAMPLES[key];
      errorInput.focus();
    }
  });
});

// Code Context Toggle
if (toggleCodeCtxBtn && codeContextWrapper) {
  toggleCodeCtxBtn.addEventListener('click', () => {
    codeContextWrapper.classList.toggle('hidden');
    const isHidden = codeContextWrapper.classList.contains('hidden');
    toggleCodeCtxBtn.querySelector('span').textContent = isHidden 
      ? 'Add code snippet context (optional)' 
      : 'Hide code snippet context';
  });
}

// Focus Mode Toggle
if (focusModeBtn) {
  focusModeBtn.addEventListener('click', () => {
    document.body.classList.toggle('deep-focus-active');
    const isFocus = document.body.classList.contains('deep-focus-active');
    focusModeBtn.classList.toggle('focus-active', isFocus);
    focusBtnText.textContent = isFocus ? 'Exit Focus' : 'Focus Mode';
  });
}

// Copy Code Button
if (copyCodeBtn) {
  copyCodeBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(codeSnippet.innerText).then(() => {
      copyBtnText.textContent = "Copied!";
      copyCodeBtn.style.color = "#10b981";
      setTimeout(() => {
        copyBtnText.textContent = "Copy Fix";
        copyCodeBtn.style.color = "";
      }, 2000);
    });
  });
}

// Sharp Canvas Audio Waveform
function drawWaveform() {
  animationFrameId = requestAnimationFrame(drawWaveform);
  ctx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);

  const width = waveformCanvas.width;
  const height = waveformCanvas.height;
  const centerY = height / 2;

  if (!isPlaying) {
    // Sharp subtle baseline
    ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
    return;
  }

  // Active sharp frequency bars
  const numBars = 32;
  const barWidth = 3;
  const gap = (width - numBars * barWidth) / (numBars - 1);
  const time = Date.now() * 0.009;

  for (let i = 0; i < numBars; i++) {
    const barHeight = Math.abs(Math.sin(time + i * 0.35)) * 22 + 4;
    const x = i * (barWidth + gap);
    const y = centerY - barHeight / 2;

    ctx.fillStyle = i % 2 === 0 ? "#38bdf8" : "#10b981";
    ctx.fillRect(Math.floor(x), Math.floor(y), barWidth, Math.floor(barHeight));
  }
}
drawWaveform();

// Audio playback management
function playAudio(audioData, directText) {
  stopAudio();

  if (audioData && audioData.audio_b64) {
    companionAudio.src = `data:${audioData.mime_type};base64,${audioData.audio_b64}`;
    audioStatus.textContent = "ElevenLabs Stream";
    companionAudio.play().then(() => {
      isPlaying = true;
      playIcon.textContent = "⏸";
    }).catch(err => {
      console.warn("Autoplay fallback to speech synthesis:", err);
      speakWithBrowserTTS(directText);
    });
  } else {
    audioStatus.textContent = "Web Speech Engine";
    speakWithBrowserTTS(directText);
  }
}

function speakWithBrowserTTS(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 1.0;
  
  utterance.onstart = () => {
    isPlaying = true;
    playIcon.textContent = "⏸";
  };
  utterance.onend = () => {
    stopAudio();
  };
  utterance.onerror = () => {
    stopAudio();
  };
  
  window.speechSynthesis.speak(utterance);
}

function stopAudio() {
  isPlaying = false;
  playIcon.textContent = "▶";
  companionAudio.pause();
  companionAudio.currentTime = 0;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

playPauseBtn.addEventListener('click', () => {
  if (isPlaying) {
    stopAudio();
  } else if (currentSpokenScript) {
    playAudio(null, currentSpokenScript);
  }
});

companionAudio.addEventListener('ended', () => {
  stopAudio();
});

// Submit / Whisper Button
whisperBtn.addEventListener('click', async () => {
  const errorText = errorInput.value.trim();
  if (!errorText) {
    errorInput.placeholder = "Please paste an error log or click a preset button above first.";
    errorInput.focus();
    return;
  }

  idleState.classList.add('hidden');
  diagnosisContainer.classList.add('hidden');
  loadingState.classList.remove('hidden');
  stopAudio();

  const startTime = performance.now();

  try {
    const res = await fetch('/api/debug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error_log: errorText,
        code_context: codeContextInput ? codeContextInput.value.trim() : null,
        with_voice: voiceCheckbox.checked
      })
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    const d = data.diagnosis;

    empathyText.textContent = d.empathy_note || "Take a breath. You've got this.";
    causeText.textContent = d.plain_english_cause || "Here is what happened.";
    
    const action = d.single_next_action || {};
    actionTitle.textContent = action.title || "Next Step";
    actionLocation.textContent = action.file_or_location ? `Location: ${action.file_or_location}` : "";
    codeSnippet.textContent = action.suggested_code || "// No code snippet needed";
    actionExplanation.textContent = action.explanation || "";

    tipText.textContent = d.quick_tip || "Check one line at a time.";
    currentSpokenScript = d.spoken_script || "";

    telemetryProvider.textContent = `Engine: ${d.provider_used || "Gemma 2"}`;
    telemetryLatency.textContent = `Latency: ~${elapsed}ms`;

    loadingState.classList.add('hidden');
    diagnosisContainer.classList.remove('hidden');

    if (voiceCheckbox.checked && currentSpokenScript) {
      playAudio(data.voice, currentSpokenScript);
    }

  } catch (err) {
    console.error(err);
    loadingState.classList.add('hidden');
    idleState.classList.remove('hidden');
    alert("Could not reach BugWhisperer server. Ensure backend is running!");
  }
});

// Explain Simpler Button
simplerBtn.addEventListener('click', () => {
  if (!currentSpokenScript) return;
  const simplerSpeech = `Hey, let's keep it simple. Open your file, check the single line highlighted in the blue action box, add the safe check, and run it again.`;
  currentSpokenScript = simplerSpeech;
  playAudio(null, simplerSpeech);
});
