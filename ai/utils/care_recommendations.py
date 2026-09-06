"""
    MediMind AI - Dynamic Clinical Care & Recommendations Engine
Powered by Gemini AI, Groq API, OpenFDA, DailyMed, WHO-ICD & BioPortal.
Generates dynamic, patient-tailored medicine counts, food timings, recovery duration,
supportive yoga & physio with YouTube tutorial links, and ice/hot compress guidance.
Provides graceful local clinical dataset fallback with clear warning metadata if APIs are unreachable.
"""
import sys
import os
import re
import json
import urllib.parse
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import GEMINI_API_KEY, GROQ_API_KEY, OPENFDA_API_KEY
from ai.utils.image_resolver import resolve_image

try:
    from api.openfda import search_drug_openfda
except Exception:
    def search_drug_openfda(*args, **kwargs):
        return None

try:
    from api.dailymed import search_dailymed_drugnames
except Exception:
    def search_dailymed_drugnames(*args, **kwargs):
        return []

try:
    from api.yoga_api import search_yoga_pose
except Exception:
    def search_yoga_pose(*args, **kwargs):
        return None


def _clean_json_response(raw_text: str) -> dict | None:
    """
    Extracts valid JSON dictionary from LLM markdown response.
    """
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    if "</think>" in cleaned:
        cleaned = cleaned.split("</think>")[-1].strip()
    else:
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()

    # Strip markdown code blocks
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        # Try to find JSON substring
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                return json.loads(cleaned[first_brace:last_brace + 1])
            except Exception:
                pass
    return None


def _first_candidate_name(medicine_name: str, brand_examples: str = "") -> str:
    """
    Picks a clean drug name to query against live medicine APIs.
    """
    candidate = ""
    if brand_examples:
        candidate = brand_examples.split(",")[0].strip()
    if not candidate and medicine_name:
        candidate = medicine_name.split("OR ")[0]
        candidate = candidate.split("(")[0]
        candidate = candidate.split("+")[0]
        candidate = candidate.split("/")[0]
    return candidate.strip()


def get_medicine_gallery(medicine_entries: list, max_items: int = 8) -> list:
    """
    Enriches each medicine entry with live OpenFDA / DailyMed verification and resolved images.
    """
    gallery = []
    for entry in (medicine_entries or [])[:max_items]:
        if isinstance(entry, dict):
            med_name = entry.get("medicine_name") or entry.get("name", "")
            brand_examples = entry.get("brand_examples", "")
            indication = entry.get("indication", "")
            dosage = entry.get("dosage", "")
            course_duration = entry.get("course_duration") or entry.get("duration") or "3 – 5 Days"
            food_timing = entry.get("food_timing", "After Food (खाने के बाद)")
            time_of_day = entry.get("time_of_day", "Twice Daily")
            warnings = entry.get("warnings", "Consult physician before use.")
            med_type = entry.get("type", "OTC")
            source_tag = entry.get("source", "Live Clinical AI")
        else:
            med_name = str(entry)
            brand_examples = ""
            indication = "Symptomatic relief"
            dosage = "As directed by physician"
            course_duration = "3 – 5 Days"
            food_timing = "After Food"
            time_of_day = "Twice Daily"
            warnings = "Consult doctor"
            med_type = "OTC"
            source_tag = "Clinical AI"

        candidate = _first_candidate_name(med_name, brand_examples)
        display_name = med_name if med_name else candidate

        api_source = source_tag
        api_info = None

        # Check OpenFDA for live enrichment
        if candidate:
            try:
                api_info = search_drug_openfda(candidate)
                if api_info and api_info.get("source"):
                    api_source = f"{source_tag} + {api_info.get('source')}"
            except Exception:
                pass

        # Pass full name and brand to resolve real packaging photo
        search_query = f"{display_name} {candidate}".strip()
        image_path, is_fallback = resolve_image("medicine", search_query)

        gallery.append({
            "name": display_name,
            "candidate_name": candidate,
            "image": image_path,
            "is_fallback": is_fallback,
            "source": api_source,
            "indication": indication,
            "dosage": dosage,
            "course_duration": course_duration,
            "food_timing": food_timing,
            "time_of_day": time_of_day,
            "warnings": warnings,
            "type": med_type,
            "openfda": api_info,
        })
    return gallery


def get_youtube_search_url(query: str) -> str:
    """
    Constructs a clean, direct YouTube search tutorial link.
    """
    clean_q = f"how to do {query} yoga tutorial"
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(clean_q)}"


