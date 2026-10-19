from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from datetime import date
from uuid import uuid4

from guardian_core.numerology import build_numerology_reading, calculate_profile, gematria
from guardian_core.reading import ReadingResult, project_reading_result, run_reading

from .models import (
    CameraCue,
    CameraMode,
    ExperienceCommand,
    GuideAnimation,
    GuideCue,
    GuideEmotion,
    InteractionCue,
    InteractionOption,
    InteractionType,
    SceneId,
    WorldObjectCue,
    WorldObjectType,
    WorldSnapshot,
)


class WorldState(StrEnum):
    ARRIVAL = "arrival"
    AVATAR_SELECTION = "avatar_selection"
    LIBRARY_ENTRANCE = "library_entrance"
    GUIDE_GREETING = "guide_greeting"
    SECRET_DOOR = "secret_door"
    READING_ROOM = "reading_room"
    QUESTION = "question"
    METHOD_CHOICE = "method_choice"
    NUMEROLOGY_NAME = "numerology_name"
    NUMEROLOGY_BIRTH = "numerology_birth"
    READING = "reading"
    REFLECTION = "reflection"
    RETURN_TO_LIBRARY = "return_to_library"


class WorldAction(StrEnum):
    BEGIN = "begin"
    CHOOSE_AVATAR = "choose_avatar"
    ENTER_LIBRARY = "enter_library"
    TALK_TO_GUIDE = "talk_to_guide"
    FOLLOW_GUIDE = "follow_guide"
    ENTER_SECRET_ROOM = "enter_secret_room"
    ASK_QUESTION = "ask_question"
    CHOOSE_METHOD = "choose_method"
    COMPLETE_READING = "complete_reading"
    REFLECT = "reflect"
    RETURN = "return"


@dataclass
class WorldSession:
    session_id: str
    state: WorldState = WorldState.ARRIVAL
    sequence: int = 0
    avatar_id: str | None = None
    question: str | None = None
    history: list[str] = field(default_factory=list)
    object_states: dict[str, str] = field(default_factory=lambda: {
        "library_doors": "closed",
        "secret_door": "hidden",
        "reading_book": "absent",
    })
    guide_activity: str = "waiting_at_entrance"
    reading_result: ReadingResult | None = None
    method: str | None = None
    full_name: str | None = None
    birth_date: date | None = None

    def command(self) -> ExperienceCommand:
        self.sequence += 1
        command = _command_for(self)
        self.history.append(command.command_id)
        return command

    def apply(self, action: WorldAction, payload: dict | None = None) -> ExperienceCommand:
        payload = payload or {}
        allowed = TRANSITIONS.get(self.state, {})
        if action not in allowed:
            expected = ", ".join(a.value for a in allowed) or "none"
            raise ValueError(f"action '{action.value}' is not allowed in state '{self.state.value}'. Expected: {expected}")
        if action is WorldAction.CHOOSE_AVATAR:
            avatar_id = str(payload.get("avatar_id", "")).strip()
            if not avatar_id:
                raise ValueError("avatar_id is required")
            self.avatar_id = avatar_id
        target = allowed[action]

        if action is WorldAction.ASK_QUESTION and self.state is WorldState.NUMEROLOGY_NAME:
            full_name = " ".join(str(payload.get("full_name", "")).split())
            if not full_name:
                raise ValueError("full_name is required")
            if gematria(full_name) == 0:
                raise ValueError(_NUMEROLOGY_ERRORS["full_name must contain Hebrew letters"])
            self.full_name = full_name
        elif action is WorldAction.ASK_QUESTION and self.state is WorldState.NUMEROLOGY_BIRTH:
            self.birth_date = _parse_birth_date(str(payload.get("birth_date", "")))
            try:
                profile = calculate_profile(birth_date=self.birth_date, full_name=self.full_name or "")
            except ValueError as exc:
                raise ValueError(_NUMEROLOGY_ERRORS.get(str(exc), str(exc))) from exc
            self.reading_result = build_numerology_reading(profile)
        elif action is WorldAction.ASK_QUESTION:
            question = str(payload.get("question", "")).strip()
            if not question:
                raise ValueError("question is required")
            awaiting_clarification = self.reading_result is not None and self.reading_result.status == "clarification_required"
            # A clarification answer extends the original question; it must not replace it,
            # and the stale clarification result must be cleared so the flow can advance.
            self.question = f"{self.question} {question}".strip() if awaiting_clarification and self.question else question
            self.reading_result = None
        elif action is WorldAction.CHOOSE_METHOD:
            method = str(payload.get("option_id", "")).strip()
            if method not in METHODS:
                raise ValueError(f"option_id must be one of: {', '.join(METHODS)}")
            self.method = method
            if method == "numerology":
                target = WorldState.NUMEROLOGY_NAME

        if action is WorldAction.COMPLETE_READING:
            outcome = run_reading(question=self.question or "", seed=payload.get("seed"))
            self.reading_result = project_reading_result(outcome)
            if outcome.status == "completed":
                self.state = target
                self._apply_world_effects(action)
        else:
            previous = self.state
            self.state = target
            self._apply_world_effects(action, previous)
        return self.command()

    def _apply_world_effects(self, action: WorldAction, previous: WorldState | None = None) -> None:
        if action is WorldAction.ENTER_LIBRARY:
            self.object_states["library_doors"] = "open"
            self.guide_activity = "greeting_visitor"
        elif action is WorldAction.TALK_TO_GUIDE:
            self.object_states["secret_door"] = "revealed"
            self.guide_activity = "walking_to_bookshelf"
        elif action is WorldAction.FOLLOW_GUIDE:
            self.object_states["secret_door"] = "opening"
            self.guide_activity = "opening_secret_passage"
        elif action is WorldAction.ENTER_SECRET_ROOM:
            self.object_states["secret_door"] = "open"
            self.guide_activity = "waiting_by_reading_table"
        elif action is WorldAction.ASK_QUESTION and previous is WorldState.QUESTION:
            self.guide_activity = "offering_methods"
        elif action is WorldAction.ASK_QUESTION and previous is WorldState.NUMEROLOGY_NAME:
            self.guide_activity = "preparing_numerology"
        elif action is WorldAction.ASK_QUESTION and previous is WorldState.NUMEROLOGY_BIRTH:
            self.object_states["reading_book"] = "created"
            self.guide_activity = "holding_reflective_space"
        elif action is WorldAction.ASK_QUESTION:
            self.guide_activity = "preparing_reading"
        elif action is WorldAction.CHOOSE_METHOD:
            self.guide_activity = "preparing_numerology" if self.method == "numerology" else "preparing_reading"
        elif action is WorldAction.COMPLETE_READING:
            self.object_states["reading_book"] = "created"
            self.guide_activity = "holding_reflective_space"
        elif action is WorldAction.REFLECT:
            self.object_states["reading_book"] = "shelved"
            self.guide_activity = "returning_to_library"
        elif action is WorldAction.RETURN:
            self.guide_activity = "arranging_books"


