# Guardian Experience Contract v1.0

`ExperienceCommand` is the transport contract between Guardian Brain and an interactive client.

The backend decides **what happens next**. The client decides **how it is rendered**.

## Responsibilities

Guardian Brain owns:

- session and narrative state
- current scene ID
- guide dialogue, emotion, and semantic animation cue
- camera intent
- available interaction
- structured payload

Web or Unity owns:

- scene loading
- animation clips and Animator mappings
- character movement
- camera implementation
- voice playback and lip sync
- sound, lighting, particles, and UI

## Example

```json
{
  "contract_version": "1.0",
  "command_id": "cmd-001",
  "session_id": "session-001",
  "sequence": 3,
  "scene": "library",
  "guide": {
    "character_id": "keeper_of_light",
    "dialogue": "ברוכה הבאה לספרייה.",
    "emotion": "welcoming",
    "animation": "greet",
    "voice_style": "warm"
  },
  "camera": {
    "mode": "focus",
    "target": "keeper_of_light",
    "duration_seconds": 1.5
  },
  "interaction": {
    "type": "choose_option",
    "prompt": "מה תרצי לעשות?",
    "options": [
      {
        "id": "follow_guide",
        "label": "ללכת אחרי המדריך",
        "enabled": true,
        "metadata": {}
      }
    ],
    "input_key": null
  },
  "effects": ["library_dust_motes"],
  "payload": {}
}
```

## Compatibility rule

Clients must map semantic IDs such as `greet`, `invite_follow`, and `library` to local assets. No Python code references Unity Animator state names or asset paths.
