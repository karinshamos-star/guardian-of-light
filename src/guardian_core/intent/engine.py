from __future__ import annotations
import re
from collections import defaultdict
from .models import *

DOMAIN_TERMS={
Domain.RELATIONSHIP:("זוגיות","בן זוג","בת זוג","אהבה","קשר","אליי","בינינו","מרגיש כלפיי","מרגישה כלפיי"),
Domain.CAREER:("עבודה","קריירה","מנהל","תפקיד","משרד","מקצוע","משרה"),
Domain.FAMILY:("משפחה","אמא","אבא","הורים","ילד","ילדה","אח","אחות"),
Domain.FINANCE_REFLECTION:("כסף","חוב","השקעה","מניה","תקציב","משכורת"),
Domain.HEALTH_REFLECTION:("בריאות","תרופה","טיפול","החלמה","מחלה","רופא"),
Domain.PERSONAL_GROWTH:("גבולות","ביטחון עצמי","לשחרר","הרגל","זהות","עצמי"),
Domain.SPIRITUAL_GROWTH:("רוחני","אינטואיציה","משמעות","נשמה","מדיטציה"),
Domain.CREATIVITY:("יצירה","כתיבה","אמנות","מוזיקה","השראה"),
Domain.DAILY_GUIDANCE:("מסר להיום","הכוונה יומית")
}
EMOTION_TERMS={EmotionalState.UNCERTAINTY:("מתלבט","מתלבטת","לא בטוח","לא בטוחה"), EmotionalState.FEAR:("פחד","מפחד","מפחדת","חושש","חוששת"), EmotionalState.GUILT:("אשמה","אשם"), EmotionalState.CONFUSION:("מבולבל","מבולבלת"), EmotionalState.SADNESS:("עצוב","עצובה"), EmotionalState.OVERWHELM:("מוצף","מוצפת")}
CHOICE_TERMS=("כדאי","לבחור","להישאר","לעזוב"," או ","להחליט","לעבור")
PREDICTIVE_TERMS=("האם הוא","האם היא","מה יקרה","מתי","יחזור","תחזור","יקרה")
ADVICE_TERMS=("מה לעשות","מה כדאי","איך כדאי","האם להפסיק","האם לעזוב")

def normalize(t): return re.sub(r"\s+"," ",t.strip())
def detect_safety(t):
    f=[]
    if any(x in t for x in ("לא רוצה לחיות","להרוג את עצמי","להתאבד","למות")): f.append(SafetyFlag.SELF_HARM_OR_SUICIDE)
    if any(x in t for x in ("מכה אותי","מאיים עליי","כופה עליי","אלימות","התעללות")): f.append(SafetyFlag.ABUSE_OR_COERCION)
    if any(x in t for x in ("בסכנה עכשיו","עומד לפגוע בי","נשק")): f.append(SafetyFlag.IMMEDIATE_DANGER)
    if any(x in t for x in ("להפסיק לקחת את התרופה","איזו תרופה","לאבחן אותי")): f.append(SafetyFlag.MEDICAL_HIGH_STAKES)
    if any(x in t for x in ("באיזו מניה","להשקיע את כל","השקעה בטוחה")): f.append(SafetyFlag.FINANCIAL_HIGH_STAKES)
    if any(x in t for x in ("מה הוא באמת מרגיש","מה היא באמת מרגישה","מה הוא מסתיר","מה היא מסתירה")): f.append(SafetyFlag.THIRD_PARTY_MIND_READING)
    if any(x in t for x in PREDICTIVE_TERMS): f.append(SafetyFlag.DETERMINISTIC_PREDICTION_REQUEST)
    return list(dict.fromkeys(f))
def style(t):
    if any(x in t for x in PREDICTIVE_TERMS): return QuestionStyle.PREDICTIVE
    if any(x in t for x in ADVICE_TERMS): return QuestionStyle.ADVICE_SEEKING
    if t.startswith("האם ") or " או " in t: return QuestionStyle.BINARY
    if t.startswith(("מה ","איך ","למה ","איזה ","אילו ")): return QuestionStyle.OPEN
    return QuestionStyle.EXPLORATORY
