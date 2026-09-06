"""
    MediMind AI - Multilingual Conversational Healthcare Assistant
Powered by Groq & Gemini Online Generative AI with strict clinical guardrails
and customer-care style dynamic question tree generation.
"""
import os
import re
import json
import requests
from config.settings import GEMINI_API_KEY, GROQ_API_KEY

def generate_dynamic_patient_questions(clinical_context: dict = None, lang_code: str = "en") -> list:
    """
    Generates 4-5 contextual, customer-care style guided questions in the user's preferred language,
    tailored to the exact symptoms, condition, and medicines currently entered (Zero Emojis).
    """
    clinical_context = clinical_context or {}
    symptoms = clinical_context.get("symptoms", [])
    top_disease = clinical_context.get("top_disease", "")
    medicines = clinical_context.get("medicines", [])
    
    sym_name = symptoms[0] if symptoms else ""
    disease_name = top_disease if top_disease else "my condition"
    med_name = medicines[0].get("medicine_name", "Paracetamol").split()[0] if medicines else "Dolo / Paracetamol"
    
    if lang_code == "hi":
        questions = [
            {"label": f"{med_name} कब और कैसे लेनी चाहिए?", "query": f"{med_name} दवा की खुराक (Dosage), लेने का सही समय और सावधानियां बताएं।"},
            {"label": f"{disease_name or 'इस बीमारी'} में क्या परहेज करें?", "query": f"{disease_name or sym_name} में क्या खाना चाहिए और क्या परहेज (Foods to avoid) करना चाहिए?"},
            {"label": "खतरे के संकेत: डॉक्टर को कब दिखाएं?", "query": f"{sym_name or disease_name} में कौन से गंभीर लक्षण (Red-flag symptoms) दिखने पर तुरंत डॉक्टर के पास जाना चाहिए?"},
            {"label": "लक्षणों का सरल भाषा में अर्थ समझें", "query": f"मेरे बताए गए लक्षणों ({', '.join(symptoms) if symptoms else 'स्वास्थ्य स्थिति'}) का सरल भाषा में क्या मतलब है?"},
            {"label": "MediMind AI कैसे मदद करता है?", "query": "MediMind AI क्या है और यह मरीजों की स्वास्थ्य जांच व दवाइयों में कैसे मदद करता है?"}
        ]
    elif lang_code == "gu":
        questions = [
            {"label": f"{med_name} ક્યારે અને કેટલી લેવી?", "query": f"{med_name} દવા ક્યારે લેવી, યોગ્ય ડોઝ અને શું સાવચેતી રાખવી?"},
            {"label": f"{disease_name or 'આ તકલીફ'}માં શું પરહેજ રાખવો?", "query": f"{disease_name or sym_name} માં શું ખાવું જોઈએ અને કઈ વસ્તુઓનો પરહેજ કરવો?"},
            {"label": "ક્યારે ડૉક્ટરને તાત્કાલિક બતાવવું?", "query": f"{sym_name or disease_name} માં કયા ગંભીર લક્ષણો જણાય તો તરત જ ડૉક્ટર પાસે જવું જોઈએ?"},
            {"label": "મારા લક્ષણો સરળ ભાષામાં સમજાવો", "query": f"મેં આપેલા લક્ષણો ({', '.join(symptoms) if symptoms else 'આરોગ્ય સ્થિતિ'}) નો સરળ ભાષામાં શું અર્થ થાય છે?"},
            {"label": "MediMind AI શું છે?", "query": "MediMind AI શું છે અને તે દર્દીઓને કેવી રીતે મદદ કરે છે?"}
        ]
    else:
        questions = [
            {"label": f"When & how to take {med_name}?", "query": f"What is the recommended dosage, timing, and precautions for {med_name}?"},
            {"label": f"Diet & foods to avoid in {disease_name or 'this condition'}?", "query": f"What foods should I eat and what dietary restrictions should I follow for {disease_name or sym_name}?"},
            {"label": "When to consult a doctor urgently?", "query": f"What are the red-flag emergency symptoms for {sym_name or disease_name} that require immediate medical attention?"},
            {"label": "Explain my symptoms in simple terms", "query": f"Can you explain what my symptoms ({', '.join(symptoms) if symptoms else 'health query'}) mean in simple, plain language?"},
            {"label": "What is MediMind AI & how it works?", "query": "What is MediMind AI and how does it assist patients with symptom triage and medication safety?"}
        ]
    return questions


