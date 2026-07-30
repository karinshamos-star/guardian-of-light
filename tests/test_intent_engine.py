from guardian_core.intent import IntentRequest,classify_intent
from guardian_core.intent.models import *

def c(q,context=None): return classify_intent(IntentRequest(question=q,conversation_context=context or [],language="he"))
def test_career_decision():
 r=c("אני מתלבט אם לעבור עבודה"); assert r.domain is Domain.CAREER; assert Domain.DECISION in r.secondary_domains; assert r.core_need is CoreNeed.DECISION_SUPPORT; assert EmotionalState.UNCERTAINTY in r.emotional_state; assert r.complexity=="medium"; assert not r.clarification_required
def test_predictive_relationship():
 r=c("האם הוא יחזור אליי?"); assert r.domain is Domain.RELATIONSHIP; assert r.question_style is QuestionStyle.PREDICTIVE; assert SafetyFlag.DETERMINISTIC_PREDICTION_REQUEST in r.safety_flags
def test_ambiguous_departure():
 r=c("אני רוצה לעזוב"); assert r.confidence<.65 and r.clarification_required and r.clarification_question
def test_context_resolution():
 r=c("אני רוצה לעזוב",[{"role":"user","content":"אני שחוק מאוד במקום העבודה ובמשרד"}]); assert r.domain is Domain.CAREER; assert Domain.DECISION in r.secondary_domains; assert any(e.source=="conversation_context" for e in r.evidence)
def test_daily_guidance():
 r=c("איזה מסר להיום יכול לעזור לי?"); assert r.domain is Domain.DAILY_GUIDANCE; assert r.core_need is CoreNeed.EXPLORATION
def test_health_reflection():
 r=c("איך אני יכולה להתמודד רגשית עם תקופת ההחלמה?"); assert r.domain is Domain.HEALTH_REFLECTION; assert r.core_need is CoreNeed.HEALING; assert SafetyFlag.MEDICAL_HIGH_STAKES not in r.safety_flags
def test_medical_instruction():
 r=c("האם להפסיק לקחת את התרופה?"); assert r.domain is Domain.HEALTH_REFLECTION; assert SafetyFlag.MEDICAL_HIGH_STAKES in r.safety_flags
def test_mind_reading():
 r=c("מה הוא באמת מרגיש כלפיי אבל מסתיר?"); assert r.domain is Domain.RELATIONSHIP; assert SafetyFlag.THIRD_PARTY_MIND_READING in r.safety_flags
def test_financial_high_stakes():
 r=c("באיזו מניה כדאי לי להשקיע את כל הכסף שלי?"); assert r.domain is Domain.FINANCE_REFLECTION; assert r.core_need is CoreNeed.DECISION_SUPPORT; assert SafetyFlag.FINANCIAL_HIGH_STAKES in r.safety_flags
def test_personal_growth():
 r=c("מה יעזור לי להציב גבולות בלי להרגיש אשמה?"); assert r.domain is Domain.PERSONAL_GROWTH; assert EmotionalState.GUILT in r.emotional_state; assert r.question_style is QuestionStyle.OPEN
def test_crisis():
 r=c("אני לא רוצה לחיות יותר"); assert SafetyFlag.SELF_HARM_OR_SUICIDE in r.safety_flags; assert not r.clarification_required

def test_multiple_emotions_and_secondary_need():
 r=c("אני מתלבטת אם לעבור עבודה כי אני מפחדת לטעות אבל גם מקווה לשינוי")
 assert r.domain is Domain.CAREER
 assert EmotionalState.UNCERTAINTY in r.emotional_state
 assert EmotionalState.FEAR in r.emotional_state
 assert EmotionalState.HOPE in r.emotional_state
 assert CoreNeed.COURAGE in r.secondary_needs
 assert r.complexity=="high"

def test_clarification_is_specific():
 r=c("אני רוצה לעזוב")
 assert r.clarification_required
 assert "קשר" in r.clarification_question
 assert "עבודה" in r.clarification_question

def test_readiness_detects_committed_action():
 r=c("כבר החלטתי לעבור עבודה ואני רוצה להבין איך לעשות את זה נכון")
 assert r.readiness==4
