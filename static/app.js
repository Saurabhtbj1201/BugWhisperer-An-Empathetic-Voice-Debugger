// Sample error presets
const SAMPLES = {
  react: `TypeError: Cannot read properties of undefined (reading 'avatar')
    at UserProfileCard (UserProfile.tsx:42:25)
    at renderWithHooks (react-dom.development.js:15486:18)
    at mountIndeterminateComponent (react-dom.development.js:20103:13)
    at beginWork (react-dom.development.js:21626:16)`,
  python: `Traceback (most recent call last):
  File "/workspace/app/services/data_cleaner.py", line 64, in normalize_dataset
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
let audioContext = null;
let analyser = null;
let sourceNode = null;
let animationFrameId = null;

// Initialize health & status
async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      const data = await res.json();
      const modelBadge = document.getElementById('modelBadge');
      const voiceBadge = document.getElementById('voiceBadge');
      if (modelBadge && data.gemma_model) {
        modelBadge.querySelector('span:last-child').textContent = `Gemma 2 (${data.integrations.gemma})`;
      }
      if (voiceBadge) {
        voiceBadge.querySelector('span:last-child').textContent = 
          data.integrations.elevenlabs === 'configured' ? 'ElevenLabs Active' : 'Web Speech Fallback';
      }
    }
  } catch (e) {
    console.log("Local standalone mode");
  }
}
checkHealth();

// Sample Chips handler
document.querySelectorAll('.sample-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const key = chip.dataset.sample;
    if (SAMPLES[key]) {
      errorInput.value = SAMPLES[key];
      errorInput.focus();
    }
  });
});

// Code Context Toggle
toggleCodeCtxBtn.addEventListener('click', () => {
  codeContextWrapper.classList.toggle('hidden');
  toggleCodeCtxBtn.textContent = codeContextWrapper.classList.contains('hidden') 
    ? '+ Add snippet context (optional)' 
    : '- Hide snippet context';
});

// Focus Mode Toggle
focusModeBtn.addEventListener('click', () => {
  document.body.classList.toggle('deep-focus-active');
  const isFocus = document.body.classList.contains('deep-focus-active');
  focusModeBtn.classList.toggle('focus-active', isFocus);
  focusBtnText.textContent = isFocus ? 'Exit Focus Mode' : 'Focus Mode';
});

// Copy Code Button
copyCodeBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(codeSnippet.innerText).then(() => {
    copyBtnText.textContent = "Copied! ✨";
    copyCodeBtn.style.color = "#10b981";
    setTimeout(() => {
      copyBtnText.textContent = "Copy Fix";
      copyCodeBtn.style.color = "";
    }, 2000);
  });
});

// Waveform visualizer loop
function drawWaveform() {
  animationFrameId = requestAnimationFrame(drawWaveform);
  ctx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);

  const width = waveformCanvas.width;
  const height = waveformCanvas.height;
  const centerY = height / 2;

  if (!isPlaying) {
    // Idle flat gentle wave
    ctx.beginPath();
    ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
    ctx.lineWidth = 2;
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
    return;
  }

  // Active pulsing bars
  const numBars = 24;
  const barWidth = width / numBars - 2;
  const time = Date.now() * 0.008;

  for (let i = 0; i < numBars; i++) {
    const barHeight = Math.sin(time + i * 0.5) * 12 + 14;
    const x = i * (barWidth + 2);
    const y = centerY - barHeight / 2;
    
    const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
    grad.addColorStop(0, '#38bdf8');
    grad.addColorStop(1, '#10b981');
    
    ctx.fillStyle = grad;
    ctx.fillRect(x, y, barWidth, barHeight);
  }
}
drawWaveform();

// Audio playback management
function playAudio(audioData, directText) {
  stopAudio();

  if (audioData && audioData.audio_b64) {
    companionAudio.src = `data:${audioData.mime_type};base64,${audioData.audio_b64}`;
    audioStatus.textContent = "ElevenLabs Empathetic Stream";
    companionAudio.play().then(() => {
      isPlaying = true;
      playIcon.textContent = "⏸";
    }).catch(err => {
      console.warn("Autoplay prevented, fallback to speech synthesis:", err);
      speakWithBrowserTTS(directText);
    });
  } else {
    // Web Speech API fallback
    audioStatus.textContent = "Browser Web Speech Engine";
    speakWithBrowserTTS(directText);
  }
}

function speakWithBrowserTTS(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // Slightly slower for calming effect
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
    errorInput.placeholder = "⚠️ Please paste an error or click one of the quick test chips above first!";
    errorInput.focus();
    return;
  }

  // UI state transitions
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
        code_context: codeContextInput.value.trim() || null,
        with_voice: voiceCheckbox.checked
      })
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    const d = data.diagnosis;

    // Populate UI
    empathyText.textContent = d.empathy_note || "Take a breath. You've got this.";
    causeText.textContent = d.plain_english_cause || "Here is what happened.";
    
    const action = d.single_next_action || {};
    actionTitle.textContent = action.title || "Next Step";
    actionLocation.textContent = action.file_or_location ? `📂 Location: ${action.file_or_location}` : "";
    codeSnippet.textContent = action.suggested_code || "// No code snippet needed";
    actionExplanation.textContent = action.explanation || "";

    tipText.textContent = d.quick_tip || "Check one line at a time.";
    currentSpokenScript = d.spoken_script || "";

    telemetryProvider.textContent = `Provider: ${d.provider_used || "Gemma 2"}`;
    telemetryLatency.textContent = `Latency: ~${elapsed}ms`;

    // Show result
    loadingState.classList.add('hidden');
    diagnosisContainer.classList.remove('hidden');

    // Trigger audio if requested
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
  const simplerSpeech = `Hey, let's make it super simple. Don't worry about all that technical jargon. Just open your file and check that one line shown in the blue card. Add the safe check, save, and you're good to go.`;
  currentSpokenScript = simplerSpeech;
  playAudio(null, simplerSpeech);
});
