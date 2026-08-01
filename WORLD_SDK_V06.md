# Guardian World SDK v0.6

## מטרה

להפוך את העולם למודל דומיין עצמאי שאינו תלוי ב-Web, Unity או מנוע תצוגה אחר.

## WorldSnapshot

כל `ExperienceCommand` כולל כעת snapshot סמנטי של העולם:

- `location_id`
- `guide_activity`
- רשימת `objects`

## WorldObjectCue

כל אובייקט מתואר באמצעות:

- `object_id`
- `object_type`
- `state`
- `visible`
- `interactive`
- `available_actions`
- `metadata`

השרת מתאר מה קורה; הלקוח מחליט כיצד להציג זאת.

## אובייקטים ב-vertical slice

- `keeper_of_light`
- `library_doors`
- `secret_door`
- `reading_book`

## דוגמת שינוי מצב

`talk_to_guide` משנה את `secret_door` מ-`hidden` ל-`revealed`.

`follow_guide` משנה אותו ל-`opening`.

`enter_secret_room` משנה אותו ל-`open`.

לא נשלחים שמות קבצים, Animator states או פרטי מנוע.
