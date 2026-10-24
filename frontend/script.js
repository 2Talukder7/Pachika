// Use same-origin API in production; local static previews (e.g. Live Server :5500)
// should still talk to the local Flask server on :5000. A separately hosted API can
// be configured by defining window.PACHIKA_API_BASE before this script.
const isLocalHost = ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
const API_BASE = (window.PACHIKA_API_BASE || (
  window.location.protocol === "file:" || (isLocalHost && window.location.port !== "5000")
    ? "http://127.0.0.1:5000"
    : window.location.origin
)).replace(/\/$/, "");

// Keep the chat's available height synchronized with mobile browser chrome and
// the on-screen keyboard. visualViewport is supported by current Android browsers.
(function syncChatViewportHeight() {
  const update = () => {
    const height = window.visualViewport?.height || window.innerHeight;
    if (height > 0) {
      document.documentElement.style.setProperty("--pachika-viewport-height", `${Math.round(height)}px`);
    }
  };
  update();
  window.addEventListener("resize", update, { passive: true });
  window.addEventListener("orientationchange", update, { passive: true });
  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", update, { passive: true });
  }
})();

const PLACEHOLDER_IMG = "assets/mortar-illustration-t.png";
const USER_AVATAR = "assets/user-avatar.png";
const PACHIKA_AVATAR = "assets/pachika-avatar.png";
const THUMB_STEPS = [500, 330, 250];
const MIN_TIMER_MINUTES = 5;
const MAX_TIMERS_PER_RECIPE = 3;
const BN_DIGITS = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"];

const $ = (id) => document.getElementById(id);
const on = (el, evt, fn, opts) => {
  if (el) el.addEventListener(evt, fn, opts);
};

const landingScreen = $("landingScreen");
const chatScreen = $("chatScreen");
const weatherScreen = $("weatherScreen");
const navLandingBtn = $("navLandingBtn");
const navChatBtn = $("navChatBtn");
const navWeatherBtn = $("navWeatherBtn");
const startCookingBtn = $("startCookingBtn");
const viewWeatherPicksBtn = $("viewWeatherPicksBtn");
const themeToggleBtn = $("themeToggleBtn");
const themeIcon = $("themeIcon");
const langToggleBtn = $("langToggleBtn");
const langLabel = $("langLabel");
const infoBtn = $("infoBtn");
const toastEl = $("toastNotification");
const chatWindow = $("chatWindow");
const emptyState = $("emptyState");
const chatForm = $("chatForm");
const messageInput = $("messageInput");
const recipeCardTemplate = $("recipeCardTemplate");
const sidebar = $("sidebar");
const menuToggle = $("menuToggle");
const newChatBtn = $("newChatBtn");
const micBtn = $("micBtn");
const sendBtn = $("sendBtn");
const recipeSearchInput = $("recipeSearchInput");
const categoryTabs = $("categoryTabs");
const recipeDirectory = $("recipeDirectory");
const recipeCountLabel = $("recipeCountLabel");
const promptChips = $("promptChips");
const voiceStatusBar = $("voiceStatusBar");
const voiceStatusText = $("voiceStatusText");
const audioPlayer = $("audioPlayer");
const useGeoLocationBtn = $("useGeoLocationBtn");
const cityInput = $("cityInput");
const citySearchBtn = $("citySearchBtn");
const weatherLoading = $("weatherLoading");
const weatherError = $("weatherError");
const weatherContent = $("weatherContent");
const weatherIconLarge = $("weatherIconLarge");
const weatherCityText = $("weatherCityText");
const weatherTempNum = $("weatherTempNum");
const weatherCondText = $("weatherCondText");
const weatherHumidityText = $("weatherHumidityText");
const weatherPrecipText = $("weatherPrecipText");
const weatherReasonText = $("weatherReasonText");
const festiveBannerCard = $("festiveBannerCard");
const festiveTitle = $("festiveTitle");
const festiveDesc = $("festiveDesc");
const weatherRecipesGrid = $("weatherRecipesGrid");

function readStored(key) {
  try {
    return localStorage.getItem(key);
  } catch (e) {
    return null;
  }
}

function writeStored(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (e) {}
}

let currentSessionId = readStored("pachika_session_id") || `sess_${Date.now()}`;
writeStored("pachika_session_id", currentSessionId);
const DEFAULT_SERVINGS = 4;
let globalLang = readStored("pachika_lang") === "en" ? "en" : "bn";
let allRecipes = [];
let allCategories = [];
let activeCategory = "all";
let lastWeatherData = null;
let isWeatherLoaded = false;