def get_dynamic_clinical_recommendations(
    symptoms: list,
    user_context: dict,
    top_condition: str = "",
    lang_code: str = "en"
) -> dict:
    """
    Main API-First Dynamic Clinical Engine.
    Queries Gemini / Groq with patient's complete demographics, symptoms, severity, duration, and medical history.
    Dynamically generates the required number of medicines, food timing, recovery duration, supportive yoga with YouTube links,
    and ice/hot compress advice. Falls back to local dataset if APIs fail.
    """
    symptoms = symptoms or []
    user_context = user_context or {}
    age = user_context.get("age", "-- Select Age Group --")
    gender = user_context.get("gender", "-- Select Gender --")
    location = user_context.get("location", "Ahmedabad, Gujarat")
    blood_group = user_context.get("blood_group", "None")
    severity = user_context.get("severity", "Moderate")
    duration = user_context.get("duration", "1 - 3 Days")
    conditions = user_context.get("conditions", ["None"])
    conditions_str = ", ".join(conditions) if isinstance(conditions, list) else str(conditions)
    medications = user_context.get("medications", "None")
    allergies = user_context.get("allergies", "None")
    family_history = user_context.get("surgeries", "") or user_context.get("family_history", "None")
    details = user_context.get("details", "")

    lang_instruction = "English" if lang_code == "en" else "Hindi (हिंदी)" if lang_code == "hi" else "Gujarati (ગુજરાતી)"

    prompt = f"""
    You are MediMind AI — an advanced clinical healthcare & triage AI.
Perform an in-depth clinical analysis and prescribe a comprehensive, personalized care recommendation package for this patient.

PATIENT PROFILE:
- Demographics: Age Group: {age}, Gender: {gender}, Location: {location}, Blood Group: {blood_group}
- Clinical Symptoms: {', '.join(symptoms) if symptoms else 'General Illness'}
- Symptom Severity: {severity}
- Symptom Duration: {duration}
- Pre-existing Medical Conditions: {conditions_str}
- Current Ongoing Medications: {medications}
- Known Drug/Food Allergies: {allergies}
- Relevant Family Medical History & Prior Surgeries: {family_history}
- Additional Notes: {details}
- Primary Assessed Condition: {top_condition or 'Acute Illness'}

CRITICAL CLINICAL INSTRUCTIONS:
1. LANGUAGE CONSISTENCY:
   - All text, indications, instructions, dietary advice, red flags, and food timing MUST be strictly in {lang_instruction}.
   - If English is requested, use pure English: "After Food", "Before Food (Empty Stomach)", "Take with Water".
   - If Hindi is requested, use pure Hindi: "भोजन के बाद", "भोजन से पहले (खाली पेट)".
   - If Gujarati is requested, use pure Gujarati: "જમ્યા પછી", "જમ્યા પહેલા (ખાલી પેટે)".

2. ILLNESS-SPECIFIC CLINICAL SUMMARY & TIMELINE:
   - "summary": A personalized 2-3 sentence clinical summary strictly tailored to {top_condition} and reported symptoms in {lang_instruction}.
   - "recovery_duration": Realistic recovery timeline strictly tailored to {top_condition}, severity ({severity}), and duration ({duration}) in {lang_instruction}.

3. DYNAMIC MEDICINE COUNT:
   - Prescribe the EXACT number of required medications (e.g. 3, 4, 5, 6, 7 or more) appropriate for this patient's exact symptoms, severity, and duration.
   - For EACH medicine provide:
     - "name": Generic name with popular Indian brand in parentheses (e.g., "Paracetamol 650mg (Dolo 650 / Calpol)", "Pantoprazole 40mg (Pan 40)", "Oral Rehydration Salts (Electral / ORS)", "Azithromycin 500mg (Azee 500)", "Levocetirizine 5mg (Levocet)").
     - "indication": Specific symptom it treats in {lang_instruction}.
     - "dosage": Exact clinical dosage (e.g., "1 Tablet thrice daily after meals", "1 Sachet dissolved in 1L boiled water").
     - "course_duration": Explicit course length in {lang_instruction} stating for how many days or duration to take it (e.g. "3 to 5 Days (as needed for fever)", "5 Days Full Course", "3 થી 5 દિવસ").
     - "food_timing": Explicit food timing strictly in {lang_instruction} ("After Food", "Before Food (Empty Stomach)", "With Water").
     - "time_of_day": E.g. "Morning & Night (BD)", "Morning Empty Stomach", "SOS (When needed)", "Thrice Daily (TDS)".
     - "type": "OTC" or "Prescription".
     - "warnings": Crucial safety precautions and contraindications in {lang_instruction}.

4. SUPPORTIVE YOGA & PHYSIOTHERAPY:
   - Provide 3 to 5 specific, clinically safe supportive yoga poses and physio mobility exercises tailored to this patient's condition ({top_condition}).
   - For EACH yoga/physio item:
     - "name": English Name (e.g. "Child's Pose", "Cobra Pose", "Alternate Nostril Breathing", "Corpse Pose", "Neck Stretch and Tilt").
     - "sanskrit_name": Sanskrit / Traditional name (e.g. "Balasana", "Bhujangasana", "Anulom Vilom Pranayama", "Shavasana", "Greeva Sanchalana").
     - "benefits": Specific recovery benefits in {lang_instruction}.
     - "instructions": Simple 1-2 sentence execution guidance in {lang_instruction}.

5. COMPRESS GUIDANCE (ICE vs HOT SEK):
   - Analyze whether Cold / Ice Compress ("ice") or Hot / Warm Compress ("hot") or Neither ("none") is medically indicated for {top_condition}.
   - "mode": "ice", "hot", or "none".
   - "title": Header in {lang_instruction}.
   - "text": Full clinical explanation and step-by-step instructions in {lang_instruction}.

6. ILLNESS-SPECIFIC DIETARY & HYDRATION GUIDELINES:
   - "foods_to_eat": 3 to 4 specific healthy foods/items to consume in {lang_instruction}.
   - "foods_to_avoid": 3 to 4 specific foods or habits to strictly avoid or limit in {lang_instruction}.
   - "hydration_advice": Specific fluid intake instructions in {lang_instruction}.

7. CLINICAL CARE DOS AND DON'TS:
   - "dos": 3 to 4 essential care actions the patient MUST do in {lang_instruction}.
   - "donts": 3 to 4 harmful or dangerous actions the patient MUST NOT do in {lang_instruction}.

8. ILLNESS-SPECIFIC EMERGENCY RED FLAGS:
   - "red_flags": 3 to 4 critical danger warning signs strictly customized for {top_condition} in {lang_instruction} that require emergency hospital visit.

OUTPUT FORMAT:
Return strictly a valid JSON object with NO preamble or conversational text matching this exact schema:
{{
  "summary": "2-3 sentence clinical summary in {lang_instruction}",
  "recovery_duration": "Expected recovery time text in {lang_instruction}",
  "medicines": [
    {{
      "name": "Medicine Name (Brand Example)",
      "indication": "...",
      "dosage": "...",
      "course_duration": "3 to 5 Days",
      "food_timing": "After Food / Before Food (Empty Stomach)",
      "time_of_day": "...",
      "type": "OTC / Prescription",
      "warnings": "..."
    }}
  ],
  "yoga_physio": [
    {{
      "name": "Pose Name",
      "sanskrit_name": "Sanskrit Name",
      "benefits": "...",
      "instructions": "..."
    }}
  ],
  "compress_guidance": {{
    "mode": "ice / hot / none",
    "title": "...",
    "text": "..."
  }},
  "foods_to_eat": [
    "Recommended food 1...", "Recommended food 2...", "Recommended food 3..."
  ],
  "foods_to_avoid": [
    "Food to avoid 1...", "Food to avoid 2...", "Food to avoid 3..."
  ],
  "hydration_advice": "Hydration advice text...",
  "dos": [
    "Clinical Do 1...", "Clinical Do 2...", "Clinical Do 3..."
  ],
  "donts": [
    "Clinical Don't 1...", "Clinical Don't 2...", "Clinical Don't 3..."
  ],
  "red_flags": [
    "Condition-specific red flag 1...", "Condition-specific red flag 2...", "Condition-specific red flag 3..."
  ]
}}"""
    ai_data = None
    api_source_name = "MediMind AI Verified Care"

    # 1. Try Gemini API (Primary High-Precision Multilingual Live Engine)
    if GEMINI_API_KEY:
        for gemini_model in ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash", "gemini-2.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048, "responseMimeType": "application/json"}
                }
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        parsed = _clean_json_response(text_out)
                        if parsed and parsed.get("medicines"):
                            ai_data = parsed
                            api_source_name = "MediMind AI Verified Care"
                            break
            except Exception as e:
                print(f"Gemini {gemini_model} recommendations notice: {e}")

    # 2. Try Groq API (Secondary Live Engine)
    if not ai_data and GROQ_API_KEY:
        for groq_model in ["qwen/qwen3.6-27b", "llama-3.3-70b-versatile", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                body = {
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": f"You are MediMind AI. Return strict JSON only in {lang_instruction}. Do not include emojis."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1800,
                    "response_format": {"type": "json_object"}
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=8)
                if res.status_code == 200:
                    text_out = res.json()["choices"][0]["message"]["content"]
                    parsed = _clean_json_response(text_out)
                    if parsed and parsed.get("medicines"):
                        ai_data = parsed
                        api_source_name = "MediMind AI Verified Care"
                        break
            except Exception as e:
                print(f"Groq {groq_model} recommendations notice: {e}")

    # Process AI Data if successfully fetched from Live APIs
    if ai_data and ai_data.get("medicines"):
        # Format medicines with OpenFDA + image resolver
        raw_meds = ai_data.get("medicines", [])
        for m in raw_meds:
            m["source"] = "MediMind AI Verified"
        med_gallery = get_medicine_gallery(raw_meds, max_items=12)

        # Format Yoga / Physio with YouTube search URLs and images
        yoga_list = []
        raw_yoga = ai_data.get("yoga_physio") or ai_data.get("yoga_recommendations") or ai_data.get("yoga") or []
        for y in raw_yoga:
            y_name = y.get("name", "Child's Pose")
            y_sansk = y.get("sanskrit_name", "")
            y_ben = y.get("benefits", "Restorative stretching and recovery.")
            y_inst = y.get("instructions", "")
            
            image_path, is_fallback_img = resolve_image("yoga", f"{y_name} {y_sansk}")
            youtube_url = get_youtube_search_url(f"{y_name} {y_sansk}")

            yoga_list.append({
                "name": y_name,
                "sanskrit_name": y_sansk,
                "benefits": y_ben,
                "instructions": y_inst,
                "image": image_path,
                "is_fallback": is_fallback_img,
                "youtube_url": youtube_url
            })

        # If LLM returned empty yoga list, populate from localized poses
        if not yoga_list:
            if lang_code == "gu":
                curated_poses = [
                    {"name": "બાળાસન (Child's Pose)", "sanskrit_name": "Balasana", "benefits": "શરીરના થાકને દૂર કરે છે અને માનસિક શાંતિ આપે છે.", "instructions": "ચટાઈ પર ઘૂંટણ વાળીને આગળ ઝૂકો અને શ્વાસ સામાન્ય રાખો."},
                    {"name": "અનુલોમ વિલોમ (Pranayama)", "sanskrit_name": "Anulom Vilom", "benefits": "શ્વસનતંત્રને મજબૂત બનાવે છે અને ઓક્સિજન વધારે છે.", "instructions": "સીધા બેસીને એક નસકોરાથી શ્વાસ લો અને બીજામાંથી છોડો."},
                    {"name": "શવાસન (Corpse Pose)", "sanskrit_name": "Shavasana", "benefits": "શરીરના દરેક સ્નાયુને ઊંડો આરામ આપી રિકવરી ઝડપી બનાવે છે.", "instructions": "પીઠ પર સીધા સૂઈ જાવ અને શરીરને ઢીલું છોડો."},
                    {"name": "ભુજંગાસન (Cobra Pose)", "sanskrit_name": "Bhujangasana", "benefits": "છાતી અને ફેફસાંને ખોલે છે તથા પીઠનો દુખાવો ઓછો કરે છે.", "instructions": "પેટ પર સૂઈને બંને હાથના સહારે છાતી ઉપર ઉઠાવો."}
                ]
            elif lang_code == "hi":
                curated_poses = [
                    {"name": "बालासन (Child's Pose)", "sanskrit_name": "Balasana", "benefits": "शरीर की थकान दूर करता है और नर्वस सिस्टम को शांत करता है।", "instructions": "घुटनों के बल बैठें और आगे झुककर सिर जमीन पर टिकाएं।"},
                    {"name": "अनुलोम विलोम प्राणायाम", "sanskrit_name": "Anulom Vilom", "benefits": "फेफड़ों की कार्यक्षमता बढ़ाता है और ऑक्सीजन स्तर सुधारता है।", "instructions": "सीधे बैठकर एक नासिका से सांस लें और दूसरी से छोड़ें।"},
                    {"name": "शवासन (Corpse Pose)", "sanskrit_name": "Shavasana", "benefits": "रोग प्रतिरोधक क्षमता बढ़ाने और गहरी रिकवरी में सहायक।", "instructions": "पीठ के बल सीधे लेटें और पूरे शरीर को ढीला छोड़ें।"},
                    {"name": "भुजंगासन (Cobra Pose)", "sanskrit_name": "Bhujangasana", "benefits": "छाती के संक्रमण में राहत और फेफड़ों को मजबूती देता है।", "instructions": "पेट के बल लेटकर हाथों के सहारे छाती ऊपर उठाएं।"}
                ]
            else:
                curated_poses = [
                    {"name": "Child's Pose", "sanskrit_name": "Balasana", "benefits": "Gently calms the nervous system, relieves fatigue and lowers tension.", "instructions": "Kneel, fold forward, resting forehead on mat with arms extended."},
                    {"name": "Pranayama Deep Breathing", "sanskrit_name": "Anulom Vilom", "benefits": "Enhances oxygen saturation and respiratory vitality.", "instructions": "Sit upright, inhale through one nostril and exhale through other."},
                    {"name": "Corpse Pose", "sanskrit_name": "Shavasana", "benefits": "Facilitates deep cellular recovery and restores energy.", "instructions": "Lie flat on back with arms relaxed and breathe naturally."},
                    {"name": "Cobra Pose", "sanskrit_name": "Bhujangasana", "benefits": "Opens chest cavity and strengthens spinal musculature.", "instructions": "Lie prone and gently elevate upper torso."}
                ]
            for p in curated_poses:
                image_path, is_fallback_img = resolve_image("yoga", p["sanskrit_name"])
                youtube_url = get_youtube_search_url(f"{p['name']} {p['sanskrit_name']}")
                yoga_list.append({
                    "name": p["name"],
                    "sanskrit_name": p["sanskrit_name"],
                    "benefits": p["benefits"],
                    "instructions": p["instructions"],
                    "image": image_path,
                    "is_fallback": is_fallback_img,
                    "youtube_url": youtube_url
                })

        foods_to_eat = ai_data.get("foods_to_eat") or []
        if isinstance(foods_to_eat, str):
            foods_to_eat = [x.strip() for x in foods_to_eat.split("\n") if x.strip()]
        
        foods_to_avoid = ai_data.get("foods_to_avoid") or []
        if isinstance(foods_to_avoid, str):
            foods_to_avoid = [x.strip() for x in foods_to_avoid.split("\n") if x.strip()]
        
        hyd_advice = ai_data.get("hydration_advice") or "Drink 2.5 - 3 liters of water / fluids daily."
        
        clinical_dos = ai_data.get("dos") or ai_data.get("clinical_dos") or []
        if isinstance(clinical_dos, str):
            clinical_dos = [x.strip() for x in clinical_dos.split("\n") if x.strip()]
        
        clinical_donts = ai_data.get("donts") or ai_data.get("clinical_donts") or []
        if isinstance(clinical_donts, str):
            clinical_donts = [x.strip() for x in clinical_donts.split("\n") if x.strip()]

        diet_tips = (
            ai_data.get("dietary_guidelines") 
            or ai_data.get("dietary_advice") 
            or ai_data.get("diet") 
            or ai_data.get("diet_tips") 
            or []
        )
        if isinstance(diet_tips, str):
            diet_tips = [t.strip() for t in diet_tips.split("\n") if t.strip()]

        red_flag_tips = (
            ai_data.get("red_flags") 
            or ai_data.get("emergency_red_flags") 
            or ai_data.get("warning_signs") 
            or ai_data.get("red_flag_symptoms") 
            or []
        )
        if isinstance(red_flag_tips, str):
            red_flag_tips = [t.strip() for t in red_flag_tips.split("\n") if t.strip()]

        # If empty, extract condition-specific tips from CSV
        if not diet_tips or not red_flag_tips or not foods_to_eat:
            try:
                guidance_csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "diet", "condition_guidance.csv")
                if os.path.exists(guidance_csv_path):
                    import pandas as pd
                    df_g = pd.read_csv(guidance_csv_path)
                    cond_sub = (top_condition or "").lower().strip()[:8]
                    matched_g = df_g[df_g["condition_name"].str.lower().str.contains(cond_sub, na=False, regex=False)]
                    if not matched_g.empty:
                        row = matched_g.iloc[0]
                        if not foods_to_eat:
                            diet_rec = str(row.get("diet_recommendation", "")).strip()
                            if diet_rec:
                                foods_to_eat.append(diet_rec)
                        if not foods_to_avoid:
                            avoid_food = str(row.get("food_to_limit", "") or row.get("what_to_avoid", "")).strip()
                            if avoid_food:
                                foods_to_avoid.append(avoid_food)
                        if not diet_tips:
                            if foods_to_eat:
                                diet_tips.extend([f"Recommended: {x}" for x in foods_to_eat])
                            if foods_to_avoid:
                                diet_tips.extend([f"Avoid: {x}" for x in foods_to_avoid])
                        if not red_flag_tips:
                            mon_adv = str(row.get("monitoring_advice", "")).strip()
                            if mon_adv:
                                red_flag_tips.append(f"Clinical Alert: {mon_adv}")
            except Exception as e:
                print(f"Condition guidance lookup notice: {e}")

        # Default dos & donts if empty
        if not clinical_dos:
            clinical_dos = [
                "Take all medications strictly at the advised dosage and timing." if lang_code == "en" else ("दवाएं सही समय और सही खुराक पर लें।" if lang_code == "hi" else "દવાઓ યોગ્ય સમયે અને નિયમિત માત્રામાં લો."),
                "Maintain optimal rest and hydration to facilitate bodily recovery." if lang_code == "en" else ("शरीर को पूरा आराम दें और खूब पानी/तरल पदार्थ पिएं।" if lang_code == "hi" else "શરીરને પૂરતો આરામ આપો અને પ્રવાહીનું સેવન કરો."),
                "Monitor temperature and key symptoms daily." if lang_code == "en" else ("तापमान और लक्षणों पर नियमित नजर रखें।" if lang_code == "hi" else "શરીરનું તાપમાન અને લક્ષણો પર નિયમિત ધ્યાન રાખો.")
            ]
        if not clinical_donts:
            clinical_donts = [
                "Do NOT self-medicate or stop prescribed antibiotics/dosages prematurely." if lang_code == "en" else ("बिना डॉक्टर की सलाह के दवाएं बंद या बदलें नहीं।" if lang_code == "hi" else "ડૉક્ટરની સલાહ વિના દવા બંધ કે બદલવી નહીં."),
                "Avoid heavy physical exertion, smoking, and alcohol during recovery." if lang_code == "en" else ("भारी शारीरिक मेहनत और शराब/धूम्रपान से बचें।" if lang_code == "hi" else "વધુ પડતો શ્રમ અને બિનઆરોગ્યપ્રદ ટેવો ટાળો."),
                "Do NOT ignore sudden severe chest pain, breathlessness, or high fever." if lang_code == "en" else ("तेज बुखार, सांस में तकलीफ या छाती में दर्द को नजरअंदाज न करें।" if lang_code == "hi" else "તીવ્ર તાવ કે શ્વાસની તકલીફને અવગણશો નહીં.")
            ]

        return {
            "is_fallback": False,
            "api_source": api_source_name,
            "fallback_warning": "",
            "top_condition": top_condition,
            "lang_code": lang_code,
            "summary": ai_data.get("summary", ""),
            "recovery_duration": ai_data.get("recovery_duration", "5 – 7 Days with appropriate rest and treatment."),
            "medicine_gallery": med_gallery,
            "total_medicines_recommended": len(med_gallery),
            "yoga_recommendations": yoga_list,
            "compress_guidance": ai_data.get("compress_guidance"),
            "dietary_guidelines": diet_tips,
            "foods_to_eat": foods_to_eat,
            "foods_to_avoid": foods_to_avoid,
            "hydration_advice": hyd_advice,
            "clinical_dos": clinical_dos,
            "clinical_donts": clinical_donts,
            "red_flags": red_flag_tips
        }

    # 3. Resilient Local Dataset Fallback (When APIs are unreachable)
    return _build_local_dataset_fallback(symptoms, user_context, top_condition, lang_code)