def detect_redirect_action(text: str, lang_code: str = "en"):
    """
    Detects if the user query or assistant reply pertains to a specific MediMind app module
    and returns target panel info for rendering interactive redirect buttons in the chat.
    """
    if not text:
        return None
    t = text.lower()
    
    # 1. Medical Report Scanner / Prescription / Radiology / Blood Test
    if any(w in t for w in [
        "lab report", "blood report", "medical report", "scan report", "upload report", "report scan", 
        "x-ray", "mri", "ct scan", "radiology", "prescription", "percha", "parcha", 
        "रिपोर्ट", "परचा", "खून की जांच", "रक्त परीक्षण",
        "પ્રિસ્ક્રિપ્શન", "લેબ રિપોર્ટ", "રિપોર્ટ", "સ્કેન"
    ]):
        labels = {
            "en": "Go to Medical Report Scanner",
            "hi": "मेडिकल रिपोर्ट स्कैनर खोलें",
            "gu": "મેડિકલ રિપોર્ટ સ્કેનર ખોલો"
        }
        return {"panel": "Medical Report", "label": labels.get(lang_code, labels["en"])}
        
    # 2. Nearby Healthcare / Hospital / Clinic / Doctor Locator
    elif any(w in t for w in [
        "hospital", "clinic", "doctor", "nearby", "dispensary", "emergency room", "locate hospital", "find doctor",
        "अस्पताल", "डॉक्टर", "दवाखाना", "क्लिनिक", "नजदीकी अस्पताल",
        "નજીકની હોસ્પિટલ", "હોસ્પિટલ", "દાક્તર", "દવાખાનું"
    ]):
        labels = {
            "en": "Find Nearby Hospitals & Clinics",
            "hi": "पास के अस्पताल व क्लिनिक खोजें",
            "gu": "નજીકના હોસ્પિટલ અને ક્લિનિક શોધો"
        }
        return {"panel": "Nearby Healthcare", "label": labels.get(lang_code, labels["en"])}
        
    # 3. Symptom Assessment & Triage
    elif any(w in t for w in [
        "symptom check", "triage", "start assessment", "check symptoms", "health assessment", "symptom triage",
        "लक्षण जांच", "जांच शुरू करें", "लक्षण विश्लेषण",
        "લક્ષણો તપાસ", "તપાસ શરૂ કરો", "લક્ષણ વિશ્લેષણ"
    ]):
        labels = {
            "en": "Start Health & Symptom Assessment",
            "hi": "स्वास्थ्य व लक्षण जांच शुरू करें",
            "gu": "આરોગ્ય અને લક્ષણ તપાસ શરૂ કરો"
        }
        return {"panel": "Health Assessment", "label": labels.get(lang_code, labels["en"])}
        
    # 4. Health Records / History
    elif any(w in t for w in [
        "health record", "saved report", "my history", "past record", "medical history",
        "रिकॉर्ड", "इतिहास", "पुराने रिकॉर्ड",
        "ઇતિહાસ", "રેકોર્ડ", "જૂના રિપોર્ટ"
    ]):
        labels = {
            "en": "View My Health Records",
            "hi": "स्वास्थ्य रिकॉर्ड देखें",
            "gu": "હેલ્થ રેકોર્ડ જુઓ"
        }
        return {"panel": "Health Records", "label": labels.get(lang_code, labels["en"])}

    # 5. National Command Center / PHC Supply Chain / Stockout / Redistribution
    elif any(w in t for w in [
        "supply chain", "phc", "command center", "stockout", "shortage", "redistribution", "bed capacity", 
        "workforce", "national health", "daskroi", "sanand", "bavla", "olpad", "insulin stock",
        "सप्लाई चेन", "कमान केंद्र", "दवा की कमी", "पुनर्वितरण", "पीएचसी", "बेड उपलब्धता",
        "સપ્લાય ચેઈન", "કમાન્ડ સેન્ટર", "દવા અછત", "રીડિસ્ટ્રિબ્યુશન", "બેડ ઉપલબ્ધતા"
    ]):
        labels = {
            "en": "Open National Command Center",
            "hi": "राष्ट्रीय कमान केंद्र खोलें",
            "gu": "રાષ્ટ્રીય કમાન્ડ સેન્ટર ખોલો"
        }
        return {"panel": "National Command Center", "label": labels.get(lang_code, labels["en"])}

    return None


