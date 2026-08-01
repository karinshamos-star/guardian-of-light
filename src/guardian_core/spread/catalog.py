from .models import SpreadDefinition, SpreadPosition

DEFAULT_SPREADS = [
    SpreadDefinition(
        spread_id="single-reflection",
        name="Single Reflection",
        supported_needs=["exploration", "perspective", "clarity"],
        supported_complexities=["low"],
        positions=[
            SpreadPosition(
                id="focus",
                label="מוקד ההתבוננות",
                purpose="הסמל המרכזי שכדאי לפגוש עכשיו",
                weight=1.0,
            )
        ],
    ),
    SpreadDefinition(
        spread_id="decision-three",
        name="Decision Support",
        supported_needs=["decision_support", "courage", "clarity"],
        supported_complexities=["medium", "high"],
        positions=[
            SpreadPosition(
                id="factors",
                label="הגורמים הפועלים",
                purpose="מה משפיע על הבחירה כרגע",
                weight=1.0,
            ),
            SpreadPosition(
                id="tension",
                label="המתח המרכזי",
                purpose="מה מושך לכיוונים שונים או דורש איזון",
                weight=1.2,
            ),
            SpreadPosition(
                id="grounded_step",
                label="הצעד המעשי",
                purpose="פעולה קטנה שמחזירה את הבחירה למשתמש",
                weight=1.1,
            ),
        ],
    ),
    SpreadDefinition(
        spread_id="pattern-three",
        name="Pattern Reflection",
        supported_needs=["healing", "closure", "acceptance", "validation", "perspective"],
        supported_complexities=["medium", "high"],
        positions=[
            SpreadPosition(
                id="current_pattern",
                label="הדפוס הנוכחי",
                purpose="מה חוזר או מבקש תשומת לב",
                weight=1.1,
            ),
            SpreadPosition(
                id="underlying_need",
                label="הצורך שמתחת",
                purpose="מה מבקש הכרה, ריפוי או הבנה",
                weight=1.2,
            ),
            SpreadPosition(
                id="integration",
                label="דרך לאינטגרציה",
                purpose="כיצד ניתן לפגוש את המצב באופן שלם יותר",
                weight=1.0,
            ),
        ],
    ),
    SpreadDefinition(
        spread_id="complex-five",
        name="Complex Situation",
        supported_needs=[
            "clarity", "perspective", "decision_support", "healing",
            "closure", "acceptance", "validation", "courage"
        ],
        supported_complexities=["high"],
        positions=[
            SpreadPosition(id="present", label="המצב הנוכחי", purpose="התמונה המרכזית", weight=1.0),
            SpreadPosition(id="influence", label="השפעה מרכזית", purpose="מה מעצב את המצב", weight=1.0),
            SpreadPosition(id="tension", label="מתח", purpose="מה מתנגש או מעכב", weight=1.2),
            SpreadPosition(id="resource", label="משאב", purpose="מה יכול לתמוך", weight=1.0),
            SpreadPosition(id="next_step", label="צעד מקורקע", purpose="פעולה אפשרית אחת", weight=1.1),
        ],
    ),
]
