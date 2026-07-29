# שדרוג Guardian לגרסה 0.4

## מה נוסף

- חיבור אופציונלי ל-OpenAI Responses API
- ניסוח אישי יותר של הקריאה
- fallback אוטומטי לקריאה התבניתית אם השירות אינו זמין
- endpoint חדש: `/v1/system/status`
- המשתנה `reading_source` בתשובת הקריאה מציין `ai` או `template`

## העלאת הגרסה

1. החליפי את קבצי המאגר ב-GitHub בקבצים מחבילה זו.
2. בצעי Commit ל-main.
3. Render יתחיל Deploy אוטומטי דרך ה-Blueprint.

## הפעלת AI ב-Render

1. פתחי את השירות `guardian-of-light`.
2. עברי ל-Environment.
3. הוסיפי Secret בשם `OPENAI_API_KEY`.
4. הדביקי את מפתח ה-API ושמרי.
5. ודאי שקיים `OPENAI_MODEL` עם הערך `gpt-5-mini`.
6. Render יפרוס מחדש את השירות.

אין להכניס את מפתח ה-API לקוד או ל-GitHub.

## בדיקה

- `/health` צריך להחזיר גרסה `0.4.0`
- `/v1/system/status` צריך להחזיר `ai_enabled: true` אחרי הוספת המפתח
