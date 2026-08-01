from __future__ import annotations
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Domain(StrEnum):
    RELATIONSHIP="relationship"; CAREER="career"; FAMILY="family"; FINANCE_REFLECTION="finance_reflection"; HEALTH_REFLECTION="health_reflection"; PERSONAL_GROWTH="personal_growth"; SPIRITUAL_GROWTH="spiritual_growth"; DECISION="decision"; CREATIVITY="creativity"; DAILY_GUIDANCE="daily_guidance"; OTHER="other"
class CoreNeed(StrEnum):
    CLARITY="clarity"; PERSPECTIVE="perspective"; DECISION_SUPPORT="decision_support"; REASSURANCE="reassurance"; COURAGE="courage"; HEALING="healing"; CLOSURE="closure"; ACCEPTANCE="acceptance"; VALIDATION="validation"; EXPLORATION="exploration"
class EmotionalState(StrEnum):
    UNCERTAINTY="uncertainty"; FEAR="fear"; HOPE="hope"; SADNESS="sadness"; GRIEF="grief"; ANGER="anger"; FRUSTRATION="frustration"; CONFUSION="confusion"; CURIOSITY="curiosity"; LONGING="longing"; GUILT="guilt"; SHAME="shame"; RELIEF="relief"; CALM="calm"; EXCITEMENT="excitement"; OVERWHELM="overwhelm"
class QuestionStyle(StrEnum):
    OPEN="open"; BINARY="binary"; PREDICTIVE="predictive"; ADVICE_SEEKING="advice_seeking"; EXPLORATORY="exploratory"
class SafetyFlag(StrEnum):
    MEDICAL_HIGH_STAKES="medical_high_stakes"; LEGAL_HIGH_STAKES="legal_high_stakes"; FINANCIAL_HIGH_STAKES="financial_high_stakes"; SELF_HARM_OR_SUICIDE="self_harm_or_suicide"; ABUSE_OR_COERCION="abuse_or_coercion"; IMMEDIATE_DANGER="immediate_danger"; DELUSIONAL_OR_PARANOID_FRAMING="delusional_or_paranoid_framing"; DEPENDENCY_SEEKING="dependency_seeking"; DETERMINISTIC_PREDICTION_REQUEST="deterministic_prediction_request"; THIRD_PARTY_MIND_READING="third_party_mind_reading"
class ConversationTurn(BaseModel):
    role: Literal["user","assistant"]
    content: str=Field(min_length=1)
class IntentRequest(BaseModel):
    question: str=Field(min_length=1)
    conversation_context: list[ConversationTurn]=Field(default_factory=list)
    language: Literal["he","en"]="he"
    @field_validator("question")
    @classmethod
    def clean(cls,v):
        v=v.strip()
        if not v: raise ValueError("question must not be blank")
        return v
class Evidence(BaseModel):
    field:str; value:str; source:Literal["question","conversation_context","structure","safety_rule"]; excerpt:str; weight:float=Field(ge=0,le=1); rule_id:str|None=None
class QuestionDNA(BaseModel):
    surface_question:str; normalized_question:str; domain:Domain; secondary_domains:list[Domain]=Field(default_factory=list); core_need:CoreNeed; secondary_needs:list[CoreNeed]=Field(default_factory=list,max_length=2); emotional_state:list[EmotionalState]=Field(default_factory=list,max_length=3); readiness:int=Field(ge=0,le=5); complexity:Literal["low","medium","high"]; question_style:QuestionStyle; clarification_required:bool; clarification_reason:str|None=None; clarification_question:str|None=None; confidence:float=Field(ge=0,le=1); safety_flags:list[SafetyFlag]=Field(default_factory=list); evidence:list[Evidence]=Field(default_factory=list)