def ask_medimind_ai(user_message: str, chat_history: list = None, clinical_context: dict = None, lang_code: str = "en") -> str:
    """
    Answers strictly medical, pharmaceutical, triage, or MediMind AI related questions.
    Politely refuses any non-medical or unrelated topics. No emojis emitted.
    """
    if not user_message or not user_message.strip():
        return "Please ask a question regarding your health, symptoms, medicines, or MediMind AI."
    chat_history = chat_history or []
    clinical_context = clinical_context or {}

    symptoms = clinical_context.get("symptoms", [])
    top_disease = clinical_context.get("top_disease", "")
    medicines = clinical_context.get("medicines", [])
    age_group = clinical_context.get("age", "Adult")
    gender = clinical_context.get("gender", "Unspecified")
    report_text = clinical_context.get("report_text", "")
    report_type = clinical_context.get("report_type", "")

    report_context_section = f"\n- Uploaded Medical Report Type: {report_type}\n- Extracted Medical Report / Prescription Content:\n{report_text}\n" if report_text else ""

    context_str = f"""
Current Active Session Context:
- Identified Symptoms: {', '.join(symptoms) if symptoms else 'General Medical Consultation'}
- Top Assessed Condition: {top_disease if top_disease else 'General Inquiry'}
- Prescribed / Identified Medications: {', '.join([m.get('medicine_name', '') for m in medicines]) if medicines else 'None specified'}
- Demographics: Age: {age_group}, Gender: {gender}{report_context_section}
"""
    system_prompt = f"""You are MediMind AI — an intelligent, empathetic, and clinically objective Healthcare & Triage AI Copilot.
{context_str}

STRICT MEDICAL & MEDIMIND SCOPE POLICY:
1. You MUST ONLY answer questions strictly related to:
   - Medical symptoms, diseases, diagnostic blood/lab reports, and prescriptions
   - Medication dosages, timings, Indian brand names (e.g. Dolo 650, Pan 40, Ondem, Electral), and side effects
   - Dietary guidelines, recovery care, and home remedies (Parhez)
   - Emergency warning signs & when to visit a hospital/doctor
   - Explaining what MediMind AI is (an enterprise AI healthcare suite with symptom triage, report analyzer, prescription OCR, and nearby hospital finder)
2. NON-MEDICAL PROHIBITION:
   - If the user asks ANY question unrelated to health/medicine/MediMind AI (such as politics, entertainment, coding, mathematics, crypto, sports, or random chat), you MUST POLITELY REFUSE in the user's language:
     "I am MediMind AI, dedicated exclusively to healthcare, medical symptoms, medicines, and triage guidance. Please ask any health-related question." (Translate to the user's language/dialect).
3. MULTILINGUAL DIALECT MATCHING:
   - ALWAYS reply in the EXACT SAME LANGUAGE and DIALECT as the user's request (Hindi, Gujarati, Hinglish, Gujlish, English).
4. FORMATTING & EMOJI BAN:
   - DO NOT USE ANY EMOJIS in your output. Use clean text headings and concise bullet points (e.g. Dosage:, Timing:, Precautions:, Dietary Advice:).
   - DO NOT generate wide markdown tables as they look squished on narrow chat windows. Always present structured medical points as clear bullet cards.
   - Keep explanations clear, concise, and easy for a patient to understand.
   - Include emergency 108 helpline advisory for severe symptoms.
   - Conclude with a brief standard medical disclaimer."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_message})

    # 1. Try Groq API (High Speed LLM)
    if GROQ_API_KEY:
        for groq_model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "qwen/qwen3.6-27b", "groq/compound"]:
            try:
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                body = {
                    "model": groq_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 700
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=8)
                if res.status_code == 200:
                    raw_ans = res.json()["choices"][0]["message"]["content"]
                    if "</think>" in raw_ans:
                        answer = raw_ans.split("</think>")[-1].strip()
                    else:
                        answer = re.sub(r"<think>.*?</think>", "", raw_ans, flags=re.DOTALL).strip()
                    if answer:
                        return answer
            except Exception as e:
                print(f"Groq chat notice: {e}")

    # 2. Try Gemini API
    if GEMINI_API_KEY:
        for gem_model in ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash", "gemini-2.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gem_model}:generateContent?key={GEMINI_API_KEY}"
                prompt_full = f"{system_prompt}\n\nUser Question: {user_message}"
                gemini_body = {
                    "contents": [{"parts": [{"text": prompt_full}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600}
                }
                res_g = requests.post(url, json=gemini_body, timeout=10)
                if res_g.status_code == 200:
                    candidates = res_g.json().get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
            except Exception as e:
                print(f"Gemini chat notice: {e}")

    # 3. Knowledge-Base Resilient Fallback
    q_lower = user_message.lower()
    
    # Check for MediMind overview query
    if "medimind" in q_lower or "kaya he" in q_lower or "kya hai" in q_lower or "what is" in q_lower:
        if lang_code == "hi" or "kya" in q_lower:
            return """**MediMind AI क्या है?**