const T = {
  themeDark: { bn: "ডার্ক থিম সক্রিয় করা হয়েছে", en: "Dark theme enabled" },
  themeLight: { bn: "লাইট থিম সক্রিয় করা হয়েছে", en: "Light theme enabled" },
  langChosen: { bn: "ভাষা: বাংলা নির্বাচিত", en: "Language: English selected" },
  serverError: {
    bn: "সার্ভারের সাথে সংযোগ করা যায়নি। দয়া করে ব্যাকএন্ড চালু আছে কিনা যাচাই করুন।",
    en: "Could not reach the server. Please check that the backend is running.",
  },
  recipeLoadError: {
    bn: "রেসিপিটি লোড করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।",
    en: "There was a problem loading the recipe. Please try again.",
  },
  recipeLoaded: {
    bn: (d, n) => `এই নিন **${d.dish}** রেসিপি (${num(n)} জনের জন্য)। নিচে বিস্তারিত প্রস্তুতপ্রণালী দেওয়া হলো:`,
    en: (d, n) => `Here is the **${d.dish_en}** recipe (for ${n} servings). The full method is below:`,
  },
  noRecipes: { bn: "কোনো রেসিপি মেলেনি।", en: "No recipes found." },
  geoUnsupported: {
    bn: "আপনার ব্রাউজারে লোকেশন সমর্থন নেই। শহরের নাম লিখুন।",
    en: "Your browser does not support location. Please type a city name.",
  },
  geoAsking: { bn: "📍 লোকেশন অ্যাক্সেস চাওয়া হচ্ছে...", en: "📍 Asking for location access..." },
  geoDenied: {
    bn: "লোকেশন অ্যাক্সেস পাওয়া যায়নি। ব্রাউজারে অনুমতি দিন অথবা শহরের নাম লিখুন।",
    en: "Location access was not granted. Allow it in your browser or type a city name.",
  },
  geoUnavailable: {
    bn: "আপনার অবস্থান নির্ণয় করা যাচ্ছে না। অনুগ্রহ করে শহরের নাম লিখুন।",
    en: "Your position could not be determined. Please type a city name.",
  },
  geoTimeout: {
    bn: "অবস্থান পেতে বেশি সময় লাগছে। আবার চেষ্টা করুন অথবা শহরের নাম লিখুন।",
    en: "Finding your location took too long. Try again or type a city name.",
  },
  geoInsecure: {
    bn: "লোকেশন শুধু https বা localhost-এ কাজ করে। শহরের নাম লিখুন।",
    en: "Location only works on https or localhost. Please type a city name.",
  },
  geoInvalid: {
    bn: "অবস্থানের তথ্য সঠিক নয়। শহরের নাম লিখুন।",
    en: "The location data was not valid. Please type a city name.",
  },
  copied: { bn: "📋 রেসিপি সফলভাবে কপি করা হয়েছে!", en: "📋 Recipe copied successfully!" },
  copyFailed: { bn: "কপি করতে ব্যর্থ হয়েছে।", en: "Copying failed." },
  speaking: { bn: "🔊 পাচিকা কথা বলছে...", en: "🔊 Pachika is speaking..." },
  micUnsupported: {
    bn: "আপনার ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়। Chrome বা Edge ব্রাউজারে ব্যবহার করুন।",
    en: "Voice input is not supported in your browser. Please use Chrome or Edge.",
  },
  listening: { bn: "শুনছি... আপনার রান্নার কথা বলুন!", en: "Listening... tell me what to cook!" },
  heard: { bn: (x) => `পাওয়া গেছে: "${x}"`, en: (x) => `Heard: "${x}"` },
  micError: { bn: "কথা স্পষ্ট বোঝা যায়নি। আবার চেষ্টা করুন।", en: "I couldn't hear that clearly. Please try again." },
  newChat: { bn: "নতুন রান্নার আলাপ শুরু করা হলো", en: "A new cooking chat has started" },
  timerDone: { bn: "🔔 রান্নার ধাপ সম্পন্ন হয়েছে!", en: "🔔 Cooking step completed!" },
  timerStart: { bn: "টাইমার শুরু করুন", en: "Start Timer" },
  timerPause: { bn: "থামান", en: "Pause" },
  timerResume: { bn: "চালান", en: "Resume" },
  timerCancel: { bn: "বাতিল", en: "Cancel" },
  timerDismiss: { bn: "মুছে ফেলুন", en: "Dismiss" },
  timerFinished: { bn: "✓ সমাপ্ত!", en: "✓ Done!" },
  minutesWord: { bn: "মিনিট", en: "min" },
  minutesShort: { bn: "মি.", en: "min" },
  servesWord: { bn: "জনের পরিবেশন", en: "servings" },
  servingWord: { bn: "জন", en: "servings" },
  mmWord: { bn: "মিমি", en: "mm" },
  listenBtn: { bn: "🔊 শুনুন", en: "🔊 Listen" },
  imageCredit: {
    bn: (a, l) => `ছবি: ${a || "উইকিমিডিয়া"} (${l})`,
    en: (a, l) => `Photo: ${a || "Wikimedia"} (${l})`,
  },
  pachikaArt: { bn: "পাচিকা আর্টওয়ার্ক", en: "Pachika artwork" },
  sourceCurated: {
    bn: "উৎস: ঐতিহ্যবাহী খাঁটি পারিবারিক রেসিপি আর্কাইভ (Curated)",
    en: "Source: curated traditional family recipe archive",
  },
  sourceAi: {
    bn: "উৎস: গুগল জেমিনাই এআই দ্বারা তৈরি রেসিপি (AI Generated)",
    en: "Source: recipe generated by Google Gemini AI (AI-generated)",
  },
  weatherLoadFail: { bn: "আবহাওয়া তথ্য লোড করতে সমস্যা হয়েছে।", en: "There was a problem loading the weather." },
  weatherNetFail: {
    bn: "সার্ভার বা আবহাওয়া এপিআই সংযোগে ত্রুটি হয়েছে। ইন্টারনেট সংযোগ পরীক্ষা করুন।",
    en: "Could not connect to the server or the weather service. Please check your internet connection.",
  },
  yourLocation: { bn: "আপনার অবস্থান", en: "Your location" },
  userHelpQuestion: { bn: "কীভাবে পাচিকা ব্যবহার করব?", en: "How do I use Pachika?" },
  helpAnswer: {
    bn:
      "👩‍🍳 **পাচিকা ব্যবহার করার সহজ নিয়ম:**\n\n" +
      "1. **যেকোনো খাবারের নাম লিখুন**: যেমন 'খিচুড়ি', 'পোলাও', 'মুরগির মাংস ভুনা'।\n" +
      "2. **মানুষের সংখ্যা জানান**: যেমন '৬ জনের জন্য পোলাও'। রেসিপি কার্ডের − ও + বোতামেও পরিমাণ বদলাতে পারবেন।\n" +
      "3. **উপকরণ দিয়ে খুঁজুন**: ফ্রিজে যা আছে লিখুন, যেমন 'ডিম ও আলু আছে, কী রাঁধব?'\n" +
      "4. **ইন্টারেক্টিভ টাইমার ও চেকলিস্ট**: রেসিপি কার্ডের টিক দিয়ে উপকরণ ট্র্যাক করুন এবং যে ধাপে অপেক্ষা করতে হয় সেখানকার টাইমার চালু করুন!\n" +
      "5. **আজকের সুপারিশ ট্যাব**: ওপরের 'আজকের সুপারিশ' ট্যাবে গিয়ে আজকের আবহাওয়ার বিশেষ রান্না দেখুন।",
    en:
      "👩‍🍳 **How to use Pachika:**\n\n" +
      "1. **Type any dish name**: for example 'khichuri', 'pulao', 'chicken bhuna'.\n" +
      "2. **Tell me how many people**: for example 'pulao for 6'. You can also change the amount with the − and + buttons on the recipe card.\n" +
      "3. **Search by ingredients**: tell me what is in your fridge, like 'I have egg and potato, what can I cook?'\n" +
      "4. **Interactive timers and checklist**: tick off ingredients on the recipe card and start the timer on steps that need waiting.\n" +
      "5. **Today's Recommendation tab**: open it above to see dishes that suit today's weather.",
  },
  onlineResultsTitle: { bn: "🌐 ইন্টারনেট থেকে পাওয়া রেসিপি (TheMealDB)", en: "🌐 Recipes found online (TheMealDB)" },
  onlineLoadError: {
    bn: "অনলাইন রেসিপিটি লোড করা যায়নি। ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন।",
    en: "The online recipe could not be loaded. Check your internet connection and try again.",
  },
  sourceOnline: { bn: (n) => `উৎস: ${n} (ইন্টারনেট)`, en: (n) => `Source: ${n} (online)` },
  viewOriginal: { bn: "মূল রেসিপি দেখুন ↗", en: "View original recipe ↗" },
  unknownValue: { bn: "—", en: "—" },
  pageTitle: {
    bn: "পাচিকা — আপনার খাঁটি বাঙালি রান্নার সহকারী",
    en: "Pachika — Your Authentic Bengali Cooking Assistant",
  },
};

function num(n, lang = globalLang) {
  return lang === "bn" ? String(n).replace(/\d/g, (d) => BN_DIGITS[d]) : String(n);
}

function t(key, ...args) {
  const entry = T[key];
  if (!entry) return "";
  const v = entry[globalLang];
  return typeof v === "function" ? v(...args) : v;
}

