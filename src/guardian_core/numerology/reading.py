"""Builds the client-safe ReadingResult for a numerology encounter.

PLACEHOLDER CONTENT: every Hebrew string in NUMBER_TEXT and the section
templates below was written for the interactive demo so the flow can be tested
end to end. It is general-tradition wording, not drawn from any registered
source, and is meant to be replaced by authored knowledge entities.
"""
from __future__ import annotations

from guardian_core.numerology.engine import NumerologyProfile
from guardian_core.reading.models import ReadingResult, ReadingSection

# number -> (title, essence, invitation)
NUMBER_TEXT: dict[int, tuple[str, str, str]] = {
    1: ("ההתחלה", "מספר של יוזמה, עצמאות ופתיחת דרך חדשה.",
        "אפשר לשאול איפה את מוכנה להיות הראשונה, ומתי העצמאות הופכת לבדידות."),
    2: ("השותפות", "מספר של הקשבה, רגישות ושיתוף פעולה.",
        "אפשר לשאול למי את מקשיבה, והאם גם הקול שלך נשמע בתוך הקשר."),
    3: ("הביטוי", "מספר של יצירה, תקשורת ושמחה.",
        "אפשר לשאול מה מבקש לצאת החוצה ועדיין לא קיבל מילים."),
    4: ("היסוד", "מספר של סדר, התמדה ובנייה יציבה.",
        "אפשר לשאול מה כבר בנוי היטב אצלך, ואיפה היציבות הפכה לנוקשות."),
    5: ("התנועה", "מספר של שינוי, סקרנות וחופש.",
        "אפשר לשאול איזו תנועה מזמינה אותך כעת, ומה צריך להישאר יציב בזמן שאת זזה."),
    6: ("הטיפוח", "מספר של אחריות, אהבה והרמוניה סביב הבית והקרובים.",
        "אפשר לשאול כמה מהטיפול שאת נותנת חוזר אלייך."),
    7: ("העומק", "מספר של התבוננות, חקר ופנימיות.",
        "אפשר לשאול איזו שאלה מחכה לשקט שלך, ומתי העומק הופך לריחוק."),
    8: ("המימוש", "מספר של כוח, הישג ויחסים עם כסף ושליטה.",
        "אפשר לשאול מה המשמעות שלך להצלחה, ומה היא דורשת ממך לשלם."),
    9: ("ההשלמה", "מספר של סיום, חמלה ושחרור.",
        "אפשר לשאול מה הגיע לסיומו, ומה עוד נשאר לשחרר כדי לפנות מקום."),
}

_HARMONY_TEXT = {
    "individual": "המספרים שלך נוטים לעצמאות ולחשיבה עצמית. הם עובדים טוב בשקט, ולפעמים שוכחים לשתף.",
    "framework": "המספרים שלך נוטים לסדר, לקשרים ולמסגרת. הם מחפשים איזון בתוך הסביבה הקרובה.",
    "universal": "המספרים שלך נוטים לפתיחות ולזרימה. הם נהנים מקשר, יצירה ונתינה.",
}


def _text(number: int) -> tuple[str, str, str]:
    return NUMBER_TEXT.get(number, ("האפס", "מקום של בחירה חופשית ופוטנציאל פתוח.", "אפשר לשאול מה את בוחרת."))


def _section(position: str, number: int, lead: str) -> ReadingSection:
    title, essence, invitation = _text(number)
    return ReadingSection(
        position=position,
        card=f"{number} · {title}",
        text=f"{lead} {essence} {invitation}",
    )


def build_numerology_reading(profile: NumerologyProfile) -> ReadingResult:
    sections = [
        _section("שביל הגורל", profile.destiny_path,
                 "שביל הגורל בנוי מתאריך הלידה, והוא מתאר כיוון ולא גזירה."),
        _section("מספר השם", profile.full_name_number,
                 "הגימטריה של השם המלא מציעה אופי של ביטוי בעולם."),
        _section("מספר הכוח", profile.power_number,
                 "מספר הכוח משלב שם ושביל גורל, ומצביע על מקום שבו הכול מתחבר."),
        _section("השנה האישית", profile.cycle.year_classic,
                 "השנה האישית מזמינה להתבונן בנושא שמתעורר בשנה הזו."),
    ]
    for harmony in profile.harmonies:
        sections.append(ReadingSection(position="הרמוניה", card=harmony_title(harmony), text=_HARMONY_TEXT[harmony]))

    return ReadingResult(
        status="completed",
        central_message="המספרים הם שפה להתבוננות. הם מציעים כיוונים, והבחירה נשארת שלך.",
        sections=sections,
        reflection_question="איזה מהמספרים האלה מרגיש לך מוכר, ואיזה מפתיע אותך?",
        grounded_action="בחרי מספר אחד מהקריאה, ורשמי משפט אחד על איך הוא מופיע בחיים שלך השבוע.",
        closing="המספרים מציעים תבנית. המשמעות נוצרת כשאת פוגשת אותם בחיים שלך.",
    )


def harmony_title(harmony: str) -> str:
    return {"individual": "הרמוניית האינדיבידואל", "framework": "הרמוניית המסגרת", "universal": "הרמוניית האוניברסליות"}[harmony]