MediMind AI एक अत्याधुनिक **मल्टीलिंगुअल क्लिनिकल हेल्थकेयर प्लेटफॉर्म** है, जो मरीजों को उनकी स्थानीय भाषा (हिंदी, गुजराती, हिंग्लिश, इंग्लिश) में स्वास्थ्य मार्गदर्शन प्रदान करता है:
1. **AI लक्षण जांच (Symptom Triage):** आपके लक्षणों के आधार पर संभावित बीमारी और जोखिम स्तर की पहचान।
2. **दवा और प्राथमिक उपचार:** लक्षणों के अनुसार सही दवा (जैसे Dolo 650, Pan 40), खुराक और परहेज की जानकारी।
3. **लैब और ब्लड रिपोर्ट विश्लेषक (OCR AI):** खून की जांच रिपोर्ट पढ़कर सामान्य/असामान्य मान समझाना।
4. **प्रिस्क्रिप्शन स्कैनर:** डॉक्टर की पर्ची की डिजिटल जांच और दवा सुरक्षा।
5. **नजदीकी अस्पताल व क्लिनिक फाइंडर:** लाइव गूगल मैप्स और नेविगेशन रूट।

*(नोट: यह प्रणाली प्राथमिक मार्गदर्शन के लिए है, गंभीर स्थिति में डॉक्टर से संपर्क करें।)*"""
        elif lang_code == "gu":
            return """**MediMind AI શું છે?**
MediMind AI એ એક આધુનિક **હેલ્થકેર AI પ્લેટફોર્મ** છે જે દર્દીઓને સરળ ગુજરાતી ભાષામાં સચોટ માર્ગદર્શન આપે છે:
1. **AI લક્ષણ વિશ્લેષણ:** તાવ, માથાનો દુખાવો વગેરે લક્ષણો પરથી સંભવિત બીમારીનું આકલન.
2. **દવા અને પ્રાથમિક ઉપચાર:** લક્ષણ મુજબ સાચી દવા, ડોઝ અને પરહેજની માહિતી.
3. **બ્લડ રિપોર્ટ એનાલાઇઝર (OCR):** લેબ રિપોર્ટ સરળ ભાષામાં સમજાવે છે.
4. **નજીકના હોસ્પિટલ અને ક્લિનિક:** લાઈવ મેપ અને રૂટ સાથે ઉપલબ્ધ સુવિધાઓ.