function tl(key, lang, ...args) {
  const v = T[key][lang];
  return typeof v === "function" ? v(...args) : v;
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function applyStatic(root, lang) {
  root.querySelectorAll("[data-bn][data-en]").forEach((el) => {
    el.textContent = lang === "bn" ? el.dataset.bn : el.dataset.en;
  });
  root.querySelectorAll("[data-ph-bn]").forEach((el) => {
    el.placeholder = lang === "bn" ? el.dataset.phBn : el.dataset.phEn;
  });
  root.querySelectorAll("[data-title-bn]").forEach((el) => {
    const v = lang === "bn" ? el.dataset.titleBn : el.dataset.titleEn;
    el.title = v;
    el.setAttribute("aria-label", v);
  });
}

const UNIT_BN = {
  kg: "কেজি",
  g: "গ্রাম",
  l: "লিটার",
  ml: "মি.লি.",
  tsp: "চা চামচ",
  tbsp: "টেবিল চামচ",
  cup: "কাপ",
  piece: "টি",
  set: "সেট",
  shot: "শট",
};

const HEAT_LABELS = {
  low: { bn: "কম আঁচ", en: "low" },
  "low-medium": { bn: "কম-মাঝারি আঁচ", en: "low-medium" },
  medium: { bn: "মাঝারি আঁচ", en: "medium" },
  "medium-high": { bn: "মাঝারি-উচ্চ আঁচ", en: "medium-high" },
  high: { bn: "উচ্চ আঁচ", en: "high" },
};

function heatLabel(value, lang) {
  const entry = HEAT_LABELS[value];
  return entry ? entry[lang] : value;
}

function unitLabel(unit, lang) {
  if (!unit) return "";
  return lang === "bn" ? UNIT_BN[unit] || unit : unit;
}

function noteLabel(note, lang) {
  if (!note) return "";
  const both = note.match(/^(.*?)\s*\((.+)\)\s*$/);
  if (both && /[\u0980-\u09FF]/.test(both[1])) return lang === "bn" ? both[1] : both[2];
  if (note.toLowerCase() === "adjust to taste") return lang === "bn" ? "স্বাদমতো" : note;
  return note;
}

function categoryLabel(id, lang) {
  const cat = allCategories.find((c) => c.id === id);
  if (!cat) return id || (lang === "bn" ? "খাবার" : "Dish");
  return `${cat.icon} ${lang === "bn" ? cat.name_bn : cat.name_en}`;
}

function showToast(message, duration = 3000) {
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.classList.add("show");
  setTimeout(() => toastEl.classList.remove("show"), duration);
}

function switchScreen(screenName) {
  [landingScreen, chatScreen, weatherScreen].forEach((s) => s && s.classList.remove("active"));
  // Use a body class rather than relying on :has(), which is missing in older mobile browsers.
  document.body.classList.toggle("chat-mode", screenName === "chat");
  [navLandingBtn, navChatBtn, navWeatherBtn].forEach((b) => b && b.classList.remove("active"));

  if (screenName === "landing") {
    landingScreen.classList.add("active");
    navLandingBtn.classList.add("active");
  } else if (screenName === "chat") {
    chatScreen.classList.add("active");
    navChatBtn.classList.add("active");
    if (messageInput) messageInput.focus();
  } else if (screenName === "weather") {
    weatherScreen.classList.add("active");
    navWeatherBtn.classList.add("active");
    if (!isWeatherLoaded) loadWeatherRecommendations("Dhaka");
  }
}

on(navLandingBtn, "click", () => switchScreen("landing"));
on(navChatBtn, "click", () => switchScreen("chat"));
on(navWeatherBtn, "click", () => switchScreen("weather"));
on(startCookingBtn, "click", () => switchScreen("chat"));
on(viewWeatherPicksBtn, "click", () => switchScreen("weather"));

window.openDishInChat = function (dishName, displayName) {
  switchScreen("chat");
  sendMessage(dishName, displayName);
};

document.querySelectorAll(".preview-btn").forEach((btn) => {
  btn.removeAttribute("onclick");
  btn.addEventListener("click", () => {
    const card = btn.closest(".preview-card");
    const heading = card && card.querySelector("h4");
    openDishInChat(card.dataset.dish, heading ? heading.textContent : card.dataset.dish);
  });
});

function updateThemeIcon(theme) {
  if (themeIcon) themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
}

function initTheme() {
  updateThemeIcon(document.documentElement.getAttribute("data-theme") || "light");
}

on(themeToggleBtn, "click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  writeStored("pachika_theme", next);
  updateThemeIcon(next);
  showToast(next === "dark" ? t("themeDark") : t("themeLight"), 1500);
});

async function initRecipeCatalog() {
  try {
    const [recRes, catRes] = await Promise.all([
      fetch(`${API_BASE}/api/recipes`),
      fetch(`${API_BASE}/api/categories`),
    ]);
    if (recRes.ok) {
      const data = await recRes.json();
      allRecipes = data.recipes || [];
    }
    if (catRes.ok) {
      const catData = await catRes.json();
      allCategories = catData.categories || [];
    }
  } catch (err) {
    console.warn("Could not load catalog:", err);
  }
  renderCategoryTabs();
  renderRecipeDirectory();
}

function renderCategoryTabs() {
  if (!categoryTabs) return;
  categoryTabs.innerHTML = "";

  const allTab = document.createElement("button");
  allTab.type = "button";
  allTab.className = `cat-tab ${activeCategory === "all" ? "active" : ""}`;
  allTab.textContent = globalLang === "bn" ? `সব (${num(allRecipes.length)})` : `All (${allRecipes.length})`;
  allTab.addEventListener("click", () => {
    activeCategory = "all";
    renderCategoryTabs();
    renderRecipeDirectory();
  });
  categoryTabs.appendChild(allTab);

  allCategories.forEach((cat) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = `cat-tab ${activeCategory === cat.id ? "active" : ""}`;
    tab.textContent = `${cat.icon} ${globalLang === "bn" ? cat.name_bn : cat.name_en}`;
    tab.addEventListener("click", () => {
      activeCategory = cat.id;
      renderCategoryTabs();
      renderRecipeDirectory();
    });
    categoryTabs.appendChild(tab);
  });

  if (recipeCountLabel) recipeCountLabel.textContent = allRecipes.length ? `(${num(allRecipes.length)})` : "";
}

function renderRecipeDirectory() {
  if (!recipeDirectory) return;
  recipeDirectory.innerHTML = "";
  const query = ((recipeSearchInput && recipeSearchInput.value) || "").trim().toLowerCase();

  const filtered = allRecipes.filter((r) => {
    const matchesCat = activeCategory === "all" || r.category === activeCategory;
    const matchesQuery =
      !query ||
      r.dish.toLowerCase().includes(query) ||
      r.dish_en.toLowerCase().includes(query) ||
      r.id.toLowerCase().includes(query);
    return matchesCat && matchesQuery;
  });

  if (filtered.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding:14px 8px;font-size:0.8rem;color:rgba(255,255,255,0.7);text-align:center;";
    empty.textContent = t("noRecipes");
    recipeDirectory.appendChild(empty);
    return;
  }

  filtered.forEach((r) => {
    const item = document.createElement("div");
    item.className = "recipe-nav-item";
    const primary = globalLang === "bn" ? r.dish : r.dish_en;
    const secondary = globalLang === "bn" ? `<span class="nav-dish-en">${escapeHtml(r.dish_en)}</span>` : "";
    item.innerHTML = `
      <div class="nav-dish-info">
        <span class="nav-dish-title">${escapeHtml(primary)}</span>
        ${secondary}
      </div>
      <span class="nav-dish-time">⏱️ ${num(r.total_time_min)} ${t("minutesShort")}</span>
    `;
    item.addEventListener("click", () => {
      loadRecipeById(r.id);
      if (window.innerWidth <= 860 && sidebar) sidebar.classList.remove("open");
    });
    recipeDirectory.appendChild(item);
  });
}