def score_domains(t,c):
    s=defaultdict(float); e=[]
    for d,terms in DOMAIN_TERMS.items():
        for term in terms:
            if term in t:
                s[d]+=0.6; e.append(Evidence(field="domain",value=d.value,source="question",excerpt=term,weight=.8,rule_id="INT-001"))
            elif term in c:
                s[d]+=0.6; e.append(Evidence(field="domain",value=d.value,source="conversation_context",excerpt=term,weight=.55,rule_id="INT-006"))
    if any(x in t for x in CHOICE_TERMS):
        s[Domain.DECISION]+=.6; e.append(Evidence(field="domain",value="decision",source="structure",excerpt="explicit choice framing",weight=.85,rule_id="INT-002"))
    return {k:min(v,1) for k,v in s.items()},e
def select_domains(s):
    concrete=sorted([(d,v) for d,v in s.items() if d is not Domain.DECISION],key=lambda x:x[1],reverse=True)
    ds=s.get(Domain.DECISION,0)
    if concrete and concrete[0][1]>=.55:
        sec=[d for d,v in concrete[1:] if v>=.45]
        if ds>=.45: sec.append(Domain.DECISION)
        return concrete[0][0],sec[:2]
    if ds>=.55:return Domain.DECISION,[]
    return Domain.OTHER,[]
def select_need(t,st,d):
    if any(x in t for x in CHOICE_TERMS) or st in {QuestionStyle.BINARY,QuestionStyle.ADVICE_SEEKING}: n=CoreNeed.DECISION_SUPPORT
    elif any(x in t for x in ("לשחרר","החלמה","כאב","פגיעה","אבל")): n=CoreNeed.HEALING
    elif any(x in t for x in ("לחזור","יחזור","תחזור")): n=CoreNeed.REASSURANCE
    elif any(x in t for x in ("גבולות","אומץ","מפחד")): n=CoreNeed.COURAGE
    elif d is Domain.DAILY_GUIDANCE:n=CoreNeed.EXPLORATION
    elif st is QuestionStyle.OPEN:n=CoreNeed.CLARITY
    else:n=CoreNeed.PERSPECTIVE
    return n,[Evidence(field="core_need",value=n.value,source="structure",excerpt=st.value,weight=.75,rule_id="INT-002")]
def emotions(t):
    out=[];ev=[]
    for em,terms in EMOTION_TERMS.items():
        for term in terms:
            if term in t:
                out.append(em);ev.append(Evidence(field="emotional_state",value=em.value,source="question",excerpt=term,weight=.9,rule_id="INT-005"));break
    return out[:3],ev
def confidence(s,d,e_count,has_context):
    if d is Domain.OTHER:return .42
    vals=sorted(s.values(),reverse=True);top=vals[0] if vals else 0;runner=vals[1] if len(vals)>1 else 0
    val=top*.45+max(top-runner,0)*.2+min(e_count/3,1)*.2+(1 if has_context else .75)*.15
    if e_count<2:val=min(val,.74)
    if d not in {Domain.OTHER, Domain.DECISION} and e_count >= 2:
        val=max(val,.68)
    return round(min(max(val,0),1),2)
def classify_intent(req):
    t=normalize(req.question);c=normalize(" ".join(x.content for x in req.conversation_context));sf=detect_safety(t);st=style(t);scores,de=score_domains(t,c);d,sd=select_domains(scores);need,ne=select_need(t,st,d);ems,ee=emotions(t+" "+c);ev=de+ne+ee;conf=confidence(scores,d,len(ev),bool(c)); crisis={SafetyFlag.SELF_HARM_OR_SUICIDE,SafetyFlag.ABUSE_OR_COERCION,SafetyFlag.IMMEDIATE_DANGER};clar=(d is Domain.OTHER or conf<.65) and not crisis.intersection(sf);cq=("כשאת אומרת לעזוב, למה את מתכוונת?" if "לעזוב" in t else "למה הכוונה?") if clar else None; readiness=3 if any(x in t for x in ("מתלבט","מתלבטת","שוקל","שוקלת")) else (1 if st is QuestionStyle.PREDICTIVE else 2); comp="medium" if sd or len(ems)>=2 or any(x in t for x in CHOICE_TERMS) else "low"
    return QuestionDNA(surface_question=req.question,normalized_question=t,domain=d,secondary_domains=sd,core_need=need,emotional_state=ems,readiness=readiness,complexity=comp,question_style=st,clarification_required=clar,clarification_reason="classification_confidence_below_threshold" if clar else None,clarification_question=cq,confidence=conf,safety_flags=sf,evidence=ev)
