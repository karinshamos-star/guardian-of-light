from __future__ import annotations

import re
from collections import defaultdict

from .models import *

DOMAIN_TERMS = {
    Domain.RELATIONSHIP: ("זוגיות", "בן זוג", "בת זוג", "אהבה", "קשר", "פרידה", "דייט", "אליי", "בינינו", "מרגיש כלפיי", "מרגישה כלפיי"),
    Domain.CAREER: ("עבודה", "קריירה", "מנהל", "מנהלת", "תפקיד", "משרד", "מקצוע", "משרה", "קידום", "ראיון"),
    Domain.FAMILY: ("משפחה", "אמא", "אבא", "הורים", "ילד", "ילדה", "אח", "אחות"),
    Domain.FINANCE_REFLECTION: ("כסף", "חוב", "השקעה", "מניה", "תקציב", "משכורת", "הלוואה"),
    Domain.HEALTH_REFLECTION: ("בריאות", "תרופה", "טיפול", "החלמה", "מחלה", "רופא", "רופאה"),
    Domain.PERSONAL_GROWTH: ("גבולות", "ביטחון עצמי", "לשחרר", "הרגל", "זהות", "עצמי", "תקועה", "תקוע"),
    Domain.SPIRITUAL_GROWTH: ("רוחני", "אינטואיציה", "משמעות", "נשמה", "מדיטציה"),
    Domain.CREATIVITY: ("יצירה", "כתיבה", "אמנות", "מוזיקה", "השראה"),
    Domain.DAILY_GUIDANCE: ("מסר להיום", "הכוונה יומית", "קלף יומי"),
}

EMOTION_TERMS = {
    EmotionalState.UNCERTAINTY: ("מתלבט", "מתלבטת", "לא בטוח", "לא בטוחה", "לא יודעת", "לא יודע"),
    EmotionalState.FEAR: ("פחד", "מפחד", "מפחדת", "חושש", "חוששת", "חרדה"),
    EmotionalState.HOPE: ("מקווה", "תקווה", "אופטימי", "אופטימית"),
    EmotionalState.SADNESS: ("עצוב", "עצובה", "עצב", "כואב לי"),
    EmotionalState.GRIEF: ("אבל", "אובדן", "מתגעגע", "מתגעגעת"),
    EmotionalState.ANGER: ("כועס", "כועסת", "זעם"),
    EmotionalState.FRUSTRATION: ("מתוסכל", "מתוסכלת", "נמאס לי"),
    EmotionalState.CONFUSION: ("מבולבל", "מבולבלת", "לא מבינה", "לא מבין"),
    EmotionalState.CURIOSITY: ("מסקרן", "סקרן", "סקרנית"),
    EmotionalState.LONGING: ("כמיהה", "משתוקק", "משתוקקת", "מתגעגע"),
    EmotionalState.GUILT: ("אשמה", "אשם", "רגשות אשם"),
    EmotionalState.SHAME: ("בושה", "מתבייש", "מתביישת"),
    EmotionalState.RELIEF: ("הקלה", "הוקל לי"),
    EmotionalState.CALM: ("רגועה", "רגוע", "שלווה"),
    EmotionalState.EXCITEMENT: ("מתרגש", "מתרגשת", "נרגש", "נרגשת"),
    EmotionalState.OVERWHELM: ("מוצף", "מוצפת", "עמוס לי", "יותר מדי"),
}

CHOICE_TERMS = ("כדאי", "לבחור", "להישאר", "לעזוב", " או ", "להחליט", "לעבור")
PREDICTIVE_TERMS = ("האם הוא", "האם היא", "מה יקרה", "מתי", "יחזור", "תחזור", "יקרה")
ADVICE_TERMS = ("מה לעשות", "מה כדאי", "איך כדאי", "האם להפסיק", "האם לעזוב")
HEALING_TERMS = ("לשחרר", "החלמה", "כאב", "פגיעה", "אבל", "להתגבר")
COURAGE_TERMS = ("גבולות", "אומץ", "מפחד", "מפחדת", "חושש", "חוששת")


def normalize(text: str) -> str:
    text = text.replace("־", "-")
    return re.sub(r"\s+", " ", text.strip())