on(recipeSearchInput, "input", renderRecipeDirectory);

async function loadRecipeById(recipeId) {
  hideEmptyState();
  const typingRow = addTypingIndicator();
  try {
    const res = await fetch(`${API_BASE}/api/recipe/${recipeId}?servings=${DEFAULT_SERVINGS}`);
    if (!res.ok) throw new Error("Recipe not found");
    const recipe = await res.json();
    typingRow.remove();
    addMessage(
      tl("recipeLoaded", "bn", recipe, recipe.base_servings),
      "bot",
      tl("recipeLoaded", "en", recipe, recipe.base_servings)
    );
    renderRecipeCard(recipe);
  } catch (err) {
    typingRow.remove();
    addMessage(tl("recipeLoadError", "bn"), "bot", tl("recipeLoadError", "en"));
  }
}

function submitChat() {
  if (!messageInput) return;
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = "";
  messageInput.style.height = "auto";
  sendMessage(text);
}

on(messageInput, "keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    submitChat();
  }
});

on(messageInput, "input", () => {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 140)}px`;
});

on(chatForm, "submit", (e) => {
  e.preventDefault();
  submitChat();
});

async function sendMessage(text, displayText) {
  hideEmptyState();
  addMessage(displayText || text, "user");

  if (sendBtn) {
    sendBtn.classList.add("sending");
    setTimeout(() => sendBtn.classList.remove("sending"), 400);
  }

  const typingRow = addTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        servings: DEFAULT_SERVINGS,
        session_id: currentSessionId,
      }),
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const data = await res.json();

    if (data.session_id) {
      currentSessionId = data.session_id;
      writeStored("pachika_session_id", currentSessionId);
    }

    typingRow.remove();
    addMessage(data.reply, "bot", data.reply_en);

    if (data.clarification_options && data.clarification_options.length > 0) {
      renderClarificationPills(data.clarification_options);
    }
    if (data.online_results && data.online_results.length > 0) {
      renderOnlineResults(data.online_results);
    }
    if (data.recipe) renderRecipeCard(data.recipe);
    if (data.suggestions && data.suggestions.length > 1) renderSuggestionPills(data.suggestions);
  } catch (err) {
    typingRow.remove();
    addMessage(tl("serverError", "bn"), "bot", tl("serverError", "en"));
    console.error(err);
  }
}

function hideEmptyState() {
  if (emptyState) emptyState.style.display = "none";
}

function formatMarkdown(text) {
  if (!text) return "";
  const html = escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>");

  let inList = false;
  const formatted = [];
  for (const line of html.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.startsWith("• ") || trimmed.startsWith("- ")) {
      if (!inList) {
        formatted.push("<ul>");
        inList = true;
      }
      formatted.push(`<li>${trimmed.substring(2)}</li>`);
    } else {
      if (inList) {
        formatted.push("</ul>");
        inList = false;
      }
      if (trimmed) formatted.push(`<p>${trimmed}</p>`);
    }
  }
  if (inList) formatted.push("</ul>");
  return formatted.join("");
}

function pickMessage(row) {
  const m = row._msg;
  return globalLang === "en" && m.en ? m.en : m.bn;
}

function addMessage(textBn, who, textEn) {
  const row = document.createElement("div");
  row.className = `msg-row ${who}`;
  row._msg = { bn: textBn, en: textEn || textBn };

  const avatar = document.createElement("img");
  avatar.className = "msg-avatar";
  avatar.src = who === "user" ? USER_AVATAR : PACHIKA_AVATAR;
  avatar.alt = who === "user" ? "You" : "Pachika";

  const wrap = document.createElement("div");
  wrap.className = "msg-content-wrap";

  const bubble = document.createElement("div");
  bubble.className = "msg";
  bubble.innerHTML = formatMarkdown(pickMessage(row));
  wrap.appendChild(bubble);

  if (who === "bot") {
    const actions = document.createElement("div");
    actions.className = "msg-actions";
    const speakBtn = document.createElement("button");
    speakBtn.type = "button";
    speakBtn.className = "msg-speak-btn";
    speakBtn.innerHTML = `<span>${t("listenBtn")}</span>`;
    speakBtn.addEventListener("click", () => playSpeech(pickMessage(row)));
    actions.appendChild(speakBtn);
    wrap.appendChild(actions);
  }

  row.appendChild(avatar);
  row.appendChild(wrap);
  const wasNearBottom = chatWindow.scrollHeight - chatWindow.scrollTop - chatWindow.clientHeight < 120;
  chatWindow.appendChild(row);
  if (who === "user" || wasNearBottom) {
    requestAnimationFrame(() => { chatWindow.scrollTop = chatWindow.scrollHeight; });
  }
  return row;
}

function retranslateMessages() {
  chatWindow.querySelectorAll(".msg-row").forEach((row) => {
    if (!row._msg) return;
    const bubble = row.querySelector(".msg");
    if (bubble) bubble.innerHTML = formatMarkdown(pickMessage(row));
    const speak = row.querySelector(".msg-speak-btn span");
    if (speak) speak.textContent = t("listenBtn");
  });
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  const avatar = document.createElement("img");
  avatar.className = "msg-avatar";
  avatar.src = PACHIKA_AVATAR;
  avatar.alt = "Pachika";
  const bubble = document.createElement("div");
  bubble.className = "msg typing";
  bubble.innerHTML = "<span></span><span></span><span></span>";
  row.appendChild(avatar);
  row.appendChild(bubble);
  chatWindow.appendChild(row);
  requestAnimationFrame(() => { chatWindow.scrollTop = chatWindow.scrollHeight; });
  return row;
}

function renderPillRow(items, onClick) {
  const container = document.createElement("div");
  container.className = "prompt-chips";
  container.style.padding = "4px 0 10px 48px";
  items.forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.textContent = globalLang === "bn" ? `🍲 ${item.dish} (${item.dish_en})` : `🍲 ${item.dish_en}`;
    btn.addEventListener("click", () => onClick(item));
    container.appendChild(btn);
  });
  chatWindow.appendChild(container);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function renderClarificationPills(options) {
  renderPillRow(options, (opt) => sendMessage(opt.dish, globalLang === "bn" ? opt.dish : opt.dish_en));
}

function renderSuggestionPills(suggestions) {
  renderPillRow(suggestions, (s) => loadRecipeById(s.id));
}

function safeHttpUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : "";
  } catch (e) {
    return "";
  }
}

function renderOnlineResults(items) {
  const wrap = document.createElement("div");
  wrap.className = "online-results";

  const title = document.createElement("div");
  title.className = "online-results-title";
  title.textContent = t("onlineResultsTitle");
  wrap.appendChild(title);

  const grid = document.createElement("div");
  grid.className = "online-results-grid";
  items.forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "online-card";

    const img = document.createElement("img");
    img.loading = "lazy";
    img.alt = item.title;
    img.src = safeHttpUrl(item.thumb) || PLACEHOLDER_IMG;

    const body = document.createElement("span");
    body.className = "online-card-body";
    const name = document.createElement("strong");
    name.textContent = item.title;
    const meta = document.createElement("small");
    meta.textContent = [item.category, item.area].filter(Boolean).join(" • ") || item.provider_name;
    body.appendChild(name);
    body.appendChild(meta);

    card.appendChild(img);
    card.appendChild(body);
    card.addEventListener("click", () => loadOnlineRecipe(item, card));
    grid.appendChild(card);
  });
  wrap.appendChild(grid);

  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadOnlineRecipe(item, button) {
  if (button) button.disabled = true;
  hideEmptyState();
  const typingRow = addTypingIndicator();
  try {
    const params = new URLSearchParams({ provider: item.provider, id: item.id, session_id: currentSessionId });
    const res = await fetch(`${API_BASE}/api/online/recipe?${params.toString()}`);
    const data = await res.json();
    typingRow.remove();
    if (!res.ok || !data.recipe) {
      const bn = data.error_bn || tl("onlineLoadError", "bn");
      const en = data.error || tl("onlineLoadError", "en");
      addMessage(bn, "bot", en);
      return;
    }
    addMessage(data.reply, "bot", data.reply_en);
    renderRecipeCard(data.recipe);
  } catch (err) {
    typingRow.remove();
    addMessage(tl("onlineLoadError", "bn"), "bot", tl("onlineLoadError", "en"));
    console.error(err);
  } finally {
    if (button) button.disabled = false;
  }
}

function formatAmount(rawAmt, lang) {
  let out;
  if (Math.abs(rawAmt - Math.round(rawAmt)) < 0.04) out = String(Math.round(rawAmt));
  else if (Math.abs(rawAmt * 2 - Math.round(rawAmt * 2)) < 0.05) out = (Math.round(rawAmt * 2) / 2).toFixed(1);
  else out = rawAmt.toFixed(2);
  return num(out, lang);
}

function scaledAmount(ing, factor) {
  if (ing.amount === null || ing.amount === undefined) return null;
  let ingFactor = factor;
  const nameEn = (ing.name_en || "").toLowerCase();
  const nameBn = ing.name || "";
  const isSalt = nameEn.includes("salt") || nameBn.includes("লবণ");
  const isChili = nameEn.includes("chili") || nameEn.includes("pepper") || nameBn.includes("মরিচ");
  if (factor > 1) {
    if (isSalt) ingFactor = Math.pow(factor, 0.82);
    else if (isChili) ingFactor = Math.pow(factor, 0.85);
  }
  return ing.amount * ingFactor;
}

function pickTimerSteps(steps) {
  const eligible = steps
    .map((step, index) => ({ index, minutes: step.duration_min || 0 }))
    .filter((s) => s.minutes >= MIN_TIMER_MINUTES)
    .sort((a, b) => b.minutes - a.minutes || a.index - b.index)
    .slice(0, MAX_TIMERS_PER_RECIPE);
  return new Set(eligible.map((s) => s.index));
}

function renderRecipeCard(recipe) {
  const node = recipeCardTemplate.content.cloneNode(true);
  const card = node.querySelector(".recipe-card");

  card._recipeData = recipe;
  card._baseServings = recipe.base_servings;
  card._currentServings = recipe.base_servings;
  card._cardLang = globalLang;
  card._timers = {};
  card.dataset.recipeId = recipe.id;

  updateCardDOM(card);

  on(card.querySelector(".tts-listen-btn"), "click", () => {
    const r = card._recipeData;
    const lang = card._cardLang;
    const text =
      lang === "bn"
        ? `${r.dish}। ${num(card._currentServings, "bn")} জনের জন্য।${r.total_time_min == null ? "" : ` মোট সময় ${num(r.total_time_min, "bn")} মিনিট।`}`
        : `${r.dish_en}. For ${card._currentServings} servings.${r.total_time_min == null ? "" : ` Total time ${r.total_time_min} minutes.`}`;
    playSpeech(text, lang);
  });

  on(card.querySelector(".card-lang-btn"), "click", () => {
    card._cardLang = card._cardLang === "bn" ? "en" : "bn";
    updateCardDOM(card);
  });

  on(card.querySelector(".copy-recipe-btn"), "click", () => {
    copyRecipeToClipboard(card._recipeData, card._currentServings, card._cardLang);
  });

  on(card.querySelector(".print-recipe-btn"), "click", () => window.print());

  on(card.querySelector(".scale-minus"), "click", () => {
    if (card._currentServings > 1) {
      card._currentServings -= 1;
      updateCardDOM(card);
    }
  });

  on(card.querySelector(".scale-plus"), "click", () => {
    if (card._currentServings < 30) {
      card._currentServings += 1;
      updateCardDOM(card);
    }
  });

  chatWindow.appendChild(card);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function updateCardDOM(card) {
  const r = card._recipeData;
  const servings = card._currentServings;
  const factor = servings / card._baseServings;
  const lang = card._cardLang;
  const isBn = lang === "bn";

  applyStatic(card, lang);

  const imgEl = card.querySelector(".recipe-main-img");
  const licenseEl = card.querySelector(".image-license-info");
  const wantedSrc = r.image && r.image.url ? r.image.url : PLACEHOLDER_IMG;
  if (imgEl.dataset.wanted !== wantedSrc) {
    imgEl.dataset.wanted = wantedSrc;
    delete imgEl.dataset.fallbackDone;
    imgEl.src = wantedSrc;
  }
  imgEl.alt = r.image && r.image.url ? (isBn ? r.image.alt_bn || r.dish : r.image.alt || r.dish_en) : isBn ? r.dish : r.dish_en;
  if (r.image && r.image.url && r.image.license) {
    licenseEl.textContent = tl("imageCredit", lang, r.image.author, r.image.license);
  } else {
    licenseEl.textContent = tl("pachikaArt", lang);
  }

  card.querySelector(".recipe-title").textContent = isBn ? r.dish : r.dish_en;
  card.querySelector(".recipe-subtitle").textContent = isBn
    ? `${r.dish_en} • ${num(servings, lang)} ${tl("servesWord", lang)}`
    : `${servings} ${tl("servesWord", lang)}`;
  card.querySelector(".category-badge").textContent = categoryLabel(r.category, lang);
  const heatBadge = card.querySelector(".heat-badge");
  const isOnline = Boolean(r.source && r.source.type === "online");
  heatBadge.style.display = isOnline && !r.heat_level ? "none" : "";
  heatBadge.textContent = `🔥 ${r.heat_level ? heatLabel(r.heat_level, lang) : isBn ? "মাঝারি আঁচ" : "medium"}`;

  renderSource(card, r, lang);

  card.querySelector(".serving-number").textContent = num(servings, lang);
  card.querySelector(".card-lang-btn .tool-text").textContent = isBn ? "Eng" : "বাং";

  const minutes = (v) =>
    v === null || v === undefined ? tl("unknownValue", lang) : `${num(v, lang)} ${tl("minutesWord", lang)}`;
  card.querySelector(".prep-time").textContent = minutes(r.prep_time_min);
  card.querySelector(".cook-time").textContent = minutes(r.cook_time_min);
  card.querySelector(".total-time").textContent = minutes(r.total_time_min);

  const ingList = card.querySelector(".ingredient-list");
  const checkedState = Array.from(ingList.querySelectorAll(".ingredient-checkbox")).map((c) => c.checked);
  ingList.innerHTML = "";
  r.ingredients.forEach((ing, idx) => {
    const li = document.createElement("li");
    li.className = "ingredient-item";

    const chk = document.createElement("input");
    chk.type = "checkbox";
    chk.className = "ingredient-checkbox";
    chk.checked = Boolean(checkedState[idx]);
    li.classList.toggle("checked", chk.checked);
    chk.addEventListener("change", () => li.classList.toggle("checked", chk.checked));

    const span = document.createElement("span");
    span.className = "ingredient-text";
    const strong = document.createElement("strong");
    const shownAmount = scaledAmount(ing, factor);
    if (shownAmount !== null) {
      strong.textContent = `${formatAmount(shownAmount, lang)} ${unitLabel(ing.unit, lang)}`.trim();
      span.appendChild(strong);
      span.appendChild(document.createTextNode(` ${isBn ? ing.name : ing.name_en || ing.name}`));
    } else {
      strong.textContent = isBn ? ing.name : ing.name_en || ing.name;
      span.appendChild(strong);
    }

    if (ing.note) {
      const noteSpan = document.createElement("span");
      noteSpan.className = "ing-note";
      noteSpan.textContent = ` (${noteLabel(ing.note, lang)})`;
      span.appendChild(noteSpan);
    }

    li.appendChild(chk);
    li.appendChild(span);
    ingList.appendChild(li);
  });

  const stepsList = card.querySelector(".steps-list");
  stepsList.innerHTML = "";
  const timerSteps = pickTimerSteps(r.steps);

  r.steps.forEach((step, idx) => {
    const li = document.createElement("li");
    li.className = "step-item";

    const topDiv = document.createElement("div");
    topDiv.className = "step-top";
    const badge = document.createElement("span");
    badge.className = "step-badge";
    badge.textContent = num(idx + 1, lang);
    const instruction = document.createElement("div");
    instruction.className = "step-instruction";
    instruction.textContent = isBn ? step.instruction : step.instruction_en || step.instruction;
    topDiv.appendChild(badge);
    topDiv.appendChild(instruction);
    li.appendChild(topDiv);

    const meta = document.createElement("div");
    meta.className = "step-meta";

    if (step.duration_min) {
      const durPill = document.createElement("span");
      durPill.className = "step-pill";
      durPill.textContent = `⏱️ ${minutes(step.duration_min)}`;
      meta.appendChild(durPill);

      if (timerSteps.has(idx)) {
        const timerBtn = document.createElement("button");
        timerBtn.type = "button";
        timerBtn.className = "step-timer-btn";
        timerBtn.textContent = `⏱️ ${tl("timerStart", lang)}`;
        timerBtn.addEventListener("click", () => startStepTimer(card, idx, step.duration_min));
        meta.appendChild(timerBtn);
      }
    }

    if (step.heat) {
      const heatPill = document.createElement("span");
      heatPill.className = "step-pill heat";
      heatPill.textContent = `🔥 ${heatLabel(step.heat, lang)}`;
      meta.appendChild(heatPill);
    }

    li.appendChild(meta);
    stepsList.appendChild(li);
  });

  Object.keys(card._timers).forEach((idx) => renderTimerBox(card, Number(idx)));

  const subSection = card.querySelector(".substitutions-section");
  const subList = card.querySelector(".substitutions-list");
  subList.innerHTML = "";
  if (r.substitutions && r.substitutions.length > 0) {
    subSection.style.display = "block";
    r.substitutions.forEach((s) => {
      const item = document.createElement("div");
      item.className = "substitution-item";
      const strong = document.createElement("strong");
      strong.textContent = `${isBn ? s.ingredient_bn : s.ingredient}:`;
      const em = document.createElement("em");
      em.textContent = isBn ? s.impact_bn : s.impact;
      item.appendChild(strong);
      item.appendChild(document.createTextNode(` ${isBn ? s.substitute_bn : s.substitute} — `));
      item.appendChild(em);
      subList.appendChild(item);
    });
  } else {
    subSection.style.display = "none";
  }
}

function renderSource(card, r, lang) {
  const badge = card.querySelector(".recipe-source-badge");
  const textEl = card.querySelector(".source-text");
  const isBn = lang === "bn";
  const old = badge.querySelector(".source-link");
  if (old) old.remove();
  const oldNote = card.querySelector(".recipe-assumption");
  if (oldNote) oldNote.remove();

  const source = r.source || {};
  if (source.type === "online") {
    textEl.textContent = tl("sourceOnline", lang, source.name || "TheMealDB");
    const href = safeHttpUrl(source.source_url);
    if (href) {
      const link = document.createElement("a");
      link.className = "source-link";
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = tl("viewOriginal", lang);
      badge.appendChild(link);
    }
    const assumptions = (isBn ? r.assumptions_bn : r.assumptions_en) || [];
    if (assumptions.length) {
      const note = document.createElement("div");
      note.className = "recipe-assumption";
      note.textContent = `ℹ️ ${assumptions.join(" ")}`;
      badge.insertAdjacentElement("afterend", note);
    }
    return;
  }
  textEl.textContent = source.is_ai_generated ? tl("sourceAi", lang) : tl("sourceCurated", lang);
}

function formatTimer(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

function startStepTimer(card, idx, minutes) {
  const existing = card._timers[idx];
  if (existing) clearInterval(existing.interval);
  const timer = { remaining: minutes * 60, paused: false, done: false, interval: null };
  timer.interval = setInterval(() => tickTimer(card, idx), 1000);
  card._timers[idx] = timer;
  renderTimerBox(card, idx);
}

function tickTimer(card, idx) {
  const timer = card._timers[idx];
  if (!timer || timer.paused || timer.done) return;
  timer.remaining -= 1;
  if (timer.remaining <= 0) {
    timer.remaining = 0;
    timer.done = true;
    clearInterval(timer.interval);
    playChimeSound();
    showToast(tl("timerDone", card._cardLang), 5000);
  }
  renderTimerBox(card, idx);
}

function renderTimerBox(card, idx) {
  const timer = card._timers[idx];
  const stepLi = card.querySelectorAll(".step-item")[idx];
  if (!stepLi) return;

  let box = stepLi.querySelector(".timer-box-active");
  if (!timer) {
    if (box) box.remove();
    return;
  }

  const lang = card._cardLang;
  if (!box) {
    box = document.createElement("div");
    box.className = "timer-box-active";
    stepLi.appendChild(box);
  }
  box.innerHTML = "";

  const label = document.createElement("span");
  label.className = "timer-countdown";
  label.textContent = timer.done ? tl("timerFinished", lang) : formatTimer(timer.remaining);

  const controls = document.createElement("div");
  controls.className = "timer-controls";

  if (!timer.done) {
    const pauseBtn = document.createElement("button");
    pauseBtn.type = "button";
    pauseBtn.className = "timer-action-btn";
    pauseBtn.textContent = timer.paused ? tl("timerResume", lang) : tl("timerPause", lang);
    pauseBtn.addEventListener("click", () => {
      timer.paused = !timer.paused;
      renderTimerBox(card, idx);
    });
    controls.appendChild(pauseBtn);
  }

  const stopBtn = document.createElement("button");
  stopBtn.type = "button";
  stopBtn.className = "timer-action-btn";
  stopBtn.textContent = timer.done ? tl("timerDismiss", lang) : tl("timerCancel", lang);
  stopBtn.addEventListener("click", () => {
    clearInterval(timer.interval);
    delete card._timers[idx];
    renderTimerBox(card, idx);
  });
  controls.appendChild(stopBtn);

  box.appendChild(label);
  box.appendChild(controls);

  if (timer.done) {
    box.style.background = "#E8F5E9";
    box.style.borderColor = "var(--success-green)";
  } else {
    box.style.background = "";
    box.style.borderColor = "";
  }
}

function clearAllTimers() {
  chatWindow.querySelectorAll(".recipe-card").forEach((card) => {
    Object.values(card._timers || {}).forEach((timer) => clearInterval(timer.interval));
    card._timers = {};
  });
}

function playChimeSound() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(587.33, ctx.currentTime);
    osc.frequency.setValueAtTime(880, ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.8);
  } catch (e) {
    console.warn("Audio chime error:", e);
  }
}

function weatherIcon(w) {
  const night = w.is_day === 0;
  switch (w.condition_type) {
    case "clear":
      return night ? "🌙" : "☀️";
    case "cloudy":
      return night ? "☁️" : "⛅";
    case "fog":
      return "🌫️";
    case "rain":
      return "🌧️";
    case "storm":
      return "⛈️";
    case "cold":
      return "❄️";
    default:
      return "🌤️";
  }
}

function renderWeather(data) {
  const loc = data.location || {};
  const w = data.weather || {};
  const isBn = globalLang === "bn";

  weatherIconLarge.textContent = weatherIcon(w);
  const cityName = loc.name;
  const isGps = loc.name === "Your Location";
  if (isGps) {
    const coords = Number.isFinite(Number(loc.lat)) ? ` (${num(Number(loc.lat).toFixed(2))}, ${num(Number(loc.lon).toFixed(2))})` : "";
    weatherCityText.textContent = `${t("yourLocation")}${coords}`;
  } else {
    weatherCityText.textContent =
      isBn && loc.name_bn && loc.name_bn !== cityName ? `${loc.name_bn} (${cityName})` : isBn && loc.name_bn ? loc.name_bn : cityName;
  }
  weatherTempNum.textContent = `${num(Math.round(w.temperature_c))}°C`;
  weatherCondText.textContent = isBn ? w.condition_bn : w.condition_en;
  weatherHumidityText.textContent = w.humidity_percent == null ? "—" : `${num(w.humidity_percent)}%`;
  weatherPrecipText.textContent = `${num(w.precipitation_mm)} ${t("mmWord")}`;
  weatherReasonText.textContent = isBn ? data.reason_bn : data.reason_en;

  if (data.festive) {
    festiveBannerCard.style.display = "block";
    festiveTitle.textContent = isBn ? data.festive.name_bn : data.festive.name_en;
    festiveDesc.textContent = isBn ? data.festive.description_bn : data.festive.description_en;
  } else {
    festiveBannerCard.style.display = "none";
  }

  weatherRecipesGrid.innerHTML = "";
  (data.weather_recipes || []).forEach((r) => {
    const card = document.createElement("div");
    card.className = "weather-recipe-card";

    const img = document.createElement("img");
    img.className = "w-card-img";
    img.loading = "lazy";
    img.alt = isBn ? r.dish : r.dish_en;
    img.src = r.image && r.image.url ? r.image.url : PLACEHOLDER_IMG;

    const body = document.createElement("div");
    body.className = "w-card-body";
    const h4 = document.createElement("h4");
    h4.textContent = isBn ? r.dish : r.dish_en;
    const sub = document.createElement("span");
    sub.textContent = `${isBn ? `${r.dish_en} • ` : ""}⏱️ ${num(r.total_time_min)} ${t("minutesWord")}`;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "w-card-btn";
    btn.textContent = isBn ? "🍲 রেসিপি দেখুন" : "🍲 View recipe";
    btn.addEventListener("click", () => openDishInChat(r.dish, isBn ? r.dish : r.dish_en));

    body.appendChild(h4);
    body.appendChild(sub);
    body.appendChild(btn);
    card.appendChild(img);
    card.appendChild(body);
    weatherRecipesGrid.appendChild(card);
  });
}

async function loadWeatherRecommendations(city = null, lat = null, lon = null) {
  weatherLoading.style.display = "block";
  weatherContent.style.display = "none";
  weatherError.style.display = "none";

  let queryUrl = `${API_BASE}/api/weather/recommendations?`;
  if (city) queryUrl += `city=${encodeURIComponent(city)}`;
  else if (lat !== null && lon !== null) queryUrl += `lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
  else queryUrl += "city=Dhaka";

  try {
    const res = await fetch(queryUrl);
    const data = await res.json();
    weatherLoading.style.display = "none";

    if (!res.ok || !data.success) {
      weatherError.style.display = "block";
      weatherError.textContent =
        (globalLang === "bn" ? data.error_bn : data.error) || data.error || t("weatherLoadFail");
      return;
    }

    isWeatherLoaded = true;
    lastWeatherData = data;
    weatherContent.style.display = "block";
    renderWeather(data);
  } catch (err) {
    weatherLoading.style.display = "none";
    weatherError.style.display = "block";
    weatherError.textContent = t("weatherNetFail");
    console.error(err);
  }
}

