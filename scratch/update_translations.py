import json

keys = {
    "en": {
        "course_duration_label": "Course Duration (How long to take)",
        "course_label": "Duration"
    },
    "hi": {
        "course_duration_label": "लेने की अवधि (कितने दिन/समय तक लें)",
        "course_label": "अवधि"
    },
    "gu": {
        "course_duration_label": "લેવાનો સમયગાળો (કેટલા દિવસ/સમય સુધી લેવી)",
        "course_label": "સમયગાળો"
    }
}

for lang, filename in [("en", "translations/english.json"), ("hi", "translations/hindi.json"), ("gu", "translations/gujarati.json")]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.update(keys[lang])
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {filename} with course duration keys.")