def detect_safety(text: str) -> list[SafetyFlag]:
    flags: list[SafetyFlag] = []
    if any(x in text for x in ("לא רוצה לחיות", "להרוג את עצמי", "להתאבד", "למות")):
        flags.append(SafetyFlag.SELF_HARM_OR_SUICIDE)
    if any(x in text for x in ("מכה אותי", "מאיים עליי", "כופה עליי", "אלימות", "התעללות")):
        flags.append(SafetyFlag.ABUSE_OR_COERCION)
    if any(x in text for x in ("בסכנה עכשיו", "עומד לפגוע בי", "נשק")):
        flags.append(SafetyFlag.IMMEDIATE_DANGER)
    if any(x in text for x in ("להפסיק לקחת את התרופה", "איזו תרופה", "לאבחן אותי")):
        flags.append(SafetyFlag.MEDICAL_HIGH_STAKES)
    if any(x in text for x in ("באיזו מניה", "להשקיע את כל", "השקעה בטוחה")):
        flags.append(SafetyFlag.FINANCIAL_HIGH_STAKES)
    if any(x in text for x in ("מה הוא באמת מרגיש", "מה היא באמת מרגישה", "מה הוא מסתיר", "מה היא מסתירה")):
        flags.append(SafetyFlag.THIRD_PARTY_MIND_READING)
    if any(x in text for x in PREDICTIVE_TERMS):
        flags.append(SafetyFlag.DETERMINISTIC_PREDICTION_REQUEST)
    return list(dict.fromkeys(flags))


def style(text: str) -> QuestionStyle:
    if any(x in text for x in PREDICTIVE_TERMS):
        return QuestionStyle.PREDICTIVE
    if any(x in text for x in ADVICE_TERMS):
        return QuestionStyle.ADVICE_SEEKING
    if text.startswith("האם ") or " או " in text:
        return QuestionStyle.BINARY
    if text.startswith(("מה ", "איך ", "למה ", "איזה ", "אילו ")):
        return QuestionStyle.OPEN
    return QuestionStyle.EXPLORATORY


def score_domains(text: str, context: str):
    scores: dict[Domain, float] = defaultdict(float)
    evidence: list[Evidence] = []
    for domain, terms in DOMAIN_TERMS.items():
        for term in terms:
            if term in text:
                scores[domain] += 0.6
                evidence.append(Evidence(field="domain", value=domain.value, source="question", excerpt=term, weight=.8, rule_id="INT-001"))
            elif term in context:
                scores[domain] += 0.6
                evidence.append(Evidence(field="domain", value=domain.value, source="conversation_context", excerpt=term, weight=.55, rule_id="INT-006"))
    if any(x in text for x in CHOICE_TERMS):
        scores[Domain.DECISION] += .6
        evidence.append(Evidence(field="domain", value="decision", source="structure", excerpt="explicit choice framing", weight=.85, rule_id="INT-002"))
    return {k: min(v, 1) for k, v in scores.items()}, evidence


def select_domains(scores: dict[Domain, float]):
    concrete = sorted(((d, v) for d, v in scores.items() if d is not Domain.DECISION), key=lambda x: x[1], reverse=True)
    decision_score = scores.get(Domain.DECISION, 0)
    if concrete and concrete[0][1] >= .55:
        secondary = [d for d, v in concrete[1:] if v >= .45]
        if decision_score >= .45:
            secondary.append(Domain.DECISION)
        return concrete[0][0], secondary[:2]
    if decision_score >= .55:
        return Domain.DECISION, []
    return Domain.OTHER, []


def select_need(text: str, question_style: QuestionStyle, domain: Domain):
    secondary: list[CoreNeed] = []
    if any(x in text for x in CHOICE_TERMS) or question_style in {QuestionStyle.BINARY, QuestionStyle.ADVICE_SEEKING}:
        primary = CoreNeed.DECISION_SUPPORT
        if any(x in text for x in COURAGE_TERMS):
            secondary.append(CoreNeed.COURAGE)
    elif any(x in text for x in HEALING_TERMS):
        primary = CoreNeed.HEALING
    elif any(x in text for x in ("לחזור", "יחזור", "תחזור")):
        primary = CoreNeed.REASSURANCE
    elif any(x in text for x in COURAGE_TERMS):
        primary = CoreNeed.COURAGE
    elif domain is Domain.DAILY_GUIDANCE:
        primary = CoreNeed.EXPLORATION
    elif question_style is QuestionStyle.OPEN:
        primary = CoreNeed.CLARITY
    else:
        primary = CoreNeed.PERSPECTIVE
    return primary, secondary[:2], [Evidence(field="core_need", value=primary.value, source="structure", excerpt=question_style.value, weight=.75, rule_id="INT-002")]


