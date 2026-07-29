from __future__ import annotations

CARD_THEMES = {
    "major-00": "פתיחות להתחלה חדשה, לצד צורך בצעד מודע",
    "major-01": "יכולת להשתמש במשאבים שכבר נמצאים בידייך",
    "major-02": "הקשבה למה שעדיין לא קיבל מילים",
    "major-03": "טיפוח, יצירה וצמיחה הדרגתית",
    "major-04": "מבנה, גבולות ואחריות",
    "major-05": "בחינה של ערכים, מסגרות ואמונות",
    "major-06": "בחירה שמבקשת הלימה בין לב לערכים",
    "major-07": "כיוון, נחישות ותנועה",
    "major-08": "עוצמה שקטה ואומץ שאינו כוחני",
    "major-09": "צורך במרחב פנימי ובהאטה",
    "major-10": "שינוי מחזורי ויכולת להגיב בגמישות",
    "major-11": "איזון בין אמת, אחריות והשלכות",
    "major-12": "השהיה שמאפשרת נקודת מבט חדשה",
    "major-13": "סיום שמפנה מקום לשינוי",
    "major-14": "איזון, סבלנות ושילוב בין קצוות",
    "major-15": "זיהוי של דפוס כובל או תלות",
    "major-16": "מבנה שמתערער כדי לחשוף אמת",
    "major-17": "תקווה, ריפוי וחיבור מחדש לכיוון",
    "major-18": "אי־ודאות, אינטואיציה וצורך לא למהר למסקנה",
    "major-19": "בהירות, חיות וביטחון",
    "major-20": "הכרה, התעוררות וקבלת אחריות",
    "major-21": "השלמה, אינטגרציה ומעבר לשלב הבא",
}

SUIT_THEMES = {
    "wands": "יוזמה, אנרגיה ורצון לפעול",
    "cups": "רגש, קשרים ויכולת לקבל",
    "swords": "מחשבה, אמת ומתח פנימי",
    "pentacles": "יציבות, גוף, זמן ומשאבים",
}


def _theme(card_id: str) -> str:
    if card_id in CARD_THEMES:
        return CARD_THEMES[card_id]
    suit = card_id.split("-", 1)[0]
    return SUIT_THEMES.get(suit, "התבוננות סמלית במצב")


def create_reading(question_dna, spread, draw):
    sections = []
    for position, card in zip(spread.positions, draw.cards):
        orientation_note = "בצורה הפוכה, ולכן הדגש עשוי להיות פנימי או מעוכב" if card.orientation == "reversed" else "בצורה ישרה"
        sections.append({
            "position": position.label,
            "card": card.name_he,
            "text": f"{card.name_he} מופיע {orientation_note}. הוא מציע להתבונן ב{_theme(card.card_id)}."
        })

    central = (
        "הקריאה אינה מחליטה במקומך. היא מציעה לראות את המצב דרך כמה נקודות מבט, "
        "ולבדוק איזו מהן מרגישה מדויקת ורלוונטית לחייך."
    )

    if question_dna.core_need.value == "decision_support":
        action = "כתבי שתי אפשרויות מעשיות, ולצד כל אחת צייני מה היא דורשת ממך ומה היא מאפשרת לך."
        reflection = "איזו בחירה מקרבת אותך יותר לערכים שלך, גם אם היא אינה הקלה ביותר?"
    elif question_dna.core_need.value == "healing":
        action = "בחרי פעולה עדינה אחת שתתמוך בך היום, בלי לדרוש מעצמך לפתור הכול."
        reflection = "מה בתוכך מבקש כרגע הכרה לפני שינוי?"
    else:
        action = "בחרי משפט אחד מהקריאה ורשמי כיצד הוא פוגש את היום שלך."
        reflection = "איזה חלק בקריאה מרגיש חי או משמעותי עבורך עכשיו?"

    return {
        "central_message": central,
        "sections": sections,
        "reflection_question": reflection,
        "grounded_action": action,
        "closing": "הקלפים מציעים שפה לסיפור שלך — הבחירה והמשמעות נשארות בידייך."
    }