TRANSITIONS: dict[WorldState, dict[WorldAction, WorldState]] = {
    # AVATAR_SELECTION is kept in WorldState for contract compatibility but is no longer
    # reachable: it had no effect on the experience (see EXPERIENCE_FLOW_V1.md §1.5).
    WorldState.ARRIVAL: {WorldAction.BEGIN: WorldState.LIBRARY_ENTRANCE},
    WorldState.LIBRARY_ENTRANCE: {WorldAction.ENTER_LIBRARY: WorldState.GUIDE_GREETING},
    WorldState.GUIDE_GREETING: {WorldAction.TALK_TO_GUIDE: WorldState.SECRET_DOOR},
    WorldState.SECRET_DOOR: {WorldAction.FOLLOW_GUIDE: WorldState.READING_ROOM},
    WorldState.READING_ROOM: {WorldAction.ENTER_SECRET_ROOM: WorldState.QUESTION},
    WorldState.QUESTION: {WorldAction.ASK_QUESTION: WorldState.METHOD_CHOICE},
    WorldState.METHOD_CHOICE: {WorldAction.CHOOSE_METHOD: WorldState.READING},
    WorldState.NUMEROLOGY_NAME: {WorldAction.ASK_QUESTION: WorldState.NUMEROLOGY_BIRTH},
    WorldState.NUMEROLOGY_BIRTH: {WorldAction.ASK_QUESTION: WorldState.REFLECTION},
    WorldState.READING: {
        WorldAction.ASK_QUESTION: WorldState.READING,
        WorldAction.COMPLETE_READING: WorldState.REFLECTION,
    },
    WorldState.REFLECTION: {WorldAction.REFLECT: WorldState.RETURN_TO_LIBRARY},
    WorldState.RETURN_TO_LIBRARY: {WorldAction.RETURN: WorldState.GUIDE_GREETING},
}


METHODS = ("tarot", "numerology")

_NUMEROLOGY_ERRORS = {
    "birth_date is in the future": "תאריך הלידה נמצא בעתיד. אפשר לנסות שוב?",
    "full_name must contain Hebrew letters": "השם צריך להיכתב באותיות עבריות.",
}