def emotions(text: str):
    found: list[tuple[EmotionalState, float, str]] = []
    for emotion, terms in EMOTION_TERMS.items():
        matches = [term for term in terms if term in text]
        if matches:
            score = min(.72 + .08 * len(matches), .96)
            found.append((emotion, score, matches[0]))
    found.sort(key=lambda item: item[1], reverse=True)
    values = [emotion for emotion, _, _ in found[:3]]
    evidence = [Evidence(field="emotional_state", value=emotion.value, source="question", excerpt=term, weight=score, rule_id="INT-005") for emotion, score, term in found[:3]]
    return values, evidence


def confidence(scores: dict[Domain, float], domain: Domain, evidence_count: int, has_context: bool) -> float:
    if domain is Domain.OTHER:
        return .42
    values = sorted(scores.values(), reverse=True)
    top = values[0] if values else 0
    runner = values[1] if len(values) > 1 else 0
    value = top * .5 + max(top - runner, 0) * .2 + min(evidence_count / 4, 1) * .2 + (.1 if has_context else .05)
    return round(min(max(value, 0), .97), 2)


def clarification_for(text: str, domain: Domain, confidence_value: float, safety_flags: list[SafetyFlag]):
    crisis = {SafetyFlag.SELF_HARM_OR_SUICIDE, SafetyFlag.ABUSE_OR_COERCION, SafetyFlag.IMMEDIATE_DANGER}
    required = (domain is Domain.OTHER or (domain is Domain.DECISION and confidence_value < .65)) and not crisis.intersection(safety_flags)
    if not required:
        return False, None, None
    if "לעזוב" in text:
        question = "כשאת אומרת לעזוב, למה את מתכוונת — קשר, עבודה, מקום מגורים או משהו אחר?"
    elif len(text.split()) <= 4:
        question = "אפשר לכתוב עוד משפט אחד על המצב ומה היית רוצה להבין ממנו?"
    else:
        question = "מהו התחום המרכזי של השאלה, ומה הכי חשוב לך להבין כרגע?"
    reason = "domain_not_resolved" if domain is Domain.OTHER else "classification_confidence_below_threshold"
    return True, reason, question


def classify_intent(req: IntentRequest) -> QuestionDNA:
    text = normalize(req.question)
    context = normalize(" ".join(x.content for x in req.conversation_context))
    safety_flags = detect_safety(text)
    question_style = style(text)
    scores, domain_evidence = score_domains(text, context)
    domain, secondary_domains = select_domains(scores)
    core_need, secondary_needs, need_evidence = select_need(text, question_style, domain)
    emotional_state, emotion_evidence = emotions(f"{text} {context}")
    evidence = domain_evidence + need_evidence + emotion_evidence
    confidence_value = confidence(scores, domain, len(evidence), bool(context))
    clarification_required, clarification_reason, clarification_question = clarification_for(text, domain, confidence_value, safety_flags)

    if any(x in text for x in ("כבר החלטתי", "אני עומדת", "אני עומד", "מחר אני")):
        readiness = 4
    elif any(x in text for x in ("מתלבט", "מתלבטת", "שוקל", "שוקלת")):
        readiness = 3
    elif question_style is QuestionStyle.PREDICTIVE:
        readiness = 1
    else:
        readiness = 2

    complexity = "high" if len(secondary_domains) >= 2 or len(emotional_state) >= 3 else ("medium" if secondary_domains or len(emotional_state) >= 2 or any(x in text for x in CHOICE_TERMS) else "low")

    return QuestionDNA(
        surface_question=req.question,
        normalized_question=text,
        domain=domain,
        secondary_domains=secondary_domains,
        core_need=core_need,
        secondary_needs=secondary_needs,
        emotional_state=emotional_state,
        readiness=readiness,
        complexity=complexity,
        question_style=question_style,
        clarification_required=clarification_required,
        clarification_reason=clarification_reason,
        clarification_question=clarification_question,
        confidence=confidence_value,
        safety_flags=safety_flags,
        evidence=evidence,
    )
