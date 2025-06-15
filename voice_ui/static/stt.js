
let socket, recorder, chunks = [];
let selectedEngine = '';
let selectedModel = '';

async function fetchEnginesAndModels() {
  try {
    const response = await fetch("http://localhost:5000/api/stt/models", { method: "GET" });
    const data = await response.json();
    const engines = Object.keys(data.models);

    const engineSelect = document.getElementById("engine-select");
    const modelSelect = document.getElementById("model-select");

    window.modelsPerEngine = data.models;

    engineSelect.innerHTML = '';
    engines.forEach(engine => {
      const opt = document.createElement("option");
      opt.value = engine;
      opt.textContent = engine;
      engineSelect.appendChild(opt);
    });

    const defaultEngine = "openai_whisper";
    const defaultModel = "small.en";

    if (engines.includes(defaultEngine)) {
      engineSelect.value = defaultEngine;
      selectedEngine = defaultEngine;

      const models = data.models[defaultEngine];
      modelSelect.innerHTML = '<option value="">-- Select Model --</option>';
      models.forEach(model => {
        const opt = document.createElement("option");
        opt.value = model;
        opt.textContent = model;
        modelSelect.appendChild(opt);
      });

      if (models.includes(defaultModel)) {
        modelSelect.value = defaultModel;
        selectedModel = defaultModel;
      }
    }
  } catch (e) {
    console.error("Failed to load engines:", e);
  }
}

function updateModelsDropdown() {
  const engine = document.getElementById("engine-select").value;
  selectedEngine = engine;

  const modelSelect = document.getElementById("model-select");
  modelSelect.innerHTML = `<option value="">-- Select Model --</option>`;

  if (window.modelsPerEngine && window.modelsPerEngine[engine]) {
    window.modelsPerEngine[engine].forEach(model => {
      const opt = document.createElement("option");
      opt.value = model;
      opt.textContent = model;
      modelSelect.appendChild(opt);
    });
  }
}

async function loadModel() {
  selectedModel = document.getElementById("model-select").value;
  if (!selectedEngine || !selectedModel) {
    log("⚠️ Please select both engine and model.");
    return;
  }

  const spinner = document.getElementById("spinner");
  spinner.style.display = "block";

  try {
    const params = new URLSearchParams({ engine: selectedEngine, model_name: selectedModel });
    const res = await fetch(`http://localhost:5000/api/stt/models/load?${params.toString()}`, { method: "POST" });
    const data = await res.json();
    if (res.ok) {
      log(`✅ ${data.message}`);
    } else {
      log(`❌ Failed to load model: ${data.detail}`);
    }
  } catch (e) {
    log("❌ Error loading model.");
    console.error(e);
  } finally {
    spinner.style.display = "none";
  }
}

function log(text) {
  const logElem = document.getElementById("log");
  const line = document.createElement("div");
  line.textContent = text;
  logElem.appendChild(line);
}

function logBanner(text) {
  const logElem = document.getElementById("log");
  const banner = document.createElement("div");
  banner.className = "banner";
  banner.textContent = text;
  logElem.appendChild(banner);
}

async function start() {
  if (!selectedEngine || !selectedModel) {
    log("⚠️ Select engine and model before starting.");
    return;
  }

  try {
    log("🔐 Requesting microphone permission...");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    log("✅ Microphone access granted.");

    const wsUrl = `ws://localhost:5000/api/stt/transcribe/stream?engine=${encodeURIComponent(selectedEngine)}&model_name=${encodeURIComponent(selectedModel)}`;
    socket = new WebSocket(wsUrl);
    chunks = [];

    socket.onopen = () => {
      log("✅ WebSocket connection established.");
      recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = async () => {
        log("🛑 Stopped recording. Finalizing audio...");
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const buffer = await blob.arrayBuffer();

        log(`📤 Ready to send ${buffer.byteLength} bytes`);

        if (socket.readyState === WebSocket.OPEN) {
          socket.send(buffer);
          log("📤 Sent buffer to server");

          socket.onmessage = (e) => {
            logBanner("📄 Transcription received:");
            log(e.data);
            socket.close();
          };
        } else {
          log("❌ WebSocket not open");
        }
      };

      recorder.start();
      log("🎙️ Recording started...");
    };

    socket.onerror = (e) => {
      log("❌ WebSocket error.");
      console.error("WebSocket error:", e);
    };

    socket.onclose = () => {
      log("🔌 WebSocket connection closed.");
    };
  } catch (err) {
    log("❌ Error accessing microphone.");
    console.error(err);
  }
}

function stop() {
  if (recorder && recorder.state === "recording") {
    log("🛑 Stopping recording...");
    recorder.stop();
  } else {
    log("⚠️ Recorder not running.");
  }
}

window.onload = () => {
  fetchEnginesAndModels();
  fetchTtsModels();
};
