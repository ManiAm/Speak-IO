let ttsModels = {};
let selectedTtsEngine = "coqui";
let currentModelName = "";

function showTtsEngine(engine) {
  selectedTtsEngine = engine;

  document.querySelectorAll(".tts-engine-tab").forEach(tab => tab.style.display = "none");
  document.querySelectorAll(".tts-tab-button").forEach(btn => btn.classList.remove("active"));

  document.getElementById(`${engine}-tab`).style.display = "block";
  document.querySelector(`.tts-tab-button[onclick="showTtsEngine('${engine}')"]`).classList.add("active");
}

async function fetchTtsModels() {
  try {
    const res = await fetch("http://localhost:5500/api/tts/models");
    const data = await res.json();
    ttsModels = data.models;

    initCoquiDropdowns();
    initPiperDropdowns();
  } catch (e) {
    console.error("Failed to fetch TTS models:", e);
  }
}

function initCoquiDropdowns() {
  const modelTypes = Object.keys(ttsModels.coqui || {}).sort();
  const modelTypeSelect = document.getElementById("coqui-model-type");
  modelTypeSelect.innerHTML = "";

  modelTypes.forEach(type => {
    const opt = document.createElement("option");
    opt.value = type;
    opt.textContent = type;
    modelTypeSelect.appendChild(opt);
  });

  if (modelTypes.includes("tts_model")) {
    modelTypeSelect.value = "tts_model";
  }

  modelTypeSelect.onchange = updateCoquiLanguages;
  updateCoquiLanguages();
}

function updateCoquiLanguages() {
  const type = document.getElementById("coqui-model-type").value;
  const langs = Object.keys(ttsModels.coqui[type] || {}).sort();
  const langSelect = document.getElementById("coqui-language");
  langSelect.innerHTML = "";

  langs.forEach(lang => {
    const opt = document.createElement("option");
    opt.value = lang;
    opt.textContent = lang;
    langSelect.appendChild(opt);
  });

  if (langs.includes("en")) {
    langSelect.value = "en";
  }

  langSelect.onchange = updateCoquiModels;
  updateCoquiModels();
}

function updateCoquiModels() {
  const type = document.getElementById("coqui-model-type").value;
  const lang = document.getElementById("coqui-language").value;
  const models = (ttsModels.coqui[type][lang] || []).slice().sort();

  const modelSelect = document.getElementById("coqui-model-name");
  modelSelect.innerHTML = "";

  models.forEach(model => {
    const opt = document.createElement("option");
    opt.value = model;
    opt.textContent = model;
    modelSelect.appendChild(opt);
  });
}

function initPiperDropdowns() {
  const langs = Object.keys(ttsModels.piper || {}).sort();
  const langSelect = document.getElementById("piper-language");
  langSelect.innerHTML = "";

  langs.forEach(lang => {
    const opt = document.createElement("option");
    opt.value = lang;
    opt.textContent = lang;
    langSelect.appendChild(opt);
  });

  if (langs.includes("en_US")) {
    langSelect.value = "en_US";
  }

  langSelect.onchange = updatePiperVoices;
  updatePiperVoices();
}

function updatePiperVoices() {
  const lang = document.getElementById("piper-language").value;
  const voices = Object.keys(ttsModels.piper[lang] || {}).sort();
  const voiceSelect = document.getElementById("piper-voice");
  voiceSelect.innerHTML = "";

  voices.forEach(voice => {
    const opt = document.createElement("option");
    opt.value = voice;
    opt.textContent = voice;
    voiceSelect.appendChild(opt);
  });

  if (voices.includes("amy")) {
    voiceSelect.value = "amy";
  }

  voiceSelect.onchange = updatePiperQualities;
  updatePiperQualities();
}

function updatePiperQualities() {
  const lang = document.getElementById("piper-language").value;
  const voice = document.getElementById("piper-voice").value;
  const qualities = Object.keys(ttsModels.piper[lang][voice] || {});
  const qualitySelect = document.getElementById("piper-quality");
  qualitySelect.innerHTML = "";

  qualities.forEach(q => {
    const opt = document.createElement("option");
    opt.value = q;
    opt.textContent = q;
    qualitySelect.appendChild(opt);
  });

  if (qualities.includes("medium")) {
    qualitySelect.value = "medium";
  }

  qualitySelect.onchange = updatePiperModelNames;
  updatePiperModelNames();
}