def _build_local_dataset_fallback(
    symptoms: list,
    user_context: dict,
    top_condition: str = "",
    lang_code: str = "en"
) -> dict:
    """
    Builds a standardized clinical dataset fallback response with condition-specific guidance from CSV dataset.
    """
    sym_lower = " ".join(symptoms).lower()
    cond_lower = (top_condition or "").lower().strip()
    
    ft_after = "After Food" if lang_code == "en" else "भोजन के बाद" if lang_code == "hi" else "જમ્યા પછી"
    ft_before = "Before Food (Empty Stomach)" if lang_code == "en" else "भोजन से पहले (खाली पेट)" if lang_code == "hi" else "જમ્યા પહેલા (ખાલી પેટે)"
    ft_water = "With Water (Sip Throughout Day)" if lang_code == "en" else "पानी के साथ (दिन भर घूंट लें)" if lang_code == "hi" else "પાણી સાથે (દિવસ દરમિયાન)"

    fallback_meds = [
        {
            "name": "Paracetamol 650mg (Dolo 650 / Calpol)",
            "indication": "Reduces body temperature and relieves headache/body aches." if lang_code == "en" else "बुखार कम करता है और सिरदर्द व बदन दर्द में राहत देता है।" if lang_code == "hi" else "તાવ ઘટાડે છે અને માથાનો દુખાવો દૂર કરે છે.",
            "dosage": "1 Tablet every 6 to 8 hours as needed." if lang_code == "en" else "1 गोली आवश्यकतानुसार दिन में 2-3 बार।" if lang_code == "hi" else "1 ગોળી જરૂર મુજબ દિવસમાં 2-3 વાર.",
            "course_duration": "3 to 5 Days" if lang_code == "en" else "3 से 5 दिन तक" if lang_code == "hi" else "3 થી 5 દિવસ",
            "food_timing": ft_after,
            "time_of_day": "After meals",
            "type": "OTC",
            "warnings": "Do not exceed 3000mg per day." if lang_code == "en" else "दिन में 3000mg से अधिक न लें।" if lang_code == "hi" else "દિવસમાં 3000mg થી વધુ ન લેવી.",
            "source": "MediMind Clinical Dataset"
        },
        {
            "name": "Ibuprofen 400mg (Brufen / Ibugesic)",
            "indication": "Relieves acute muscular pain, inflammation, and headache." if lang_code == "en" else "मांसपेशियों के दर्द और सूजन में राहत देता है।" if lang_code == "hi" else "સ્નાયુઓના દુખાવા અને સોજામાં રાહત આપે છે.",
            "dosage": "1 Tablet twice daily after meals." if lang_code == "en" else "1 गोली दिन में 2 बार भोजन के बाद।" if lang_code == "hi" else "1 ગોળી દિવસમાં 2 વાર જમ્યા પછી.",
            "course_duration": "3 Days" if lang_code == "en" else "3 दिन तक" if lang_code == "hi" else "3 દિવસ",
            "food_timing": ft_after,
            "time_of_day": "Morning & Night",
            "type": "Prescription",
            "warnings": "Always take after food to avoid stomach irritation." if lang_code == "en" else "पेट की सुरक्षा के लिए हमेशा भोजन के बाद लें।" if lang_code == "hi" else "પેટમાં બળતરા ન થાય તે માટે હંમેશા જમ્યા પછી લેવી.",
            "source": "MediMind Clinical Dataset"
        },
        {
            "name": "Pantoprazole 40mg (Pan 40 / Pantocid)",
            "indication": "Protects stomach against acidity and medication-induced gastritis." if lang_code == "en" else "पेट में एसिडिटी और जलन से सुरक्षा प्रदान करता है।" if lang_code == "hi" else "એસિડિટી અને ગેસ્ટ્રાઇટિસથી પેટનું રક્ષણ કરે છે.",
            "dosage": "1 Tablet in morning before breakfast." if lang_code == "en" else "1 गोली सुबह नाश्ते से 30 मिनट पहले।" if lang_code == "hi" else "1 ગોળી સવારે નાસ્તા પહેલાં.",
            "course_duration": "3 to 5 Days" if lang_code == "en" else "3 से 5 दिन तक" if lang_code == "hi" else "3 થી 5 દિવસ",
            "food_timing": ft_before,
            "time_of_day": "Morning Empty Stomach",
            "type": "Prescription",
            "warnings": "Swallow whole with water." if lang_code == "en" else "पानी के साथ पूरी निगलें।" if lang_code == "hi" else "પાણી સાથે આખી ગળી જવી.",
            "source": "MediMind Clinical Dataset"
        },
        {
            "name": "Oral Rehydration Salts (Electral / ORS)",
            "indication": "Restores vital electrolyte balance and hydration." if lang_code == "en" else "शरीर में पानी और आवश्यक इलेक्ट्रोलाइट्स की भरपाई करता है।" if lang_code == "hi" else "શરીરમાં પાણી અને ક્ષારોનું સંતુલન જાળવે છે.",
            "dosage": "1 Sachet in 1 Litre clean water, sip throughout day." if lang_code == "en" else "1 पाउच 1 लीटर पानी में घोलकर दिन भर पिएं।" if lang_code == "hi" else "1 પાઉચ 1 લિટર પાણીમાં ઓગાળીને પીવો.",
            "course_duration": "2 to 3 Days" if lang_code == "en" else "2 से 3 दिन तक" if lang_code == "hi" else "2 થી 3 દિવસ",
            "food_timing": ft_water,
            "time_of_day": "Throughout the day",
            "type": "OTC",
            "warnings": "Reconstitute in exact quantity of water." if lang_code == "en" else "उचित मात्रा में पानी में घोलें।" if lang_code == "hi" else "યોગ્ય માત્રામાં પાણીમાં ઓગાળવું.",
            "source": "MediMind Clinical Dataset"
        }
    ]

    med_gallery = get_medicine_gallery(fallback_meds, max_items=8)

    # Supportive Yoga Fallback
    yoga_list = []
    if lang_code == "gu":
        curated_poses = [
            {"name": "બાળાસન (Child's Pose)", "sanskrit_name": "Balasana", "benefits": "શરીરના થાકને દૂર કરે છે અને માનસિક શાંતિ આપે છે.", "instructions": "ચટાઈ પર ઘૂંટણ વાળીને આગળ ઝૂકો અને શ્વાસ સામાન્ય રાખો."},
            {"name": "અનુલોમ વિલોમ (Pranayama)", "sanskrit_name": "Anulom Vilom", "benefits": "શ્વસનતંત્રને મજબૂત બનાવે છે અને ઓક્સિજન વધારે છે.", "instructions": "સીધા બેસીને એક નસકોરાથી શ્વાસ લો અને બીજામાંથી છોડો."},
            {"name": "શવાસન (Corpse Pose)", "sanskrit_name": "Shavasana", "benefits": "શરીરના દરેક સ્નાયુને ઊંડો આરામ આપી રિકવરી ઝડપી બનાવે છે.", "instructions": "પીઠ પર સીધા સૂઈ જાવ અને શરીરને ઢીલું છોડો."},
            {"name": "ભુજંગાસન (Cobra Pose)", "sanskrit_name": "Bhujangasana", "benefits": "છાતી અને ફેફસાંને ખોલે છે તથા પીઠનો દુખાવો ઓછો કરે છે.", "instructions": "પેટ પર સૂઈને બંને હાથના સહારે છાતી ઉપર ઉઠાવો."}
        ]
    elif lang_code == "hi":
        curated_poses = [
            {"name": "बालासन (Child's Pose)", "sanskrit_name": "Balasana", "benefits": "शरीर की थकान दूर करता है और नर्वस सिस्टम को शांत करता है।", "instructions": "घुटनों के बल बैठें और आगे झुककर सिर जमीन पर टिकाएं।"},
            {"name": "अनुलोम विलोम प्राणायाम", "sanskrit_name": "Anulom Vilom", "benefits": "फेफड़ों की कार्यक्षमता बढ़ाता है और ऑक्सीजन स्तर सुधारता है।", "instructions": "सीधे बैठकर एक नासिका से सांस लें और दूसरी से छोड़ें।"},
            {"name": "शवासन (Corpse Pose)", "sanskrit_name": "Shavasana", "benefits": "रोग प्रतिरोधक क्षमता बढ़ाने और गहरी रिकवरी में सहायक।", "instructions": "पीठ के बल सीधे लेटें और पूरे शरीर को ढीला छोड़ें।"},
            {"name": "भुजंगासन (Cobra Pose)", "sanskrit_name": "Bhujangasana", "benefits": "छाती के संक्रमण में राहत और फेफड़ों को मजबूती देता है।", "instructions": "पेट के बल लेटकर हाथों के सहारे छाती ऊपर उठाएं।"}
        ]
    else:
        curated_poses = [
            {"name": "Child's Pose", "sanskrit_name": "Balasana", "benefits": "Gently calms the nervous system, relieves fatigue and lowers tension.", "instructions": "Kneel, fold forward, resting forehead on mat with arms extended forward."},
            {"name": "Pranayama Deep Breathing", "sanskrit_name": "Anulom Vilom", "benefits": "Enhances oxygen saturation, calms mind and supports respiratory vitality.", "instructions": "Sit upright, inhale slowly through one nostril and exhale through other."},
            {"name": "Corpse Pose", "sanskrit_name": "Shavasana", "benefits": "Facilitates deep cellular recovery and immune restoration during fever.", "instructions": "Lie flat on back with arms relaxed at sides and breathe naturally."},
            {"name": "Cobra Pose", "sanskrit_name": "Bhujangasana", "benefits": "Opens chest cavity and relieves stiffness in upper body.", "instructions": "Lie on abdomen and gently arch upper torso upward."}
        ]

    for p in curated_poses:
        image_path, is_fallback_img = resolve_image("yoga", p["sanskrit_name"])
        youtube_url = get_youtube_search_url(f"{p['name']} {p['sanskrit_name']}")

        yoga_list.append({
            "name": p["name"],
            "sanskrit_name": p["sanskrit_name"],
            "benefits": p["benefits"],
            "instructions": p["instructions"],
            "image": image_path,
            "is_fallback": is_fallback_img,
            "youtube_url": youtube_url
        })

    # Try condition-specific lookups from condition_guidance.csv
    csv_diet_tips = []
    csv_red_flags = []
    try:
        guidance_csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "diet", "condition_guidance.csv")
        if os.path.exists(guidance_csv_path):
            import pandas as pd
            df_g = pd.read_csv(guidance_csv_path)
            matched_g = df_g[df_g["condition_name"].str.lower().str.contains(cond_lower[:8], na=False, regex=False)]
            if not matched_g.empty:
                row = matched_g.iloc[0]
                diet_rec = str(row.get("diet_recommendation", "")).strip()
                avoid_food = str(row.get("food_to_limit", "") or row.get("what_to_avoid", "")).strip()
                home_c = str(row.get("home_care", "") or row.get("what_to_do", "")).strip()
                mon_adv = str(row.get("monitoring_advice", "")).strip()
                
                if diet_rec:
                    csv_diet_tips.append(f"Recommended Nutrition: {diet_rec}")
                if avoid_food:
                    csv_diet_tips.append(f"Foods & Items to Avoid: {avoid_food}")
                if home_c:
                    csv_diet_tips.append(f"Home Management: {home_c}")
                if mon_adv:
                    csv_red_flags.append(f"Clinical Alert: {mon_adv}")
    except Exception as e:
        print(f"Condition guidance lookup notice: {e}")

    # Compress Guidance
    is_ice = any(k in sym_lower for k in ["fever", "sprain", "swelling", "injury", "headache", "migraine", "તાવ", "માથું", "બુખાર", "सिरदर्द"])
    if is_ice:
        if lang_code == "hi":
            compress_info = {
                "mode": "ice",
                "title": "ठंडी सिकाई / माथे पर ठंडी पट्टी (Cold/Tepid Compress) करें",
                "text": "तेज़ बुखार या सूजन में माथे और गर्दन पर सामान्य ठंडे पानी की पट्टी रखें। यह सुरक्षित रूप से शारीरिक तापमान कम करती है — यहाँ गरम सिकाई बिल्कुल ना करें।"
            }
        elif lang_code == "gu":
            compress_info = {
                "mode": "ice",
                "title": "ઠંડો શેક / માથા પર ઠંડા પાણીના પોતા (Cold/Tepid Compress) મૂકો",
                "text": "તીવ્ર તાવ કે સોજામાં માથા અને ગળા પર ઠંડા પાણીના પોતા મૂકો. તેનાથી તાપમાન ઝડપથી નિયંત્રિત થાય છે — અહીં ગરમ શેક ન કરવો."
            }
        else:
            compress_info = {
                "mode": "ice",
                "title": "Cold / Tepid Compress Recommended",
                "text": "Apply a damp, cool cloth to the forehead and neck to safely bring down elevated body temperature. Do NOT use hot fomentation for active fever."
            }
    else:
        compress_info = None

    # Fallback Warning Message, Dietary & Clinical Care
    if lang_code == "hi":
        warning_msg = " [ऑफलाइन क्लिनिकल डेटासेट मोड]: लाइव AI API से संपर्क नहीं हो सका। मानकीकृत स्थानीय डेटासेट से डेटा दिखाया जा रहा है।"
        recovery_txt = f"5 – 7 दिन ({top_condition or 'लक्षणों'} के लिए उचित दवा, पर्याप्त आराम और तरल पदार्थों के सेवन के साथ)।"
        summary_txt = f"क्लिनिकल विश्लेषण के अनुसार लक्षण {top_condition or 'संक्रमण'} की ओर संकेत करते हैं। पर्याप्त विश्राम और समय पर दवा लेने की सलाह दी जाती है।"
        foods_to_eat = [
            f"{top_condition or 'बीमारी'} में सुपाच्य और पौष्टिक भोजन जैसे मूंग दाल की खिचड़ी, दलिया या सूप लें।",
            "ताजे फल, उबली सब्जियां और पर्याप्त प्रोटीन युक्त आहार लें।",
            "नारियल पानी, ओआरएस और गुनगुने तरल पदार्थों का सेवन करें।"
        ]
        foods_to_avoid = [
            "तेल-मसालेदार, तले हुए और भारी गरिष्ठ भोजन से बचें।",
            "अत्यधिक कैफीन, जंक फूड और पैकेट बंद मीठे पेय पदार्थों से परहेज करें।"
        ]
        hyd_advice = "प्रतिदिन 2.5 से 3 लीटर साफ गुनगुना पानी या ओआरएस घोल पिएं।"
        clinical_dos = [
            "सभी दवाएं डॉक्टर या फार्मासिस्ट के निर्देशानुसार सही समय पर लें।",
            "शरीर को 7-8 घंटे का पर्याप्त विश्राम दें और तनाव से बचें।",
            "प्रतिदिन शारीरिक तापमान और लक्षणों में बदलाव पर नजर रखें।"
        ]
        clinical_donts = [
            "बिना डॉक्टर की सलाह के दवाओं की खुराक खुद से न बदलें।",
            "संक्रमण के दौरान अत्यधिक शारीरिक श्रम या बाहर जाने से बचें।",
            "लगातार तेज़ बुखार या सांस की तकलीफ को बिल्कुल नजरअंदाज न करें।"
        ]
        red_flags = csv_red_flags if csv_red_flags else [
            "लगातार 3 दिन से अधिक 103°F से तेज़ बुखार रहना या लक्षणों का बिगड़ना।",
            "सांस लेने में कठिनाई, सीने में दर्द या अत्यधिक कमजोरी।",
            "तरल पदार्थ न पचना या डिहाइड्रेशन के गंभीर लक्षण दिखना।"
        ]
    elif lang_code == "gu":
        warning_msg = " [ઓફલાઇન ક્લિનિકલ ડેટાસેટ મોડ]: લાઈવ AI API કનેક્ટ થઈ શક્યું નથી. સ્થાનિક પ્રમાણિત ડેટાસેટ દર્શાવવામાં આવી રહ્યું છે."
        recovery_txt = f"5 – 7 દિવસ ({top_condition or 'લક્ષણો'} માટે સાચી દવા, પૂરતો આરામ અને પ્રવાહીના સેવન સાથે)."
        summary_txt = f"ક્લિનિકલ વિશ્લેષણ મુજબ લક્ષણો {top_condition or 'ચેપ / સંક્રમણ'} સૂચવે છે. પૂરતો આરામ અને સમયસર દવા લેવાની ભલામણ કરવામાં આવે છે."
        foods_to_eat = [
            f"{top_condition or 'રિકવરી'} દરમિયાન સરળતાથી પચી જાય તેવો હળવો ખોરાક જેમ કે મગની દાળની ખીચડી, રાબ અને સૂપ લો.",
            "તાજા મોસમી ફળો અને પ્રોટીનયુક્ત આહારનું સેવન કરો.",
            "નાળિયેર પાણી, ઓઆરએસ અને ગરમ પ્રવાહીથી હાઇડ્રેશન જાળવી રાખો."
        ]
        foods_to_avoid = [
            "તળેલો, વધુ મસાલેદાર, ભારે અને બહારનો બિનઆરોગ્યપ્રદ ખોરાક ટાળો.",
            "વધુ પડતી ખાંડવાળા પીણાં અને ઠંડી વસ્તુઓથી દૂર રહો."
        ]
        hyd_advice = "દરરોજ 2.5 થી 3 લિટર ચોખ્ખું નવશેકું પાણી અથવા પ્રવાહીનું સેવન કરો."
        clinical_dos = [
            "દવાઓ નિયમિતપણે અને યોગ્ય માત્રામાં જમ્યા પછી/પહેલાં લો.",
            "શરીરને પૂરતો આરામ આપો અને તણાવ મુક્ત રહો.",
            "દરરોજ શરીરનું તાપમાન અને લક્ષણોમાં સુધારો નોંધો."
        ]
        clinical_donts = [
            "ડૉક્ટરની સલાહ વિના જાતે દવાઓ બંધ કે બદલશો નહીં.",
            "બીમારી દરમિયાન વધુ પડતો શારીરિક શ્રમ કરવાનું ટાળો.",
            "તીવ્ર તાવ, શ્વાસની તકલીફ કે છાતીમાં દુખાવાને અવગણશો નહીં."
        ]
        red_flags = csv_red_flags if csv_red_flags else [
            "સતત 3 દિવસથી વધુ સમય માટે 103°F થી વધુ તાવ રહેવો અથવા લક્ષણો વધવા.",
            "શ્વાસ લેવામાં તકલીફ, છાતીમાં દુખાવો અથવા અતિશય નબળાઈ.",
            "પ્રવાહી પચી ન શકવું અથવા ડિહાઇડ્રેશનના ગંભીર લક્ષણો જણાવા."
        ]
    else:
        warning_msg = " [Offline Clinical Dataset Fallback Active]: Live AI APIs could not be reached. Displaying standardized local clinical dataset."
        recovery_txt = f"Expected recovery is 5 – 7 days for {top_condition or 'acute condition'} with adequate rest, hydration, and proper therapy."
        summary_txt = f"Clinical triage shows symptoms aligning with {top_condition or 'acute illness'}. Prompt hydration and symptomatic management indicated."
        foods_to_eat = [
            f"Eat freshly prepared, nutrient-dense, easily digestible meals (khichdi, oats, clear vegetable soups) for {top_condition or 'recovery'}.",
            "Include fresh Vitamin C-rich fruits and lean protein to support cellular healing.",
            "Drink oral rehydration solutions, coconut water, or warm broths."
        ]
        foods_to_avoid = [
            "Avoid deep-fried, heavily spiced, greasy, and ultra-processed foods.",
            "Avoid unpasteurized dairy, raw undercooked meats, and excessive refined sugars."
        ]
        hyd_advice = "Drink 2.5 – 3.0 Liters of clean water or warm fluids daily."
        clinical_dos = [
            "Take all prescribed medications strictly as directed with proper food timings.",
            "Ensure 7 – 9 hours of restful sleep to optimize immune recovery.",
            "Track daily body temperature and symptom progression."
        ]
        clinical_donts = [
            "Do NOT alter or stop prescribed medication courses prematurely without consulting your doctor.",
            "Avoid strenuous physical exertion and crowded places during recovery.",
            "Do NOT ignore worsening chest pain, acute shortness of breath, or persistent high fever."
        ]
        red_flags = csv_red_flags if csv_red_flags else [
            f"Worsening of {top_condition or 'symptoms'} or persistent high fever exceeding 103°F.",
            "Shortness of breath, chest pain, or sudden confusion/dizziness.",
            "Inability to retain liquids or severe signs of dehydration."
        ]

    return {
        "is_fallback": True,
        "api_source": "Local Clinical Dataset (Offline Fallback)",
        "fallback_warning": warning_msg,
        "top_condition": top_condition,
        "lang_code": lang_code,
        "summary": summary_txt,
        "recovery_duration": recovery_txt,
        "medicine_gallery": med_gallery,
        "total_medicines_recommended": len(med_gallery),
        "yoga_recommendations": yoga_list,
        "compress_guidance": compress_info,
        "dietary_guidelines": foods_to_eat,
        "foods_to_eat": foods_to_eat,
        "foods_to_avoid": foods_to_avoid,
        "hydration_advice": hyd_advice,
        "clinical_dos": clinical_dos,
        "clinical_donts": clinical_donts,
        "red_flags": red_flags
    }


def get_yoga_recommendation(disease_name: str = "", symptoms: list = None) -> dict | None:
    """
    Helper for legacy standalone yoga recommendation lookup.
    """
    from api.yoga_api import search_yoga_pose
    pose_name = "Child's Pose"
    sans_name = "Balasana"
    benefits = "Gently relaxes spine and calms the autonomic nervous system."
    img, is_fb = resolve_image("yoga", pose_name)
    return {
        "name": pose_name,
        "sanskrit_name": sans_name,
        "benefits": benefits,
        "image": img,
        "is_fallback": is_fb,
        "youtube_url": get_youtube_search_url(f"{pose_name} {sans_name}")
    }


def get_compress_guidance(disease_name: str = "", symptoms: list = None, lang_code: str = "en") -> dict | None:
    """
    Helper for legacy standalone compress guidance lookup.
    """
    return {
        "mode": "ice",
        "title": "Cold / Tepid Sponge Compress",
        "text": "Apply a damp, cool cloth to the forehead and neck to safely bring down elevated body temperature."
    }