on(citySearchBtn, "click", () => {
  const city = cityInput.value.trim();
  if (city) loadWeatherRecommendations(city);
});

on(cityInput, "keydown", (e) => {
  if (e.key === "Enter" && !e.isComposing) {
    const city = cityInput.value.trim();
    if (city) loadWeatherRecommendations(city);
  }
});

on(useGeoLocationBtn, "click", () => {
  if (!navigator.geolocation) {
    showToast(t("geoUnsupported"), 3500);
    return;
  }
  if (window.isSecureContext === false) {
    showToast(t("geoInsecure"), 4500);
    return;
  }
  showToast(t("geoAsking"), 2500);
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude } = pos.coords;
      if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
        showToast(t("geoInvalid"), 3500);
        return;
      }
      if (cityInput) cityInput.value = "";
      loadWeatherRecommendations(null, latitude.toFixed(4), longitude.toFixed(4));
    },
    (err) => {
      const key = err && err.code === 1 ? "geoDenied" : err && err.code === 3 ? "geoTimeout" : "geoUnavailable";
      showToast(t(key), 4500);
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
  );
});

async function playSpeech(text, lang = globalLang) {
  if (!text) return;
  showToast(tl("speaking", lang), 2000);

  if (lang === "bn") {
    try {
      const res = await fetch(`${API_BASE}/api/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.audio) {
          audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
          audioPlayer.play();
          return;
        }
      }
    } catch (err) {
      console.warn("Backend TTS unreachable, falling back to browser speech:", err);
    }
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.replace(/[*#_•`]/g, "").substring(0, 300));
    utterance.lang = lang === "bn" ? "bn-BD" : "en-US";
    utterance.rate = 0.95;
    const voice = window.speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith(lang));
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  }
}