function updatePiperModelNames() {
  const lang = document.getElementById("piper-language").value;
  const voice = document.getElementById("piper-voice").value;
  const quality = document.getElementById("piper-quality").value;
  const models = (ttsModels.piper[lang][voice][quality] || []).slice().sort();

  const modelSelect = document.getElementById("piper-model-name");
  modelSelect.innerHTML = "";

  models.forEach(model => {
    const opt = document.createElement("option");
    opt.value = model;
    opt.textContent = model;
    modelSelect.appendChild(opt);
  });
}

async function loadTtsModel() {
  let modelName;

  if (selectedTtsEngine === "coqui") {
    modelName = document.getElementById("coqui-model-name").value;
  } else {
    modelName = document.getElementById("piper-model-name").value;
  }

  if (!modelName) return alert("Select a model first.");

  const params = new URLSearchParams({ engine: selectedTtsEngine, model_name: modelName });

  try {
    const res = await fetch(`http://localhost:5500/api/tts/models/load?${params.toString()}`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) {
      alert(`❌ ${data.detail}`);
      return;
    }

    currentModelName = modelName;
    alert(`✅ ${data.message}`);
  } catch (err) {
    console.error("Load model failed:", err);
    alert("❌ Failed to load model");
  }
}

async function speak() {
  const text = document.getElementById("tts-text").value.trim();
  if (!text || !currentModelName) {
    alert("Please load a model and enter text.");
    return;
  }

  try {
    const params = new URLSearchParams({
      engine: selectedTtsEngine,
      model_name: currentModelName
    });

    const res = await fetch(`http://localhost:5500/api/tts/synthesize?${params.toString()}`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: text
    });

    if (!res.ok) {
      const data = await res.json();
      alert("Error: " + data.detail);
      return;
    }

    const audioBlob = await res.blob();
    const audioURL = URL.createObjectURL(audioBlob);
    const audioElement = document.getElementById("tts-audio");

    audioElement.src = audioURL;
    audioElement.style.display = "block";
    audioElement.play();
  } catch (e) {
    console.error("TTS error:", e);
    alert("TTS failed.");
  }
}

