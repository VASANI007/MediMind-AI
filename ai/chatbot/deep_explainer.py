"""
    Deep Clinical Explanation & Assessment Follow-Up Q&A Engine
Powered by Gemini & Groq AI. Provides in-depth medical rationale, drug synergy analysis,
and interactive question-answering tailored to the patient's exact assessment results.
"""
import json
import requests
from config.settings import GEMINI_API_KEY, GROQ_API_KEY

def generate_deep_explanation(
    symptoms: list,
    user_context: dict,
    top_condition: str,
    ranked_conditions: list,
    medicines: list,
    yoga_recs: list,
    lang: str = "en"
) -> str:
    """
    Generates a structured, comprehensive, patient-friendly clinical deep explanation.
    """
    lang_name = "English" if lang == "en" else "Hindi (हिंदी)" if lang == "hi" else "Gujarati (ગુજરાતી)"
    
    med_names = [m.get("name", "") for m in (medicines or []) if isinstance(m, dict)]
    yoga_names = [y.get("name", "") for y in (yoga_recs or []) if isinstance(y, dict)]
    cond_names = [c.get("name", "") for c in (ranked_conditions or []) if isinstance(c, dict)]

    prompt = f"""You are MediMind AI — Senior Clinical Healthcare & Diagnostic Consultant.
    Provide an exhaustive, transparent, and comforting Clinical Deep Explanation of this patient's assessment findings.

PATIENT PROFILE:
- Reported Symptoms: {', '.join(symptoms) if symptoms else 'General Symptoms'}
- Duration: {user_context.get('duration', '1 - 3 Days')}
- Severity: {user_context.get('severity', 'Moderate')}
- Age Group: {user_context.get('age', 'Adult')}, Gender: {user_context.get('gender', 'Male')}
- Existing Medical Conditions: {', '.join(user_context.get('conditions', ['None']))}
- Primary Assessed Condition: {top_condition}
- Ranked Conditions Evaluated: {', '.join(cond_names[:3])}
- Recommended Medications: {', '.join(med_names)}
- Supportive Yoga & Mobility: {', '.join(yoga_names)}

INSTRUCTIONS:
Write a comprehensive, beautifully structured clinical explanation strictly in {lang_name}. Do NOT use emojis.
Include the following clear sections with Markdown headings:

### 1. Diagnostic Rationale (Why These Conditions Were Identified)
Explain in simple, empathetic terms how the specific combination of symptoms ({', '.join(symptoms)}) aligns with {top_condition} and related diagnostic pathways.

### 2. Medication Strategy & Biochemical Synergy
Explain why each prescribed medicine was chosen and how they work together as a team (e.g. pain relief + stomach protection + rehydration). Mention why taking them at the right time (before vs after food) is vital.

### 3. Holistic Recovery (Yoga, Hydration & Dietary Science)
Explain the physiological benefits of the recommended restorative yoga poses and dietary guidelines in speeding up natural cellular recovery.

### 4. Red Flags & Urgent Care Advice
Clear clinical advice on when symptoms require immediate in-person medical evaluation.

Write in a reassuring, professional, and clear tone in {lang_name}."""

    # 1. Groq AI (Ultra-Fast Live Engine)
    if GROQ_API_KEY:
        for model in ["qwen/qwen3.6-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]:
            try:
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                body = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": f"You are MediMind AI. Write clear clinical explanations in {lang_name}. Do not use emojis."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=8)
                if res.status_code == 200:
                    txt = res.json()["choices"][0]["message"]["content"]
                    if txt and len(txt.strip()) > 100:
                        return txt.strip()
            except Exception as e:
                print(f"Deep explanation Groq notice: {e}")

    # 2. Gemini AI
    if GEMINI_API_KEY:
        for model in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-pro"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
                }
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, json=payload, headers=headers, timeout=8)
                if res.status_code == 200:
                    candidates = res.json().get("candidates", [])
                    if candidates:
                        txt = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if txt and len(txt.strip()) > 100:
                            return txt.strip()
            except Exception as e:
                print(f"Deep explanation Gemini notice: {e}")

    # Local fallback (Clean, no emojis)
    if lang == "hi":
        return f"""### 1. यह स्वास्थ्य स्थिति क्यों पाई गई
आपके द्वारा बताए गए लक्षण (**{', '.join(symptoms)}**) मुख्य रूप से **{top_condition}** के पैटर्न से मेल खाते हैं। इस स्थिति में शरीर की रोग प्रतिरोधक प्रणाली सक्रिय हो जाती है जिससे सिरदर्द, बदन दर्द या थकावट महसूस हो सकती है।

### 2. दवाओं का संयोजन और प्रभाव
- बुखार और दर्द निवारक: शरीर के तापमान और मांसपेशियों के दर्द को नियंत्रित करने के लिए।
- पेट की सुरक्षा (Gastric Shield): एसिडिटी और पेट में जलन से बचाव के लिए इसे खाली पेट लेने की सलाह दी गई है।
- हाइड्रेशन (ORS): शरीर में तरल और आवश्यक इलेक्ट्रोलाइट्स की भरपाई के लिए।

### 3. योग और आहार द्वारा स्वास्थ्य लाभ
विश्रामदायक योगासन मांसपेशियों के तनाव को कम करते हैं और रक्त प्रवाह को बढ़ाते हैं। हल्का और सुपाच्य भोजन (जैसे खिचड़ी, दलिया, सूप) जल्दी ठीक होने में मदद करता है।

### 4. डॉक्टर से परामर्श
यदि 3 दिन से अधिक तेज बुखार बना रहे या सांस लेने में कठिनाई हो, तो तुरंत चिकित्सक से परामर्श लें।"""
    elif lang == "gu":
        return f"""### 1. આ સ્થિતિનું નિદાન કેમ થયું
તમે જણાવેલા લક્ષણો (**{', '.join(symptoms)}**) મુખ્યત્વે **{top_condition}** સાથે મેળ ખાય છે.

### 2. દવાઓનું આયોજન
- તાવ અને દુખાવાની દવા: શરીરનું તાપમાન ઘટાડવા અને દુખાવો ઓછો કરવા માટે.
- પેટની સુરક્ષા: એસિડિટીથી બચવા માટે ખાલી પેટે લેવી.
- હાઇડ્રેશન (ORS): શરીરમાં પાણી અને ક્ષારોનું સંતુલન જાળવવા.

### 3. યોગ અને આહાર
યોગાસનો સ્નાયુઓનો તણાવ દૂર કરે છે અને પૌષ્ટિક આહાર ઝડપી સ્વસ્થતા આપે છે."""
    else:
        return f"""### 1. Clinical Assessment Rationale
Your reported symptoms (**{', '.join(symptoms)}**) closely correspond to the clinical presentation of **{top_condition}**. The body's inflammatory response to this condition creates localized fatigue, discomfort, and physiological strain.

### 2. Medication Teamwork & Synergy
- Symptom Relief & Antipyretic: Directly addresses elevated temperature and acute pain.
- Gastric Protection (PPI): Protects the gastric lining against acidity when taking other medications.
- Cellular Rehydration (ORS): Replenishes vital electrolytes (Sodium, Potassium) to combat dizziness and dehydration.

### 3. Restorative Yoga & Dietary Protocol
Gentle mobility postures relieve muscle stiffness and improve oxygen circulation, while nutrient-dense foods (warm soups, light meals) accelerate healing without burdening the digestive tract.

### 4. Red Flags
Seek immediate medical consultation if symptoms worsen, high fever persists beyond 3 days, or breathing difficulty occurs."""