def _parse_birth_date(text: str) -> date:
    parts = [p for p in text.replace("/", ".").replace("-", ".").replace(" ", ".").split(".") if p]
    try:
        day, month, year = (int(p) for p in parts)
        return date(year, month, day)
    except (ValueError, TypeError):
        raise ValueError("תאריך הלידה צריך להיכתב כך: יום.חודש.שנה, למשל 15.03.1990") from None


def new_session() -> WorldSession:
    return WorldSession(session_id=str(uuid4()))


def _world_for(session: WorldSession, scene: SceneId) -> WorldSnapshot:
    objects = [
        WorldObjectCue(object_id="keeper_of_light", object_type=WorldObjectType.NPC,
                       state=session.guide_activity, visible=True, interactive=scene is SceneId.LIBRARY,
                       available_actions=["talk_to_guide"] if scene is SceneId.LIBRARY else []),
        WorldObjectCue(object_id="library_doors", object_type=WorldObjectType.DOOR,
                       state=session.object_states["library_doors"], visible=scene is SceneId.LIBRARY_ENTRANCE),
        WorldObjectCue(object_id="secret_door", object_type=WorldObjectType.DOOR,
                       state=session.object_states["secret_door"],
                       visible=scene in {SceneId.LIBRARY, SceneId.SECRET_PASSAGE}),
        WorldObjectCue(object_id="reading_book", object_type=WorldObjectType.BOOK,
                       state=session.object_states["reading_book"],
                       visible=scene is SceneId.SECRET_READING_ROOM or session.object_states["reading_book"] == "shelved"),
    ]
    return WorldSnapshot(location_id=scene.value, objects=objects, guide_activity=session.guide_activity)