function updateTtsExample() {
  const selected = document.getElementById("tts-example-select").value;
  const textarea = document.getElementById("tts-text");

  const examples = {
    en: `Hello, and welcome to the future of speech synthesis! Today is Tuesday, June 18th, 2025, and the temperature outside is a pleasant 72 degrees Fahrenheit. In a world full of possibilities, artificial intelligence continues to reshape how we communicate, learn, and explore. Can you believe that just a few years ago, real-time voice generation like this was considered science fiction? Now, whether you're narrating a documentary, reading a bedtime story, or delivering emergency instructions, the clarity and naturalness of your voice really matter. So let's pause, take a breath, and appreciate just how far technology has come. Shall we?`,

    zh: `你好，欢迎来到语音合成的未来！今天是2025年6月18日，星期二，外面的温度是22摄氏度。在充满可能性的世界里，人工智能正在不断改变我们沟通、学习和探索的方式。你能相信就在几年前，像这样实时生成语音还被认为是科幻吗？如今，无论是讲解纪录片、讲睡前故事，还是发布紧急通知，语音的清晰度和自然度都变得至关重要。那么，让我们停下来，深呼吸一下，感受科技发展的奇迹吧。`,

    hi: `नमस्ते! भाषण संश्लेषण के भविष्य में आपका स्वागत है। आज मंगलवार, 18 जून 2025 है, और बाहर का तापमान लगभग 22 डिग्री सेल्सियस है। संभावनाओं से भरी इस दुनिया में, कृत्रिम बुद्धिमत्ता हमारे संवाद, सीखने और अन्वेषण के तरीके को लगातार बदल रही है। क्या आप विश्वास कर सकते हैं कि कुछ साल पहले तक, इस तरह की वास्तविक समय में आवाज़ बनाना विज्ञान-कथा जैसा लगता था? अब, चाहे आप कोई डॉक्यूमेंट्री सुना रहे हों, बच्चों को कहानी सुना रहे हों या आपातकालीन निर्देश दे रहे हों — आवाज़ की स्पष्टता और स्वाभाविकता बेहद महत्वपूर्ण है। तो चलिए एक पल रुकें, गहरी सांस लें और सोचें कि हमने तकनीक में कितनी तरक्की की है।`,

    es: `¡Hola y bienvenido al futuro de la síntesis de voz! Hoy es martes 18 de junio de 2025 y la temperatura exterior es de unos agradables 22 grados centígrados. En un mundo lleno de posibilidades, la inteligencia artificial sigue transformando cómo nos comunicamos, aprendemos y exploramos. ¿Puedes creer que hace unos años generar voz en tiempo real era ciencia ficción? Ahora, ya sea que estés narrando un documental, leyendo un cuento para dormir o dando instrucciones de emergencia, la claridad y naturalidad de tu voz importan mucho. Así que hagamos una pausa, respiremos profundamente y apreciemos cuánto ha avanzado la tecnología.`,

    fr: `Bonjour et bienvenue dans le futur de la synthèse vocale ! Nous sommes le mardi 18 juin 2025 et il fait 22 degrés à l'extérieur. Dans un monde rempli de possibilités, l'intelligence artificielle continue de transformer notre manière de communiquer, d'apprendre et d'explorer. Pouvez-vous croire qu'il y a quelques années à peine, la génération de voix en temps réel relevait de la science-fiction ? Aujourd'hui, que vous racontiez un documentaire, lisiez une histoire du soir ou donniez des instructions d'urgence, la clarté et la naturalité de la voix sont essentielles. Prenons donc un instant pour respirer et apprécier les progrès technologiques.`,

    ar: `مرحبًا بكم في مستقبل توليد الصوت! اليوم هو الثلاثاء، 18 يونيو 2025، ودرجة الحرارة في الخارج تبلغ حوالي 22 درجة مئوية. في عالم مليء بالإمكانيات، يواصل الذكاء الاصطناعي تغيير الطريقة التي نتواصل ونتعلم ونستكشف بها. هل تصدق أنه قبل بضع سنوات فقط، كان إنتاج الصوت في الوقت الحقيقي يبدو كخيال علمي؟ الآن، سواء كنت تروي وثائقيًا، أو تقرأ قصة قبل النوم، أو تقدم تعليمات طارئة، فإن وضوح الصوت وطبيعته أمران مهمان للغاية. فلنأخذ لحظة لنستريح ونتأمل في مدى تطور التكنولوجيا.`,

    bn: `হ্যালো, এবং কৃত্রিম কণ্ঠস্বর প্রযুক্তির ভবিষ্যতে আপনাকে স্বাগতম! আজ মঙ্গলবার, ১৮ জুন ২০২৫, এবং বাইরে তাপমাত্রা প্রায় ২২ ডিগ্রি সেলসিয়াস। সম্ভাবনায় ভরা এই পৃথিবীতে, কৃত্রিম বুদ্ধিমত্তা আমাদের যোগাযোগ, শেখা এবং অনুসন্ধানের পদ্ধতি পরিবর্তন করছে। আপনি কি বিশ্বাস করতে পারেন, কয়েক বছর আগেও এই ধরনের রিয়েল-টাইম ভয়েস জেনারেশন ছিল শুধুই বিজ্ঞান কল্পকাহিনী? এখন, আপনি যদি একটি ডকুমেন্টারি বর্ণনা করেন, একটি শুয়োর গল্প বলেন অথবা জরুরি নির্দেশ দেন — কণ্ঠের স্বাভাবিকতা এবং স্পষ্টতা অত্যন্ত গুরুত্বপূর্ণ। চলুন এক মুহূর্ত থেমে, একটা শ্বাস নিই, এবং প্রযুক্তির উন্নতিকে কৃতজ্ঞচিত্তে গ্রহণ করি।`,

    ru: `Здравствуйте и добро пожаловать в будущее синтеза речи! Сегодня вторник, 18 июня 2025 года, и на улице около 22 градусов Цельсия. В мире, полном возможностей, искусственный интеллект продолжает менять способы нашего общения, обучения и исследования. Можете ли вы поверить, что всего несколько лет назад генерация речи в реальном времени считалась научной фантастикой? Сейчас, будь то документальный фильм, сказка на ночь или экстренные инструкции — важны чёткость и естественность голоса. Давайте сделаем паузу, глубоко вдохнём и осознаем, как далеко продвинулись технологии.`,

    pt: `Olá e bem-vindo ao futuro da síntese de voz! Hoje é terça-feira, 18 de junho de 2025, e a temperatura lá fora está agradáveis 22 graus Celsius. Em um mundo cheio de possibilidades, a inteligência artificial continua a transformar a forma como nos comunicamos, aprendemos e exploramos. Você consegue acreditar que há apenas alguns anos, a geração de voz em tempo real era considerada ficção científica? Agora, seja narrando um documentário, lendo uma história para dormir ou dando instruções de emergência, a clareza e a naturalidade da voz são fundamentais. Então vamos parar por um momento, respirar fundo e apreciar o quão longe a tecnologia chegou.`,

    de: `Hallo und willkommen in der Zukunft der Sprachsynthese! Heute ist Dienstag, der 18. Juni 2025, und draußen sind es angenehme 22 Grad Celsius. In einer Welt voller Möglichkeiten verändert künstliche Intelligenz weiterhin, wie wir kommunizieren, lernen und entdecken. Können Sie glauben, dass die Erzeugung von Sprache in Echtzeit noch vor wenigen Jahren als Science-Fiction galt? Ob Sie nun einen Dokumentarfilm erzählen, eine Gutenachtgeschichte vorlesen oder Notfallanweisungen geben — die Klarheit und Natürlichkeit der Stimme ist entscheidend. Nehmen wir uns also einen Moment Zeit, atmen tief durch und schätzen, wie weit die Technologie gekommen ist.`,

    ja: `こんにちは、音声合成の未来へようこそ！今日は2025年6月18日火曜日で、外の気温は約22度です。可能性に満ちた世界で、人工知能は私たちのコミュニケーション、学習、探求の方法を変え続けています。ほんの数年前まで、リアルタイムでの音声生成はSFのように思われていました。今では、ドキュメンタリーのナレーションでも、子供への読み聞かせでも、緊急時の案内でも、声の明瞭さと自然さが非常に重要です。さあ、一息ついて、ここまで進化したテクノロジーに感謝しましょう。`,

    fa: `سلام! به آینده‌ی تولید صدای مصنوعی خوش آمدید! امروز سه‌شنبه، ۲۸ خرداد ۱۴۰۴ است و دمای هوا حدود ۲۲ درجه‌ی سانتی‌گراد است. در جهانی پر از امکانات، هوش مصنوعی همچنان در حال تغییر شیوه‌ی ارتباط، یادگیری و اکتشاف ماست. باور می‌کنید که فقط چند سال پیش، تولید آنیِ صدا چیزی شبیه به داستان‌های علمی-تخیلی بود؟ حالا چه در حال روایت یک مستند باشید، چه خواندن قصه‌ی شب برای کودکی، یا دادن دستورهای اضطراری، طبیعی و واضح بودن صدا بسیار اهمیت دارد. پس بیایید کمی مکث کنیم، نفسی بکشیم، و قدردانِ پیشرفت‌های تکنولوژی باشیم — موافقید؟`,

    tr: `Merhaba, konuşma sentezinin geleceğine hoş geldiniz! Bugün 18 Haziran 2025 Salı ve dışarısı 22 derece. Olasılıklarla dolu bir dünyada, yapay zeka iletişim, öğrenme ve keşif yöntemlerimizi dönüştürmeye devam ediyor. Sadece birkaç yıl önce, gerçek zamanlı ses üretimi bilim kurgu gibi görünüyordu. Şimdi ister bir belgesel anlatıyor olun, ister bir masal okuyun ya da acil durum talimatları verin — sesinizin netliği ve doğallığı büyük önem taşıyor. Hadi bir nefes alalım ve teknolojinin ne kadar ilerlediğini takdir edelim.`,

    ko: `안녕하세요, 음성 합성의 미래에 오신 것을 환영합니다! 오늘은 2025년 6월 18일 화요일이고, 바깥 기온은 약 22도입니다. 무한한 가능성의 세상에서 인공지능은 우리가 소통하고 배우고 탐험하는 방식을 계속해서 바꾸고 있습니다. 불과 몇 년 전만 해도 실시간 음성 생성은 공상 과학처럼 느껴졌습니다. 이제 다큐멘터리를 설명하든, 아이에게 동화를 읽어주든, 긴급 지시를 전달하든, 목소리의 명확성과 자연스러움이 매우 중요합니다. 잠시 멈춰서 숨을 깊이 들이쉬고, 기술이 얼마나 발전했는지 되새겨봅시다.`
  };

  textarea.value = examples[selected] || "";
  textarea.dir = (["fa", "ar", "he", "ur"].includes(selected)) ? "rtl" : "ltr";
}

window.onload = () => {
  fetchEnginesAndModels();
  fetchTtsModels();
};

