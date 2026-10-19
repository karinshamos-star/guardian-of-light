"use strict";

const $ = (s) => document.querySelector(s);
const sceneLabel = $("#sceneLabel");
const luminaMessage = $("#luminaMessage");
const loading = $("#loading");
const error = $("#error");
const interactionEl = $("#interaction");
const readingContent = $("#readingContent");

let sessionId = null;
let autoAdvanceTimer = null;

// Maps an ExperienceCommand's interaction.type to the WorldAction it must send back.
// The client never branches on scene/state names -- only on this small, stable set
// of interaction types, so it stays a generic renderer of whatever the server sends.
function actionFor(interaction) {
  switch (interaction.type) {
    case "continue":
      return { action: interaction.input_key, buildPayload: () => ({}) };
    case "ask_question":
      return { action: "ask_question", buildPayload: (value) => ({ [interaction.input_key || "question"]: value }) };
    case "choose_option":
      return { action: "choose_avatar", buildPayload: (value) => ({ avatar_id: value }) };
    case "talk_to_guide":
      return { action: "talk_to_guide", buildPayload: () => ({}) };
    case "follow_guide":
      return { action: "follow_guide", buildPayload: () => ({}) };
    default:
      return null;
  }
}

function renderInteraction(command) {
  clearTimeout(autoAdvanceTimer);
  interactionEl.innerHTML = "";
  const interaction = command.interaction;
  const resolved = actionFor(interaction);
  if (!resolved) return;

  if (interaction.type === "choose_option") {
    const wrap = document.createElement("div");
    wrap.className = "options";
    (interaction.options || []).forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = option.label;
      button.addEventListener("click", () => sendAction(resolved.action, resolved.buildPayload(option.id)));
      wrap.appendChild(button);
    });
    interactionEl.appendChild(wrap);
    return;
  }

  if (interaction.type === "ask_question") {
    const form = document.createElement("form");
    form.className = "question";
    form.innerHTML = `
      <label class="sr-only" for="questionInput">${interaction.prompt || ""}</label>
      <input id="questionInput" autocomplete="off" placeholder="${interaction.prompt || ""}">
      <button type="submit">לשלוח</button>`;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const value = form.querySelector("#questionInput").value.trim();
      if (!value) return;
      sendAction(resolved.action, resolved.buildPayload(value));
    });
    interactionEl.appendChild(form);
    return;
  }

  // "continue", "talk_to_guide", "follow_guide" all render as a single button.
  const button = document.createElement("button");
  button.type = "button";
  button.className = "primary";
  button.textContent = interaction.prompt || "המשך";
  button.addEventListener("click", () => sendAction(resolved.action, resolved.buildPayload()));
  interactionEl.appendChild(button);

  // Passthrough step: advance on its own unless the user already acted (sendAction clears the timer).
  if (interaction.auto_advance_seconds) {
    autoAdvanceTimer = setTimeout(
      () => sendAction(resolved.action, resolved.buildPayload()),
      interaction.auto_advance_seconds * 1000,
    );
  }
}

function renderReading(command) {
  const result = command.payload && command.payload.reading;
  if (!result || result.status !== "completed") {
    readingContent.hidden = true;
    return;
  }

  const cardsRoot = $("#cards");
  cardsRoot.innerHTML = "";
  (result.sections || []).forEach((section, index) => {
    const article = document.createElement("article");
    article.className = "card";
    article.style.animationDelay = `${index * 160}ms`;
    article.innerHTML = `<h3>${section.card}</h3><p>${section.text}</p>`;
    cardsRoot.appendChild(article);
  });
  $("#action").textContent = result.grounded_action || "";
  $("#reflection").textContent = result.reflection_question || "";
  $("#closing").textContent = result.closing || "";
  readingContent.hidden = false;
}

function renderCommand(command) {
  luminaMessage.textContent = command.guide.dialogue || "";
  sceneLabel.textContent = command.world ? command.world.guide_activity || "" : "";
  renderReading(command);
  renderInteraction(command);
}

async function sendAction(action, payload) {
  clearTimeout(autoAdvanceTimer);
  loading.hidden = false;
  error.hidden = true;
  interactionEl.innerHTML = "";
  try {
    const response = await fetch(`/v1/world/sessions/${sessionId}/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, payload }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "הפעולה לא הושלמה.");
    renderCommand(data.command);
  } catch (e) {
    error.textContent = e.message;
    error.hidden = false;
  } finally {
    loading.hidden = true;
  }
}

async function start() {
  loading.hidden = false;
  try {
    const response = await fetch("/v1/world/sessions", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error("לא הצלחתי לפתוח את השער.");
    sessionId = data.session.session_id;
    renderCommand(data.command);
  } catch (e) {
    error.textContent = e.message;
    error.hidden = false;
  } finally {
    loading.hidden = true;
  }
}

start();