on(micBtn, "click", () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert(t("micUnsupported"));
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = globalLang === "bn" ? "bn-BD" : "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  micBtn.classList.add("listening");
  voiceStatusBar.classList.add("active");
  voiceStatusText.textContent = t("listening");

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    voiceStatusText.textContent = t("heard", transcript);
    setTimeout(() => {
      voiceStatusBar.classList.remove("active");
      sendMessage(transcript);
    }, 600);
  };

  recognition.onerror = () => {
    voiceStatusText.textContent = t("micError");
    setTimeout(() => voiceStatusBar.classList.remove("active"), 1500);
  };

  recognition.onend = () => {
    micBtn.classList.remove("listening");
    setTimeout(() => voiceStatusBar.classList.remove("active"), 1000);
  };

  recognition.start();
});

function copyRecipeToClipboard(recipe, servings, lang) {
  const isBn = lang === "bn";
  const factor = servings / recipe.base_servings;

  let text = `🍲 ${isBn ? recipe.dish : recipe.dish_en} (${isBn ? recipe.dish_en : recipe.dish})\n`;
  const timesBn = recipe.prep_time_min == null ? "" : ` | প্রস্তুতি: ${num(recipe.prep_time_min, lang)} মিনিট | রান্না: ${num(recipe.cook_time_min, lang)} মিনিট`;
  const timesEn = recipe.prep_time_min == null ? "" : ` | Prep: ${recipe.prep_time_min} min | Cook: ${recipe.cook_time_min} min`;
  text += isBn
    ? `পরিবেশন: ${num(servings, lang)} জন${timesBn}\n\n--- উপকরণ তালিকা ---\n`
    : `Servings: ${servings}${timesEn}\n\n--- Ingredients ---\n`;

  recipe.ingredients.forEach((ing) => {
    const value = scaledAmount(ing, factor);
    const label = isBn ? ing.name : ing.name_en || ing.name;
    text += value === null
      ? `• ${label}${ing.note ? ` (${noteLabel(ing.note, lang)})` : ""}\n`
      : `• ${label}: ${formatAmount(value, lang)} ${unitLabel(ing.unit, lang)}\n`;
  });

  text += isBn ? "\n--- রান্নার ধাপসমূহ ---\n" : "\n--- Cooking steps ---\n";
  recipe.steps.forEach((step, i) => {
    text += `${num(i + 1, lang)}. ${isBn ? step.instruction : step.instruction_en || step.instruction}\n`;
  });
  text += isBn ? "\n— পাচিকা রান্নার সহকারী" : "\n— Pachika cooking assistant";

  const done = () => showToast(t("copied"), 3000);
  const fail = () => showToast(t("copyFailed"), 2000);
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done, fail);
  } else {
    fail();
  }
}