*(નોંધ: આ માહિતી માત્ર માર્ગદર્શન માટે છે, ડૉક્ટરની સલાહ અનિવાર્ય છે.)*"""
        else:
            return """**What is MediMind AI?**
MediMind AI is an enterprise clinical healthcare and triage intelligence platform:
1. **AI Symptom Assessment & Triage:** Analyzes reported symptoms to identify possible conditions and risk levels.
2. **Medication Reference:** Provides verified dosage, timings, and dietary guidance.
3. **Lab Report Analyzer (OCR):** Evaluates blood and diagnostic reports against standard reference intervals.
4. **Prescription Scanner:** Digitally parses clinical prescriptions and checks interactions.
5. **Nearby Healthcare GIS:** Locates 24/7 trauma centers, hospitals, and pharmacies with live routing.

*(Note: For informational guidance only. Always seek advice from a licensed medical professional.)*"""

    # Check for Non-Medical queries
    non_med_keywords = ["cricket", "movie", "film", "cinema", "song", "python", "code", "java", "math", "modi", "politics", "weather", "crypto", "stock", "joke"]
    if any(k in q_lower for k in non_med_keywords):
        if lang_code == "hi":
            return "**MediMind AI केवल स्वास्थ्य और चिकित्सा परामर्श के लिए है।**\nमैं केवल लक्षणों, बीमारियों, दवाइयों और स्वास्थ्य से जुड़े सवालों के जवाब दे सकता हूँ। कृपया अपना कोई स्वास्थ्य संबंधित प्रश्न पूछें।"
        elif lang_code == "gu":
            return "**MediMind AI ફક્ત સ્વાસ્થ્ય અને તબીબી સલાહ માટે છે.**\nહું ફક્ત બીમારી, દવાઓ અને આરોગ્ય સંબંધિત પ્રશ્નોના જવાબ આપી શકું છું. કૃપા કરીને તમારો સ્વાસ્થ્ય લક્ષી પ્રશ્ન પૂછો."
        else:
            return "**MediMind AI is strictly a medical and healthcare assistant.**\nI can only assist with symptoms, illnesses, medications, dosages, and triage guidance. Please ask a health-related question."

    # General Medical Advice
    if lang_code == "gu":
        return f"""**મેડીમાઇન્ડ એઆઈ ક્લિનિકલ સહાય:**
તમારા પ્રશ્ન મુજબ: **{user_message}**
- પૂરતો આરામ લો, પ્રવાહીનું સેવન વધારો અને પ્રમાણિત માર્ગદર્શિકાનું પાલન કરો.
- જો લક્ષણો 3 દિવસથી વધુ સમય રહે અથવા વધે, તો તરત જ ડૉક્ટરનો સંપર્ક કરો.

*(માત્ર શૈક્ષણિક અને ટ્રાયજ માર્ગદર્શન માટે. ઔપચારિક સારવાર માટે ડૉક્ટરની સલાહ લો.)*"""
    elif lang_code == "hi":
        return f"""**मेडीमाइंड एआई क्लिनिकल परामर्श:**
आपके प्रश्न के अनुसार: **{user_message}**
- पर्याप्त विश्राम करें, तरल पदार्थों का सेवन बनाए रखें और सुझाई गई खुराक का पालन करें।
- यदि लक्षण 3 दिन से अधिक बने रहें या गंभीर हों, तो तुरंत चिकित्सक से संपर्क करें।

*(केवल सूचनात्मक मार्गदर्शन के लिए। आधिकारिक उपचार हेतु डॉक्टर से परामर्श करें।)*"""
    else:
        return f"""**MediMind AI Clinical Guidance:**
Regarding your query: **{user_message}**
- Ensure adequate rest, hydration, and follow recommended clinical guidelines.
- If symptoms persist or worsen beyond 3 days, consult a qualified physician immediately.

*(Educational guidance only. Always consult a healthcare provider for official treatment.)*"""
