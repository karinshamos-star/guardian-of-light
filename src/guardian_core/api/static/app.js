const submit = document.getElementById("submit");
const question = document.getElementById("question");
const error = document.getElementById("error");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const clarification = document.getElementById("clarification");

submit.addEventListener("click", async () => {
  const value = question.value.trim();
  error.hidden = true;
  result.hidden = true;
  clarification.hidden = true;

  if (!value) {
    error.textContent = "כתבי שאלה קצרה כדי להתחיל.";
    error.hidden = false;
    return;
  }

  loading.hidden = false;
  submit.disabled = true;

  try {
    const response = await fetch("/v1/readings", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: value, conversation_context: [], language: "he"})
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "הקריאה לא הושלמה.");

    if (data.status === "clarification_required") {
      document.getElementById("clarificationText").textContent = data.clarification_question;
      clarification.hidden = false;
      return;
    }

    document.getElementById("central").textContent = data.reading.central_message;
    document.getElementById("reflection").textContent = data.reading.reflection_question;
    document.getElementById("action").textContent = data.reading.grounded_action;
    document.getElementById("closing").textContent = data.reading.closing;

    const cards = document.getElementById("cards");
    cards.innerHTML = "";
    data.reading.sections.forEach((section, index) => {
      const drawn = data.draw.cards[index];
      const article = document.createElement("article");
      article.className = "card";
      article.innerHTML = `
        <div class="position">${section.position}</div>
        <h3>${section.card}</h3>
        <div class="orientation">${drawn.orientation === "reversed" ? "הפוך" : "ישר"}</div>
        <p>${section.text}</p>`;
      cards.appendChild(article);
    });

    result.hidden = false;
    result.scrollIntoView({behavior: "smooth"});
  } catch (e) {
    error.textContent = e.message;
    error.hidden = false;
  } finally {
    loading.hidden = true;
    submit.disabled = false;
  }
});
