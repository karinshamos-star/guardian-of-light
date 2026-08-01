from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

class AIReadingUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class AIReadingProvider:
    api_key: str | None = None
    model: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, *, question: str, question_dna: Any, spread: Any, draw: Any) -> dict[str, Any]:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise AIReadingUnavailable("OPENAI_API_KEY is not configured.")

        model = self.model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AIReadingUnavailable("OpenAI SDK is not installed.") from exc

        client = OpenAI(api_key=key, timeout=30.0, max_retries=1)

        cards = [
            {
                "position": position.label,
                "position_purpose": position.purpose,
                "card": card.name_he,
                "orientation": card.orientation,
            }
            for position, card in zip(spread.positions, draw.cards)
        ]

        instructions = """
את/ה שומר האור — מנחה רפלקטיבי, חם, צלול ולא נבואי.

כללים:
1. הקלפים הם סמלים ונקודות מבט, לא ידיעה של העתיד.
2. אין להחליט במקום המשתמשת.
3. אין לתת הוראות רפואיות, משפטיות או פיננסיות.
4. אין לטעון לידיעה על מחשבות של אדם שלישי.
5. אין להפחיד, לייצר תלות או להציג ודאות.
6. כתוב בעברית טבעית, רגישה ולא דרמטית.
7. סיים בשאלת התבוננות אחת ובפעולה קטנה ובטוחה.
8. אל תוסיף פרטי חיים או קלפים שלא נמסרו.
9. החזר JSON תקין בלבד, ללא Markdown.

מבנה:
{
  "central_message": "2-4 משפטים",
  "sections": [
    {
      "position": "שם המיקום כפי שנמסר",
      "card": "שם הקלף כפי שנמסר",
      "text": "2-3 משפטים רפלקטיביים"
    }
  ],
  "reflection_question": "שאלה אחת",
  "grounded_action": "פעולה אחת",
  "closing": "משפט שמחזיר את הסוכנות למשתמשת"
}
"""

        payload = {
            "question": question,
            "question_dna": {
                "domain": question_dna.domain.value,
                "core_need": question_dna.core_need.value,
                "emotions": [emotion.value for emotion in question_dna.emotional_state],
                "complexity": question_dna.complexity,
                "question_style": question_dna.question_style.value,
            },
            "cards": cards,
        }

        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=json.dumps(payload, ensure_ascii=False),
            )
            parsed = json.loads(response.output_text)
        except Exception as exc:
            raise AIReadingUnavailable("AI reading generation failed.") from exc

        self._validate(parsed, expected_cards=len(cards))
        return parsed

    @staticmethod
    def _validate(value: Any, *, expected_cards: int) -> None:
        if not isinstance(value, dict):
            raise AIReadingUnavailable("AI response is not an object.")

        for field in ("central_message", "reflection_question", "grounded_action", "closing"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise AIReadingUnavailable(f"Missing or invalid field: {field}")

        sections = value.get("sections")
        if not isinstance(sections, list) or len(sections) != expected_cards:
            raise AIReadingUnavailable("Invalid sections list.")

        for section in sections:
            if not isinstance(section, dict):
                raise AIReadingUnavailable("Invalid section.")
            for field in ("position", "card", "text"):
                if not isinstance(section.get(field), str) or not section[field].strip():
                    raise AIReadingUnavailable(f"Invalid section field: {field}")