def answer_assessment_question(
    user_question: str,
    symptoms: list,
    user_context: dict,
    top_condition: str,
    medicines: list,
    lang: str = "en"
) -> str:
    """
    Answers any follow-up question regarding the patient's assessment and medications.
    """
    lang_name = "English" if lang == "en" else "Hindi (हिंदी)" if lang == "hi" else "Gujarati (ગુજરાતી)"
    med_summary = ", ".join([f"{m.get('name')} ({m.get('food_timing', 'After Food')})"
        for m in (medicines or []) if isinstance(m, dict)])

    prompt = f"""You are MediMind AI Clinical Consultation Assistant.
    Answer the following patient question regarding their current health assessment and medications.

PATIENT CONTEXT:
- Symptoms: {', '.join(symptoms)}
- Assessed Condition: {top_condition}
- Prescribed Medicines: {med_summary}
- Demographics: Age {user_context.get('age', 'Adult')}, Gender {user_context.get('gender', 'Male')}

PATIENT'S QUESTION:
"{user_question}"

INSTRUCTIONS:
1. Provide a direct, compassionate, scientifically accurate answer strictly in {lang_name}.
2. Explain clearly in 2-4 concise paragraphs with practical advice.
3. If they ask about taking medicines together, food timings, side effects, or recovery, provide exact clinical guidance.
4. Conclude with a warm safety reminder."""

    if GEMINI_API_KEY:
        for model in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.7-flash", "gemini-flash-latest"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
                }
                res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
                if res.status_code == 200:
                    candidates = res.json().get("candidates", [])
                    if candidates:
                        txt = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if txt and len(txt.strip()) > 20:
                            return txt.strip()
            except Exception as e:
                print(f"Q&A Gemini notice: {e}")

    if GROQ_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            body = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": f"You are MediMind AI. Answer patient questions clinically in {lang_name}."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=8)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Q&A Groq notice: {e}")

    return f"Based on your assessment for {top_condition}, please follow the prescribed dosage and food timing instructions carefully. If symptoms persist or cause discomfort, consult a doctor immediately."