if (promptChips) {
  promptChips.querySelectorAll(".chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = globalLang === "bn" ? btn.dataset.promptBn : btn.dataset.promptEn;
      if (prompt) {
        switchScreen("chat");
        sendMessage(prompt);
      }
    });
  });
}

on(newChatBtn, "click", () => {
  clearAllTimers();
  currentSessionId = `sess_${Date.now()}`;
  writeStored("pachika_session_id", currentSessionId);
  chatWindow.innerHTML = "";
  chatWindow.appendChild(emptyState);
  emptyState.style.display = "block";
  if (sidebar) sidebar.classList.remove("open");
  showToast(t("newChat"), 2000);
});

on(menuToggle, "click", () => sidebar && sidebar.classList.toggle("open"));

function setLanguage(lang, announce) {
  globalLang = lang;
  writeStored("pachika_lang", lang);
  document.documentElement.lang = lang;
  document.title = t("pageTitle");
  if (langLabel) langLabel.textContent = lang === "bn" ? "English" : "বাংলা";

  applyStatic(document, lang);
  renderCategoryTabs();
  renderRecipeDirectory();
  retranslateMessages();
  chatWindow.querySelectorAll(".online-results-title").forEach((el) => {
    el.textContent = t("onlineResultsTitle");
  });

  chatWindow.querySelectorAll(".recipe-card").forEach((card) => {
    card._cardLang = lang;
    updateCardDOM(card);
  });

  if (lastWeatherData) renderWeather(lastWeatherData);
  if (announce) showToast(t("langChosen"), 2000);
}

