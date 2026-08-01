const modes = {
  holistic: {
    title: "קריאה הוליסטית",
    text: "נשלב כמה עדשות לקריאה אחת. בגרסה הזו הטארוט פעיל, והמבנה כבר מוכן לנומרולוגיה, קבלה וקריסטלים.",
  },
  tarot: {
    title: "קריאת טארוט",
    text: "ניכנס לחדר הסמלים ונבחן דפוסים, מתחים ואפשרויות — בלי לקבוע עבורך מה יקרה.",
  },
  numerology: {
    title: "קריאה נומרולוגית",
    text: "חדר המספרים נמצא בבנייה. תאריך הלידה שתבחרי לשתף יאפשר להוסיף את הרובד הזה בקרוב.",
  },
  kabbalah: {
    title: "התבוננות קבלית",
    text: "היכל הקבלה יציע ערכים ועקרונות להתבוננות. הוא ייפתח בגרסה הבאה.",
  },
  crystals: {
    title: "גן הקריסטלים",
    text: "גן הקריסטלים יציע סמל וכוונה שילוו את התהליך, לא הבטחה רפואית או נבואית.",
  },
};

let selectedMode = "holistic";
const portals = [...document.querySelectorAll(".portal")];
const guideText = document.getElementById("guideText");
const beginButton = document.getElementById("beginButton");
const soundToggle = document.getElementById("soundToggle");

function selectMode(mode) {
  selectedMode = mode;
  portals.forEach((portal) => portal.classList.toggle("active", portal.dataset.guide === mode));
  guideText.textContent = modes[mode].text;
  beginButton.textContent = mode === "holistic" ? "להתחיל במסע המשולב" : "להיכנס לחדר";
}

portals.forEach((portal) => portal.addEventListener("click", () => selectMode(portal.dataset.guide)));

beginButton.addEventListener("click", () => {
  window.location.href = "/world-demo";
});

soundToggle.addEventListener("click", () => {
  const enabled = soundToggle.getAttribute("aria-pressed") !== "true";
  soundToggle.setAttribute("aria-pressed", String(enabled));
  soundToggle.textContent = enabled ? "קול: פעיל" : "קול: כבוי";
  if (enabled && "speechSynthesis" in window) {
    const utterance = new SpeechSynthesisUtterance(guideText.textContent);
    utterance.lang = "he-IL";
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  }
});

selectMode(selectedMode);