def _command_for(session: WorldSession) -> ExperienceCommand:
    sid = session.session_id
    seq = session.sequence
    common = dict(session_id=sid, sequence=seq, command_id=f"{session.state.value}:{seq}")

    if session.state is WorldState.ARRIVAL:
        return ExperienceCommand(**common, scene=SceneId.LIBRARY_ENTRANCE, world=_world_for(session, SceneId.LIBRARY_ENTRANCE),
            guide=GuideCue(dialogue="המסע שלך יכול להתחיל עכשיו.", emotion=GuideEmotion.WELCOMING, animation=GuideAnimation.GREET),
            camera=CameraCue(mode=CameraMode.FOCUS, target="library_doors", duration_seconds=2),
            interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="להתחיל", input_key="begin"), effects=["soft_light"])
    if session.state is WorldState.AVATAR_SELECTION:
        return ExperienceCommand(**common, scene=SceneId.AVATAR_SELECTION, world=_world_for(session, SceneId.AVATAR_SELECTION),
            guide=GuideCue(dialogue="בחרי את הדמות שתלווה אותך בעולם.", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.SPEAK),
            interaction=InteractionCue(type=InteractionType.CHOOSE_OPTION, prompt="בחירת דמות", options=[
                InteractionOption(id="seeker", label="מחפשת האור"), InteractionOption(id="scribe", label="שומרת הידע"), InteractionOption(id="wanderer", label="הנודדת")]))
    if session.state is WorldState.LIBRARY_ENTRANCE:
        return ExperienceCommand(**common, scene=SceneId.LIBRARY_ENTRANCE, world=_world_for(session, SceneId.LIBRARY_ENTRANCE),
            guide=GuideCue(dialogue="הספרייה מחכה לך מעבר לדלת.", emotion=GuideEmotion.WELCOMING, animation=GuideAnimation.INVITE_FOLLOW),
            camera=CameraCue(mode=CameraMode.FOCUS, target="library_doors", duration_seconds=1.5),
            interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="להיכנס לספרייה", input_key="enter_library", auto_advance_seconds=1.5))
    if session.state is WorldState.GUIDE_GREETING:
        return ExperienceCommand(**common, scene=SceneId.LIBRARY, world=_world_for(session, SceneId.LIBRARY),
            guide=GuideCue(dialogue="ברוכה הבאה. אני לומינה, ואשמור איתך על המרחב הזה.", emotion=GuideEmotion.WELCOMING, animation=GuideAnimation.GREET),
            camera=CameraCue(mode=CameraMode.FOCUS, target="keeper_of_light", duration_seconds=2),
            interaction=InteractionCue(type=InteractionType.TALK_TO_GUIDE, prompt="לדבר עם לומינה", auto_advance_seconds=1.5), effects=["fireplace_glow"])
    if session.state is WorldState.SECRET_DOOR:
        return ExperienceCommand(**common, scene=SceneId.LIBRARY, world=_world_for(session, SceneId.LIBRARY),
            guide=GuideCue(dialogue="יש מקום שקט יותר לקריאה. בואי אחריי.", emotion=GuideEmotion.REASSURING, animation=GuideAnimation.WALK_TO_BOOKSHELF),
            camera=CameraCue(mode=CameraMode.FOLLOW, target="keeper_of_light", duration_seconds=3),
            interaction=InteractionCue(type=InteractionType.FOLLOW_GUIDE, prompt="לעקוב אחרי לומינה", auto_advance_seconds=1.5))
    if session.state is WorldState.READING_ROOM:
        return ExperienceCommand(**common, scene=SceneId.SECRET_PASSAGE, world=_world_for(session, SceneId.SECRET_PASSAGE),
            guide=GuideCue(dialogue="המדף נפתח. החדר נמצא מעבר למעבר.", emotion=GuideEmotion.THOUGHTFUL, animation=GuideAnimation.OPEN_SECRET_PASSAGE),
            camera=CameraCue(mode=CameraMode.FOCUS, target="secret_passage", duration_seconds=2.5),
            interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="להיכנס לחדר הסודי", input_key="enter_secret_room", auto_advance_seconds=1.5), effects=["bookshelf_open", "dust_particles"])
    if session.state is WorldState.QUESTION:
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue="מה מבקש ממך תשומת לב עכשיו?", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.LISTEN),
            camera=CameraCue(mode=CameraMode.FOCUS, target="reading_table", duration_seconds=2),
            interaction=InteractionCue(type=InteractionType.ASK_QUESTION, prompt="כתבי את השאלה שלך", input_key="question"), effects=["candles_on"])
    if session.state is WorldState.METHOD_CHOICE:
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue="איך תרצי שנתבונן בשאלה הזו יחד?", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.SPEAK),
            interaction=InteractionCue(type=InteractionType.CHOOSE_OPTION, prompt="בחירת דרך", input_key="choose_method", options=[
                InteractionOption(id="tarot", label="קלפי טארוט"), InteractionOption(id="numerology", label="נומרולוגיה")]))
    if session.state is WorldState.NUMEROLOGY_NAME:
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue="נתחיל מהשם. איך קוראים לך, בשם מלא?", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.LISTEN),
            interaction=InteractionCue(type=InteractionType.ASK_QUESTION, prompt="שם מלא בעברית", input_key="full_name"))
    if session.state is WorldState.NUMEROLOGY_BIRTH:
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue="ועכשיו תאריך הלידה.", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.LISTEN),
            interaction=InteractionCue(type=InteractionType.ASK_QUESTION, prompt="תאריך לידה (יום.חודש.שנה)", input_key="birth_date"))
    if session.state is WorldState.READING:
        if session.reading_result is not None and session.reading_result.status == "clarification_required":
            return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
                guide=GuideCue(dialogue=session.reading_result.clarification_question or "אשמח להבין קצת יותר לפני שאני פותחת את הקריאה.", emotion=GuideEmotion.CURIOUS, animation=GuideAnimation.LISTEN),
                interaction=InteractionCue(type=InteractionType.ASK_QUESTION, prompt="ננסח את השאלה מחדש יחד", input_key="question"))
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue="אני פותחת את הקריאה כהזמנה להתבוננות, לא כנבואה.", emotion=GuideEmotion.THOUGHTFUL, animation=GuideAnimation.PRESENT_READING_TABLE),
            interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="לפתוח את הקריאה", input_key="complete_reading"), payload={"question": session.question})
    if session.state is WorldState.REFLECTION:
        result = session.reading_result
        dialogue = result.central_message if result and result.central_message else "קחי רגע ובחרי דבר אחד שאת רוצה לשאת איתך מכאן."
        payload = {"reading": result.model_dump(mode="json")} if result is not None else {}
        return ExperienceCommand(**common, scene=SceneId.SECRET_READING_ROOM, world=_world_for(session, SceneId.SECRET_READING_ROOM),
            guide=GuideCue(dialogue=dialogue, emotion=GuideEmotion.REASSURING, animation=GuideAnimation.SPEAK),
            interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="סיימתי להתבונן", input_key="reflect"), payload=payload)
    return ExperienceCommand(**common, scene=SceneId.LIBRARY, world=_world_for(session, SceneId.LIBRARY),
        guide=GuideCue(dialogue="הקריאה נשמרה כספר חדש בספרייה שלך.", emotion=GuideEmotion.WELCOMING, animation=GuideAnimation.GREET),
        camera=CameraCue(mode=CameraMode.FOCUS, target="personal_bookshelf", duration_seconds=2),
        interaction=InteractionCue(type=InteractionType.CONTINUE, prompt="לחזור אל לומינה", input_key="return"), effects=["new_book_glow"])