on(langToggleBtn, "click", () => setLanguage(globalLang === "bn" ? "en" : "bn", true));

on(infoBtn, "click", () => {
  switchScreen("chat");
  hideEmptyState();
  addMessage(tl("userHelpQuestion", "bn"), "user", tl("userHelpQuestion", "en"));
  addMessage(tl("helpAnswer", "bn"), "bot", tl("helpAnswer", "en"));
});

function fallbackImage(img) {
  if (!(img instanceof HTMLImageElement) || img.dataset.fallbackDone) return;
  const src = img.currentSrc || img.src;
  const m = src.match(/\/(\d+)px-[^/]+$/);
  if (m && src.includes("upload.wikimedia.org")) {
    const current = Number(m[1]);
    const next = THUMB_STEPS.find((s) => s < current);
    if (next) {
      img.src = src.replace(`/${current}px-`, `/${next}px-`);
      return;
    }
  }
  img.dataset.fallbackDone = "1";
  if (!src.endsWith(PLACEHOLDER_IMG)) img.src = PLACEHOLDER_IMG;
}

document.addEventListener("error", (e) => fallbackImage(e.target), true);

function recheckImages() {
  document.querySelectorAll("img").forEach((img) => {
    if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) fallbackImage(img);
  });
}

(function initSparkles() {
  const layer = document.createElement("div");
  layer.className = "sparkle-layer";
  layer.setAttribute("aria-hidden", "true");
  document.body.appendChild(layer);

  const colors = ["#FF8A00", "#FF9F1C", "#FFB347", "#FF6A00", "#FFC15E"];
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const rand = (min, max) => min + Math.random() * (max - min);

  function burst(x, y) {
    if (layer.childElementCount > 90) return;
    const calm = reduced.matches;
    const count = calm ? 6 : 12;
    for (let i = 0; i < count; i++) {
      const spark = document.createElement("span");
      const angle = (Math.PI * 2 * i) / count + rand(-0.3, 0.3);
      const distance = calm ? rand(6, 14) : rand(22, 56);
      const size = rand(7, 15);
      spark.className = `sparkle${i % 3 === 0 ? " dot" : ""}${calm ? " calm" : ""}`;
      spark.style.left = `${x}px`;
      spark.style.top = `${y}px`;
      spark.style.setProperty("--s", `${size}px`);
      spark.style.setProperty("--c", colors[i % colors.length]);
      spark.style.setProperty("--dx", `${Math.cos(angle) * distance}px`);
      spark.style.setProperty("--dy", `${Math.sin(angle) * distance}px`);
      spark.style.setProperty("--r", `${rand(-120, 120)}deg`);
      spark.style.setProperty("--d", `${calm ? 420 : rand(520, 820)}ms`);
      spark.addEventListener("animationend", () => spark.remove());
      layer.appendChild(spark);
    }
  }

  document.addEventListener(
    "pointerdown",
    (e) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      burst(e.clientX, e.clientY);
    },
    true
  );
})();

function init() {
  initTheme();
  setLanguage(globalLang, false);
  initRecipeCatalog();
  recheckImages();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
