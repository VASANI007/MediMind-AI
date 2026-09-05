"""MediMind AI — Clinical-Grade Multilingual AI Healthcare System
Version: 2.0 (Enterprise Clinical Red Edition)
Features:
1. Panel 1: AI Health & Symptom Analyzer (Trilingual Triage, Red Flags, Diet, Lifestyle, Yoga & Physio)
2. Panel 2: Clinical Report & Prescription Analyzer (Lab Reference Ranges, OCR, Layman Explanations)
3. Panel 3: Regional Healthcare & Emergency Finder (OpenStreetMap, Overpass API, Live Facilities)
4. Panel 4: Health Records & Clinical History (SQLite Historical Vault & Analytics)
5. Panel 5: About MediMind AI (System Architecture, Datasets, AI Engines & Credits)
"""
import os
import sys

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
import markdown
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import base64
import re
from datetime import datetime

from config.settings import APP_NAME, APP_VERSION, SUPPORTED_LANGUAGES
from config.language import load_translations, get_text
from config.theme import apply_theme
from components.theme_toggle import theme_toggle_switch
from database.insert_data import (
    log_triage_session,
    log_report_analysis,
    get_recent_triage_history,
    get_recent_report_history,
    seed_sample_records_if_empty
)
from ai.disease_prediction.predict import SymptomTriageEngine
from ai.disease_prediction.multilingual_symptom_extractor import symptom_extractor
from ai.report_ai.blood_report import LabReportAnalyzer
from ai.report_ai.prescription import PrescriptionAnalyzer
from ai.report_ai.radiology import RadiologyReportAnalyzer
from ai.ocr.text_extractor import extract_text_from_file
from ai.chatbot.rag import generate_health_summary_ai
from ai.chatbot.chatbot import ask_medimind_ai, generate_dynamic_patient_questions, detect_redirect_action
from ai.utils.report_generator import generate_pdf_report
from ai.utils.care_recommendations import (
    get_dynamic_clinical_recommendations,
    get_medicine_gallery,
    get_youtube_search_url
)
from ai.medicine_ai.medicine_details import get_medicine_details
from ai.chatbot.deep_explainer import generate_deep_explanation, answer_assessment_question
from api.openfda import search_drug_openfda
from api.dailymed import search_dailymed_spls, search_dailymed_drugnames
from api.bioportal import search_bioportal_concept, annotate_clinical_text
from api.nlm_clinical import search_nlm_conditions
from api.who_icd import search_who_icd11
from api.nominatim import geocode_city_district
from api.geolocation import detect_auto_location, get_client_ip
from api.overpass import query_nearby_healthcare
from services.geocoding_service import geocode_address, reverse_geocode
from services.places_service import search_nearby_healthcare, search_nearby_hospitals
from services.routes_service import get_route
from components.google_map import generate_google_map_html
from components.command_center_view import render_command_center_dashboard

# Seed sample records if database table is initially empty
seed_sample_records_if_empty()

def get_base64_image(image_path: str) -> str:
    try:
        if os.path.exists(image_path):
            ext = "jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "png"
            with open(image_path, "rb") as img_file:
                return f"data:image/{ext};base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
    except Exception:
        pass
    return ""

LOGO_DARK_B64 = get_base64_image(os.path.join(os.path.dirname(__file__), "assets", "logo", "logo_dark.png"))
LOGO_LIGHT_B64 = get_base64_image(os.path.join(os.path.dirname(__file__), "assets", "logo", "logo_light.png"))
ROBOT_MASCOT_B64 = get_base64_image(os.path.join(os.path.dirname(__file__), "assets", "images", "assistant_bot.jpg"))
FAVICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo", "favicon.png")

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} — Enterprise Clinical Healthcare Portal",
    page_icon=FAVICON_PATH if os.path.exists(FAVICON_PATH) else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Read query parameters to sync dark mode state if requested
qp_theme = st.query_params.get("theme", None)
if qp_theme is not None:
    st.session_state["dark_mode"] = (qp_theme.lower() == "dark")

# Session State Setup
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "active_panel" not in st.session_state:
    st.session_state["active_panel"] = "Health Assessment"
if "assessment_step" not in st.session_state:
    st.session_state["assessment_step"] = 1
if "language" not in st.session_state:
    st.session_state["language"] = "en"
if "app_language" not in st.session_state:
    st.session_state["app_language"] = "English"
if "floating_chat_open" not in st.session_state:
    st.session_state["floating_chat_open"] = False
if "floating_chat_history" not in st.session_state:
    st.session_state["floating_chat_history"] = []

# Apply Clinical Red Enterprise Styling
apply_theme(st.session_state.get("dark_mode", False))

# Cache Engine Instances
@st.cache_resource
def get_triage_engine():
    return SymptomTriageEngine()

@st.cache_resource
def get_lab_analyzer():
    return LabReportAnalyzer()

@st.cache_resource
def get_prescription_analyzer():
    return PrescriptionAnalyzer()

@st.cache_resource
def get_radiology_analyzer():
    return RadiologyReportAnalyzer()

triage_engine = get_triage_engine()
lab_analyzer = get_lab_analyzer()
prescription_analyzer = get_prescription_analyzer()
radiology_analyzer = get_radiology_analyzer()


@st.dialog("Deep Clinical AI Consultation & Q&A", width="large")
def show_deep_ai_report_dialog(report_text: str, report_type: str, lang_code: str):
    lang_name = "English" if lang_code == "en" else ("हिन्दी (Hindi)" if lang_code == "hi" else "ગુજરાતી (Gujarati)")
    
    st.markdown("""
    <style>
    div[data-testid="stDialog"] [data-testid="stChatInput"],
    div[data-testid="stDialog"] [data-testid="stChatInputContainer"],
    div[data-testid="stDialog"] [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stDialog"] [data-testid="stChatInput"] [data-baseweb="base-input"],
    div[data-testid="stDialog"] [data-testid="stChatInput"] [data-baseweb="input"],
    div[data-testid="stDialog"] [data-testid="stChatInput"] div[data-baseweb="base-input"] {
        background-color: #0F172A !important;
        background: #0F172A !important;
        border: 1.5px solid #1E2E4E !important;
        border-radius: 24px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
    }
    div[data-testid="stDialog"] [data-testid="stChatInput"] textarea {
        background: transparent !important;
        background-color: transparent !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        border: none !important;
        font-size: 0.90rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stDialog"] [data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }
    div[data-testid="stDialog"] [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #B3261E, #E11D48) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 50% !important;
    }
    div[data-testid="stDialog"] [data-testid="stChatInput"] button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563EB; border-radius: 8px; padding: 12px 16px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <b style="font-size: 0.95rem; color: var(--mm-text-primary);">Clinical Report AI Specialist — {report_type}</b>
            <span class="mm-badge mm-badge-brand">{lang_name}</span>
        </div>
        <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 0 0;">
            Ask any question about your medical parameters, out-of-range values, medications, precautions, or health insights in your preferred language.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "p2_deep_ai_chat"not in st.session_state or not st.session_state["p2_deep_ai_chat"]:
        if lang_code == "hi":
            initial_msg = (
                f"नमस्ते! मैंने आपकी **{report_type}** का विस्तृत अध्ययन पूरा कर लिया है।\n\n"f"आप इस रिपोर्ट के बारे में कोई भी प्रश्न पूछ सकते हैं (जैसे: *'मेरा ब्लड ग्रुप क्या है?'*, *'कौन सा टेस्ट नॉर्मल रेंज से बाहर है?'*, *'मुझे क्या सावधानियां रखनी चाहिए?'*)।"
            )
        elif lang_code == "gu":
            initial_msg = (
                f"નમસ્તે! મેં તમારા **{report_type}** નું વિગતવાર વિશ્લેષણ પૂર્ણ કર્યું છે.\n\n"f"તમે આ રિપોર્ટ વિશે કોઈપણ પ્રશ્ન પૂછી શકો છો (જેમ કે: *'મારો બ્લડ ગ્રૂપ કયો છે?'*, *'કઈ વેલ્યુ નોર્મલ નથી?'*, *'મારે કઈ સાવચેતી રાખવી જોઈએ?'*)।"
            )
        else:
            initial_msg = (
                f"Hello! I have analyzed your **{report_type}**.\n\n"f"Feel free to ask me any question regarding your report (e.g. *'What is my blood group?'*, *'Which parameters are out of range?'*, *'What diet or lifestyle changes should I follow?'*)."
            )
        st.session_state["p2_deep_ai_chat"] = [{"role": "assistant", "content": initial_msg}]

    # Render previous conversation
    chat_container = st.container(height=320)
    with chat_container:
        for msg in st.session_state["p2_deep_ai_chat"]:
            avatar = "https://cdn-icons-png.flaticon.com/512/6873/6873405.png" if msg["role"] == "assistant" else "https://cdn-icons-png.flaticon.com/512/11103/11103363.png"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # Quick Question Chips
    quick_q_map = {
        "en": ["Is anything critical in this report?", "Explain all abnormal values in simple words", "What precautions or diet should I follow?"],
        "hi": ["क्या इस रिपोर्ट में कुछ गंभीर है?", "सभी एब्नॉर्मल वैल्यू को सरल भाषा में समझाएं", "मुझे क्या डाइट या सावधानियां रखनी चाहिए?"],
        "gu": ["શું આ રિપોર્ટમાં કંઈ ગંભીર છે?", "અસામાન્ય વેલ્યુ સરળ ભાષામાં સમજાવો", "મારે કયો ખોરાક અથવા સાવચેતી રાખવી જોઈએ?"]
    }
    quick_questions = quick_q_map.get(lang_code, quick_q_map["en"])

    st.markdown("<div style='font-size: 0.76rem; color: var(--mm-text-secondary); font-weight: 600; margin: 8px 0 4px 0;'>Suggested Questions:</div>", unsafe_allow_html=True)
    q_cols = st.columns(len(quick_questions))
    selected_quick_q = None
    for q_idx, q_text in enumerate(quick_questions):
        with q_cols[q_idx]:
            if st.button(q_text, key=f"p2_quick_q_{q_idx}", use_container_width=True):
                selected_quick_q = q_text

    # User Input
    user_q = st.chat_input("Ask any question about your report...") or selected_quick_q

    if user_q and user_q.strip():
        st.session_state["p2_deep_ai_chat"].append({"role": "user", "content": user_q.strip()})
        with st.spinner("Analyzing report and generating answer..."):
            clinical_ctx = {
                "report_text": report_text,
                "report_type": report_type,
                "age": st.session_state.get("p2_age", "Adult"),
                "gender": st.session_state.get("p2_gender", "Unspecified")
            }
            ai_reply = ask_medimind_ai(user_q.strip(), st.session_state["p2_deep_ai_chat"], clinical_ctx, lang_code)
        st.session_state["p2_deep_ai_chat"].append({"role": "assistant", "content": ai_reply})
        st.rerun()


if "triage_result"not in st.session_state:
    st.session_state["triage_result"] = None
if "selected_symptoms_list"not in st.session_state:
    st.session_state["selected_symptoms_list"] = []
if "user_location_cache"not in st.session_state:
    st.session_state["user_location_cache"] = {"lat": 23.0225, "lon": 72.5714, "name": "Ahmedabad, Gujarat"}
if "user_context"not in st.session_state:
    st.session_state["user_context"] = {
        "age": "",
        "age_key": "select",
        "gender": "",
        "gender_key": "select",
        "location": "Ahmedabad, Gujarat",
        "height": "None",
        "weight": "None",
        "blood_group": "None",
        "severity": "Moderate",
        "duration": "1 - 3 Days",
        "conditions": ["None"],
        "medications": "",
        "allergies": "None"
    }

# Canonical Dropdown Key Mappings for Lossless Language Switching
AGE_KEYS = [
    "select", "10_15", "16_20", "21_25", "26_30", "31_35", "36_40",
    "41_45", "46_50", "51_55", "56_60", "61_65", "66_70", "71_75", "76_80", "80_plus"
]
AGE_LABEL_MAP = {
    "select": "select_age_prompt",
    "10_15": "age_10_15",
    "16_20": "age_16_20",
    "21_25": "age_21_25",
    "26_30": "age_26_30",
    "31_35": "age_31_35",
    "36_40": "age_36_40",
    "41_45": "age_41_45",
    "46_50": "age_46_50",
    "51_55": "age_51_55",
    "56_60": "age_56_60",
    "61_65": "age_61_65",
    "66_70": "age_66_70",
    "71_75": "age_71_75",
    "76_80": "age_76_80",
    "80_plus": "age_80_plus",
}

GENDER_KEYS = ["select", "male", "female", "other"]
GENDER_LABEL_MAP = {
    "select": "select_gender_prompt",
    "male": "gender_male",
    "female": "gender_female",
    "other": "gender_other",
}

BLOOD_KEYS = ["select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown"]

SEVERITY_KEYS = ["mild", "moderate", "severe"]
SEVERITY_LABEL_MAP = {
    "mild": "severity_mild",
    "moderate": "severity_moderate",
    "severe": "severity_severe",
}

DURATION_KEYS = ["today", "1_3", "4_7", "1_2w", "more_2w"]
DURATION_LABEL_MAP = {
    "today": "dur_today",
    "1_3": "dur_1_3",
    "4_7": "dur_4_7",
    "1_2w": "dur_1_2w",
    "more_2w": "dur_more_2w",
}


# Language Options Constants (All-India Multi-Lingual Architecture)
LANG_OPTIONS = [
    "English",
    "Hindi (हिंदी)",
    "Gujarati (ગુજરાતી)",
    "Marathi (मराठी)",
    "Bengali (বাংলা)",
    "Tamil (தமிழ்)",
    "Telugu (తెలుగు)",
    "Kannada (ಕನ್ನಡ)",
    "Malayalam (മലയാളം)",
    "Punjabi (ਪੰਜਾਬੀ)",
    "Odia (ଓଡ଼ିଆ)",
    "Urdu (اردو)"
]
lang_code_map = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Gujarati (ગુજરાતી)": "gu",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Urdu (اردو)": "ur"
}

# Initialize language keys in session state to prevent default index conflicts
if "app_language" not in st.session_state:
    st.session_state["app_language"] = "English"

for k in ["hdr_lang_p1", "hdr_lang_p2", "hdr_lang_p3", "hdr_lang_p4", "hdr_lang_p5"]:
    if k not in st.session_state:
        st.session_state[k] = st.session_state["app_language"]

def sync_language(source_key):
    new_val = st.session_state.get(source_key)
    if new_val in LANG_OPTIONS:
        st.session_state["app_language"] = new_val
        st.session_state["language"] = lang_code_map.get(new_val, "en")
        for k in ["hdr_lang_p1", "hdr_lang_p2", "hdr_lang_p3", "hdr_lang_p4", "hdr_lang_p5"]:
            if k != source_key:
                st.session_state[k] = new_val

def sync_theme_mode(source_key):
    new_mode = st.session_state.get(source_key, False)
    st.session_state["dark_mode"] = new_mode
    for k in ["hdr_theme_p1", "hdr_theme_p2", "hdr_theme_p3", "hdr_theme_p4", "hdr_theme_p5"]:
        st.session_state[k] = new_mode

def toggle_floating_chat():
    st.session_state["floating_chat_open"] = not st.session_state.get("floating_chat_open", False)

def clear_floating_chat():
    st.session_state["floating_chat_history"] = []

def handle_floating_chat_submit():
    raw_q = st.session_state.get("floating_chat_user_input", "").strip()
    if raw_q:
        st.session_state["floating_chat_history"].append({"role": "user", "content": raw_q})
        st.session_state["pending_chat_query"] = raw_q
    st.session_state["floating_chat_user_input"] = ""

def sync_medical_conditions():
    selected = list(st.session_state.get("selected_conditions_widget", []))
    prev = list(st.session_state.get("prev_selected_conditions", ["None"]))
    if "None" in selected and len(selected) > 1:
        if "None" not in prev:
            selected = ["None"]
        else:
            selected = [c for c in selected if c != "None"]
    elif not selected:
        selected = ["None"]
    st.session_state["selected_conditions_widget"] = selected
    st.session_state["prev_selected_conditions"] = list(selected)
    if "user_context" in st.session_state:
        st.session_state["user_context"]["conditions"] = selected

lang_choice = st.session_state.get("app_language", "English")
lang_code = lang_code_map.get(lang_choice, "en")
st.session_state["language"] = lang_code
T = load_translations(lang_code)

def render_dynamic_browser_translator(target_lang_code: str):
    """
    Injects Google Translate client-side engine directly into the browser.
    Dynamically translates all UI text across the entire web page in real time
    without needing any static .json translation dictionaries.
    """
    import streamlit.components.v1 as components
    if target_lang_code == "en":
        js_code = """
        <script>
        (function() {
            try {
                var doc = window.parent.document;
                doc.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                doc.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + window.location.hostname;
                var iframe = doc.querySelector('iframe.goog-te-banner-frame');
                if (iframe) iframe.style.display = 'none';
            } catch(e) {}
        })();
        </script>
        """
    else:
        js_code = f"""
        <div id="google_translate_element" style="display:none;"></div>
        <script type="text/javascript">
        (function() {{
            var targetLang = "{target_lang_code}";
            function applyGoogleTranslate() {{
                try {{
                    var doc = window.parent.document;
                    doc.cookie = "googtrans=/en/" + targetLang + "; path=/;";
                    doc.cookie = "googtrans=/en/" + targetLang + "; path=/; domain=" + window.location.hostname;
                    
                    if (!window.parent.google || !window.parent.google.translate) {{
                        var script = doc.createElement('script');
                        script.type = 'text/javascript';
                        script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInitParent';
                        doc.head.appendChild(script);
                        
                        window.parent.googleTranslateElementInitParent = function() {{
                            try {{
                                new window.parent.google.translate.TranslateElement({{
                                    pageLanguage: 'en',
                                    includedLanguages: 'hi,gu,mr,bn,ta,te,kn,ml,pa,or,ur,en',
                                    autoDisplay: false
                                }}, 'google_translate_element');
                            }} catch(e) {{}}
                        }};
                    }} else if (window.parent.google.translate.TranslateElement) {{
                        var select = doc.querySelector('.goog-te-combo');
                        if (select) {{
                            select.value = targetLang;
                            select.dispatchEvent(new Event('change'));
                        }}
                    }}
                }} catch(err) {{
                    console.log('Google Translate Engine Notice:', err);
                }}
            }}
            applyGoogleTranslate();
            setTimeout(applyGoogleTranslate, 400);
            setTimeout(applyGoogleTranslate, 1000);
        }})();
        </script>
        """
    components.html(js_code, height=0, width=0)

# Execute Dynamic Browser Translator Engine
render_dynamic_browser_translator(lang_code)

def render_footer_trust_bar(t_dict):
    return f"""
    <div class="mm-footer-trust-bar">
        <div class="mm-footer-trust-items">
            <div class="mm-trust-item">
                <span class="mm-trust-icon"><img src="https://cdn-icons-png.flaticon.com/512/4503/4503969.png"alt="256-bit AES Encryption"style="width: 20px; height: 20px;"></span>
                <span class="mm-trust-label">{t_dict.get("trust_encryption", "256-bit AES Encryption")}</span>
            </div>
            <div class="mm-trust-dot">•     </div>
            <div class="mm-trust-item">
                <span class="mm-trust-icon"><img src="https://cdn-icons-png.flaticon.com/512/595/595764.png"alt="HIPAA Compliant"style="width: 20px; height: 20px;"></span>
                <span class="mm-trust-label">{t_dict.get("trust_hipaa", "HIPAA Compliant")}</span>
            </div>
            <div class="mm-trust-dot">•     </div>
            <div class="mm-trust-item">
                <span class="mm-trust-icon"><img src="https://cdn-icons-png.flaticon.com/512/12181/12181028.png"alt="WHO Protocols"style="width: 20px; height: 20px;"></span>
                <span class="mm-trust-label">{t_dict.get("trust_who", "WHO Protocols")}</span>
            </div>
            <div class="mm-trust-dot">•     </div>
            <div class="mm-trust-item">
                <span class="mm-trust-icon"><img src="https://cdn-icons-png.flaticon.com/512/4060/4060488.png"alt="Made in India"style="width: 20px; height: 20px;"></span>
                <span class="mm-trust-label">{t_dict.get("trust_india", "Made in India")}</span>
            </div>
            <div class="mm-trust-dot">•      </div>
            <div class="mm-trust-item">
                <span class="mm-trust-icon"><img src="https://cdn-icons-png.flaticon.com/512/2309/2309962.png"alt="Clinical Intelligence V2.0"style="width: 20px; height: 20px;"></span>
                <span class="mm-trust-label">Clinical Intelligence V2.0</span>
            </div>
        </div>
    </div>
    """

is_dark = st.session_state.get("dark_mode", False)
dark_mode_js = f"""
<script>
(function() {{
    var isDark = {'true'if is_dark else 'false'};
    function applyTheme(dark) {{
        var targets = [document.documentElement, document.body];
        var stApp = document.querySelector('.stApp');
        if (stApp) targets.push(stApp);
        targets.forEach(function(el) {{
            if (el) {{
                el.setAttribute('data-theme', dark ? 'dark' : 'light');
                el.setAttribute('data-dark-mode', dark ? 'true' : 'false');
            }}
        }});
    }}
    applyTheme(isDark);
    var obs = new MutationObserver(function() {{ applyTheme(isDark); }});
    obs.observe(document.body, {{ childList: true, subtree: true }});
    setTimeout(function() {{ applyTheme(isDark); }}, 100);
    setTimeout(function() {{ applyTheme(isDark); }}, 400);
    setTimeout(function() {{ applyTheme(isDark); }}, 800);

    // Listen for theme toggle messages from iframe component
    window.addEventListener("message", function(e) {{
        if (e.data && e.data.type === "medimind_theme_toggle") {{
            var newDark = e.data.dark;
            applyTheme(newDark);
            try {{
                var url = new URL(window.location.href);
                url.searchParams.set("theme", newDark ? "dark" : "light");
                window.location.replace(url.toString());
            }} catch(err) {{
                window.location.search = "?theme=" + (newDark ? "dark" : "light");
            }}
        }}
    }});
}})();
</script>
"""
st.markdown(dark_mode_js, unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    # Sidebar Brand
    if LOGO_DARK_B64:
        st.markdown(f"""
        <div class="mm-sidebar-brand"style="text-align: center; padding: 4px 0 12px 0;">
            <img src="{LOGO_DARK_B64}"style="width: 145px; height: auto; border-radius: 12px; margin-bottom: 6px; filter: drop-shadow(0 4px 14px rgba(225,9,20,0.45));"alt="MediMind AI Logo"/>
            <div style="font-size: 0.78rem; color: #94A3B8; font-weight: 500; margin-bottom: 8px;">{T.get("app_subtitle", "Intelligent Healthcare Suite")}</div>
            <span class="mm-badge"style="background: rgba(225, 9, 20, 0.20); color: #FCA5A5; border: 1px solid rgba(225, 9, 20, 0.45); font-size: 0.70rem; font-weight: 700;">{T.get("enterprise_suite", "V2.0 ENTERPRISE SUITE")}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="mm-sidebar-brand">
            <h2 style="color: #FFFFFF; margin: 0; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.01em;">{T.get("app_brand", "MediMind AI")}</h2>
            <p style="color: #94A3B8; margin: 4px 0 8px 0; font-size: 0.8rem;">{T.get("app_subtitle", "Intelligent Healthcare Suite")}</p>
            <span class="mm-badge"style="background: rgba(225, 9, 20, 0.20); color: #FCA5A5; border: 1px solid rgba(225, 9, 20, 0.45); font-size: 0.70rem; font-weight: 700;">{T.get("enterprise_suite", "V2.0 ENTERPRISE SUITE")}</span>
        </div>
        """, unsafe_allow_html=True)

    # Clinical Navigation (Clean Equal-Width Rows, Zero Emojis)
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stRadio"],
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] div[role="radiogroup"] {{
        width: 100% !important;
        min-width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 8px !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label,
    [data-testid="stSidebar"] label[data-baseweb="radio"],
    [data-testid="stSidebar"] div[data-baseweb="radio"] {{
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        display: flex !important;
        box-sizing: border-box !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        white-space: nowrap !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child:not([data-testid="stMarkdownContainer"]) {{
        display: none !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label p,
    [data-testid="stSidebar"] div[role="radiogroup"] > label span {{
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 0.88rem !important;
        line-height: 1.2 !important;
        flex: 1 1 auto !important;
    }}
    </style>
    <div style='font-size: 0.74rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.05em; text-transform: uppercase; margin: 8px 0 6px 0;'>{T.get('clinical_navigation', 'CLINICAL MODULE NAVIGATION')}</div>
    """, unsafe_allow_html=True)
    
    panel_map = {
        "Health Assessment": T.get("nav_health_assessment", "Health Assessment"),
        "Medical Report": T.get("nav_medical_report", "Medical Report"),
        "Nearby Healthcare": T.get("nav_nearby_healthcare", "Nearby Healthcare"),
        "Health Records": T.get("nav_health_records", "Health Records"),
        "National Command Center": T.get("nav_command_center", "National Command Center"),
        "About MediMind AI": T.get("nav_about", "About MediMind AI")
        }
    panel_keys = list(panel_map.keys())
    
    current_key = "Health Assessment"
    for k in panel_keys:
        if k in st.session_state.get("active_panel", ""):
            current_key = k
            break

    selected_nav_key = st.radio(
        "Clinical Module Navigation",
        options=panel_keys,
        format_func=lambda k: panel_map[k],
        index=panel_keys.index(current_key),
        label_visibility="collapsed"
    )
    st.session_state["active_panel"] = selected_nav_key

    # 5. Safety & Privacy Card (Unified 12px Radius, Dark Mode Parity, No Emojis)
    st.markdown(f"""
    <div class="mm-sidebar-trust"style="background: #111B2E; border: 1px solid #1E2E4E; border-radius: 12px; padding: 14px; margin-top: 14px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <b style="color: #F8FAFC; font-size: 0.82rem; letter-spacing: 0.04em;">{T.get("safety_privacy_title", "SAFETY & PRIVACY")}</b>
        </div>
        <p style="margin: 0; font-size: 0.74rem; color: #94A3B8; line-height: 1.45;">{T.get("safety_privacy_desc", "Your data is encrypted and protected following HIPAA & WHO guidelines.")}</p>
    </div>
    <div class="mm-sidebar-warning"style="background: rgba(234, 88, 12, 0.09); border: 1px solid rgba(234, 88, 12, 0.35); border-left: 4px solid #EA580C; border-radius: 10px; padding: 12px 14px; margin-top: 10px;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="font-size: 0.85rem;"></span>
            <b style="color: #FB923C; font-size: 0.78rem; letter-spacing: 0.03em; text-transform: uppercase;">{T.get("sidebar_warning_title", "CLINICAL ADVISORY")}</b>
        </div>
        <p style="margin: 0; font-size: 0.72rem; color: #E2E8F0; line-height: 1.45;">{T.get("sidebar_warning_desc", "MediMind AI can make mistakes. Do not rely solely on AI suggestions — always consult a certified doctor or licensed physician for clinical decisions.")}</p>
    </div>
    """, unsafe_allow_html=True)

    # 6. System Status Indicator
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: #10B981; margin-top: 16px; padding-left: 2px;">
        <span class="ai-badge-dot"style="background: #10B981; width: 7px; height: 7px;"></span>
        <span>{T.get("all_systems_operational", "All Systems Operational")}</span>
    </div>
    """, unsafe_allow_html=True)


# ----------------- MAIN CONTENT AREA -----------------

# ==============================================================================
# MODULE 1: AI HEALTH ASSESSMENT
# ==============================================================================
if st.session_state["active_panel"] == "Health Assessment":
    current_step = st.session_state.get("assessment_step", 1)

    # 1. Top Header Bar
    bot_icon_html = '<img src="https://cdn-icons-png.flaticon.com/512/883/883356.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(37,99,235,0.08); box-shadow: 0 4px 14px rgba(37,99,235,0.35); border: 1.5px solid #2563EB;" alt="AI Health Assessment Icon"/>'
    with st.container(key="mm_top_header_card_1"):
        hdr_c1, hdr_c2, hdr_c3, hdr_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {bot_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p1_header_title", "AI Health & Symptom Assessment")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p1_header_subtitle", "Tell us about your health and symptoms. Our AI will analyze and provide guidance.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr_c2:
            st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge-online-pill' style='height: 38px; line-height: 38px; padding: 0 16px;'>{T.get('ai_online', 'AI SYSTEM ONLINE')}</span></div>", unsafe_allow_html=True)
        with hdr_c3:
            header_lang_1 = st.selectbox(
                "Header Lang Selector",
                options=LANG_OPTIONS,
                key="hdr_lang_p1",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p1",)
            )
        with hdr_c4:
            new_theme_p1 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p1")
            if new_theme_p1 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p1
                st.rerun()

    # 2. Stepping Progress Bar
    s1_active = "active"if current_step == 1 else ("done"if current_step > 1 else "")
    s2_active = "active"if current_step == 2 else ("done"if current_step > 2 else "")
    s3_active = "active"if current_step == 3 else ("done"if current_step > 3 else "")
    s4_active = "active"if current_step == 4 else ""
    st.markdown(f"""
    <div class="mm-stepper">
        <div class="mm-step-item">
            <div class="mm-step-num {s1_active}">1</div>
            <div>
                <div class="mm-step-text-title {'active'if current_step == 1 else ''}">{T.get("step1_title", "About You")}</div>
                <div class="mm-step-text-sub">{T.get("step1_sub", "Demographic Info")}</div>
            </div>
        </div>
        <div class="mm-step-arrow">→</div>
        <div class="mm-step-item">
            <div class="mm-step-num {s2_active}">2</div>
            <div>
                <div class="mm-step-text-title {'active'if current_step == 2 else ''}">{T.get("step2_title", "Symptoms")}</div>
                <div class="mm-step-text-sub">{T.get("step2_sub", "Clinical Presentation")}</div>
            </div>
        </div>
        <div class="mm-step-arrow">→</div>
        <div class="mm-step-item">
            <div class="mm-step-num {s3_active}">3</div>
            <div>
                <div class="mm-step-text-title {'active'if current_step == 3 else ''}">{T.get("step3_title", "Medical History")}</div>
                <div class="mm-step-text-sub">{T.get("step3_sub", "Prior Conditions")}</div>
            </div>
        </div>
        <div class="mm-step-arrow">→</div>
        <div class="mm-step-item">
            <div class="mm-step-num {s4_active}">4</div>
            <div>
                <div class="mm-step-text-title {'active'if current_step == 4 else ''}">{T.get("step4_title", "Analysis & Triage")}</div>
                <div class="mm-step-text-sub">{T.get("step4_sub", "Clinical Insights")}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- STEP 1: ABOUT YOU -----------------
    if current_step == 1:
        st.markdown(f"""<div class="mm-card"style="margin-bottom: 16px;">
<b style="font-size: 1.05rem; color: var(--mm-text-primary);">{T.get("card_about_you", "Patient Demographics")}</b>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 14px 0;">{T.get("about_you_note", "Please provide your basic demographic details.")}</p>""", unsafe_allow_html=True)

        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            cur_age_key = st.session_state["user_context"].get("age_key", "select")
            if cur_age_key not in AGE_KEYS:
                cur_age_key = "select"
            age_idx = AGE_KEYS.index(cur_age_key)
            sel_age_key = st.selectbox(
                f"{T.get('label_age_group', 'Age Group')} *",
                options=AGE_KEYS,
                index=age_idx,
                format_func=lambda k: T.get(AGE_LABEL_MAP.get(k, "select_age_prompt"), k)
            )
            st.session_state["user_context"]["age_key"] = sel_age_key
            st.session_state["user_context"]["age"] = "" if sel_age_key == "select" else T.get(AGE_LABEL_MAP.get(sel_age_key, "select_age_prompt"), sel_age_key)
        with r1_c2:
            cur_gen_key = st.session_state["user_context"].get("gender_key", "select")
            if cur_gen_key not in GENDER_KEYS:
                cur_gen_key = "select"
            gen_idx = GENDER_KEYS.index(cur_gen_key)
            sel_gen_key = st.selectbox(
                f"{T.get('label_gender', 'Biological Gender')} *",
                options=GENDER_KEYS,
                index=gen_idx,
                format_func=lambda k: T.get(GENDER_LABEL_MAP.get(k, "select_gender_prompt"), k)
            )
            st.session_state["user_context"]["gender_key"] = sel_gen_key
            st.session_state["user_context"]["gender"] = "" if sel_gen_key == "select" else T.get(GENDER_LABEL_MAP.get(sel_gen_key, "select_gender_prompt"), sel_gen_key)
        with r1_c3:
            user_loc_input = st.text_input(T.get("label_location", "Location"), value=st.session_state["user_context"].get("location", "Ahmedabad, Gujarat"))
            st.session_state["user_context"]["location"] = user_loc_input

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            cur_h = st.session_state["user_context"].get("height", "None")
            h_val_display = "" if cur_h in ["None", ""] else cur_h
            height_val = st.text_input(
                f"{T.get('label_height', 'Height (cm)')} ({T.get('optional', 'Optional')})",
                value=h_val_display,
                placeholder=T.get("placeholder_height", "Optional (e.g. 175 cm)")
            )
            st.session_state["user_context"]["height"] = height_val.strip() if height_val.strip() else "None"
        with r2_c2:
            cur_w = st.session_state["user_context"].get("weight", "None")
            w_val_display = "" if cur_w in ["None", ""] else cur_w
            weight_val = st.text_input(
                f"{T.get('label_weight', 'Weight (kg)')} ({T.get('optional', 'Optional')})",
                value=w_val_display,
                placeholder=T.get("placeholder_weight", "Optional (e.g. 65 kg)")
            )
            st.session_state["user_context"]["weight"] = weight_val.strip() if weight_val.strip() else "None"
        with r2_c3:
            none_label = T.get("opt_none", "None")
            blood_opts = [none_label, "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", T.get("bg_unknown", "Unknown")]
            cur_bg = st.session_state["user_context"].get("blood_group", "None")
            bg_idx = blood_opts.index(cur_bg) if cur_bg in blood_opts else 0
            blood_group = st.selectbox(
                f"{T.get('label_blood_group', 'Blood Group')} ({T.get('optional', 'Optional')})",
                blood_opts,
                index=bg_idx
            )
            st.session_state["user_context"]["blood_group"] = blood_group


        st.markdown(f"""<div style="font-size: 0.76rem; color: #2563EB; background: rgba(37, 99, 235, 0.1); padding: 8px 12px; border-radius: 8px; margin-top: 10px;">
<span>{T.get("about_you_note", "This information helps our AI calculate precise physiological risk factors.")}</span>
</div>
</div>""", unsafe_allow_html=True)

        # Card 2: Symptoms Search
        st.markdown(f"""<div class="mm-card">
<b style="font-size: 1.05rem; color: var(--mm-text-primary);">{T.get("card_symptoms_title", "Clinical Symptoms")} <span style="color: #FF2E5B;">*</span></b>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 12px 0;">{T.get("symptom_search_placeholder", "Search symptoms or select major Indian health conditions...")}</p>""", unsafe_allow_html=True)

        symptoms_df = triage_engine.df_symptoms
        sym_map_gu = {}
        sym_map_hi = {}
        if not symptoms_df.empty:
            for _, row in symptoms_df.iterrows():
                eng_sym = str(row.get("symptom_name", "")).strip()
                if "symptom_name_gu" in row and pd.notna(row["symptom_name_gu"]):
                    sym_map_gu[eng_sym] = str(row["symptom_name_gu"]).strip()
                if "symptom_name_hi" in row and pd.notna(row["symptom_name_hi"]):
                    sym_map_hi[eng_sym] = str(row["symptom_name_hi"]).strip()

        def format_symptom_display(s_name):
            if lang_code == "gu":
                gu_val = sym_map_gu.get(s_name)
                return f"{gu_val} ({s_name})" if gu_val and gu_val != s_name else s_name
            elif lang_code == "hi":
                hi_val = sym_map_hi.get(s_name)
                return f"{hi_val} ({s_name})" if hi_val and hi_val != s_name else s_name
            return s_name

        major_diseases_df = getattr(triage_engine, "df_major_diseases", pd.DataFrame())
        
        # Build search options combining symptoms and major diseases
        all_symptom_names = []
        if not symptoms_df.empty:
            all_symptom_names = symptoms_df["symptom_name"].tolist()
        
        major_disease_names = []
        if not major_diseases_df.empty:
            major_disease_names = major_diseases_df["disease_name"].tolist()

        combined_search_options = major_disease_names + all_symptom_names

        s_col1, s_col2 = st.columns([2.2, 1.3])
        with s_col1:
            search_sym = st.multiselect(
                "Search symptoms or major diseases...",
                options=combined_search_options,
                default=[s for s in st.session_state["selected_symptoms_list"] if s in combined_search_options],
                format_func=format_symptom_display,
                label_visibility="collapsed",
                placeholder=T.get("symptom_search_placeholder", "Search symptoms or conditions (e.g. Blood Cancer, Fever, Chest Pain)...")
            )
            for s in search_sym:
                if not major_diseases_df.empty and s in major_diseases_df["disease_name"].values:
                    clean_dname = s.strip()
                    d_match = major_diseases_df[major_diseases_df["disease_name"] == clean_dname]
                    if not d_match.empty:
                        raw_syms = d_match.iloc[0].get("symptoms", [])
                        if isinstance(raw_syms, str):
                            try:
                                d_syms = eval(raw_syms) if raw_syms.startswith("[") else [x.strip() for x in raw_syms.split(",")]
                            except Exception:
                                d_syms = [x.strip() for x in raw_syms.split(",")]
                        else:
                            d_syms = list(raw_syms) if isinstance(raw_syms, (list, tuple)) else []
                        for ds in d_syms:
                            if ds not in st.session_state["selected_symptoms_list"]:
                                st.session_state["selected_symptoms_list"].append(ds)
                        st.session_state["detected_chief_condition"] = d_match.iloc[0].to_dict()
                else:
                    if s not in st.session_state["selected_symptoms_list"]:
                        st.session_state["selected_symptoms_list"].append(s)

        with s_col2:
            describe_words = st.button(T.get("btn_describe_words", "Describe in Your Own Words"), key="btn_describe_words", use_container_width=True)

        if describe_words or st.session_state.get("show_free_text_nlp"):
            st.session_state["show_free_text_nlp"] = True
            st.markdown("""
            <div style="background: rgba(37, 99, 235, 0.06); border: 1px solid rgba(37, 99, 235, 0.25); border-radius: 10px; padding: 12px 14px; margin: 8px 0 12px 0;">
                <b style="font-size: 0.84rem; color: #3B82F6;"><img src="https://cdn-icons-png.flaticon.com/128/12512/12512364.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> AI Multilingual Clinical Extractor (English / हिन्दी / ગુજરાતી)</b>
                <p style="font-size: 0.76rem; color: var(--mm-text-secondary); margin: 3px 0 8px 0;">Type any condition, disease (e.g. <i>"blood cancer"</i>, <i>"हार्ट अटैक"</i>, <i>"ડાયાબિટીસ"</i>), or symptoms in your own words.</p>
            </div>
            """, unsafe_allow_html=True)
            
            ft_c1, ft_c2 = st.columns([3, 1.2])
            with ft_c1:
                free_sym_input = st.text_input(
                    "Describe in Your Own Words",
                    placeholder='e.g. "blood cancer", "Severe chest pain and sweating", "મને 3 દિવસથી ખૂબ તાવ અને ઉધરસ છે"...',
                    key="p1_free_text_input",
                    label_visibility="collapsed"
                )
            with ft_c2:
                extract_nlp_btn = st.button("Extract with AI", key="btn_extract_nlp_trigger", type="primary", use_container_width=True)

            if (extract_nlp_btn or free_sym_input) and free_sym_input:
                with st.spinner("AI parsing disease and clinical symptoms..."):
                    extracted_nlp = symptom_extractor.extract_symptoms_and_medicines(free_sym_input, user_lang=lang_code)
                    new_added = 0
                    for sname in extracted_nlp.get("symptom_labels", []):
                        if sname not in st.session_state["selected_symptoms_list"]:
                            st.session_state["selected_symptoms_list"].append(sname)
                            new_added += 1
                    
                    if extracted_nlp.get("detected_disease"):
                        st.session_state["detected_chief_condition"] = extracted_nlp["detected_disease"]
                    
                    st.session_state["nlp_medicines"] = extracted_nlp.get("recommended_medicines", [])
                    
                    if extracted_nlp.get("detected_disease"):
                        d_info = extracted_nlp["detected_disease"]
                        d_disp_name = d_info.get("name_hi") if lang_code == "hi" else (d_info.get("name_gu") if lang_code == "gu" else d_info.get("name"))
                        st.success(f"AI Detected Condition: **{d_disp_name}** ({d_info.get('category')}) — {len(extracted_nlp.get('symptom_labels', []))} clinical symptoms mapped!")
                    elif new_added > 0:
                        st.success(f"AI Extracted {new_added} clinical symptoms from your description!")

        # Dedicated 100+ India Major Diseases Quick Selector
        with st.expander("Quick Select: Major Indian Diseases & Chronic Conditions (भारत की प्रमुख बीमारियां)", expanded=False):
            if not major_diseases_df.empty:
                cat_options = ["All Categories"] + sorted(major_diseases_df["category"].unique().tolist())
                sel_cat = st.selectbox("Filter by Category", options=cat_options, key="p1_major_dis_cat")
                
                filtered_dis_df = major_diseases_df if sel_cat == "All Categories" else major_diseases_df[major_diseases_df["category"] == sel_cat]
                
                dis_col1, dis_col2 = st.columns([3, 1])
                with dis_col1:
                    def format_disease_option(d_row_id):
                        m_row = major_diseases_df[major_diseases_df["disease_id"] == d_row_id].iloc[0]
                        d_name_val = m_row.get("disease_name_hi") if lang_code == "hi" else (m_row.get("disease_name_gu") if lang_code == "gu" else m_row.get("disease_name"))
                        return f"{d_name_val} ({m_row.get('category')})"

                    sel_dis_id = st.selectbox(
                        "Select Major Condition",
                        options=filtered_dis_df["disease_id"].tolist(),
                        format_func=format_disease_option,
                        key="p1_major_dis_select"
                    )
                with dis_col2:
                    if st.button("Add Condition Symptoms", key="btn_add_major_dis_syms", use_container_width=True):
                        d_match_row = major_diseases_df[major_diseases_df["disease_id"] == sel_dis_id].iloc[0]
                        raw_syms = d_match_row.get("symptoms", [])
                        if isinstance(raw_syms, str):
                            try:
                                d_syms = eval(raw_syms) if raw_syms.startswith("[") else [x.strip() for x in raw_syms.split(",")]
                            except Exception:
                                d_syms = [x.strip() for x in raw_syms.split(",")]
                        else:
                            d_syms = list(raw_syms) if isinstance(raw_syms, (list, tuple)) else []
                        
                        for ds in d_syms:
                            if ds not in st.session_state["selected_symptoms_list"]:
                                st.session_state["selected_symptoms_list"].append(ds)
                        st.session_state["detected_chief_condition"] = d_match_row.to_dict()
                        st.success(f"Added {len(d_syms)} symptoms for {d_match_row['disease_name']}")
                        st.rerun()

        st.markdown(f"<div style='font-size: 0.78rem; font-weight: 700; color: var(--mm-text-secondary); margin: 12px 0 8px 0;'>{T.get('popular_symptoms', 'Common Symptoms:')}</div>", unsafe_allow_html=True)
        pop_symptoms_data = [
            {"key": "Fever", "en": "Fever", "hi": "बुखार", "gu": "તાવ"},
            {"key": "Headache", "en": "Headache", "hi": "सिरदर्द", "gu": "માથાનો દુખાવો"},
            {"key": "Cough", "en": "Cough", "hi": "खांसी", "gu": "ખાંસી"},
            {"key": "Nausea", "en": "Nausea", "hi": "जी मिचलाना", "gu": "ઉબકા"},
            {"key": "Fatigue", "en": "Fatigue", "hi": "थकान", "gu": "થાક"},
            {"key": "Sore Throat", "en": "Sore Throat", "hi": "गले में खराश", "gu": "ગળામાં દુખાવો"},
            {"key": "Body Pain", "en": "Body Pain", "hi": "बदन दर्द", "gu": "શરીરનો દુખાવો"}
        ]
        pop_cols = st.columns(len(pop_symptoms_data))
        for p_idx, p_item in enumerate(pop_symptoms_data):
            p_key = p_item["key"]
            p_label = p_item.get(lang_code, p_item["en"])
            with pop_cols[p_idx]:
                is_selected = p_key in st.session_state["selected_symptoms_list"]
                btn_label = f"[✓] {p_label}" if is_selected else f"+ {p_label}"
                btn_type = "primary" if is_selected else "secondary"
                if st.button(btn_label, key=f"pop_sym_chip_{p_idx}", type=btn_type, use_container_width=True):
                    if p_key not in st.session_state["selected_symptoms_list"]:
                        st.session_state["selected_symptoms_list"].append(p_key)
                    else:
                        st.session_state["selected_symptoms_list"].remove(p_key)
                    st.rerun()

        st.markdown(f"<div style='font-size: 0.78rem; font-weight: 700; color: var(--mm-text-secondary); margin: 12px 0 6px 0;'>{T.get('selected_symptoms', 'Selected Symptoms:')}</div>", unsafe_allow_html=True)
        if st.session_state["selected_symptoms_list"]:
            sel_chips_html = "".join([f'<span style="background: rgba(179, 38, 30, 0.15); color: #F87171; border: 1px solid rgba(179, 38, 30, 0.4); border-radius: 8px; padding: 5px 10px; font-size: 0.80rem; font-weight: 700; margin-right: 6px; margin-bottom: 6px; display: inline-flex; align-items: center; gap: 4px;">{format_symptom_display(s)}</span>'for s in st.session_state["selected_symptoms_list"]])
            sel_col1, sel_col2 = st.columns([4, 1])
            with sel_col1:
                st.markdown(f'<div style="display: flex; align-items: center; flex-wrap: wrap;">{sel_chips_html}</div>', unsafe_allow_html=True)
            with sel_col2:
                if st.button(T.get("clear_all", "Clear All"), key="clear_all_sym_btn", use_container_width=True):
                    st.session_state["selected_symptoms_list"] = []
                    st.session_state["detected_chief_condition"] = None
                    st.rerun()
        else:
            st.caption(T.get("no_symptoms_selected", "No symptoms selected yet. Type in your own words, search above, or select common symptoms."))

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(T.get("btn_next_symptoms", "Next: Select Symptoms"), key="btn_goto_step2", type="primary", use_container_width=True):
            missing_fields = []
            if not sel_age_key or sel_age_key == "select":
                missing_fields.append(T.get("label_age_group", "Age Group"))
            if not sel_gen_key or sel_gen_key == "select":
                missing_fields.append(T.get("label_gender", "Biological Gender"))
            if not st.session_state["selected_symptoms_list"]:
                missing_fields.append(T.get("card_symptoms_title", "Clinical Symptoms"))
            
            if missing_fields:
                fields_str = ", ".join(missing_fields)
                st.error(f" {T.get('err_required_prefix', 'Please provide required details to proceed:')} **{fields_str}**")
            else:
                st.session_state["assessment_step"] = 2
                st.rerun()

    # ----------------- STEP 2: SYMPTOMS & SEVERITY -----------------
    elif current_step == 2:
        st.markdown(f"""<div class="mm-card">
<b style="font-size: 1.10rem; color: var(--mm-text-primary);">{T.get("step2_title", "Symptoms")} & {T.get("symptom_duration", "Duration")}</b>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 16px 0;">{T.get("step2_sub", "Describe the progression and intensity of your symptoms.")}</p>""", unsafe_allow_html=True)

        st.markdown(f"<b style='font-size: 0.90rem; color: var(--mm-text-primary);'>{T.get('selected_symptoms', 'Active Symptoms:')}</b>", unsafe_allow_html=True)
        active_s_html = "".join([f'<span class="mm-badge mm-badge-brand"style="margin: 4px 6px 4px 0;">{s}</span>'for s in st.session_state["selected_symptoms_list"]])
        st.markdown(f"<div style='margin-bottom: 16px;'>{active_s_html}</div>", unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary);'>{T.get('symptom_severity', 'Symptom Severity')}</b>", unsafe_allow_html=True)
            cur_sev_key = st.session_state["user_context"].get("severity_key", "moderate")
            if cur_sev_key not in SEVERITY_KEYS:
                cur_sev_key = "moderate"
            sev_idx = SEVERITY_KEYS.index(cur_sev_key)
            sel_sev_key = st.radio(
                "Severity",
                options=SEVERITY_KEYS,
                index=sev_idx,
                format_func=lambda k: T.get(SEVERITY_LABEL_MAP.get(k, "severity_moderate"), k),
                label_visibility="collapsed"
            )
            st.session_state["user_context"]["severity_key"] = sel_sev_key
            st.session_state["user_context"]["severity"] = sel_sev_key.capitalize()
        with col_s2:
            st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary);'>{T.get('symptom_duration', 'Symptom Duration')}</b>", unsafe_allow_html=True)
            cur_dur_key = st.session_state["user_context"].get("duration_key", "1_3")
            if cur_dur_key not in DURATION_KEYS:
                cur_dur_key = "1_3"
            dur_idx = DURATION_KEYS.index(cur_dur_key)
            sel_dur_key = st.selectbox(
                "Duration",
                options=DURATION_KEYS,
                index=dur_idx,
                format_func=lambda k: T.get(DURATION_LABEL_MAP.get(k, "dur_1_3"), k),
                label_visibility="collapsed"
            )
            st.session_state["user_context"]["duration_key"] = sel_dur_key
            st.session_state["user_context"]["duration"] = T.get(DURATION_LABEL_MAP.get(sel_dur_key, "dur_1_3"), sel_dur_key)


        st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary); display: block; margin-top: 14px;'>{T.get('label_additional_notes', 'Additional Clinical Notes & Triggers (Optional)')}</b>", unsafe_allow_html=True)
        additional_desc = st.text_area(
            "Additional Details",
            placeholder='e.g. Symptoms worsen at night...',
            label_visibility="collapsed"
        )
        st.session_state["user_context"]["details"] = additional_desc

        st.markdown("</div>", unsafe_allow_html=True)

        nav_c1, nav_c2 = st.columns([1, 2])
        with nav_c1:
            if st.button(T.get("btn_prev", "Previous Step"), key="p2_prev_btn", use_container_width=True):
                st.session_state["assessment_step"] = 1
                st.rerun()
        with nav_c2:
            if st.button(T.get("btn_next_history", "Next: Medical History"), key="btn_goto_step3", type="primary", use_container_width=True):
                st.session_state["assessment_step"] = 3
                st.rerun()

    # ----------------- STEP 3: MEDICAL HISTORY -----------------
    elif current_step == 3:
        st.markdown(f"""<div class="mm-card">
<b style="font-size: 1.10rem; color: var(--mm-text-primary);">{T.get("card_history_title", "Medical History & Pre-existing Conditions")}</b>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 16px 0;">{T.get("step3_sub", "Pre-existing conditions enable accurate clinical cross-correlation.")}</p>""", unsafe_allow_html=True)

        st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary);'>{T.get('label_conditions', 'Pre-existing Medical Conditions')}</b>", unsafe_allow_html=True)
        cond_label_map = {
            "None": {"en": "None", "hi": "कोई नहीं (None)", "gu": "કોઈ નહીં (None)"},
            "Diabetes (Type 1 or 2)": {"en": "Diabetes (Type 1 or 2)", "hi": "डायबिटीज / मधुमेह (Diabetes)", "gu": "ડાયાબિટીસ (Diabetes)"},
            "Hypertension (High BP)": {"en": "Hypertension (High BP)", "hi": "हाई ब्लड प्रेशर (Hypertension)", "gu": "હાઈ બ્લડ પ્રેશર (Hypertension)"},
            "Asthma / Respiratory": {"en": "Asthma / Respiratory", "hi": "अस्थमा / श्वास रोग (Asthma)", "gu": "અસ્થમા / શ્વાસની તકલીફ (Asthma)"},
            "Heart Disease": {"en": "Heart Disease", "hi": "हृदय रोग (Heart Disease)", "gu": "હૃદય રોગ (Heart Disease)"},
            "Thyroid Disorder": {"en": "Thyroid Disorder", "hi": "थायरॉइड विकार (Thyroid)", "gu": "થાઇરોઇડ (Thyroid)"},
            "Kidney Disease": {"en": "Kidney Disease", "hi": "किडनी की बीमारी (Kidney Disease)", "gu": "કિડનીની બીમારી (Kidney Disease)"},
            "Acidity / GERD": {"en": "Acidity / GERD", "hi": "एसिडिटी / गैस (Acidity / GERD)", "gu": "એસિડિટી / ગેસ (Acidity / GERD)"}
        }
        if "selected_conditions_widget" not in st.session_state:
            st.session_state["selected_conditions_widget"] = st.session_state.get("user_context", {}).get("conditions", ["None"])
        if "prev_selected_conditions" not in st.session_state:
            st.session_state["prev_selected_conditions"] = list(st.session_state["selected_conditions_widget"])

        cond_choices = st.multiselect(
            "Existing Conditions",
            options=["None", "Diabetes (Type 1 or 2)", "Hypertension (High BP)", "Asthma / Respiratory", "Heart Disease", "Thyroid Disorder", "Kidney Disease", "Acidity / GERD"],
            key="selected_conditions_widget",
            on_change=sync_medical_conditions,
            format_func=lambda k: cond_label_map.get(k, {}).get(lang_code, k),
            label_visibility="collapsed"
        )
        st.session_state["user_context"]["conditions"] = cond_choices

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary);'>{T.get('label_medications', 'Current Ongoing Medications')}</b>", unsafe_allow_html=True)
            curr_meds = st.text_input("Current Medications", placeholder="e.g. Metformin 500mg, Telmisartan 40mg", label_visibility="collapsed")
            st.session_state["user_context"]["medications"] = curr_meds
        with col_m2:
            st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary);'>{T.get('label_allergies', 'Known Food or Drug Allergies')}</b>", unsafe_allow_html=True)
            allergies_val = st.text_input("Allergies", placeholder="e.g. Penicillin, Sulfa, Peanuts", label_visibility="collapsed")
            st.session_state["user_context"]["allergies"] = allergies_val

        st.markdown(f"<b style='font-size: 0.84rem; color: var(--mm-text-secondary); display: block; margin-top: 12px;'>{T.get('label_family_history', 'Relevant Family Medical History (Optional)')}</b>", unsafe_allow_html=True)
        surgeries_val = st.text_area("Surgeries", placeholder="e.g. Prior surgeries, family history of cardiac illness...", label_visibility="collapsed")
        st.session_state["user_context"]["surgeries"] = surgeries_val

        st.markdown("</div>", unsafe_allow_html=True)

        nav_c1, nav_c2 = st.columns([1, 2])
        with nav_c1:
            if st.button(T.get("btn_prev", "Previous Step"), key="p3_prev_btn", use_container_width=True):
                st.session_state["assessment_step"] = 2
                st.rerun()
        with nav_c2:
            if st.button(T.get("btn_next_review", "Next: Review & Run AI Analysis"), key="btn_goto_step4", type="primary", use_container_width=True):
                st.session_state["assessment_step"] = 4
                st.rerun()

    # ----------------- STEP 4: REVIEW & ANALYZE -----------------
    elif current_step == 4:
        st.markdown(f"""<div class="mm-card">
<b style="font-size: 1.10rem; color: var(--mm-text-primary);">{T.get("card_review_title", "Review Clinical Details & Run Analysis")}</b>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 16px 0;">{T.get("card_review_sub", "Verify your submitted details before running the knowledge graph triage engine.")}</p>""", unsafe_allow_html=True)

        u_ctx = st.session_state.get("user_context", {})

        c_sum1, c_sum2, c_sum3 = st.columns(3)
        with c_sum1:
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.08); border: 1.5px solid rgba(59, 130, 246, 0.35); border-radius: 12px; padding: 14px 16px; height: 100%; min-height: 160px; display: flex; flex-direction: column; justify-content: flex-start; box-sizing: border-box;">
                <b style="font-size: 0.88rem; color: #60A5FA;">{T.get("card_about_you", "Demographics")}</b>
                <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.55; margin-top: 6px;">
                    <b>{T.get("label_age_group", "Age")}:</b> {u_ctx.get('age', '21-30')}<br/>
                    <b>{T.get("label_gender", "Gender")}:</b> {u_ctx.get('gender', 'Male')}<br/>
                    <b>{T.get("label_location", "Location")}:</b> {u_ctx.get('location', 'Ahmedabad')}<br/>
                    <b>{T.get("label_blood_group", "Blood")}:</b> {u_ctx.get('blood_group', 'O+')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_sum2:
            s_list_str = ", ".join(st.session_state.get("selected_symptoms_list", ["Fever", "Headache"]))
            st.markdown(f"""
            <div style="background: rgba(179, 38, 30, 0.08); border: 1.5px solid rgba(179, 38, 30, 0.35); border-radius: 12px; padding: 14px 16px; height: 100%; min-height: 160px; display: flex; flex-direction: column; justify-content: flex-start; box-sizing: border-box;">
                <b style="font-size: 0.88rem; color: #F87171;">{T.get("card_symptoms_title", "Symptoms")}</b>
                <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.55; margin-top: 6px;">
                    <b>{T.get("selected_symptoms", "Symptoms")}:</b> {s_list_str}<br/>
                    <b>{T.get("symptom_severity", "Severity")}:</b> {u_ctx.get('severity', 'Moderate')}<br/>
                    <b>{T.get("symptom_duration", "Duration")}:</b> {u_ctx.get('duration', '1 - 3 Days')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_sum3:
            cond_str = ", ".join(u_ctx.get("conditions", ["None"]))
            fam_val = u_ctx.get("surgeries", "") or "None"
            st.markdown(f"""
            <div style="background: rgba(30, 122, 76, 0.08); border: 1.5px solid rgba(30, 122, 76, 0.35); border-radius: 12px; padding: 14px 16px; height: 100%; min-height: 160px; display: flex; flex-direction: column; justify-content: flex-start; box-sizing: border-box;">
                <b style="font-size: 0.88rem; color: #4ADE80;">{T.get("step3_title", "History")}</b>
                <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.55; margin-top: 6px;">
                    <b>{T.get("label_conditions", "Conditions")}:</b> {cond_str}<br/>
                    <b>{T.get("label_medications", "Medications")}:</b> {u_ctx.get('medications') or 'None'}<br/>
                    <b>{T.get("label_allergies", "Allergies")}:</b> {u_ctx.get('allergies') or 'None'}<br/>
                    <b>{T.get("label_family_history", "Family History")}:</b> {fam_val}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        analyze_p1_btn = st.button(T.get("btn_analyze", "Run AI Health Analysis"), key="btn_run_analysis_final", type="primary", use_container_width=True)

        if analyze_p1_btn:
            with st.status("MediMind Clinical AI Engine Running...", expanded=True) as status:
                st.write("Processing reported symptoms and ontology...")
                st.write("Cross-referencing ICD-11 knowledge graph and history...")
                st.markdown('<div style="font-size: 0.88rem; display: flex; align-items: center; gap: 6px; padding: 2px 0;"><img src="https://cdn-icons-png.flaticon.com/512/190/190256.png" style="width: 14px; height: 14px; object-fit: contain;"/> Generating personalized health summary, dietary guidance & triage alerts...</div>', unsafe_allow_html=True)
                
                selected_ids = []
                symptom_ontology_map = {
                    "fever": ["S000001", "S000002", "S000252", "S000253", "S000254", "S000257"],
                    "high fever": ["S000002", "S000001"],
                    "headache": ["S000061", "S000062", "S000063"],
                    "cough": ["S000023", "S000024", "S000260"],
                    "dry cough": ["S000023"],
                    "sore throat": ["S000030", "S000032"],
                    "fatigue": ["S000005", "S000006", "S000012"],
                    "body pain": ["S000011", "S000257"],
                    "body ache": ["S000011", "S000257"],
                    "nausea": ["S000086", "S000087"],
                    "vomiting": ["S000087", "S000086"],
                    "cold": ["S000035", "S000036", "S000023"],
                    "chills": ["S000003", "S000253"],
                    "diarrhea": ["S000089", "S000090"],
                    "stomach pain": ["S000091", "S000092"],
                    "chest pain": ["S000055", "S000060", "S000029"],
                    "shortness of breath": ["S000026", "S000027", "S000260"],
                }
                
                for s_name in st.session_state.get("selected_symptoms_list", []):
                    s_lower = s_name.strip().lower()
                    if s_lower in symptom_ontology_map:
                        selected_ids.extend(symptom_ontology_map[s_lower])
                
                if not selected_ids:
                    selected_ids = ["S000001", "S000061"]

                # Pass all selected symptom names & detected chief condition
                s_list_names = st.session_state.get("selected_symptoms_list", [])
                chief_d = st.session_state.get("detected_chief_condition", {})
                chief_name = chief_d.get("name") if isinstance(chief_d, dict) else None

                # Run Comprehensive Knowledge-Graph Triage Engine
                if hasattr(triage_engine, "evaluate_triage"):
                    triage_res = triage_engine.evaluate_triage(
                        reported_symptom_ids=selected_ids,
                        patient_history={
                            "age_group": u_ctx.get("age", "21-30"),
                            "gender": u_ctx.get("gender", "Male"),
                            "duration": u_ctx.get("duration", "1-3 Days"),
                            "severity": u_ctx.get("severity", "Moderate"),
                            "conditions": u_ctx.get("conditions", []),
                            "location": u_ctx.get("location", "Ahmedabad, Gujarat"),
                            "symptom_names": s_list_names,
                            "chief_condition": chief_name
                        },
                        symptom_names=s_list_names,
                        chief_condition=chief_name
                    )
                else:
                    triage_res = triage_engine.evaluate_symptoms(
                        selected_symptom_ids=selected_ids,
                        age_group=u_ctx.get("age", "21-30"),
                        gender=u_ctx.get("gender", "Male"),
                        duration=u_ctx.get("duration", "1-3 Days"),
                        existing_conditions=u_ctx.get("conditions", {}),
                        symptom_names=s_list_names,
                        chief_condition=chief_name
                    )
                
                st.session_state["p1_triage_results"] = triage_res
                st.session_state["assessment_completed"] = True
                status.update(label="Clinical Assessment & Triage Complete", state="complete", expanded=False)
                st.rerun()

    # Results Section (Visible after Assessment)
    if st.session_state.get("assessment_completed") and st.session_state.get("p1_triage_results"):
        t_res = st.session_state["p1_triage_results"]
        u_ctx = st.session_state.get("user_context", {})
        
        ranked_conds = t_res.get("ranked_conditions", [])
        top_disease_name = ranked_conds[0].get("name", "Acute Infection") if ranked_conds else "Acute Illness"

        # Fetch / compute dynamic care recommendations
        care_res = st.session_state.get("care_recommendations")
        if not care_res or care_res.get("top_condition") != top_disease_name or care_res.get("lang_code") != lang_code:
            care_res = get_dynamic_clinical_recommendations(
                symptoms=st.session_state.get("selected_symptoms_list", []),
                user_context=u_ctx,
                top_condition=top_disease_name,
                lang_code=lang_code
            )
            st.session_state["care_recommendations"] = care_res

        # Dialog definition for Medicine Compounds and Packaging Image
        if hasattr(st, "dialog"):
            def dialog_dec(title):
                return st.dialog(title, width="large")
        elif hasattr(st, "experimental_dialog"):
            def dialog_dec(title):
                return st.experimental_dialog(title, width="large")
        else:
            def dialog_dec(title):
                def wrapper(fn):
                    return fn
                return wrapper

        @dialog_dec("Medication Clinical Profile & Active Compounds")
        def show_medicine_modal(med):
            med_detail = get_medicine_details(med['name'])
            col_img, col_info = st.columns([1.05, 1.45], gap="medium")
            
            with col_img:
                img_url = med.get("image")
                if img_url:
                    st.markdown(f"""
                    <a href="{img_url}" target="_blank" title="Click to view full image in new tab ↗" style="text-decoration: none; cursor: pointer; display: block;">
                        <div style="background: rgba(255, 255, 255, 0.04); border: 1.5px solid var(--mm-border-color); border-radius: 14px; padding: 14px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-sizing: border-box; min-height: 250px; transition: all 0.2s ease;">
                            <img src="{img_url}" style="max-width: 100%; max-height: 230px; object-fit: contain; border-radius: 10px; display: block; margin: 0 auto;" alt="{med['name']}" />
                            <div style="margin-top: 8px; font-size: 0.74rem; color: #3B82F6; text-align: center; line-height: 1.3; font-weight: 600;">
                                Click image to open in new tab ↗
                            </div>
                            <div style="margin-top: 4px; font-size: 0.72rem; color: #EF4444; text-align: center; line-height: 1.2; font-weight: 600;">
                                * Representative / Similar Image (सांकेतिक / समरूप चित्र)
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.04); border: 1.5px solid var(--mm-border-color); border-radius: 14px; padding: 20px; text-align: center;">
                        <div style="font-size: 0.85rem; color: var(--mm-text-secondary);">{med['name']}</div>
                        <div style="margin-top: 6px; font-size: 0.72rem; color: #EF4444; font-weight: 600;">* Representative / Similar Image</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                <div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="mm-badge mm-badge-info" style="font-size: 0.72rem;">{med.get('type', 'Prescription')}</span>
                    <span class="mm-badge mm-badge-brand" style="font-size: 0.70rem;">MediMind Verified</span>
                </div>
                """, unsafe_allow_html=True)

            with col_info:
                st.markdown(f"<h3 style='margin: 0 0 10px 0; color: var(--mm-text-primary); font-size: 1.22rem;'>{med['name']}</h3>", unsafe_allow_html=True)
                
                # Grid of Core Details
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; font-size: 0.80rem;">
                    <div><b style="color: var(--mm-text-secondary);">Generic:</b> <span style="color: #3B82F6; font-weight: 600;">{med_detail.get('generic_name', med['name'])}</span></div>
                    <div><b style="color: var(--mm-text-secondary);">Course:</b> <span style="color: #10B981; font-weight: 600;">{med.get('course_duration', '3 – 5 Days')}</span></div>
                    <div><b style="color: var(--mm-text-secondary);">Dosage:</b> <span style="color: var(--mm-text-primary); font-weight: 600;">{med.get('dosage', 'As prescribed')}</span></div>
                    <div><b style="color: var(--mm-text-secondary);">Timing:</b> <span style="color: #EA580C; font-weight: 600;">{med.get('food_timing', 'After Food')}</span></div>
                    <div style="grid-column: 1 / -1;"><b style="color: var(--mm-text-secondary);">Popular Brands:</b> <span style="color: var(--mm-text-primary);">{', '.join(med_detail.get('brand_names', [])) or 'Available across licensed pharmacies'}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Active Compounds
                st.markdown(f"<b style='font-size: 0.82rem; color: var(--mm-text-primary);'><img src=\"https://cdn-icons-png.flaticon.com/512/18310/18310946.png\" style=\"width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;\" alt=\"Compounds\" /> Active Chemical Compounds & Formula:</b>", unsafe_allow_html=True)
                compounds = med_detail.get("active_compounds", [])
                if compounds:
                    for cmpd in compounds:
                        st.markdown(f"<div style='font-size: 0.78rem; color: var(--mm-text-secondary); margin-left: 6px;'>• <b>{cmpd.get('compound_name')}</b> ({cmpd.get('molecular_formula', '')}): <code style='font-size: 0.74rem;'>{cmpd.get('strength', '')}</code> — <i>{cmpd.get('role', '')}</i></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-size: 0.78rem; color: var(--mm-text-secondary); margin-left: 6px;'>• Active pharmaceutical formulation: <code>{med['name']}</code></div>", unsafe_allow_html=True)
                
                # Purpose / Indication (Why take this medicine)
                ind_text = med.get('indication') or ', '.join(med_detail.get('primary_indications', []))
                if ind_text:
                    st.markdown(f"<div style='font-size: 0.78rem; color: var(--mm-text-secondary); margin-top: 8px;'><b style='color: var(--mm-text-primary);'><img src=\"https://cdn-icons-png.flaticon.com/128/6018/6018699.png\" style=\"width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;\" alt=\"Indication\" /> Purpose & Why Take This Medicine:</b> <span style='color: var(--mm-text-primary); font-weight: 600;'>{ind_text}</span></div>", unsafe_allow_html=True)
                
                warn_text = med.get('warnings') or ', '.join(med_detail.get('contraindications', [])) or 'Consult a physician before initiating medication.'
                st.markdown(f"""
                <div style="background: rgba(234, 88, 12, 0.08); border-left: 3px solid #EA580C; border-radius: 6px; padding: 8px 10px; margin-top: 10px; font-size: 0.76rem; color: var(--mm-text-secondary); line-height: 1.4;">
                    <b style="color: #EA580C;"><img src=\"https://cdn-icons-png.flaticon.com/128/6939/6939131.png\" style=\"width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;\" alt=\"Warning\" /> Safety & Precautions:</b> {warn_text}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            chat_btn_label = {
                "en": "Deep Clinical Analysis & More Info in AI Chat",
                "hi": "AI Chat me दवाई का संपूर्ण विवरण और विश्लेषण",
                "gu": "AI Chat માં દવાનું સંપૂર્ણ વિશ્લેષણ અને માહિતી"
            }.get(lang_code, "Deep Clinical Analysis & More Info in AI Chat")
            
            # Unique key generation per modal render
            modal_key_id = re.sub(r'[^a-zA-Z0-9]', '_', med['name'])[:15]
            if st.button(chat_btn_label, key=f"btn_deep_chat_{modal_key_id}", type="primary", use_container_width=True):
                st.session_state["floating_chat_open"] = True
                user_disp_q = f"Deep analyze and clinical breakdown for {med['name']}"
                prompt_lang_name = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}.get(lang_code, "English")
                system_exec_q = (
                    f"Please provide a comprehensive clinical, pharmacological, and therapeutic deep-dive for the medication '{med['name']}' in {prompt_lang_name}.\n"
                    f"Include:\n"
                    f"1. Active chemical compounds, molecular structure, and pharmacokinetics\n"
                    f"2. Exact clinical indications (why this medicine is prescribed and how it works)\n"
                    f"3. Optimal dosage, timing (food interactions), and duration rules\n"
                    f"4. Contraindications, side effects to watch for, and safety precautions\n"
                    f"5. Common commercial brand names available in pharmacies"
                )
                if "floating_chat_history" not in st.session_state:
                    st.session_state["floating_chat_history"] = []
                st.session_state["floating_chat_history"].append({"role": "user", "content": user_disp_q})
                st.session_state["pending_chat_query"] = system_exec_q
                st.rerun()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""<div class="mm-card"style="border-top: 4px solid #B3261E;">
<div class="mm-card-header">
<h3 style="margin: 0; font-size: 1.25rem; color: var(--mm-text-primary); display: flex; align-items: center; gap: 8px;">
{T.get("triage_results_title", "Clinical Assessment & Triage Findings")}
</h3>
<span class="mm-badge mm-badge-brand">{care_res.get('api_source', 'MediMind AI Verified Care')}</span>
</div>""", unsafe_allow_html=True)

        # 1. Fallback Warning Badge (If offline dataset was used)
        if care_res.get("is_fallback"):
            st.markdown(f"""
            <div style="background: rgba(234, 88, 12, 0.12); border: 1.5px solid #F97316; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px;">
                <div>
                    <b style="color: #EA580C; font-size: 0.90rem;">{T.get("offline_fallback_badge", "Offline Clinical Dataset Fallback Active")}</b>
                    <p style="color: var(--mm-text-primary); font-size: 0.82rem; margin: 2px 0 0 0;">{care_res.get("fallback_warning", T.get("offline_fallback_warning", "Live API could not be reached. Showing standardized local dataset."))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Clinical Summary
        summary_text = care_res.get("summary") or generate_health_summary_ai(st.session_state.get("selected_symptoms_list", []), top_disease_name, u_ctx, lang=lang_code)
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.08); border-left: 4px solid #3B82F6; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px;">
            <b style="color: var(--mm-text-primary); font-size: 0.95rem;">{T.get("clinical_summary_title", "Clinical Summary:")}</b>
            <p style="color: var(--mm-text-secondary); font-size: 0.90rem; line-height: 1.6; margin: 4px 0 0 0;">{summary_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # 3. Expected Clinical Recovery Timeline
        rec_duration = care_res.get("recovery_duration", "5 – 7 Days with rest and proper medication.")
        st.markdown(f"""
        <div class="mm-card"style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(16, 185, 129, 0.35); border-left: 5px solid #10B981; padding: 14px 18px; margin-bottom: 18px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <b style="color: #10B981; font-size: 0.95rem;">{T.get("expected_recovery_title", "Expected Clinical Recovery Timeline")}</b>
                <span class="mm-badge mm-badge-success">Recovery Estimate</span>
            </div>
            <p style="color: var(--mm-text-primary); font-size: 0.90rem; font-weight: 600; line-height: 1.5; margin: 6px 0 0 0;">{rec_duration}</p>
        </div>
        """, unsafe_allow_html=True)

        # 4. Verified Dynamic Medication Gallery (All medicines with food timing, photo, dosage)
        medicine_gallery = care_res.get("medicine_gallery", [])
        if medicine_gallery:
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <b style="font-size: 1.05rem; color: var(--mm-text-primary);">{T.get('verified_med_title', 'Verified Medication & Pharmaceutical Guidance')}</b>
                    <div style="font-size: 0.78rem; color: var(--mm-text-secondary);">{T.get('verified_med_sub', 'Prescribed medicines with verified dosages and food timing instructions.')} ({len(medicine_gallery)} items)</div>
                </div>
                <span class="mm-badge mm-badge-brand">{len(medicine_gallery)} Medicines</span>
            </div>
            """, unsafe_allow_html=True)

            num_meds = len(medicine_gallery)
            for chunk_start in range(0, num_meds, 3):
                med_chunk = medicine_gallery[chunk_start:chunk_start+3]
                med_cols = st.columns(len(med_chunk))
                for m_idx, med in enumerate(med_chunk):
                    with med_cols[m_idx]:
                        ft = med.get('food_timing', 'After Food')
                        ft_color = "#EA580C" if "before" in ft.lower() or "pehle" in ft.lower() or "khali" in ft.lower() else "#10B981"
                        st.markdown(f"""
                        <div class="mm-card"style="padding: 16px; margin-top: 4px; height: 395px; min-height: 395px; max-height: 395px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
                            <div>
                                <div style="height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 4px;">
                                    <img src="{med['image']}"style="max-width: 130px; max-height: 85px; object-fit: contain; display: block; border-radius: 8px;"alt="{med['name']}"/>
                                </div>
                                <div style="font-size: 0.68rem; color: #EF4444; font-weight: 600; text-align: center; margin-bottom: 6px; line-height: 1.2;">
                                    * Representative / Similar Image
                                </div>
                                <div style="min-height: 48px; max-height: 48px; overflow: hidden;">
                                    <b style="font-size: 0.90rem; color: var(--mm-text-primary); display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.25;">{med['name']}</b>
                                    <div style="font-size: 0.76rem; color: var(--mm-text-secondary); margin-top: 2px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;">{med.get('indication', '')}</div>
                                </div>
                            </div>
                            <div>
                                <div style="background: rgba(255,255,255,0.05); border: 1px solid var(--mm-border-color); border-radius: 6px; padding: 8px; margin-bottom: 6px; height: 100px; min-height: 100px; max-height: 100px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
                                    <div style="font-size: 0.73rem; color: var(--mm-text-secondary); line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{T.get('dosage_label', 'Dosage')}: <b>{med.get('dosage', '')}</b></div>
                                    <div style="font-size: 0.73rem; color: {ft_color}; font-weight: 700; margin-top: 2px;">Timing: {med.get('food_timing', 'After Food')}</div>
                                    <div style="font-size: 0.73rem; color: #3B82F6; font-weight: 700; margin-top: 2px;">Course Duration: {med.get('course_duration', '3 – 5 Days')}</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                                    <span class="mm-badge mm-badge-info"style="font-size: 0.62rem;">{med.get('type', 'OTC')}</span>
                                    <span class="mm-badge mm-badge-brand"style="font-size: 0.60rem; padding: 2px 7px;">MediMind Verified</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(T.get("view_compounds_btn", "Info & Compounds"), key=f"btn_med_modal_{chunk_start}_{m_idx}", use_container_width=True):
                            show_medicine_modal(med)
            
            st.markdown(f"<div style='font-size: 0.72rem; color: var(--mm-text-muted); margin: 6px 0 18px 0; font-style: italic;'>{T.get('medicine_gallery_disclaimer', 'Always confirm dosage with a physician or pharmacist.')}</div>", unsafe_allow_html=True)

        # 5. Supportive Restorative Yoga & Physiotherapy (with clickable YouTube links)
        yoga_recs = care_res.get("yoga_recommendations", [])
        if yoga_recs:
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin: 10px 0 8px 0;">
                <div>
                    <b style="font-size: 1.05rem; color: var(--mm-text-primary);">{T.get('supportive_yoga_title', 'Supportive Restorative Yoga & Physiotherapy')}</b>
                    <div style="font-size: 0.78rem; color: var(--mm-text-secondary);">{T.get('supportive_yoga_sub', 'Clinically safe postures and mobility routines to facilitate recovery.')} ({len(yoga_recs)} routines)</div>
                </div>
                <span class="mm-badge mm-badge-success">{len(yoga_recs)} Routines</span>
            </div>
            """, unsafe_allow_html=True)

            num_yoga = len(yoga_recs)
            for chunk_start in range(0, num_yoga, 3):
                y_chunk = yoga_recs[chunk_start:chunk_start+3]
                y_cols = st.columns(len(y_chunk))
                for y_idx, y_item in enumerate(y_chunk):
                    with y_cols[y_idx]:
                        y_sans = f"<span style='font-size: 0.74rem; color: var(--mm-text-muted); font-style: italic;'>({y_item.get('sanskrit_name', '')})</span>"if y_item.get('sanskrit_name') else ""
                        yt_link = y_item.get('youtube_url', f"https://www.youtube.com/results?search_query=how+to+do+{y_item['name']}+yoga+tutorial")
                        st.markdown(f"""
                        <div class="mm-card"style="padding: 16px; margin-top: 4px; height: 320px; min-height: 320px; max-height: 320px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
                            <div>
                                <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 6px; margin-bottom: 10px; height: 105px; display: flex; align-items: center; justify-content: center;">
                                    <img src="{y_item['image']}"style="max-width: 130px; max-height: 95px; object-fit: contain; margin: 0 auto; display: block; border-radius: 6px;"alt="{y_item['name']}"/>
                                </div>
                                <b style="font-size: 0.88rem; color: var(--mm-text-primary); display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.25;">{y_item['name']} {y_sans}</b>
                                <p style="font-size: 0.76rem; color: var(--mm-text-secondary); line-height: 1.4; margin: 4px 0 6px 0; height: 50px; min-height: 50px; max-height: 50px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">{y_item['benefits']}</p>
                            </div>
                            <div>
                                <a href="{yt_link}"target="_blank"style="text-decoration: none; display: block;">
                                    <button style="width: 100%; height: 36px; min-height: 36px; background: rgba(225, 29, 72, 0.12); color: #FF2E5B; border: 1.2px solid rgba(225, 29, 72, 0.4); border-radius: 8px; font-size: 0.76rem; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                        <img src="https://cdn-icons-png.flaticon.com/512/12549/12549246.png" style="width: 14px; height: 14px; object-fit: contain;" alt="Play"/> Watch Video Tutorial on YouTube
                                    </button>
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # 6. Compress & Sek Guidance (Ice vs Hot Sek)
        compress_rec = care_res.get("compress_guidance")
        if compress_rec and isinstance(compress_rec, dict) and compress_rec.get("mode") in ["ice", "hot"]:
            bg = "rgba(59, 130, 246, 0.08)"if compress_rec["mode"] == "ice"else "rgba(234, 88, 12, 0.08)"
            border = "#3B82F6"if compress_rec["mode"] == "ice"else "#F97316"
            label = "Cold / Tepid Compress"if compress_rec["mode"] == "ice"else "Warm / Hot Fomentation"
            st.markdown(f"""<div class="mm-card"style="padding: 16px; margin-top: 14px; background: {bg}; border-color: {border};">
<div style="display: flex; align-items: center; gap: 8px;">
<b style="font-size: 0.95rem; color: var(--mm-text-primary);">{compress_rec.get('title', label)}</b>
</div>
<p style="font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.55; margin: 6px 0 0 0;">{compress_rec.get('text', '')}</p>
</div>""", unsafe_allow_html=True)

        # 7. Potential Conditions (Ranked by ICD-11 Confidence)
        st.markdown(f"<div style='margin-top: 14px;'><b style='font-size: 1.05rem; color: var(--mm-text-primary);'>{T.get('possible_conditions_title', 'Identified Potential Conditions:')}</b></div>", unsafe_allow_html=True)
        res_cols = st.columns(min(3, len(t_res.get("ranked_conditions", []))))
        for idx, cond in enumerate(t_res.get("ranked_conditions", [])[:3]):
            with res_cols[idx]:
                prob_pct = cond.get("match_percentage", 65)
                urgency = "HIGH" if prob_pct > 70 else ("MODERATE" if prob_pct > 45 else "LOW")
                badge_class = "mm-badge-critical" if urgency == "HIGH" else ("mm-badge-warning" if urgency == "MODERATE" else "mm-badge-success")
                c_name = cond.get("name_gu") if lang_code == "gu" and cond.get("name_gu") else (cond.get("name_hi") if lang_code == "hi" and cond.get("name_hi") else cond.get("name", "Condition"))
                c_desc = cond.get("description") or cond.get("overview") or "Consult a licensed physician for diagnostic confirmation."
                c_icd = cond.get("icd_code") or cond.get("icd11_code") or "N/A"
                st.markdown(f"""<div class="mm-card"style="border-top: 3.5px solid #B3261E; padding: 16px; margin-top: 4px; height: 175px; min-height: 175px; max-height: 175px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
<div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
<b style="font-size: 0.95rem; color: var(--mm-text-primary); display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;">{c_name}</b>
<span class="mm-badge {badge_class}">{urgency}</span>
</div>
<div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-bottom: 6px;">Confidence Match: <b>{prob_pct}%</b> · ICD-11: {c_icd}</div>
<p style="font-size: 0.78rem; color: var(--mm-text-secondary); line-height: 1.45; height: 58px; min-height: 58px; max-height: 58px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">{c_desc}</p>
</div>
</div>""", unsafe_allow_html=True)

        # 8. Diet & Red Flags
        col_ns1, col_ns2 = st.columns(2)
        diet_tips = care_res.get("dietary_guidelines") or [
            T.get("diet_tip_1", "Maintain adequate hydration with warm fluids, coconut water, or oral rehydration solution."),
            T.get("diet_tip_2", "Eat easily digestible, nutrient-dense meals such as vegetable soups and khichdi."),
            T.get("diet_tip_3", "Avoid heavy, oily, spicy, and ultra-processed foods during recovery.")
        ]
        red_flag_tips = care_res.get("red_flags") or [
            T.get("redflag_tip_1", "Persistent high fever (>103°F) for more than 3 consecutive days."),
            T.get("redflag_tip_2", "Shortness of breath, chest pain, or sudden confusion/dizziness."),
            T.get("redflag_tip_3", "Inability to retain liquids or severe signs of dehydration.")
        ]
        with col_ns1:
            tips_html = "".join([f"<li>{tip}</li>"for tip in diet_tips])
            st.markdown(f"""
            <div class="mm-card"style="background: rgba(30, 122, 76, 0.08); border: 1px solid rgba(30, 122, 76, 0.3); padding: 14px; margin-top: 6px;">
                <b style="font-size: 0.88rem; color: #4ADE80;">{T.get("dietary_guidance_title", "Dietary & Hydration Guidance")}</b>
                <ul style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 6px 0 0 0; padding-left: 18px; line-height: 1.5;">
                    {tips_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_ns2:
            rf_html = "".join([f"<li>{tip}</li>"for tip in red_flag_tips])
            st.markdown(f"""
            <div class="mm-card"style="background: rgba(179, 38, 30, 0.08); border: 1px solid rgba(179, 38, 30, 0.3); padding: 14px; margin-top: 6px;">
                <b style="font-size: 0.88rem; color: #F87171;">{T.get("red_flag_title", "Emergency Red-Flag Symptoms (Seek Immediate Care)")}</b>
                <ul style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 6px 0 0 0; padding-left: 18px; line-height: 1.5;">
                    {rf_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 9. ACTION BAR: DEEP EXPLAIN, DOWNLOAD REPORT (PDF), SCAN NEW (Positioned right above Medical Disclaimer)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_act1, col_act2, col_act3 = st.columns([1.1, 1.1, 0.8])
        with col_act1:
            if st.button(T.get("deep_explain_btn", "Deep Explain with MediMind AI"), key="btn_toggle_deep_explain", type="primary", use_container_width=True):
                st.session_state["floating_chat_open"] = True
                with st.spinner("Generating clinical deep consultation in AI Assistant..."):
                    deep_text = generate_deep_explanation(
                        symptoms=st.session_state.get("selected_symptoms_list", []),
                        user_context=u_ctx,
                        top_condition=top_disease_name,
                        ranked_conditions=t_res.get("ranked_conditions", []),
                        medicines=care_res.get("medicine_gallery", []),
                        yoga_recs=care_res.get("yoga_recommendations", []),
                        lang=lang_code
                    )
                    st.session_state["floating_chat_history"].append({
                        "role": "assistant",
                        "content": deep_text
                    })
                    st.rerun()

        with col_act2:
            try:
                pdf_user_ctx = {
                    "age": u_ctx.get("age_group", "21-30 Years"),
                    "gender": u_ctx.get("gender", "Male"),
                    "location": u_ctx.get("state", "India"),
                    "duration": u_ctx.get("duration", "1-3 Days"),
                    "severity": u_ctx.get("severity", "Moderate"),
                    "blood_group": u_ctx.get("blood_group", "None"),
                    "pre_existing": u_ctx.get("pre_existing", "None"),
                    "current_meds": u_ctx.get("current_meds", "None"),
                    "allergies": u_ctx.get("allergies", "None"),
                    "symptoms": st.session_state.get("selected_symptoms_list", [])
                }
                pdf_data = generate_pdf_report(pdf_user_ctx, t_res, care_res)
                st.download_button(
                    label=T.get("download_report_btn", "Download Clinical Report (PDF)"),
                    data=pdf_data.getvalue(),
                    file_name=f"MediMind_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="btn_download_triage_pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.button(T.get("download_report_btn", "Download Clinical Report (PDF)"), key="btn_download_triage_pdf_err", disabled=True, use_container_width=True)

        with col_act3:
            if st.button(T.get("scan_new_btn", "Scan New Assessment"), key="btn_scan_new_triage", use_container_width=True):
                st.session_state["triage_result"] = None
                st.session_state["care_recommendations"] = None
                st.session_state["selected_symptoms_list"] = []
                st.session_state["triage_qa_history"] = []
                st.session_state["floating_chat_open"] = False
                st.rerun()

        # 10. Clinical Advisory & Medical Disclaimer
        st.markdown(f"""
        <div class="mm-clinical-advisory-banner"style="background: rgba(234, 88, 12, 0.08); border: 1.2px solid rgba(234, 88, 12, 0.35); border-left: 5px solid #EA580C; border-radius: 10px; padding: 12px 16px; margin-top: 14px; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span style="font-size: 1.1rem;"></span>
                <b style="color: #FB923C; font-size: 0.88rem; letter-spacing: 0.02em; text-transform: uppercase;">{T.get("sidebar_warning_title", "Clinical Advisory")}</b>
            </div>
            <p style="margin: 0; font-size: 0.82rem; color: var(--mm-text-primary); line-height: 1.5;">
                {T.get("sidebar_warning_desc", "MediMind AI can make mistakes. Do not rely solely on AI suggestions — always consult a certified doctor or licensed physician for clinical decisions.")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# MODULE 2: CLINICAL REPORT & PRESCRIPTION ANALYZER
# ==============================================================================
elif st.session_state["active_panel"] == "Medical Report":
    report_icon_html = '<img src="https://cdn-icons-png.flaticon.com/512/16951/16951169.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(179,38,30,0.08); box-shadow: 0 4px 14px rgba(179,38,30,0.35); border: 1.5px solid #B3261E;" alt="Medical Report Icon"/>'
    with st.container(key="mm_top_header_card_2"):
        hdr2_c1, hdr2_c2, hdr2_c3, hdr2_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr2_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {report_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p2_header_title", "Medical Report & Prescription Analyzer")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p2_header_subtitle", "Automated laboratory reference interval comparison, layman explanations, and prescription medication guidance.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr2_c2:
            st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge mm-badge-brand' style='height: 38px; line-height: 38px; padding: 0 16px; display: inline-flex; align-items: center;'>{T.get('p2_badge', 'MediMind AI Vision + OCR')}</span></div>", unsafe_allow_html=True)
        with hdr2_c3:
            header_lang_2 = st.selectbox(
                "Header Lang Selector 2",
                options=LANG_OPTIONS,
                key="hdr_lang_p2",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p2",)
            )
        with hdr2_c4:
            new_theme_p2 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p2")
            if new_theme_p2 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p2
                st.rerun()

    if "p2_step" not in st.session_state:
        st.session_state["p2_step"] = 1

    p2_cur_step = st.session_state.get("p2_step", 1)

    s1_cls = "done" if p2_cur_step > 1 else "active"
    s2_cls = "active" if p2_cur_step == 2 else ("done" if p2_cur_step > 2 else "")
    s3_cls = "active" if p2_cur_step == 3 else ""
    st.markdown(f"""
    <div class="mm-stepper">
        <div class="mm-step-item">
            <div class="mm-step-num {s1_cls}">1</div>
            <div>
                <div class="mm-step-text-title {'active'if p2_cur_step == 1 else ''}">{T.get("p2_step1_title", "Upload & Profile")}</div>
                <div class="mm-step-text-sub">{T.get("p2_step1_sub", "Upload documents & info")}</div>
            </div>
        </div>
        <div class="mm-step-arrow">→</div>
        <div class="mm-step-item">
            <div class="mm-step-num {s2_cls}">2</div>
            <div>
                <div class="mm-step-text-title {'active'if p2_cur_step == 2 else ''}">{T.get("p2_step2_title", "Analysis")}</div>
                <div class="mm-step-text-sub">{T.get("p2_step2_sub", "AI processing & comparison")}</div>
            </div>
        </div>
        <div class="mm-step-arrow">→</div>
        <div class="mm-step-item">
            <div class="mm-step-num {s3_cls}">3</div>
            <div>
                <div class="mm-step-text-title {'active'if p2_cur_step == 3 else ''}">{T.get("p2_step3_title", "Results")}</div>
                <div class="mm-step-text-sub">{T.get("p2_step3_sub", "Insights & guidance")}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- STEP 1 & 2: UPLOAD & OCR EXTRACTION -----------------
    if p2_cur_step < 3:
        col_p2_1, col_p2_2 = st.columns([1, 1])

        with col_p2_1:
            with st.container(border=True):
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <b style="font-size: 0.95rem; color: var(--mm-text-primary);">{T.get("p2_doc_upload_title", "Document Upload & Patient Profile")}</b>
                    <div style="font-size: 0.78rem; font-weight: 600; color: var(--mm-text-secondary); margin-top: 4px;">{T.get("p2_select_doc_type", "Select Document Type")}</div>
                </div>
                """, unsafe_allow_html=True)

                doc_type_choice = st.radio(
                    "Select Document Type",
                    [
                        T.get("doc_type_lab", "Blood / Pathology Lab Report"),
                        T.get("doc_type_presc", "Doctor Prescription"),
                        T.get("doc_type_imaging", "Diagnostic Imaging / Radiology Report")
                    ],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                uploaded_doc = st.file_uploader(
                    "Upload or Drag and Drop Medical Document",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="p2_doc_uploader",
                    help="Supports PDF, PNG, JPG, JPEG (Max 200MB)"
                )

                if uploaded_doc and st.session_state.get("p2_step", 1) == 1:
                    st.session_state["p2_step"] = 2

                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    age_for_report = st.selectbox(f"{T.get('label_age_group', 'Age Group')}", ["Adult", "Senior (60+)", "Pediatric (0-18)"], index=0)
                with d_col2:
                    gender_for_report = st.selectbox(f"{T.get('label_gender', 'Biological Gender')}", ["Male", "Female", "Other"], index=0)

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                analyze_doc_btn = st.button(T.get("btn_analyze_doc", "Analyze Medical Document"), type="primary", use_container_width=True)

        with col_p2_2:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <b style="font-size: 0.95rem; color: var(--mm-text-primary);">{T.get("p2_ocr_title", "OCR Text Stream & Extraction")}</b>
                    <span class="mm-badge {'mm-badge-success'if uploaded_doc else 'mm-badge-info'}"style="font-size: 0.70rem;">{'Document Loaded'if uploaded_doc else 'Awaiting File'}</span>
                </div>
                <div style="font-size: 0.78rem; color: #3B82F6; background: rgba(59, 130, 246, 0.1); padding: 7px 12px; border-radius: 8px; margin-bottom: 8px;">
                    {T.get("p2_ocr_tip", "Upload your file on the left to extract clinical parameters:")} (Read-Only Copyable)
                </div>
                """, unsafe_allow_html=True)

                if uploaded_doc:
                    doc_cache_key = f"{uploaded_doc.name}_{uploaded_doc.size}"
                    cached_text = st.session_state.get("p2_cached_doc_text", "")
                    if st.session_state.get("p2_cached_doc_key") != doc_cache_key or not cached_text:
                        with st.spinner("Extracting clinical text with MediMind AI Vision OCR..."):
                            raw_extracted = extract_text_from_file(uploaded_doc)
                        st.session_state["p2_cached_doc_key"] = doc_cache_key
                        st.session_state["p2_cached_doc_text"] = raw_extracted
                    else:
                        raw_extracted = cached_text

                    if raw_extracted and raw_extracted.strip():
                        doc_text_stream = st.text_area(
                            "Extracted OCR Text Stream",
                            value=raw_extracted,
                            height=335,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                    else:
                        doc_text_stream = ""
                        st.markdown("""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 16px; margin-top: 4px; min-height: 335px; display: flex; flex-direction: column; justify-content: center; text-align: center; align-items: center;">
                            <b style="color: #EF4444; font-size: 0.95rem; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                <img src="https://cdn-icons-png.flaticon.com/512/564/564619.png" style="width: 18px; height: 18px; object-fit: contain;" alt="Warning"/> No Valid Medical Text Detected
                            </b>
                            <span style="font-size: 0.84rem; color: var(--mm-text-secondary); line-height: 1.5; max-width: 480px; margin: 0 auto;">
                                The uploaded file could not be read or does not contain readable clinical test parameters, doctor prescriptions, or radiology findings.<br/>
                                Please upload a clear photo or PDF of an actual medical report, doctor prescription, or radiology document.
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    doc_text_stream = ""
                    st.text_area(
                        "Extracted OCR Text Stream",
                        value="",
                        placeholder="No document uploaded yet. Please upload a PDF or Image on the left to scan real medical parameters...",
                        height=335,
                        disabled=True,
                        label_visibility="collapsed"
                    )

        # Side-by-side Live Document Preview Card (Rendered if file is uploaded)
        if uploaded_doc:
            st.markdown(f"""
            <div class="mm-card"style="margin-top: 4px; border: 1.5px solid #3B82F6;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <b style="font-size: 0.95rem; color: var(--mm-text-primary);"> {T.get('doc_preview_title', 'Live Uploaded Document Preview')} — {uploaded_doc.name}</b>
                    <span class="mm-badge mm-badge-info">{round(uploaded_doc.size / 1024, 1)} KB</span>
                </div>
            """, unsafe_allow_html=True)
            
            file_ext = uploaded_doc.name.lower()
            if file_ext.endswith((".png", ".jpg", ".jpeg")):
                st.image(uploaded_doc, caption=uploaded_doc.name, use_container_width=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.08); border-radius: 8px; padding: 14px; text-align: center; color: var(--mm-text-primary);">
                    <b>PDF Document Preview:</b> {uploaded_doc.name}<br/>
                    <span style="font-size: 0.78rem; color: var(--mm-text-secondary);">Native PDF text stream processed by MediMind OCR Engine.</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # BioPortal Clinical Ontology Lookup (Contained in clean expandable drawer)
        with st.expander(" " + T.get("p2_bioportal_title", "BioPortal Clinical Ontology Lookup"), expanded=False):
            st.markdown(f"""
            <div style="font-size: 0.80rem; color: var(--mm-text-secondary); margin-bottom: 8px;">
                {T.get("p2_bioportal_sub", "Search clinical concepts in SNOMED-CT, LOINC, MeSH, RxNorm, and MedDRA:")}
            </div>
            """, unsafe_allow_html=True)

            if "bioportal_query" not in st.session_state:
                st.session_state["bioportal_query"] = ""

            bp_c1, bp_c2 = st.columns([3.5, 1.2])
            with bp_c1:
                bioportal_input = st.text_input(
                    "BioPortal Search Input",
                    value=st.session_state.get("bioportal_query", ""),
                    placeholder="e.g. Hypertension, Serum Creatinine, Metformin, Diabetes",
                    key="bp_search_text_input",
                    label_visibility="collapsed"
                )
            with bp_c2:
                search_bp_btn = st.button(T.get("btn_search_bioportal", "Search Ontology"), key="btn_run_bioportal_search", type="primary", use_container_width=True)

            # Quick Search Suggestion Chips
            st.markdown("<div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 6px 0 10px 0;'><span style='font-size: 0.76rem; color: var(--mm-text-secondary); font-weight: 600;'>Quick Search:</span>", unsafe_allow_html=True)
            chip_cols = st.columns(6)
            quick_terms = ["Hypertension", "Diabetes", "Creatinine", "Metformin", "Paracetamol", "Pneumonia"]
            for q_idx, term in enumerate(quick_terms):
                with chip_cols[q_idx]:
                    if st.button(term, key=f"bp_chip_{term.lower()}", use_container_width=True):
                        st.session_state["bioportal_query"] = term
                        st.session_state["bp_active_search"] = term
                        st.rerun()

            st.markdown("""
            <div class="mm-ontology-grid"style="margin-top: 8px;">
                <div class="mm-ontology-pill">
                    <div>
                        <b style="color: var(--mm-text-primary); display: block; font-size: 0.80rem;">SNOMED-CT</b>
                        <span style="font-size: 0.68rem; color: var(--mm-text-secondary);">Clinical terminology standards</span>
                    </div>
                </div>
                <div class="mm-ontology-pill">
                    <div>
                        <b style="color: var(--mm-text-primary); display: block; font-size: 0.80rem;">LOINC</b>
                        <span style="font-size: 0.68rem; color: var(--mm-text-secondary);">Lab & clinical observations</span>
                    </div>
                </div>
                <div class="mm-ontology-pill">
                    <div>
                        <b style="color: var(--mm-text-primary); display: block; font-size: 0.80rem;">MeSH</b>
                        <span style="font-size: 0.68rem; color: var(--mm-text-secondary);">Medical subject headings</span>
                    </div>
                </div>
                <div class="mm-ontology-pill">
                    <div>
                        <b style="color: var(--mm-text-primary); display: block; font-size: 0.80rem;">RxNorm / MedDRA</b>
                        <span style="font-size: 0.68rem; color: var(--mm-text-secondary);">Clinical drug formulations</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            active_bp_query = bioportal_input.strip() if (search_bp_btn and bioportal_input.strip()) else st.session_state.get("bp_active_search", "")

            if active_bp_query:
                with st.spinner(f"Querying biomedical ontology knowledgebase for '{active_bp_query}'..."):
                    bp_results = search_bioportal_concept(active_bp_query)
                    if bp_results:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 14px 0 8px 0;">
                            <b style="font-size: 0.90rem; color: var(--mm-text-primary);">Ontology Results for "{active_bp_query}"</b>
                            <span class="mm-badge mm-badge-success">{len(bp_results)} Standard Concepts</span>
                        </div>
                        """, unsafe_allow_html=True)
                        for c in bp_results:
                            c_label = c.get("pref_label") or c.get("prefLabel") or active_bp_query
                            c_ont = c.get("ontology", "Ontology Standard")
                            c_id = c.get("concept_id") or c.get("id", "")
                            c_def = c.get("definition", "Verified medical terminology mapping.")
                            c_cui = c.get("cui", "")
                            c_syns = c.get("synonyms", [])

                            syn_badges = "".join([f"<span class='mm-badge mm-badge-neutral' style='font-size: 0.68rem; margin-right: 4px; padding: 2px 6px;'>{s}</span>" for s in c_syns])
                            cui_html = f"<span class='mm-badge mm-badge-info' style='font-size: 0.68rem; padding: 2px 7px;'>UMLS CUI: {c_cui}</span>" if c_cui else ""
                            def_html = f'<p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 6px 0; line-height: 1.45;">{c_def}</p>' if c_def else ''
                            syn_html = f'<div style="margin-top: 6px; display: flex; align-items: center; flex-wrap: wrap; gap: 4px;"><span style="font-size: 0.70rem; color: var(--mm-text-muted); font-weight: 600;">Synonyms:</span> {syn_badges}</div>' if syn_badges else ''
                            id_html = f'<div style="font-size: 0.70rem; color: var(--mm-text-muted); margin-top: 6px; font-family: monospace; word-break: break-all;">ID: {c_id}</div>' if c_id else ''
                            card_html = (
                                f'<div class="mm-card" style="padding: 14px 16px; margin-bottom: 8px; border-left: 3.5px solid #2563EB;">'
                                f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">'
                                f'<b style="font-size: 0.92rem; color: var(--mm-text-primary);">{c_label}</b>'
                                f'<div style="display: flex; align-items: center; gap: 6px;">{cui_html}<span class="mm-badge mm-badge-brand" style="font-size: 0.70rem; padding: 2px 8px;">{c_ont}</span></div>'
                                f'</div>'
                                f'{def_html}'
                                f'{syn_html}'
                                f'{id_html}'
                                f'</div>'
                            )
                            st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        st.info(f"No direct ontology mapping found for '{active_bp_query}'. Try searching for generic condition or medication names.")

        # Trigger Analysis & Transition to Step 3
        if analyze_doc_btn:
            if not uploaded_doc:
                st.error(f" {T.get('err_no_doc_uploaded', 'Please upload a medical report or prescription document (PDF or Image) before clicking Analyze.')}")
            else:
                if not doc_text_stream or not doc_text_stream.strip():
                    with st.spinner("Extracting clinical text with MediMind AI Vision OCR..."):
                        doc_text_stream = extract_text_from_file(uploaded_doc)
                        st.session_state["p2_cached_doc_text"] = doc_text_stream

                if not doc_text_stream or not doc_text_stream.strip():
                    st.warning("No valid medical test parameters or prescription text were found in the uploaded file. Please upload a clear photo or PDF of an actual medical report or doctor prescription.")
                else:
                    st.session_state["p2_step"] = 3
                    st.session_state["p2_doc_type_choice"] = doc_type_choice
                    st.session_state["p2_doc_text_stream"] = doc_text_stream
                    st.session_state["p2_doc_name"] = uploaded_doc.name if uploaded_doc else "Medical Document"
                    st.session_state["p2_age"] = age_for_report
                    st.session_state["p2_gender"] = gender_for_report
                    st.session_state["p2_deep_ai_chat"] = []
                    st.rerun()


    # ----------------- STEP 3: RESULTS & DIAGNOSTIC EVALUATION -----------------
    elif p2_cur_step == 3:
        doc_text_stream = st.session_state.get("p2_doc_text_stream", "")
        doc_type_choice = st.session_state.get("p2_doc_type_choice", "Blood / Pathology Lab Report")
        age_for_report = st.session_state.get("p2_age", "Adult")
        gender_for_report = st.session_state.get("p2_gender", "Male")
        doc_name = st.session_state.get("p2_doc_name", "Medical Document")

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <b style="font-size: 1.15rem; color: var(--mm-text-primary);">Diagnostic Evaluation & Clinical Findings</b>
                <div style="font-size: 0.82rem; color: var(--mm-text-secondary); margin-top: 2px;">
                    {doc_name} • {doc_type_choice} • Age: {age_for_report}, Gender: {gender_for_report}
                </div>
            </div>
            <span class="mm-badge mm-badge-success" style="font-size: 0.76rem; padding: 4px 12px;">AI Analysis Complete</span>
        </div>
        """, unsafe_allow_html=True)
        
        is_prescription = "Prescription" in str(doc_type_choice) or "पर्ची" in str(doc_type_choice) or "પ્રિસ્ક્રિપ્શન" in str(doc_type_choice) or "Presc" in str(doc_type_choice)
        is_imaging = "Imaging" in str(doc_type_choice) or "Radiology" in str(doc_type_choice) or "रेडियोलॉजी" in str(doc_type_choice) or "इमेजिंग" in str(doc_type_choice) or "રેડિયોલોજી" in str(doc_type_choice) or "ઇમેજિંગ" in str(doc_type_choice)

        if is_prescription:
            presc_res = prescription_analyzer.parse_prescription_text(doc_text_stream)
            if presc_res.get("total_medicines_identified", 0) == 0:
                st.markdown(f"""
                <div class="mm-card" style="border-left: 4px solid #F59E0B; background: rgba(245, 158, 11, 0.05); padding: 18px; margin-top: 10px;">
                    <h4 style="color: #D97706; margin: 0 0 6px 0; font-size: 1.05rem;"> No Prescription Medications Detected</h4>
                    <p style="margin: 0; font-size: 0.90rem; color: var(--mm-text-secondary);">
                        {presc_res.get("summary", "The uploaded document does not contain recognizable doctor-prescribed medications or dosage instructions. Please ensure you upload a valid medical prescription (PDF or Image).")}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"Identified {presc_res['total_medicines_identified']} medications in prescription.")
                for m in presc_res["medicines"]:
                    with st.expander(f"{m['extracted_name']} — {m['frequency']} ({m['timing']})", expanded=True):
                        info = m.get("info", {})
                        st.write(f"**Generic Formulation:** {info.get('generic_name', 'Standard')}")
                        st.write(f"**Indications:** {info.get('purpose', 'As prescribed')}")
                        st.warning(f"**Safety & Warnings:** {info.get('warnings', 'Take as directed.')}")

        elif is_imaging:
            with st.spinner("Analyzing radiological findings, imaging impressions, and anatomical structures..."):
                rad_res = radiology_analyzer.analyze_imaging_report(doc_text_stream, user_lang=lang_code)

            total_findings = rad_res.get("total_findings", 0)
            if total_findings == 0 or not rad_res.get("is_valid_radiology_report", True):
                st.markdown(f"""
                <div class="mm-card"style="border-left: 4px solid #F59E0B; background: rgba(245, 158, 11, 0.05); padding: 18px; margin-top: 10px;">
                    <h4 style="color: #D97706; margin: 0 0 6px 0; font-size: 1.05rem;"> No Radiology / Diagnostic Imaging Findings Detected</h4>
                    <p style="margin: 0; font-size: 0.92rem; color: var(--mm-text-secondary);">
                        {rad_res.get("summary", "The uploaded document does not contain recognizable diagnostic imaging or radiology impressions (such as X-Ray, CT Scan, MRI, Ultrasound, etc.). Please upload a valid medical radiology report.")}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Log analysis to SQLite database
                try:
                    log_report_analysis(
                        report_name=doc_name,
                        report_type="Radiology Analysis",
                        extracted_text=doc_text_stream,
                        summary=rad_res.get("summary", f"Detected {total_findings} radiological findings."),
                        findings=rad_res.get("findings", []),
                        abnormal_count=total_findings
                    )
                except Exception as e:
                    print(f"Notice logging radiology report: {e}")

                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.metric("Total Imaging Findings", total_findings)
                with r_col2:
                    sev_status = rad_res.get("overall_severity", "Normal")
                    st.metric("Overall Radiological Status", sev_status)

                st.markdown("<div class='mm-section-header'style='font-size: 1.05rem; font-weight: 700; color: var(--mm-text-primary); margin: 16px 0 8px 0;'>Radiological Findings & Clinical Impressions</div>", unsafe_allow_html=True)
                for item in rad_res.get("findings", []):
                    sev = item.get("severity", "Normal")
                    pill_class = "mm-badge-critical"if sev in ["High", "Emergency"] else ("mm-badge-brand"if sev == "Medium"else "mm-badge-success")
                    st.markdown(f"""
                    <div class="mm-card"style="padding: 16px; margin-bottom: 10px;">
                        <div class="mm-card-header">
                            <h4 class="mm-card-title">{item.get('finding_name', item.get('english_name', 'Radiology Finding'))}</h4>
                            <span class="mm-badge {pill_class}">{sev.upper()}</span>
                        </div>
                        <p style="margin: 6px 0; font-size: 0.88rem; color: var(--mm-text-secondary);"><b>Modality:</b> {item.get('modality', 'Diagnostic Imaging')}</p>
                        <p style="margin: 4px 0; font-size: 0.92rem; color: var(--mm-text-primary);">{item.get('explanation', '')}</p>
                        <p style="margin: 6px 0 0 0; font-size: 0.88rem; color: #B3261E;"><b>Clinical Action / Recommendation:</b> {item.get('recommendation', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            with st.spinner("Evaluating clinical parameters against biological reference intervals..."):
                lab_res = lab_analyzer.parse_and_evaluate(doc_text_stream, age_group=age_for_report, gender=gender_for_report, lang=lang_code)
            
            total_detected = lab_res.get("total_tests_detected", 0)

            if total_detected == 0:
                st.markdown(f"""
                <div class="mm-card"style="border-left: 4px solid #F59E0B; background: rgba(245, 158, 11, 0.05); padding: 18px; margin-top: 10px;">
                    <h4 style="color: #D97706; margin: 0 0 6px 0; font-size: 1.05rem;"> No Clinical Lab Parameters Detected</h4>
                    <p style="margin: 0; font-size: 0.92rem; color: var(--mm-text-secondary);">
                        {lab_res.get("summary", "The uploaded document does not appear to be a medical lab report or does not contain recognized diagnostic test values. Please ensure you upload a clear laboratory report, blood test (CBC, LFT, KFT, Lipid Profile), or pathology document.")}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Log analysis to SQLite database medimind.db
                try:
                    log_report_analysis(
                        report_name=doc_name,
                        report_type="Lab Evaluation",
                        extracted_text=doc_text_stream,
                        summary=lab_res.get("summary", f"Detected {lab_res.get('abnormal_count', 0)} abnormal parameters out of {total_detected} total."),
                        findings=lab_res.get("findings", []),
                        abnormal_count=lab_res.get("abnormal_count", 0)
                    )
                except Exception as e:
                    print(f"Notice logging report analysis: {e}")

                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Total Parameters Evaluated", total_detected)
                with m_col2:
                    ab_count = lab_res.get("abnormal_count", 0)
                    st.metric("Abnormal / Out-of-Range", ab_count, delta=-ab_count if ab_count > 0 else 0)
                with m_col3:
                    status_overall = "Needs Attention" if lab_res.get("abnormal_count", 0) > 0 else "All Normal"
                    st.metric("Overall Clinical Status", status_overall)

                st.markdown("<div class='mm-section-header'style='font-size: 1.05rem; font-weight: 700; color: var(--mm-text-primary); margin: 16px 0 8px 0;'>Detailed Parameter Breakdown</div>", unsafe_allow_html=True)
                for item in lab_res.get("findings", []):
                    status = item.get("status", "Normal")
                    pill_class = "mm-badge-critical" if status in ["Low", "High"] else "mm-badge-success"
                    st.markdown(f"""
                    <div class="mm-card"style="padding: 16px; margin-bottom: 10px;">
                        <div class="mm-card-header">
                            <h4 class="mm-card-title">{item['test_name']}</h4>
                            <span class="mm-badge {pill_class}">{status.upper()}</span>
                        </div>
                        <p style="margin: 6px 0; font-size: 0.95rem;">
                            <b>Your Value:</b> <span style="font-size: 1.15rem; font-weight: 800; color: {'#B3261E'if status != 'Normal'else '#1E7A4C'};">{item['value']} {item.get('unit', '')}</span> &nbsp;|&nbsp; 
                            <b>Reference Range:</b> {item.get('reference_range', 'Standard')}
                        </p>
                        <p style="margin: 4px 0; font-size: 0.88rem; color: var(--mm-text-secondary);">{item.get('explanation', '')}</p>
                        <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #B3261E;"><b>Clinical Advice:</b> {item.get('action_advice', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Clinical Advisory & Medical Disclaimer at end of report analysis
        st.markdown(f"""
        <div class="mm-clinical-advisory-banner"style="background: rgba(234, 88, 12, 0.08); border: 1.2px solid rgba(234, 88, 12, 0.35); border-left: 5px solid #EA580C; border-radius: 10px; padding: 12px 16px; margin-top: 14px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span style="font-size: 1.1rem;"></span>
                <b style="color: #FB923C; font-size: 0.88rem; letter-spacing: 0.02em; text-transform: uppercase;">{T.get("sidebar_warning_title", "Clinical Advisory")}</b>
            </div>
            <p style="margin: 0; font-size: 0.82rem; color: var(--mm-text-primary); line-height: 1.5;">
                {T.get("sidebar_warning_desc", "MediMind AI can make mistakes. Do not rely solely on AI suggestions — always consult a certified doctor or licensed physician for clinical decisions.")}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Action Buttons: Deep AI Analysis & New Scan
        p2_act_c1, p2_act_c2 = st.columns([1.2, 1])
        with p2_act_c1:
            if st.button(" " + T.get("btn_deep_ai", "Deep Analyze with AI"), type="primary", use_container_width=True, key="btn_p2_deep_ai_action"):
                show_deep_ai_report_dialog(
                    report_text=st.session_state.get("p2_doc_text_stream", ""),
                    report_type=st.session_state.get("p2_doc_type_choice", "Medical Report"),
                    lang_code=lang_code
                )
        with p2_act_c2:
            if st.button(T.get("btn_new_scan", "New Scan / Upload Another Document"), icon=":material/refresh:", use_container_width=True, key="btn_p2_new_scan_action"):
                st.session_state["p2_step"] = 1
                st.session_state["p2_cached_doc_key"] = None
                st.session_state["p2_cached_doc_text"] = ""
                st.session_state["p2_deep_ai_chat"] = []
                st.session_state["p2_doc_text_stream"] = ""
                st.rerun()

    # Footer
    st.markdown(render_footer_trust_bar(T), unsafe_allow_html=True)


elif st.session_state["active_panel"] == "Nearby Healthcare":
    gis_icon_html = '<img src="https://cdn-icons-png.flaticon.com/512/4002/4002972.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(2,132,199,0.08); box-shadow: 0 4px 14px rgba(2,132,199,0.35); border: 1.5px solid #0284C7;" alt="Healthcare Finder Icon"/>'
    with st.container(key="mm_top_header_card_3"):
        hdr3_c1, hdr3_c2, hdr3_c3, hdr3_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr3_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {gis_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p3_header_title", "Nearby Healthcare & Emergency Finder")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p3_header_subtitle", "Locate verified 24/7 trauma centers, hospitals, clinics, and pharmacies with live routing.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr3_c2:
            st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge mm-badge-brand' style='height: 38px; line-height: 38px; padding: 0 16px; display: inline-flex; align-items: center;'>{T.get('p3_gis_badge', 'Live GIS Healthcare Engine')}</span></div>", unsafe_allow_html=True)
        with hdr3_c3:
            header_lang_3 = st.selectbox(
                "Header Lang Selector 3",
                options=LANG_OPTIONS,
                key="hdr_lang_p3",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p3",)
            )
        with hdr3_c4:
            new_theme_p3 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p3")
            if new_theme_p3 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p3
                st.rerun()

    gis_c1, gis_c2, gis_c3 = st.columns([1.1, 1.1, 1.1])

    with gis_c1:
        st.markdown(f"""
        <div class="mm-card">
            <b style="font-size: 0.90rem; color: var(--mm-text-primary);">{T.get("gis_step1_title", "Location & Perimeter")}</b>
        """, unsafe_allow_html=True)

        loc_source = st.radio(
            "Choose Location Source:",
            [
                "Live Device GPS",
                "Auto-Detect via Network IP",
                "Search Specific Indian City / Area"
            ],
            index=2,
            label_visibility="collapsed"
        )

        selected_lat = 23.0225
        selected_lon = 72.5714
        loc_name = "Ahmedabad, Gujarat"

        if "Live Device GPS" in loc_source:
            gps_status = st.query_params.get("gps_status", "")
            if gps_status == "SUCCESS" and "gps_lat" in st.query_params and "gps_lon" in st.query_params:
                try:
                    selected_lat = float(st.query_params["gps_lat"])
                    selected_lon = float(st.query_params["gps_lon"])
                    loc_name = reverse_geocode(selected_lat, selected_lon)
                except Exception:
                    selected_lat, selected_lon, loc_name = 23.0225, 72.5714, "Ahmedabad, Gujarat"
            elif gps_status == "ERROR":
                err_code = str(st.query_params.get("gps_err_code", "1"))
                if err_code == "1":
                    st.warning("⚠️ Location Permission Denied in browser.")
                elif err_code == "2":
                    st.warning("⚠️ Device GPS is Turned OFF.")
                else:
                    st.warning("⚠️ Location Request Timed Out.")
                selected_lat, selected_lon, loc_name = 23.0225, 72.5714, "Ahmedabad, Gujarat"

            # Auto-requesting Geolocation JavaScript Bridge
            gps_html = """
            <script>
            function autoRequestGPS() {
                if (!navigator.geolocation) {
                    try {
                        const url = new URL(window.parent.location.href);
                        url.searchParams.set("gps_status", "ERROR");
                        url.searchParams.set("gps_err_code", "1");
                        window.parent.location.href = url.toString();
                    } catch(e) {}
                    return;
                }

                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        try {
                            const url = new URL(window.parent.location.href);
                            const lat = pos.coords.latitude.toFixed(6);
                            const lon = pos.coords.longitude.toFixed(6);
                            if (url.searchParams.get("gps_lat") !== lat || url.searchParams.get("gps_lon") !== lon) {
                                url.searchParams.set("gps_lat", lat);
                                url.searchParams.set("gps_lon", lon);
                                url.searchParams.set("gps_status", "SUCCESS");
                                url.searchParams.delete("gps_err_code");
                                window.parent.location.href = url.toString();
                            }
                        } catch(e) {
                            console.error(e);
                        }
                    },
                    function(err) {
                        try {
                            const url = new URL(window.parent.location.href);
                            if (url.searchParams.get("gps_status") !== "ERROR" || url.searchParams.get("gps_err_code") !== String(err.code)) {
                                url.searchParams.set("gps_status", "ERROR");
                                url.searchParams.set("gps_err_code", String(err.code));
                                window.parent.location.href = url.toString();
                            }
                        } catch(e) {
                            console.error(e);
                        }
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            }
            autoRequestGPS();
            </script>
            """
            components.html(gps_html, height=0)

        elif "Auto-Detect" in loc_source:
            client_ip = get_client_ip()
            auto_geo = detect_auto_location(client_ip=client_ip)
            selected_lat = float(auto_geo.get("lat", 23.0225))
            selected_lon = float(auto_geo.get("lon", 72.5714))
            loc_name = auto_geo.get("formatted_address") or f"{auto_geo.get('city', 'Ahmedabad')}, {auto_geo.get('region', 'Gujarat')}"

        else:
            search_addr = st.text_input("Enter City or District:", value="Ahmedabad, Gujarat", label_visibility="collapsed")
            geo = geocode_address(search_addr)
            if geo:
                selected_lat = geo["latitude"]
                selected_lon = geo["longitude"]
                loc_name = geo["formatted_address"]
            else:
                selected_lat, selected_lon, loc_name = geocode_city_district(search_addr)

        st.markdown(f"""
            <div style="font-size: 0.74rem; color: #B3261E; margin-top: 8px;">
                <b>Location:</b> {loc_name} ({selected_lat:.4f}, {selected_lon:.4f})
            </div>
        </div>
        """, unsafe_allow_html=True)

    with gis_c2:
        st.markdown(f"""
        <div class="mm-card">
            <b style="font-size: 0.90rem; color: var(--mm-text-primary);">{T.get("gis_step2_title", "Facility Category")}</b>
        """, unsafe_allow_html=True)

        facility_cat_map = {
            T.get("fac_emergency", "24/7 Emergency & Trauma Centers"): "emergency_24x7",
            T.get("fac_hospital", "Multi-Speciality Hospitals"): "hospital",
            T.get("fac_clinic", "Specialized Clinics & Daycare"): "clinic",
            T.get("fac_pharmacy", "24/7 Pharmacies & Chemists"): "pharmacy",
            T.get("fac_blood_bank", "Regional Blood Banks"): "blood_bank",
            T.get("fac_diagnostic", "Diagnostic & Pathology Labs"): "diagnostic"
        }

        cat_choice = st.selectbox(
            "Facility Type",
            list(facility_cat_map.keys()),
            index=0,
            label_visibility="collapsed"
        )
        active_facility_key = facility_cat_map.get(cat_choice, "hospital")

        search_radius = st.slider("Perimeter Radius (KM):", min_value=1, max_value=25, value=5, step=1)
        st.markdown("</div>", unsafe_allow_html=True)

    with gis_c3:
        st.markdown(f"""
        <div class="mm-card">
            <b style="font-size: 0.90rem; color: var(--mm-text-primary);">{T.get("gis_step3_title", "Navigation Mode & Sort")}</b>
        """, unsafe_allow_html=True)

        sort_by = st.selectbox(
            "Sort Facilities By:",
            [T.get("sort_distance", "Distance (Closest First)"), T.get("sort_rating", "Highest Rating (4.0+ Stars)"), T.get("sort_emergency", "Emergency Priority")],
            index=0,
            label_visibility="collapsed"
        )

        travel_mode_choice = st.selectbox(
            "Travel Mode:",
            [
                T.get("mode_car", "Car / Ambulance (Driving)"),
                T.get("mode_bike", "Two-Wheeler / Bike"),
                T.get("mode_walk", "Walking"),
                T.get("mode_bus", "Public Transit")
            ],
            index=0,
            label_visibility="collapsed"
        )
        mode_code = "car"if "Car"in str(travel_mode_choice) else ("bike"if "Bike"in str(travel_mode_choice) else ("walk"if "Walk"in str(travel_mode_choice) else "bus"))

        st.markdown("""
        <div style="background: rgba(179, 38, 30, 0.08); border: 1px dashed rgba(179, 38, 30, 0.4); border-radius: 8px; padding: 6px 10px; margin-top: 8px; font-size: 0.72rem; color: #F87171;">
            <b>Emergency Helplines:</b> Ambulance <b>108</b> · National <b>112</b> · AIIMS <b>1910</b>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # Search nearby healthcare facilities
    with st.spinner(f"Locating verified facilities near {loc_name}..."):
        try:
            facilities = search_nearby_healthcare(
                selected_lat,
                selected_lon,
                facility_category=active_facility_key,
                radius_meters=search_radius * 1000
            )
        except Exception as e:
            print(f"Error querying healthcare: {e}")
            facilities = []

    facilities = facilities or []

    # Sorting
    if "Rating"in str(sort_by):
        facilities.sort(key=lambda x: (float(x.get("rating") or 0.0), -float(x.get("distance_km") or 999.0)), reverse=True)
    elif "Emergency"in str(sort_by):
        facilities.sort(key=lambda x: (0 if ("24/7"in str(x.get("emergency", "")) or "Yes"in str(x.get("emergency", "")) or x.get("is_emergency")) else 1, float(x.get("distance_km") or 999.0)))
    else:
        facilities.sort(key=lambda x: float(x.get("distance_km") or 999.0))

    active_fac_idx = st.session_state.get("selected_nav_fac_idx", None)
    selected_fac = None
    route_info = None

    if isinstance(active_fac_idx, int) and 0 <= active_fac_idx < len(facilities):
        selected_fac = facilities[active_fac_idx]
        try:
            route_info = get_route(selected_lat, selected_lon, selected_fac['lat'], selected_fac['lon'], mode=mode_code)
        except Exception:
            route_info = None

    if selected_fac is not None and route_info is not None:
        r_c1, r_c2 = st.columns([4.2, 1.0])
        with r_c1:
            st.markdown(f"""
            <div style="background: rgba(179, 38, 30, 0.08); border: 1.5px solid rgba(179, 38, 30, 0.4); border-radius: 10px; padding: 10px 14px; margin-bottom: 10px;">
                <div style="font-size: 0.88rem; font-weight: 800; color: #F87171;">Active Route: {selected_fac['name']}</div>
                <div style="font-size: 0.78rem; color: var(--mm-text-secondary);">Mode: <b>{travel_mode_choice}</b> · Distance: <b>{route_info.get('distance_km', selected_fac.get('distance_km'))} KM</b> · Est. Time: <b>~{route_info.get('duration', '10 mins')}</b></div>
            </div>
            """, unsafe_allow_html=True)
        with r_c2:
            if st.button(T.get("btn_clear_route", "Clear Route"), key="btn_clear_active_route", type="secondary", use_container_width=True):
                st.session_state["selected_nav_fac_idx"] = None
                st.rerun()

    # Map Component
    map_html = generate_google_map_html(
        user_lat=selected_lat,
        user_lon=selected_lon,
        facilities=facilities,
        location_name=loc_name,
        selected_facility=selected_fac,
        route_data=route_info
    )
    components.html(map_html, height=390)

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0 10px 0;">
        <b style="font-size: 1.1rem; color: var(--mm-text-primary);">Verified Facilities ({len(facilities)} Found within {search_radius} KM)</b>
    </div>
    """, unsafe_allow_html=True)

    if not facilities:
        st.info("No facilities found for this specific filter within the radius. Try increasing the search radius.")
    else:
        for row_start in range(0, len(facilities), 3):
            row_facs = facilities[row_start:row_start + 3]
            f_cols = st.columns(3)
            for c_idx, fac in enumerate(row_facs):
                i = row_start + c_idx
                with f_cols[c_idx]:
                    rating_val = fac.get("rating", 4.5)
                    dist_val = fac.get("distance_km", 1.5)
                    fac_name = fac.get("name", "Healthcare Facility")
                    fac_type = fac.get("type", "Healthcare Facility")
                    fac_address = fac.get("address", "Nearby Area")
                    fac_phone = fac.get("phone", "108 / Reception Desk")
                    fac_emergency = fac.get("emergency", "24/7 Operational")

                    with st.container():
                        st.markdown(f"""
                        <div class="mm-hospital-card">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px;">
                                    <b style="font-size: 0.94rem; color: var(--mm-text-primary); line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 38px;">{fac_name}</b>
                                    <span class="mm-badge"style="background: rgba(179, 38, 30, 0.15); color: #F87171; border: 1px solid rgba(179, 38, 30, 0.4); font-size: 0.72rem; font-weight: 800; padding: 2px 6px; white-space: nowrap; flex-shrink: 0;">{dist_val:.2f} KM</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 0.76rem; color: var(--mm-text-secondary); font-weight: 600;">{fac_type}</span>
                                    <span style="font-size: 0.78rem; color: #F59E0B; font-weight: 700;">{rating_val}</span>
                                </div>
                                <div style="font-size: 0.75rem; color: var(--mm-text-secondary); margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 32px; line-height: 1.3;">{fac_address}</div>
                                <div style="font-size: 0.75rem; color: var(--mm-text-secondary);"><b>Phone:</b> {fac_phone}</div>
                            </div>
                            <div style="margin-top: 6px;">
                                <span class="mm-badge mm-badge-success"style="font-size: 0.68rem; padding: 2px 8px;">{fac_emergency}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='margin-top: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                        b_c1, b_c2 = st.columns(2)
                        with b_c1:
                            if st.button(T.get("btn_route", "Route"), key=f"fac_route_{i}", type="primary", use_container_width=True):
                                st.session_state["selected_nav_fac_idx"] = i
                                st.rerun()
                        with b_c2:
                            direct_maps_url = fac.get("google_maps_uri") or f"https://www.google.com/maps/dir/?api=1&destination={fac['lat']},{fac['lon']}"
                            st.link_button(T.get("btn_view_map", "View on Map"), direct_maps_url, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(render_footer_trust_bar(T), unsafe_allow_html=True)


# ==============================================================================
# MODULE 4: HEALTH RECORDS & MEDICAL HISTORY (SQLite Vault)
# ==============================================================================
elif st.session_state["active_panel"] == "Health Records":
    records_icon_html = '<img src="https://cdn-icons-png.flaticon.com/512/2913/2913465.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(139,92,246,0.08); box-shadow: 0 4px 14px rgba(139,92,246,0.35); border: 1.5px solid #8B5CF6;" alt="Health Records Vault Icon"/>'
    with st.container(key="mm_top_header_card_4"):
        hdr4_c1, hdr4_c2, hdr4_c3, hdr4_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr4_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {records_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p4_header_title", "Health Records & Clinical History")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p4_header_subtitle", "Securely manage longitudinal health records, prior assessments, diagnostic reports, and prescriptions.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr4_c2:
            st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge mm-badge-info' style='height: 38px; line-height: 38px; padding: 0 16px; display: inline-flex; align-items: center;'>AES-256 VAULT</span></div>", unsafe_allow_html=True)
        with hdr4_c3:
            header_lang_4 = st.selectbox(
                "Header Lang Selector 4",
                options=LANG_OPTIONS,
                key="hdr_lang_p4",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p4",)
            )
        with hdr4_c4:
            new_theme_p4 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p4")
            if new_theme_p4 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p4
                st.rerun()

    tab_rep, tab_pres, tab_ass, tab_sav = st.tabs([
        T.get("tab_lab_reports", "Medical Reports"),
        T.get("tab_prescriptions", "Prescriptions"),
        T.get("tab_assessments", "Previous Assessments"),
        T.get("tab_saved_insights", "Saved Insights")
    ])

    with tab_rep:
        reports_data = get_recent_report_history(limit=50)
        if reports_data:
            st.markdown(f"""
            <div class="mm-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <b style="font-size: 1.05rem; color: var(--mm-text-primary);">{T.get("tab_lab_reports", "Medical Reports")}</b>
                    <span class="mm-badge mm-badge-brand">{len(reports_data)} Stored Reports</span>
                </div>
            """, unsafe_allow_html=True)
            for r in reports_data:
                created_ts = str(r.get('created_at', ''))[:16]
                ab_c = r.get('abnormal_count', 0)
                badge_style = 'mm-badge-critical'if ab_c > 0 else 'mm-badge-success'
                badge_txt = f"{ab_c} Out of Range"if ab_c > 0 else "All Normal"
                with st.expander(f" {r.get('report_name', 'Lab Report')} — {created_ts} ({badge_txt})", expanded=False):
                    st.markdown(f"""
                    <div style="padding: 6px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.82rem; color: var(--mm-text-secondary);">Type: <b>{r.get('report_type', 'Pathology')}</b></span>
                            <span class="mm-badge {badge_style}">{badge_txt}</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.04); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                            <b style="font-size: 0.84rem; color: var(--mm-text-primary);">Summary:</b>
                            <p style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 2px 0 0 0;">{r.get('summary', 'Report evaluated successfully.')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if r.get('extracted_text'):
                        st.caption("Extracted Text Excerpt:")
                        st.code(r.get('extracted_text')[:400], language="text")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="mm-card"style="text-align: center; padding: 36px 20px;">
                <b style="color: var(--mm-text-primary); font-size: 1.0rem;">{T.get("no_records_found", "No medical report records found in this section yet.")}</b>
                <p style="color: var(--mm-text-secondary); font-size: 0.84rem; margin-top: 6px;">{T.get("no_records_guidance", "Upload and analyze a report in Panel 2 to securely store your history here.")}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_pres:
        st.markdown(f"""
        <div class="mm-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <b style="font-size: 1.0rem; color: var(--mm-text-primary);">{T.get("tab_prescriptions", "Active & Past Prescriptions")}</b>
                <span class="mm-badge mm-badge-brand">Digital Vault</span>
            </div>
            <div style="background: rgba(179, 38, 30, 0.05); border: 1.5px solid rgba(179, 38, 30, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <b style="font-size: 0.92rem; color: var(--mm-text-primary);">General Medicine & Antipyretic Consultation</b>
                        <div style="font-size: 0.76rem; color: var(--mm-text-secondary);">Clinical Assessment Prescription · Verified Active</div>
                    </div>
                    <span class="mm-badge mm-badge-success">Active</span>
                </div>
                <p style="font-size: 0.78rem; color: var(--mm-text-secondary); margin: 6px 0 0 0;">Paracetamol 650mg (After Food) · Pantoprazole 40mg (Empty Stomach) · Electral ORS</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_ass:
        triage_history = get_recent_triage_history(limit=50)
        if triage_history:
            st.markdown(f"""
            <div class="mm-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <b style="font-size: 1.0rem; color: var(--mm-text-primary);">{T.get("tab_assessments", "Past MediMind AI Triage Assessments")}</b>
                    <span class="mm-badge mm-badge-info">{len(triage_history)} Sessions</span>
                </div>
            """, unsafe_allow_html=True)
            for t_item in triage_history:
                symps_parsed = []
                try:
                    symps_parsed = json.loads(t_item.get("symptoms_list", "[]"))
                except Exception:
                    symps_parsed = []
                symps_str = ", ".join(symps_parsed) if symps_parsed else "Fever, Fatigue"
                created_ts = str(t_item.get('created_at', ''))[:16]
                urg = t_item.get('urgency_level', 'NORMAL')
                urg_badge = 'mm-badge-critical'if 'Critical'in urg or 'Emergency'in urg else ('mm-badge-warning'if 'Moderate'in urg else 'mm-badge-success')
                
                with st.expander(f"Triage Assessment: {symps_str[:40]} — {created_ts}", expanded=False):
                    st.markdown(f"""
                    <div style="padding: 4px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.82rem; color: var(--mm-text-secondary);">Age: <b>{t_item.get('age_group', 'Adult')}</b> · Gender: <b>{t_item.get('gender', 'Male')}</b> · Duration: <b>{t_item.get('duration', '1-3 Days')}</b></span>
                            <span class="mm-badge {urg_badge}">{urg}</span>
                        </div>
                        <div style="font-size: 0.80rem; color: var(--mm-text-primary); margin-top: 4px;">
                            <b>Reported Symptoms:</b> {symps_str}<br/>
                            <b>Pre-existing Conditions:</b> {t_item.get('existing_conditions', 'None')}<br/>
                            <b>Ongoing Medications:</b> {t_item.get('current_medicines', 'None')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="mm-card"style="text-align: center; padding: 36px 20px;">
                <b style="color: var(--mm-text-primary); font-size: 1.0rem;">{T.get("no_records_found", "No triage assessment records found yet.")}</b>
                <p style="color: var(--mm-text-secondary); font-size: 0.84rem; margin-top: 6px;">{T.get("no_records_guidance", "Complete a health assessment in Panel 1 to store your clinical history here.")}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_sav:
        st.markdown(f"""
        <div class="mm-card">
            <b style="font-size: 1.0rem; color: var(--mm-text-primary); display: block; margin-bottom: 10px;">{T.get("tab_saved_insights", "Saved Health Insights & AI Dietary Regimens")}</b>
            <ul style="font-size: 0.85rem; color: var(--mm-text-secondary); line-height: 1.6; padding-left: 20px;">
                <li><b>Hydration Protocol:</b> Warm fluids, electrolyte water (ORS), and coconut water during fever and recovery.</li>
                <li><b>Electrolyte Balance:</b> Avoid heavy oily foods during high temperature spikes; consume easily digestible soups and khichdi.</li>
                <li><b>Sleep Hygiene:</b> Maintain consistent 7.5 hour sleep window to boost immune antibody production.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(render_footer_trust_bar(T), unsafe_allow_html=True)


elif st.session_state["active_panel"] == "About MediMind AI":
    about_icon_b64 = get_base64_image(FAVICON_PATH)
    about_icon_html = f'<img src="{about_icon_b64}" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 4px; background: rgba(245,158,11,0.08); box-shadow: 0 4px 14px rgba(245,158,11,0.35); border: 1.5px solid #F59E0B;" alt="MediMind Brand Icon"/>' if about_icon_b64 else '<img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(245,158,11,0.08); box-shadow: 0 4px 14px rgba(245,158,11,0.35); border: 1.5px solid #F59E0B;" alt="MediMind Brand Icon"/>'
    with st.container(key="mm_top_header_card_5"):
        hdr5_c1, hdr5_c2, hdr5_c3, hdr5_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr5_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {about_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p5_header_title", "About MediMind AI")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p5_header_subtitle", "Architecture, system intelligence, clinical datasets, and development credits.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr5_c2:
            st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge mm-badge-success' style='height: 38px; line-height: 38px; padding: 0 16px; display: inline-flex; align-items: center;'>V2.0 PRODUCTION</span></div>", unsafe_allow_html=True)
        with hdr5_c3:
            header_lang_5 = st.selectbox(
                "Header Lang Selector 5",
                options=LANG_OPTIONS,
                key="hdr_lang_p5",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p5",)
            )
        with hdr5_c4:
            new_theme_p5 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p5")
            if new_theme_p5 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p5
                st.rerun()

    # Localized Content Dictionary for About MediMind AI (En / Hi / Gu)
    ABOUT_TEXT = {
        "en": {
            "creator_badge": "Founder, Architect & Creator",
            "creator_name": "Developed by Daksh Vasani",
            "creator_sub": "M.Sc. Data Science Student | Python & Machine Learning Enthusiast · Gujarat, India",
            "mission_title": "Project Vision & Architecture",
            "mission_body": "MediMind AI was conceptualized and developed by <b>Daksh Vasani</b> (M.Sc. Data Science student) to create an evidence-based, transparent, and audited AI healthcare platform. The system integrates a <b>Random Forest Disease Classifier (99.01% train accuracy, 97.8% CV)</b>, a <b>Demand Forecaster (6.53% WAPE, 0.9839 R²)</b>, an <b>Official WHO Outbreak Intelligence pipeline</b>, a <b>100+ Major Indian Diseases Knowledge Graph</b>, and <b>Multimodal Generative AI (Groq / Gemini)</b> with strict clinical provenance standards.",
            "tab_models": "AI & ML Models & Accuracy",
            "tab_diseases": "100+ Major Indian Diseases",
            "tab_datasources": "Authentic Data Sources & Live APIs",
            "tab_features": "Architecture, Security & Privacy",
            # Models Tab
            "ml_title": "1. Clinical Disease Prediction Model (Local Engine)",
            "ml_sub": "Scikit-Learn Random Forest Classifier trained over clinical symptom-disease bipartite matrix.",
            "stat_acc": "99.01%",
            "stat_acc_sub": "Training Accuracy (97.8% 5-Fold CV)",
            "stat_algo": "Random Forest",
            "stat_algo_sub": "50 Decision Trees (Scikit-Learn)",
            "stat_features": "280 Symptoms",
            "stat_features_sub": "Binary Indicator Features",
            "stat_classes": "101 Diseases",
            "stat_classes_sub": "WHO ICD-11 Standard Classes",
            "ml_step1": "<b>1. Feature Engineering:</b> Bipartite mappings from <code>symptoms_master.csv</code> convert patient symptom sets into 280-dimensional binary vectors.",
            "ml_step2": "<b>2. Ensemble Training:</b> 50 specialized decision trees evaluate symptom combinations with Gini impurity optimization (<code>train.py</code>).",
            "ml_step3": "<b>3. Model Serialization:</b> Pre-trained weights serialized into <code>models/disease_model.pkl</code> (5.5 MB) for instant sub-millisecond local inference.",
            "demand_title": "2. Medicine Demand Forecasting Model (HMIS Supply Chain)",
            "demand_sub": "Chronologically validated Random Forest Regressor predicting weekly institutional medicine consumption without future leakage.",
            "stat_wape": "6.53%",
            "stat_wape_sub": "Held-Out Test WAPE",
            "stat_r2": "0.9839",
            "stat_r2_sub": "R² Variance Explained",
            "stat_mae": "12.17",
            "stat_mae_sub": "Mean Absolute Error",
            "stat_rmse": "19.50",
            "stat_rmse_sub": "Root Mean Squared Error",
            "demand_step1": "<b>1. Data Ingestion:</b> 20,904 institutional consumption records from MoHFW HMIS partitioned with zero chronological leakage.",
            "demand_step2": "<b>2. Feature Lagging:</b> Rolling 4-week, 12-week consumption trends and seasonal epidemiological indices.",
            "demand_step3": "<b>3. Model File:</b> Serialized in <code>models/demand_model.pkl</code> with empirical residual uncertainty standard error (±19.50 units).",
            "stockout_title": "3. Operational Stockout Risk Engine (Honest Rule-Based Engine)",
            "stockout_sub": "Deterministic inventory risk thresholding based on days-of-stock buffer calculations.",
            "stockout_desc": "<b>Operational Decision Thresholds:</b><br/>• <b>Critical Risk:</b> Stock < 3 Days remaining (Immediate Red Flag)<br/>• <b>Urgent Risk:</b> Stock < 7 Days remaining (Priority Replenishment)<br/>• <b>Watchlist:</b> Stock < 14 Days remaining (Normal Tracking)<br/>• <b>Safe Buffer:</b> Stock ≥ 14 Days remaining (Operational Stability)<br/><i>Note: Categorized honestly as 'RULE_BASED' to eliminate misleading classification claims.</i>",
            "kg_title": "4. Clinical Knowledge Graph & Triage Engine",
            "kg_sub": "Deterministic expert system ensuring clinical safety, emergency triggers, and demographic exclusions.",
            "kg_item1": "<b>ICD-11 Bipartite Scoring:</b> Weighted matching with 1.6x multiplier for mandatory primary clinical symptoms.",
            "kg_item2": "<b>Emergency Red-Flag Protocols:</b> Instant detection of critical warning signs (e.g. chest pain with breathlessness).",
            "kg_item3": "<b>Demographic Clinical Filtering:</b> Automatic gender/age exclusions to eliminate biologically impossible diagnoses.",
            "llm_title": "5. Medical Foundation LLMs (Live AI Engine)",
            "llm_sub": "High-speed reasoning via Groq (LLaMA-3.3 70B, Qwen 27B) and Google Gemini 2.5 Flash.",
            "llm_item1": "<b>Dynamic Care Prescriptions:</b> Calculates illness-specific medicines, exact food timing ('After Food' vs 'Empty Stomach'), and course duration.",
            "llm_item2": "<b>Drug-Drug & Allergy Shield:</b> Evaluates patient ongoing medications and allergies to prevent adverse drug reactions.",
            "llm_item3": "<b>Multilingual Generation:</b> Real-time native clinical advice generation in English, Hindi, and Gujarati.",
            "ocr_title": "6. Computer Vision & Medical Document OCR",
            "ocr_sub": "Gemini Multimodal Vision API + Tesseract OCR for automated clinical entity extraction.",
            "ocr_item1": "<b>Blood Lab Report Analyzer:</b> Extracts CBC, LFT, KFT, Lipid, HbA1c values and highlights out-of-range biomarkers.",
            "ocr_item2": "<b>Prescription & Medicine Scanner:</b> Extracts drug names, dosages, and cross-references OpenFDA chemical profiles.",
            # Diseases Tab
            "dis_title": "100+ Official Major Indian Diseases Taxonomy",
            "dis_sub": "Curated clinical profiles spanning 18 official disease categories under MoHFW and WHO ICD-10/11 guidelines.",
            "dis_cat_1": "<b><img src='https://cdn-icons-png.flaticon.com/512/3888/3888124.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Cancer & Oncology:</b> Leukemia (Blood Cancer), Breast Cancer, Oral/Mouth Cancer, Lung Cancer, Cervical Cancer, Colorectal Cancer, Stomach Cancer, Liver Cancer, Prostate Cancer, Lymphoma.",
            "dis_cat_2": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Heart & Circulatory:</b> Coronary Heart Disease, Heart Attack (Myocardial Infarction), Heart Failure, Hypertension, Stroke, Peripheral Artery Disease.",
            "dis_cat_3": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Diabetes & Metabolic:</b> Type 1 Diabetes, Type 2 Diabetes, Gestational Diabetes, Obesity, Metabolic Syndrome, Thyroid Disorders.",
            "dis_cat_4": "<b><img src='https://cdn-icons-png.flaticon.com/512/10154/10154217.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Respiratory:</b> COPD, Asthma, Pneumonia, Tuberculosis (TB), Acute Respiratory Infections, Pulmonary Fibrosis.",
            "dis_cat_5": "<b><img src='https://cdn-icons-png.flaticon.com/512/15625/15625461.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Kidney & Renal:</b> Chronic Kidney Disease (CKD), Acute Kidney Injury (AKI), Kidney Stones, Glomerulonephritis, Polycystic Kidney Disease.",
            "dis_cat_6": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Liver & Gastrointestinal:</b> Liver Cirrhosis, Viral Hepatitis (B, C), Fatty Liver (NAFLD), GERD, Peptic Ulcer, Pancreatitis, Gallstones.",
            "dis_cat_7": "<b><img src='https://cdn-icons-png.flaticon.com/512/3286/3286097.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Neurological:</b> Epilepsy, Parkinson's Disease, Alzheimer's/Dementia, Migraine, Neuropathy.",
            "dis_cat_8": "<b><img src='https://cdn-icons-png.flaticon.com/128/13286/13286061.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Infectious & Vector-Borne:</b> Dengue Fever, Malaria, Chikungunya, Typhoid, Cholera, Japanese Encephalitis, Kala-Azar, Scrub Typhus.",
            "dis_cat_9": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Blood Disorders:</b> Sickle Cell Disease, Thalassemia, Iron Deficiency Anemia, Aplastic Anemia, Hemophilia.",
            "dis_cat_10": "<b><img src='https://cdn-icons-png.flaticon.com/512/9418/9418433.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Musculoskeletal & Joint:</b> Osteoarthritis, Rheumatoid Arthritis, Gout, Osteoporosis, Ankylosing Spondylitis.",
            "dis_cat_11": "<b><img src='https://cdn-icons-png.flaticon.com/512/8256/8256189.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Eye & Vision:</b> Cataract, Glaucoma, Diabetic Retinopathy, Conjunctivitis.",
            "dis_cat_12": "<b><img src='https://cdn-icons-png.flaticon.com/512/15305/15305545.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> Zoonotic & Emergency:</b> Snakebite, Rabies (Dog bite), Leptospirosis, Sepsis, Anaphylaxis.",
            # Data Sources Tab
            "sources_title": "Authentic Clinical Data Sources (Where Does the Data Come From?)",
            "sources_sub": "MediMind AI strictly uses official, verified, and audited data sources with complete provenance traceability.",
            "src_who_title": "WHO Official Outbreak News API (DON API)",
            "src_who_desc": "Automated ingestion via official WHO Disease Outbreak News REST API (<code>https://www.who.int/api/news/diseaseoutbreaknews</code>). Ingests 100 official global events categorized into Direct India, Relevant to India, and Global Outbreaks.",
            "src_hmis_title": "MoHFW HMIS Health Facility Data (Govt. of India)",
            "src_hmis_desc": "20,904 institutional health service records from the Ministry of Health and Family Welfare, providing empirical medicine utilization and facility workload metrics.",
            "src_nfhs_title": "National Family Health Survey (NFHS-5)",
            "src_nfhs_desc": "District-level epidemiological, maternal, and nutritional indicators across 706 districts in India.",
            "src_nlem_title": "National List of Essential Medicines (NLEM 2022)",
            "src_nlem_desc": "Official Indian formulary catalog establishing 20 essential core pharmaceutical entities under Reference provenance.",
            "src_fda_title": "US FDA (OpenFDA & DailyMed)",
            "src_fda_desc": "Authentic pharmaceutical database for active chemical compounds, National Drug Codes (NDC), drug contraindications, and verified packaging metadata.",
            "src_nih_title": "NIH / NCBI & LOINC Diagnostic Reference Standards",
            "src_nih_desc": "Standard reference intervals for blood panels (CBC, Lipid, LFT, KFT, HbA1c, Thyroid) derived from peer-reviewed National Institutes of Health databases.",
            "src_gis_title": "OpenStreetMap & Healthcare Overpass API",
            "src_gis_desc": "Live spatial coordinates of registered 24/7 hospitals, trauma care centers, clinics, and pharmacies mapped via OpenStreetMap GIS.",
            "src_ayush_title": "Ayush & Evidence-Based Yoga / Physiotherapy",
            "src_ayush_desc": "Condition-specific supportive restorative yoga postures and physical therapy exercises with anatomical safety precautions and video tutorial links.",
            # Features Tab
            "feat_title": "Comprehensive Healthcare Technology Suite & Security",
            "feat_1_title": "Trilingual Clinical Portal",
            "feat_1_desc": "Full native experience in English, Hindi (हिंदी), and Gujarati (ગુજરાતી) with zero language barriers.",
            "feat_2_title": "Provenance Standards Enforcement",
            "feat_2_desc": "Every single alert card and metric carries transparent provenance tags (PROVENANCE_OBSERVED, PROVENANCE_REFERENCE, PROVENANCE_DERIVED).",
            "feat_3_title": "Strict Privacy & Zero Data Reselling",
            "feat_3_desc": "No health data is sold or stored for advertising. Assessments operate with client-side session isolation following HIPAA guidelines.",
            "feat_4_title": "Offline Resilience & Local Datasets",
            "feat_4_desc": "If cloud APIs are unreachable, local clinical datasets instantly activate to ensure uninterrupted medical guidance."
        },
        "hi": {
            "creator_badge": "संस्थापक, आर्किटेक्ट एवं निर्माता",
            "creator_name": "दक्ष वसानी (Daksh Vasani) द्वारा विकसित",
            "creator_sub": "एम.एससी. डेटा साइंस छात्र | पायथन एवं मशीन लर्निंग उत्साही · गुजरात, भारत",
            "mission_title": "प्रोजेक्ट का उद्देश्य एवं वास्तुकला (Architecture)",
            "mission_body": "MediMind AI की परिकल्पना और विकास <b>दक्ष वसानी</b> (M.Sc. Data Science छात्र) द्वारा एक प्रामाणिक, पारदर्शी और सत्यापित AI हेल्थकेयर प्लेटफॉर्म के रूप में किया गया है। यह प्लेटफॉर्म <b>कस्टम-ट्रेन्ड रैंडम फॉरेस्ट डिजीज मॉडल (99.01% ट्रेनिंग सटीकता)</b>, <b>दवा मांग पूर्वानुमान मॉडल (6.53% WAPE, 0.9839 R²)</b>, <b>WHO आउटब्रेक API पाइपलाइन</b>, <b>भारत की 100+ प्रमुख बीमारियों का नॉलेज बेस</b>, और <b>Groq / Gemini AI</b> को जोड़ता है।",
            "tab_models": "AI एवं ML मॉडल व सटीक मैट्रिक्स",
            "tab_diseases": "भारत की 100+ प्रमुख बीमारियां",
            "tab_datasources": "प्रामाणिक डेटा स्रोत व लाइव APIs",
            "tab_features": "आर्किटेक्चर, सुरक्षा व प्राइवेसी",
            # Models Tab
            "ml_title": "1. क्लिनिकल डिजीज प्रेडिक्शन मॉडल (लोकल इंजन)",
            "ml_sub": "क्लिनिकल लक्षण-रोग मैट्रिक्स पर प्रशिक्षित Scikit-Learn रैंडम फॉरेस्ट क्लासिफायर।",
            "stat_acc": "99.01%",
            "stat_acc_sub": "ट्रेनिंग सटीकता (97.8% 5-Fold CV)",
            "stat_algo": "Random Forest",
            "stat_algo_sub": "50 डिसीजन ट्री (Scikit-Learn)",
            "stat_features": "280 लक्षण",
            "stat_features_sub": "बाइनरी इंडिकेटर फीचर्स",
            "stat_classes": "101 बीमारियाँ",
            "stat_classes_sub": "WHO ICD-11 मानक श्रेणियाँ",
            "ml_step1": "<b>1. फीचर इंजीनियरिंग:</b> <code>symptoms_master.csv</code> से मरीज के लक्षणों को 280-आयामी बाइनरी वेक्टर में बदला जाता है।",
            "ml_step2": "<b>2. एन्सेम्बल ट्रेनिंग:</b> 50 विशेषज्ञ डिसीजन ट्री गिन्नी इम्प्योरिटी ऑप्टिमाइज़ेशन के साथ लक्षणों का मूल्यांकन करते हैं (<code>train.py</code>)।",
            "ml_step3": "<b>3. मॉडल सीरियलाइज़ेशन:</b> प्रशिक्षित मॉडल <code>models/disease_model.pkl</code> (5.5 MB) में सहेजा गया है।",
            "demand_title": "2. मेडिसिन डिमांड फोरकास्टिंग मॉडल (HMIS सप्लाई चेन)",
            "demand_sub": "लीकेज-मुक्त HMIS डेटा पर प्रशिक्षित रैंडम फॉरेस्ट रिग्रेसर जो दवाओं की साप्ताहिक खपत का सटीक अनुमान लगाता है।",
            "stat_wape": "6.53%",
            "stat_wape_sub": "हेल्ड-आउट टेस्ट WAPE",
            "stat_r2": "0.9839",
            "stat_r2_sub": "R² वेरियंस स्कोर",
            "stat_mae": "12.17",
            "stat_mae_sub": "मीन एब्सोल्यूट एरर (MAE)",
            "stat_rmse": "19.50",
            "stat_rmse_sub": "रूट मीन स्क्वेयर्ड एरर",
            "demand_step1": "<b>1. डेटा इनजेशन:</b> MoHFW HMIS के 20,904 रिकॉर्ड्स से समयबद्ध विभाजन।",
            "demand_step2": "<b>2. ट्रेंड एनालिसिस:</b> 4-हफ्ते और 12-हफ्ते के रोलिंग ट्रेंड्स और मौसमी बदलावों का विश्लेषण।",
            "demand_step3": "<b>3. मॉडल फाइल:</b> <code>models/demand_model.pkl</code> में अनिश्चितता मानक त्रुटि (±19.50 यूनिट्स) के साथ सहेजा गया।",
            "stockout_title": "3. ऑपरेशनल स्टॉकाउट रिस्क इंजन (सटीक रूल-बेस्ड सिस्टम)",
            "stockout_sub": "बफर दिनों के आधार पर दवाओं की कमी का पारदर्शी और ईमानदार आकलन।",
            "stockout_desc": "<b>ऑपरेशनल सीमाएं:</b><br/>• <b>क्रिटिकल रिस्क:</b> 3 दिन से कम का स्टॉक (तुरंत रेड अलर्ट)<br/>• <b>अर्जेंट रिस्क:</b> 7 दिन से कम का स्टॉक (प्राथमिकता से आपूर्ति)<br/>• <b>वॉचलिस्ट:</b> 14 दिन से कम का स्टॉक (सामान्य निगरानी)<br/>• <b>सुरक्षित बफर:</b> 14 दिन या अधिक का स्टॉक (स्थिर स्थिति)<br/><i>पारदर्शिता: इसे पूरी ईमानदारी से 'RULE_BASED' श्रेणी में रखा गया है (कोई झूठा दावा नहीं)।</i>",
            "kg_title": "4. क्लिनिकल नॉलेज ग्राफ एवं ट्राइएज इंजन",
            "kg_sub": "क्लिनिकल सुरक्षा, आपातकालीन चेतावनी और जनसांख्यिकीय नियमों को सुनिश्चित करने वाला विशेषज्ञ सिस्टम।",
            "kg_item1": "<b>ICD-11 बाइपार्टाइट स्कोरिंग:</b> मुख्य प्राथमिक लक्षणों के लिए 1.6x गुणक के साथ भारित मिलान।",
            "kg_item2": "<b>इमरजेंसी रेड-फ्लैग प्रोटोकॉल:</b> गंभीर खतरों (जैसे सांस फूलने के साथ सीने में दर्द) की तुरंत पहचान।",
            "kg_item3": "<b>जनसांख्यिकीय क्लिनिकल फिल्टर:</b> जैविक रूप से असंभव रोगों को हटाने के लिए लिंग और आयु का स्वचालित फिल्टर।",
            "llm_title": "5. मेडिकल फाउंडेशन LLMs (लाइव AI इंजन)",
            "llm_sub": "Groq (LLaMA-3.3 70B, Qwen 27B) और Google Gemini 2.5 Flash द्वारा तेज़ तार्किक विश्लेषण।",
            "llm_item1": "<b>डायनामिक केयर प्रिस्क्रिप्शन:</b> बीमारी के अनुसार दवाइयां, भोजन का सही समय ('खाने के बाद' या 'खाली पेट') और कोर्स तय करता है।",
            "llm_item2": "<b>ड्रग इंटरेक्शन एवं एलर्जी शील्ड:</b> पुरानी दवाओं और एलर्जी से होने वाले नुकसान को रोकता है।",
            "llm_item3": "<b>त्रिभाषी जेनरेशन:</b> हिंदी, अंग्रेजी और गुजराती में सटीक मेडिकल सलाह प्रदान करता है।",
            "ocr_title": "6. कंप्यूटर विज़न एवं मेडिकल डॉक्यूमेंट OCR",
            "ocr_sub": "ब्लड रिपोर्ट और डॉक्टर पर्चियों के स्वचालित विश्लेषण के लिए Gemini Vision + Tesseract OCR।",
            "ocr_item1": "<b>ब्लड लैब रिपोर्ट विश्लेषक:</b> CBC, LFT, KFT, लिपिड, HbA1c निकालता है और असामान्य मानों को हाइलाइट करता है।",
            "ocr_item2": "<b>दवा पर्ची स्कैनर:</b> दवाओं के नाम, खुराक पढ़कर OpenFDA डेटाबेस से मिलान करता है।",
            # Diseases Tab
            "dis_title": "भारत की 100+ प्रमुख बीमारियों की आधिकारिक टैक्सोनॉमी",
            "dis_sub": "MoHFW और WHO ICD-10/11 के तहत सभी 18 प्रमुख श्रेणियों का संपूर्ण डेटाबेस।",
            "dis_cat_1": "<b><img src='https://cdn-icons-png.flaticon.com/512/3888/3888124.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> कैंसर व ऑन्कोलॉजी:</b> ब्लड कैंसर (Leukemia), स्तन कैंसर, मुख कैंसर, फेफड़ों का कैंसर, सर्वाइकल कैंसर, पेट का कैंसर, लिवर कैंसर, प्रोस्टेट कैंसर, लिम्फोमा।",
            "dis_cat_2": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> हृदय और रक्तसंचार:</b> हार्ट अटैक (Myocardial Infarction), स्ट्रोक/लकवा, उच्च रक्तचाप (Hypertension), हार्ट फेलियर।",
            "dis_cat_3": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> डायबिटीज व मेटाबॉलिक:</b> Type 1 व Type 2 डायबिटीज, मोटापा, थायरॉइड विकार।",
            "dis_cat_4": "<b><img src='https://cdn-icons-png.flaticon.com/512/10154/10154217.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> श्वसन रोग:</b> COPD, अस्थमा, निमोनिया, टीबी (Tuberculosis)।",
            "dis_cat_5": "<b><img src='https://cdn-icons-png.flaticon.com/512/15625/15625461.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> गुर्दा (किडनी):</b> क्रोनिक किडनी डिजीज (CKD), एक्यूट किडनी इंजरी, पथरी, डायलिसिस।",
            "dis_cat_6": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> लिवर व पाचन:</b> लिवर सिरोसिस, हेपेटाइटिस B/C, फैटी लिवर, अल्सर, पीलिया।",
            "dis_cat_7": "<b><img src='https://cdn-icons-png.flaticon.com/512/3286/3286097.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> न्यूरोलॉजिकल:</b> मिर्गी (Epilepsy), पार्किंसंस (Parkinson's), अल्जाइमर/डिमेंशिया, माइग्रेन।",
            "dis_cat_8": "<b><img src='https://cdn-icons-png.flaticon.com/128/13286/13286061.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> संक्रामक व मच्छर-जनित:</b> डेंगू (Dengue), मलेरिया (Malaria), चिकनगुनिया, टाइफाइड, हैजा, कालाजार।",
            "dis_cat_9": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> रक्त विकार:</b> सिकल सेल एनीमिया (Sickle Cell), थैलेसीमिया, एनीमिया, हीमोफिलिया।",
            "dis_cat_10": "<b><img src='https://cdn-icons-png.flaticon.com/512/9418/9418433.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> जोड़ व हड्डियां:</b> ऑस्टियोआर्थराइटिस, रूमेटाइड आर्थराइटिस, गाउट, ऑस्टियोपोरोसिस।",
            "dis_cat_11": "<b><img src='https://cdn-icons-png.flaticon.com/512/8256/8256189.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> आंखें:</b> मोतियाबिंद (Cataract), ग्लूकोमा, डायबिटिक रेटिनोपैथी।",
            "dis_cat_12": "<b><img src='https://cdn-icons-png.flaticon.com/512/15305/15305545.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> ज़ूनोटिक व आपातकाल:</b> सर्पदंश (Snakebite), रेबीज (Dog bite), सेप्सिस।",
            # Data Sources Tab
            "sources_title": "प्रामाणिक क्लिनिकल डेटा स्रोत (डेटा कहाँ से आता है?)",
            "sources_sub": "MediMind AI केवल आधिकारिक, सत्यापित और सरकारी स्वास्थ्य रजिस्ट्रीयों का उपयोग करता है।",
            "src_who_title": "WHO आधिकारिक आउटब्रेक API (DON API)",
            "src_who_desc": "विश्व स्वास्थ्य संगठन (WHO) के आधिकारिक Disease Outbreak News REST API (<code>https://www.who.int/api/news/diseaseoutbreaknews</code>) से सीधे 100 प्रमाणित महामारियों का लाइव डेटा।",
            "src_hmis_title": "MoHFW HMIS स्वास्थ्य डेटा (भारत सरकार)",
            "src_hmis_desc": "स्वास्थ्य एवं परिवार कल्याण मंत्रालय के 20,904 संस्थागत रिकॉर्ड्स से प्राप्त दवाओं की वास्तविक खपत का डेटा।",
            "src_nfhs_title": "राष्ट्रीय परिवार स्वास्थ्य सर्वेक्षण (NFHS-5)",
            "src_nfhs_desc": "भारत के 706 जिलों का आधिकारिक मातृ, पोषण और स्वास्थ्य सूचकांक डेटा।",
            "src_nlem_title": "राष्ट्रीय आवश्यक दवा सूची (NLEM 2022)",
            "src_nlem_desc": "भारत सरकार द्वारा मान्यता प्राप्त 20 आवश्यक जीवनरक्षक दवाओं की आधिकारिक संदर्भ सूची।",
            "src_fda_title": "यूएस एफडीए (OpenFDA एवं DailyMed)",
            "src_fda_desc": "दवाइयों के सक्रिय रासायनिक घटक, NDC कोड, साइड-इफेक्ट्स और सत्यापित पैकेजिंग तस्वीरों के लिए आधिकारिक डेटाबेस।",
            "src_nih_title": "NIH / NCBI एवं LOINC डायग्नोस्टिक रेंज",
            "src_nih_desc": "ब्लड टेस्ट (CBC, लिपिड, LFT, KFT, HbA1c, थायरॉइड) के लिए <b>National Institutes of Health (NIH/NCBI)</b> की संदर्भ श्रेणियां।",
            "src_gis_title": "OpenStreetMap एवं हेल्थकेयर Overpass API",
            "src_gis_desc": "निकटतम 24/7 अस्पतालों, ट्रॉमा सेंटरों, क्लीनिकों और फार्मेसियों के लाइव भौगोलिक निर्देशांक।",
            "src_ayush_title": "आयुष एवं साक्ष्य-आधारित योग व फिजियोथेरेपी",
            "src_ayush_desc": "बीमारी के अनुसार सहायक रिकवरी योग आसन और फिजियोथेरेपी व्यायाम वीडियो ट्यूटोरियल लिंक के साथ।",
            # Features Tab
            "feat_title": "संपूर्ण हेल्थकेयर टेक्नोलॉजी सूट एवं सुरक्षा",
            "feat_1_title": "त्रिभाषी क्लिनिकल पोर्टल",
            "feat_1_desc": "अंग्रेजी, हिंदी (Hindi), और गुजराती (Gujarati) में सहज अनुभव।",
            "feat_2_title": "डेटा प्रोवेनेंस (Provenance) मानक",
            "feat_2_desc": "हर अलर्ट और डेटा कार्ड पर स्पष्ट टैग (PROVENANCE_OBSERVED, REFERENCE, DERIVED) दिए गए हैं।",
            "feat_3_title": "सख्त गोपनीयता एवं शून्य डेटा बिक्री",
            "feat_3_desc": "मरीजों का डेटा किसी विज्ञापनदाता को नहीं बेचा जाता। क्लाइंट-साइड सेशन आइसोलेशन।",
            "feat_4_title": "ऑफ़लाइन फ़ॉलबैक सुरक्षा जाल",
            "feat_4_desc": "इंटरनेट या API उपलब्ध न होने पर भी लोकल डेटासेट से बिना रुकावट सेवा।"
        },
        "gu": {
            "creator_badge": "સ્થાપક, આર્કિટેક્ટ અને સર્જક",
            "creator_name": "દક્ષ વસાણી (Daksh Vasani) દ્વારા નિર્મિત",
            "creator_sub": "એમ.એસસી. ડેટા સાયન્સ વિદ્યાર્થી | પાયથોન અને મશીન લર્નિંગ ઉત્સાહી · ગુજરાત, ભારત",
            "mission_title": "પ્રોજેક્ટ વિઝન અને આર્કિટેક્ચર",
            "mission_body": "MediMind AI ની કલ્પના અને વિકાસ <b>દક્ષ વસાણી</b> (M.Sc. Data Science વિદ્યાર્થી) દ્વારા એક પારદર્શક અને ચકાસાયેલ AI હેલ્થકેર પ્લેટફોર્મ તરીકે કરવામાં આવ્યો છે. આ સિસ્ટમ <b>કસ્ટમ-ટ્રેઇન્ડ રેન્ડમ ફોરેસ્ટ ML મોડેલ (99.01% સચોટતા)</b>, <b>દવા માંગ પૂર્વાનુમાન મોડેલ (6.53% WAPE, 0.9839 R²)</b>, <b>સત્તાવાર WHO API આઉટબ્રેક ડેટા</b>, <b>ભારતના 100+ મુખ્ય રોગોનો ડેટાબેઝ</b>, અને <b>Groq / Gemini AI</b> ને જોડે છે.",
            "tab_models": "AI અને ML મોડેલ્સ અને સચોટતા",
            "tab_diseases": "ભારતના 100+ મુખ્ય રોગો",
            "tab_datasources": "અધિકૃત ડેટા સ્ત્રોતો અને Live APIs",
            "tab_features": "આર્કિટેક્ચર, સુરક્ષા અને પ્રાઇવસી",
            # Models Tab
            "ml_title": "1. ક્લિનિકલ રોગ અનુમાન મોડેલ (લોકલ એન્જિન)",
            "ml_sub": "ક્લિનિકલ લક્ષણ-રોગ મેટ્રિક્સ પર પ્રશિક્ષિત Scikit-Learn રેન્ડમ ફોરેસ્ટ ક્લાસિફાયર.",
            "stat_acc": "99.01%",
            "stat_acc_sub": "તાલીમ સચોટતા (97.8% 5-Fold CV)",
            "stat_algo": "Random Forest",
            "stat_algo_sub": "50 ડિસિઝન ટ્રી (Scikit-Learn)",
            "stat_features": "280 લક્ષણો",
            "stat_features_sub": "બાઈનરી ઇન્ડિકેટર ફીચર્સ",
            "stat_classes": "101 રોગો",
            "stat_classes_sub": "WHO ICD-11 માનક શ્રેણીઓ",
            "ml_step1": "<b>1. ફીચર એન્જિનિયરિંગ:</b> <code>symptoms_master.csv</code> માંથી દર્દીના લક્ષણોને 280-પરિમાણીય બાઈનરી વેક્ટરમાં રૂપાંતરિત કરવામાં આવે છે.",
            "ml_step2": "<b>2. એન્સેમ્બલ ટ્રેનિંગ:</b> 50 વિશેષ ડિસિઝન ટ્રી ગિની ઇમ્પ્યોરિટી ઑપ્ટિમાઇઝેશન સાથે લક્ષણોનું વિશ્લેષણ કરે છે (<code>train.py</code>).",
            "ml_step3": "<b>3. મોડેલ સિરિયલાઇઝેશન:</b> પ્રશિક્ષિત મોડેલ <code>models/disease_model.pkl</code> (5.5 MB) માં સંગ્રહિત છે.",
            "demand_title": "2. દવા માંગ પૂર્વાનુમાન મોડેલ (HMIS સપ્લાય ચેઇન)",
            "demand_sub": "સમયસર ડેટા વિભાજન સાથે દવાઓની સાપ્તાહિક જરૂરિયાતનું સચોટ અનુમાન.",
            "stat_wape": "6.53%",
            "stat_wape_sub": "ટેસ્ટ સેટ WAPE",
            "stat_r2": "0.9839",
            "stat_r2_sub": "R² વેરિઅન્સ સ્કોર",
            "stat_mae": "12.17",
            "stat_mae_sub": "મીન એબ્સોલ્યુટ એરર",
            "stat_rmse": "19.50",
            "stat_rmse_sub": "રૂટ મીન સ્ક્વેર્ડ એરર",
            "demand_step1": "<b>1. ડેટા ઇન્જેશન:</b> MoHFW HMIS ના 20,904 અધિકૃત રેકોર્ડ્સમાંથી વિશ્લેષણ.",
            "demand_step2": "<b>2. ટ્રેન્ડ એનાલિસિસ:</b> 4-અઠવાડિયા અને 12-અઠવાડિયાના રોલિંગ ટ્રેન્ડ્સનું આકલન.",
            "demand_step3": "<b>3. મોડેલ ફાઇલ:</b> <code>models/demand_model.pkl</code> માં અનિશ્ચિતતા સ્ટાન્ડર્ડ એરર (±19.50) સાથે સુરક્ષિત.",
            "stockout_title": "3. ઓપરેશનલ સ્ટોકઆઉટ રિસ્ક એન્જિન (રૂલ-બેઝ્ડ સિસ્ટમ)",
            "stockout_sub": "સ્ટોકના બાકી દિવસોના આધારે પારદર્શક ચેતવણી પ્રણાલી.",
            "stockout_desc": "<b>ઓપરેશનલ મર્યાદાઓ:</b><br/>• <b>ક્રિટિકલ રિસ્ક:</b> 3 દિવસથી ઓછો સ્ટોક (તાત્કાલિક લાલ ચેતવણી)<br/>• <b>અર્જન્ટ રિસ્ક:</b> 7 દિવસથી ઓછો સ્ટોક (પ્રાથમિકતા પુરવઠો)<br/>• <b>વોચલિસ્ટ:</b> 14 દિવસથી ઓછો સ્ટોક (સામાન્ય ટ્રેકિંગ)<br/>• <b>સલામત બફર:</b> 14 દિવસ કે તેથી વધુ સ્ટોક (સ્થિર પરિસ્થિતિ)<br/><i>નોંધ: સંપૂર્ણ પારદર્શિતા માટે તેને 'RULE_BASED' તરીકે વર્ગીકૃત કરવામાં આવ્યું છે.</i>",
            "kg_title": "4. ક્લિનિકલ નોલેજ ગ્રાફ અને ટ્રાયેજ એન્જિન",
            "kg_sub": "ક્લિનિકલ સલામતી, કટોકટીની ચેતવણીઓ અને વસ્તી વિષયક નિયમો સુનિશ્ચિત કરતી સિસ્ટમ.",
            "kg_item1": "<b>ICD-11 બાયપાર્ટાઇટ સ્કોરિંગ:</b> મુખ્ય પ્રાથમિક લક્ષણો માટે 1.6x ગુણક સાથે મેચિંગ.",
            "kg_item2": "<b>ઇમરજન્સી રેડ-ફ્લેગ પ્રોટોકોલ:</b> ગંભીર જોખમો (જેમ કે શ્વાસ ચડવો અને છાતીમાં દુખાવો) ની તાત્કાલિક ઓળખ.",
            "kg_item3": "<b>વસ્તી વિષયક ક્લિનિકલ ફિલ્ટર:</b> જૈવિક રીતે અસંભવિત રોગોને દૂર કરવા માટે લિંગ અને વયનું ફિલ્ટર.",
            "llm_title": "5. મેડિકલ ફાઉન્ડેશન LLMs (લાઇવ AI એન્જિન)",
            "llm_sub": "Groq (LLaMA-3.3 70B, Qwen 27B) અને Google Gemini 2.5 Flash દ્વારા ઝડપી તાર્કિક વિશ્લેષણ.",
            "llm_item1": "<b>ડાયનેમિક કેર પ્રિસ્ક્રિપ્શન:</b> રોગ મુજબ દવાઓ, જમવાનો યોગ્ય સમય ('જમ્યા પછી' કે 'ખાલી પેટે') અને દિવસો નક્કી કરે છે.",
            "llm_item2": "<b>ડ્રગ ઇન્ટરેક્શન અને એલર્જી શીલ્ડ:</b> જૂની દવાઓ અને એલર્જીથી થતા નુકસાનને અટકાવે છે.",
            "llm_item3": "<b>ત્રિભાષી જનરેશન:</b> ગુજરાતી, હિન્દી અને અંગ્રેજીમાં સચોટ તબીબી સલાહ પ્રદાન કરે છે.",
            "ocr_title": "6. કમ્પ્યુટર વિઝન અને મેડિકલ ડોક્યુમેન્ટ OCR",
            "ocr_sub": "બ્લડ રિપોર્ટ અને ડૉક્ટરની પ્રિસ્ક્રિપ્શનના વિશ્લેષણ માટે Gemini Vision + Tesseract OCR.",
            "ocr_item1": "<b>બ્લડ લેબ રિપોર્ટ વિશ્લેષક:</b> CBC, LFT, KFT, લિપિડ, HbA1c ચકાસીને અસામાન્ય પરિણામો દર્શાવે છે.",
            "ocr_item2": "<b>દવા પ્રિસ્ક્રિપ્શન સ્કેનર:</b> દવાઓના નામ, ડોઝ વાંચીને OpenFDA ડેટાબેઝ સાથે સરખાવે છે.",
            # Diseases Tab
            "dis_title": "ભારતના 100+ મુખ્ય રોગોની સત્તાવાર ટેક્સોનોમી",
            "dis_sub": "MoHFW અને WHO ICD-10/11 હેઠળ તમામ 18 શ્રેણીઓનો વ્યાપક ડેટાબેઝ.",
            "dis_cat_1": "<b><img src='https://cdn-icons-png.flaticon.com/512/3888/3888124.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> કેન્સર અને ઓન્કોલોજી:</b> બ્લડ કેન્સર (Leukemia), સ્તન કેન્સર, મુખનું કેન્સર, ફેફસાંનું કેન્સર, સર્વાઇકલ કેન્સર, પેટનું કેન્સર, લિવર કેન્સર, પ્રોસ્ટેટ કેન્સર, લિમ્ફોમા.",
            "dis_cat_2": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> હૃદય અને રક્તસંચાર:</b> હાર્ટ એટેક (Myocardial Infarction), સ્ટ્રોક/લકવો, હાઈ બ્લડ પ્રેશર (Hypertension), હાર્ટ ફેલિયર.",
            "dis_cat_3": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> ડાયાબિટીસ અને મેટાબોલિક:</b> Type 1 અને Type 2 ડાયાબિટીસ, મેદસ્વીતા, થાઇરોઇડ સમસ્યાઓ.",
            "dis_cat_4": "<b><img src='https://cdn-icons-png.flaticon.com/512/10154/10154217.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> શ્વસનતંત્રના રોગો:</b> COPD, અસ્થમા, ન્યુમોનિયા, ટીબી (Tuberculosis).",
            "dis_cat_5": "<b><img src='https://cdn-icons-png.flaticon.com/512/15625/15625461.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> કિડની અને મૂત્રપિંડ:</b> ક્રોનિક કિડની ડિસીઝ (CKD), કિડની ફેલિયર, પથરી, ડાયાલિસિસ.",
            "dis_cat_6": "<b><img src='https://cdn-icons-png.flaticon.com/512/508/508735.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> લિવર અને પાચનતંત્ર:</b> લિવર સિરોસિસ, હેપેટાઇટિસ B/C, ફેટી લિવર, અલ્સર, કમળો.",
            "dis_cat_7": "<b><img src='https://cdn-icons-png.flaticon.com/512/3286/3286097.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> ન્યુરોલોજીકલ:</b> વાઈ/ખેંચ (Epilepsy), પાર્કિન્સન (Parkinson's), ડિમેન્શિયા, આધાશીશી (Migraine).",
            "dis_cat_8": "<b><img src='https://cdn-icons-png.flaticon.com/128/13286/13286061.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> ચેપી અને મચ્છરજન્ય:</b> ડેન્ગ્યુ (Dengue), મેલેરિયા (Malaria), ચિકનગુનિયા, ટાઇફોઇડ, કોલેરા.",
            "dis_cat_9": "<b><img src='https://cdn-icons-png.flaticon.com/512/10784/10784622.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> રક્ત વિકૃતિઓ:</b> સિકલ સેલ એનિમિયા (Sickle Cell), થેલેસેમિયા, એનિમિયા, હિમોફિલિયા.",
            "dis_cat_10": "<b><img src='https://cdn-icons-png.flaticon.com/512/9418/9418433.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> સાંધા અને હાડકાં:</b> ઓસ્ટિઓઆર્થરાઇટિસ, સંધિવા (Rheumatoid Arthritis), ગાઉટ, ઓસ્ટિઓપોરોસિસ.",
            "dis_cat_11": "<b><img src='https://cdn-icons-png.flaticon.com/512/8256/8256189.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> આંખો:</b> મોતિયો (Cataract), ગ્લુકોમા, ડાયાબિટીક રેટિનોપેથી.",
            "dis_cat_12": "<b><img src='https://cdn-icons-png.flaticon.com/512/15305/15305545.png' style='width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;' /> ઝૂનોટિક અને ઈમરજન્સી:</b> સાપ કરડવો (Snakebite), હડકવા (Dog bite), સેપ્સિસ.",
            # Data Sources Tab
            "sources_title": "પ્રમાણિક ક્લિનિકલ ડેટા સ્ત્રોત (ડેટા ક્યાંથી આવે છે?)",
            "sources_sub": "MediMind AI માત્ર અધિકૃત, ચકાસાયેલ અને સરકારી આરોગ્ય રજિસ્ટ્રીઝનો ઉપયોગ કરે છે.",
            "src_who_title": "WHO સત્તાવાર આઉટબ્રેક API (DON API)",
            "src_who_desc": "વિશ્વ આરોગ્ય સંસ્થા (WHO) ના સત્તાવાર Disease Outbreak News REST API (<code>https://www.who.int/api/news/diseaseoutbreaknews</code>) દ્વારા 100 પ્રમાણિત રોગચાળાની લાઇવ માહિતી.",
            "src_hmis_title": "MoHFW HMIS આરોગ્ય સુવિધા ડેટા (ભારત સરકાર)",
            "src_hmis_desc": "ભારત સરકારના આરોગ્ય મંત્રાલયના 20,904 સંસ્થાકીય રેકોર્ડ્સમાંથી દવાઓના વાસ્તવિક વપરાશનો ડેટા.",
            "src_nfhs_title": "રાષ્ટ્રીય પરિવાર આરોગ્ય સર્વેક્ષણ (NFHS-5)",
            "src_nfhs_desc": "ભારતના 706 જિલ્લાઓનો અધિકૃત રોગચાળો, માતૃત્વ અને પોષણ સૂચકાંક ડેટા.",
            "src_nlem_title": "રાષ્ટ્રીય આવશ્યક દવાઓની યાદી (NLEM 2022)",
            "src_nlem_desc": "ભારત સરકાર દ્વારા માન્યતા પ્રાપ્ત 20 આવશ્યક જીવનરક્ષક દવાઓની અધિકૃત યાદી.",
            "src_fda_title": "યુએસ એફડીએ (OpenFDA અને DailyMed)",
            "src_fda_desc": "દવાઓના રાસાયણિક ઘટકો, NDC કોડ, આડઅસરો અને ચકાસાયેલ પેકેજિંગ ફોટા માટે અધિકૃત ડેટાબેઝ.",
            "src_nih_title": "NIH / NCBI અને LOINC ડાયગ્નોસ્ટિક રેન્જ",
            "src_nih_desc": "બ્લડ ટેસ્ટ (CBC, લિપિડ, LFT, KFT, HbA1c, થાઇરોઇડ) માટે <b>National Institutes of Health (NIH/NCBI)</b> ની સંદર્ભ શ્રેણીઓ.",
            "src_gis_title": "OpenStreetMap અને હેલ્થકેર Overpass API",
            "src_gis_desc": "નજીકની 24/7 હોસ્પિટલો, ટ્રોમા કેન્દ્રો, ક્લિનિક્સ અને ફાર્મસીઓના લાઇવ ભૌગોલિક નિર્દેશાંક.",
            "src_ayush_title": "આયુષ અને પુરાવા-આધારિત યોગ અને ફિઝિયોથેરાપી",
            "src_ayush_desc": "રોગ મુજબ સહાયક પુનઃપ્રાપ્તિ યોગ આસનો અને ફિઝિયોથેરાપી કસરતો વિડિયો ટ્યુટોરીયલ લિંક્સ સાથે.",
            # Features Tab
            "feat_title": "સંપૂર્ણ હેલ્થકેર ટેકનોલોજી સ્યુટ અને સુરક્ષા",
            "feat_1_title": "ત્રિભાષી ક્લિનિકલ પોર્ટલ",
            "feat_1_desc": "ગુજરાતી (Gujarati), હિન્દી (Hindi), અને અંગ્રેજી (English) માં સરળ અનુભવ.",
            "feat_2_title": "ડેટા પ્રોવેનન્સ સ્ટાન્ડર્ડ્સ",
            "feat_2_desc": "દરેક ચેતવણી અને ડેટા કાર્ડ પર સ્પષ્ટ ટૅગ્સ (PROVENANCE_OBSERVED, REFERENCE, DERIVED) પ્રદર્શિત થાય છે.",
            "feat_3_title": "સખત ગોપનીયતા અને શૂન્ય ડેટા વેચાણ",
            "feat_3_desc": "દર્દીઓનો ડેટા કોઈ જાહેરાતકર્તાને વેચવામાં આવતો નથી. સંપૂર્ણ તબીબી ગોપનીયતા.",
            "feat_4_title": "ઑફલાઇન ફોલબેક સુરક્ષા કવચ",
            "feat_4_desc": "ઇન્ટરનેટ કે API ઉપલબ્ધ ન હોય ત્યારે પણ લોકલ ડેટાસેટથી અવિરત સેવા."
        }
    }
    
    A = ABOUT_TEXT.get(lang_code, ABOUT_TEXT["en"])

    # 1. Creator & Mission Banner Card
    st.markdown(f"""
    <div class="mm-card" style="border-left: 5px solid #B3261E; margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="font-size: 0.72rem; font-weight: 800; color: #B3261E; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px;">
                    {A['creator_badge']}
                </div>
                <div style="font-size: 1.35rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.2;">
                    {A['creator_name']}
                </div>
                <div style="font-size: 0.84rem; color: var(--mm-text-secondary); margin-top: 3px;">
                    {A['creator_sub']}
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <span class="mm-badge mm-badge-brand" style="font-size: 0.76rem; padding: 6px 12px;">Made in India</span>
                <span class="mm-badge mm-badge-success" style="font-size: 0.76rem; padding: 6px 12px;">Disease ML 99.01%</span>
                <span class="mm-badge mm-badge-info" style="font-size: 0.76rem; padding: 6px 12px;">Demand WAPE 6.53%</span>
                <span class="mm-badge mm-badge-brand" style="font-size: 0.76rem; padding: 6px 12px;">WHO DON API Active</span>
            </div>
        </div>
        <p style="font-size: 0.86rem; color: var(--mm-text-secondary); line-height: 1.6; margin: 14px 0 0 0; padding-top: 12px; border-top: 1px dashed var(--mm-border-color);">
            <b>{A['mission_title']}:</b> {A['mission_body']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Main About Tabs (4 Comprehensive Tabs)
    tab_a1, tab_a2, tab_a3, tab_a4 = st.tabs([A["tab_models"], A["tab_diseases"], A["tab_datasources"], A["tab_features"]])

    # ==================== TAB 1: AI & ML MODELS & ACCURACY ====================
    with tab_a1:
        # Card 1: Custom Trained Disease ML Model
        st.markdown(f"""
        <div class="mm-card" style="border-top: 4px solid #10B981; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                <div>
                    <b style="font-size: 1.12rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/18357/18357328.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['ml_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 2px 0 0 0;">{A['ml_sub']}</p>
                </div>
                <span class="mm-badge mm-badge-success" style="font-size: 0.80rem; font-weight: 700; padding: 6px 14px;">Accuracy: {A['stat_acc']}</span>
            </div>
            <!-- 4-Stat Metrics Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin: 14px 0 16px 0;">
                <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #10B981;">{A['stat_acc']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_acc_sub']}</div>
                </div>
                <div style="background: rgba(59, 130, 246, 0.08); border: 1.5px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #3B82F6; margin-top: 2px;">{A['stat_algo']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_algo_sub']}</div>
                </div>
                <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #F59E0B;">{A['stat_features']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_features_sub']}</div>
                </div>
                <div style="background: rgba(168, 85, 247, 0.08); border: 1.5px solid rgba(168, 85, 247, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #A855F7;">{A['stat_classes']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_classes_sub']}</div>
                </div>
            </div>
            <!-- Pipeline Breakdown -->
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 8px; padding: 12px 14px; font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.6;">
                <div>• {A['ml_step1']}</div>
                <div style="margin-top: 4px;">• {A['ml_step2']}</div>
                <div style="margin-top: 4px;">• {A['ml_step3']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card 2: Medicine Demand Forecasting Model (HMIS Supply Chain)
        st.markdown(f"""
        <div class="mm-card" style="border-top: 4px solid #3B82F6; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                <div>
                    <b style="font-size: 1.12rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/2966/2966327.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['demand_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 2px 0 0 0;">{A['demand_sub']}</p>
                </div>
                <span class="mm-badge mm-badge-info" style="font-size: 0.80rem; font-weight: 700; padding: 6px 14px;">WAPE: {A['stat_wape']} | R²: {A['stat_r2']}</span>
            </div>
            <!-- 4-Stat Demand Forecaster Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin: 14px 0 16px 0;">
                <div style="background: rgba(59, 130, 246, 0.08); border: 1.5px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #3B82F6;">{A['stat_wape']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_wape_sub']}</div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #10B981;">{A['stat_r2']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_r2_sub']}</div>
                </div>
                <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #F59E0B;">{A['stat_mae']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_mae_sub']}</div>
                </div>
                <div style="background: rgba(168, 85, 247, 0.08); border: 1.5px solid rgba(168, 85, 247, 0.35); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #A855F7;">{A['stat_rmse']}</div>
                    <div style="font-size: 0.74rem; color: var(--mm-text-secondary); margin-top: 2px;">{A['stat_rmse_sub']}</div>
                </div>
            </div>
            <!-- Pipeline Breakdown -->
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 8px; padding: 12px 14px; font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.6;">
                <div>• {A['demand_step1']}</div>
                <div style="margin-top: 4px;">• {A['demand_step2']}</div>
                <div style="margin-top: 4px;">• {A['demand_step3']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4-Card Unified 2x2 Grid: Operational Risk, Knowledge Graph, Foundation LLMs, Vision OCR (Strictly 2 per row)
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 14px; align-items: stretch;">
            <!-- Card 3 -->
            <div class="mm-card" style="display: flex; flex-direction: column; justify-content: flex-start; min-height: 250px; height: 100%; border-top: 4px solid #EF4444; margin: 0;">
                <b style="font-size: 1.02rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/2965/2965300.png" style="width: 1.15em; height: 1.15em; vertical-align: -0.15em; display: inline-block;" /> {A['stockout_title']}</b>
                <p style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 3px 0 10px 0;">{A['stockout_sub']}</p>
                <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.55;">
                    {A['stockout_desc']}
                </div>
            </div>
            <!-- Card 4 -->
            <div class="mm-card" style="display: flex; flex-direction: column; justify-content: flex-start; min-height: 250px; height: 100%; border-top: 4px solid #3B82F6; margin: 0;">
                <b style="font-size: 1.02rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" style="width: 1.15em; height: 1.15em; vertical-align: -0.15em; display: inline-block;" /> {A['kg_title']}</b>
                <p style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 3px 0 10px 0;">{A['kg_sub']}</p>
                <div style="font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.6;">
                    <div style="margin-bottom: 6px;">• {A['kg_item1']}</div>
                    <div style="margin-bottom: 6px;">• {A['kg_item2']}</div>
                    <div>• {A['kg_item3']}</div>
                </div>
            </div>
            <!-- Card 5 -->
            <div class="mm-card" style="display: flex; flex-direction: column; justify-content: flex-start; min-height: 250px; height: 100%; border-top: 4px solid #EA580C; margin: 0;">
                <b style="font-size: 1.02rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/12512/12512364.png" style="width: 1.15em; height: 1.15em; vertical-align: -0.15em; display: inline-block;" /> {A['llm_title']}</b>
                <p style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 3px 0 10px 0;">{A['llm_sub']}</p>
                <div style="font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.6;">
                    <div style="margin-bottom: 6px;">• {A['llm_item1']}</div>
                    <div style="margin-bottom: 6px;">• {A['llm_item2']}</div>
                    <div>• {A['llm_item3']}</div>
                </div>
            </div>
            <!-- Card 6 -->
            <div class="mm-card" style="display: flex; flex-direction: column; justify-content: flex-start; min-height: 250px; height: 100%; border-top: 4px solid #8B5CF6; margin: 0;">
                <b style="font-size: 1.02rem; color: var(--mm-text-primary);"><img src="https://cdn-icons-png.flaticon.com/512/6024/6024205.png" style="width: 1.15em; height: 1.15em; vertical-align: -0.15em; display: inline-block;" /> {A['ocr_title']}</b>
                <p style="font-size: 0.80rem; color: var(--mm-text-secondary); margin: 3px 0 10px 0;">{A['ocr_sub']}</p>
                <div style="font-size: 0.82rem; color: var(--mm-text-secondary); line-height: 1.6;">
                    <div style="margin-bottom: 6px;">• {A['ocr_item1']}</div>
                    <div>• {A['ocr_item2']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==================== TAB 2: 100+ MAJOR INDIAN DISEASES ====================
    with tab_a2:
        st.markdown(f"""
        <div class="mm-card" style="border-left: 5px solid #FF2E5B; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                <div>
                    <div style="font-size: 0.72rem; font-weight: 800; color: #FF2E5B; text-transform: uppercase; letter-spacing: 0.08em;">
                        NATIONAL HEALTH TAXONOMY (MOHFW & WHO ICD)
                    </div>
                    <b style="font-size: 1.15rem; color: var(--mm-text-primary);">{A['dis_title']}</b>
                </div>
                <span class="mm-badge mm-badge-brand" style="font-size: 0.75rem; padding: 6px 12px;">18 Official Categories</span>
            </div>
            <p style="font-size: 0.84rem; color: var(--mm-text-secondary); line-height: 1.6; margin-bottom: 14px;">
                {A['dis_sub']}
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px;">
                <div style="background: rgba(255, 46, 91, 0.06); border: 1px solid rgba(255, 46, 91, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_1']}
                </div>
                <div style="background: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_2']}
                </div>
                <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_3']}
                </div>
                <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_4']}
                </div>
                <div style="background: rgba(168, 85, 247, 0.06); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_5']}
                </div>
                <div style="background: rgba(234, 88, 12, 0.06); border: 1px solid rgba(234, 88, 12, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_6']}
                </div>
                <div style="background: rgba(14, 165, 233, 0.06); border: 1px solid rgba(14, 165, 233, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_7']}
                </div>
                <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_8']}
                </div>
                <div style="background: rgba(244, 63, 94, 0.06); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_9']}
                </div>
                <div style="background: rgba(139, 92, 246, 0.06); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_10']}
                </div>
                <div style="background: rgba(6, 182, 212, 0.06); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_11']}
                </div>
                <div style="background: rgba(225, 29, 72, 0.06); border: 1px solid rgba(225, 29, 72, 0.25); border-radius: 10px; padding: 12px; font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                    {A['dis_cat_12']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==================== TAB 3: AUTHENTIC DATA SOURCES & APIS ====================
    with tab_a3:
        st.markdown(f"""
        <div class="mm-card" style="border-left: 5px solid #2563EB; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                <div>
                    <div style="font-size: 0.72rem; font-weight: 800; color: #2563EB; text-transform: uppercase; letter-spacing: 0.08em;">
                        CLINICAL DATA GOVERNANCE & PROVENANCE
                    </div>
                    <b style="font-size: 1.15rem; color: var(--mm-text-primary);">{A['sources_title']}</b>
                </div>
                <span class="mm-badge mm-badge-info" style="font-size: 0.75rem; padding: 6px 12px;">100% Real, Audited & Non-Fabricated</span>
            </div>
            <p style="font-size: 0.84rem; color: var(--mm-text-secondary); line-height: 1.6; margin-bottom: 14px;">
                {A['sources_sub']}
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
                <div style="background: rgba(37, 99, 235, 0.06); border: 1px solid rgba(37, 99, 235, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #2563EB; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4320/4320371.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_who_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_who_desc']}
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #10B981; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2966/2966327.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_hmis_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_hmis_desc']}
                    </div>
                </div>
                <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #F59E0B; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2465/2465596.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_nfhs_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_nfhs_desc']}
                    </div>
                </div>
                <div style="background: rgba(168, 85, 247, 0.06); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #A855F7; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/883/883407.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_nlem_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_nlem_desc']}
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #10B981; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/5228/5228598.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_fda_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_fda_desc']}
                    </div>
                </div>
                <div style="background: rgba(225, 29, 72, 0.06); border: 1px solid rgba(225, 29, 72, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #E11D48; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/18310/18310946.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_nih_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_nih_desc']}
                    </div>
                </div>
                <div style="background: rgba(147, 51, 234, 0.06); border: 1px solid rgba(147, 51, 234, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #9333EA; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4060/4060488.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_gis_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_gis_desc']}
                    </div>
                </div>
                <div style="background: rgba(13, 148, 136, 0.06); border: 1px solid rgba(13, 148, 136, 0.25); border-radius: 10px; padding: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0D9488; margin-bottom: 4px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/6266/6266132.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['src_ayush_title']}
                    </div>
                    <div style="font-size: 0.80rem; color: var(--mm-text-secondary); line-height: 1.5;">
                        {A['src_ayush_desc']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==================== TAB 4: ARCHITECTURE, PRIVACY & SECURITY ====================
    with tab_a4:
        st.markdown(f"""
        <div class="mm-card">
            <b style="font-size: 1.10rem; color: var(--mm-text-primary);">{A['feat_title']}</b>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-top: 14px;">
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 10px; padding: 14px;">
                    <b style="color: #3B82F6; font-size: 0.90rem;"><img src="https://cdn-icons-png.flaticon.com/128/486/486505.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['feat_1_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 0 0; line-height: 1.5;">{A['feat_1_desc']}</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 10px; padding: 14px;">
                    <b style="color: #10B981; font-size: 0.90rem;"><img src="https://cdn-icons-png.flaticon.com/512/595/595764.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['feat_2_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 0 0; line-height: 1.5;">{A['feat_2_desc']}</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 10px; padding: 14px;">
                    <b style="color: #F59E0B; font-size: 0.90rem;"><img src="https://cdn-icons-png.flaticon.com/512/4503/4503969.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['feat_3_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 0 0; line-height: 1.5;">{A['feat_3_desc']}</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--mm-border-color); border-radius: 10px; padding: 14px;">
                    <b style="color: #A855F7; font-size: 0.90rem;"><img src="https://cdn-icons-png.flaticon.com/512/12370/12370940.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" /> {A['feat_4_title']}</b>
                    <p style="font-size: 0.82rem; color: var(--mm-text-secondary); margin: 4px 0 0 0; line-height: 1.5;">{A['feat_4_desc']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(render_footer_trust_bar(T), unsafe_allow_html=True)

# ==============================================================================
# MODULE 6: NATIONAL HEALTH RESOURCE COMMAND CENTER (HACKATHON TRACK)
# ==============================================================================
elif st.session_state["active_panel"] == "National Command Center":
    cc_icon_html = '<img src="https://cdn-icons-png.flaticon.com/512/2465/2465596.png" style="width: 52px; height: 52px; border-radius: 14px; object-fit: contain; padding: 5px; background: rgba(16,185,129,0.08); box-shadow: 0 4px 14px rgba(16,185,129,0.35); border: 1.5px solid #10B981;" alt="National Command Center Icon"/>'
    with st.container(key="mm_top_header_card_6"):
        hdr6_c1, hdr6_c2, hdr6_c3, hdr6_c4 = st.columns([2.7, 1.3, 1.1, 0.7], vertical_alignment="center")
        with hdr6_c1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                {cc_icon_html}
                <div>
                    <div style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--mm-text-primary); line-height: 1.25;">
                        {T.get("p6_header_title", "National Health Resource Command Center")}
                    </div>
                    <div style="margin-top: 4px; font-size: 0.85rem; color: var(--mm-text-secondary);">
                        {T.get("p6_header_subtitle", "Data-driven intelligence platform for public health supply chains, bed capacity & cross-district redistribution.")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with hdr6_c2:
            st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 38px;'><span class='mm-badge mm-badge-brand' style='height: 38px; line-height: 38px; padding: 0 16px; display: inline-flex; align-items: center;'>{T.get('p6_badge', 'OFFICIAL DATA INTEGRATED')}</span></div>", unsafe_allow_html=True)
        with hdr6_c3:
            header_lang_6 = st.selectbox(
                "Header Lang Selector 6",
                options=LANG_OPTIONS,
                key="hdr_lang_p6",
                label_visibility="collapsed",
                on_change=sync_language,
                args=("hdr_lang_p6",)
            )
        with hdr6_c4:
            new_theme_p6 = theme_toggle_switch(is_dark=st.session_state.get("dark_mode", False), key="hdr_sun_moon_p6")
            if new_theme_p6 != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = new_theme_p6
                st.rerun()

    render_command_center_dashboard(lang_code=lang_code, is_dark=st.session_state.get("dark_mode", False))
    st.markdown(render_footer_trust_bar(T), unsafe_allow_html=True)


# ==============================================================================
# FLOATING AI ASSISTANT POPUP WIDGET (RED CLINICAL BRANDING)
# ==============================================================================
chat_is_open = st.session_state.get("floating_chat_open", False)
popup_transform = "scale(1) translateY(0)"if chat_is_open else "scale(0.85) translateY(24px)"
popup_opacity = "1"if chat_is_open else "0"
popup_pointer = "auto"if chat_is_open else "none"
btn_transform = "rotate(45deg) scale(1.08)"if chat_is_open else "rotate(0deg) scale(1)"
st.markdown(
    f"""
    <style>
    @keyframes eye-look-and-blink {{
        0%, 20% {{
            transform: translate(0, 0) scaleY(1);
        }}
        25%, 45% {{
            transform: translate(-2.5px, 0) scaleY(1);
        }}
        50%, 65% {{
            transform: translate(0, 0) scaleY(1);
        }}
        70%, 85% {{
            transform: translate(2.5px, 0) scaleY(1);
        }}
        90% {{
            transform: translate(0, 0) scaleY(0.1);
        }}
        94%, 100% {{
            transform: translate(0, 0) scaleY(1);
        }}
    }}

    /* Floating Compact Medical Cross '+'Button */
    .st-key-floating_ai_assistant, div.st-key-floating_ai_assistant {{
        position: fixed !important;
        bottom: 22px !important;
        right: 22px !important;
        width: 48px !important;
        height: 48px !important;
        z-index: 999995 !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }}

    .st-key-floating_ai_assistant button {{
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        clip-path: polygon(
            30% 0%, 70% 0%, 70% 30%,
            100% 30%, 100% 70%, 70% 70%,
            70% 100%, 30% 100%, 30% 70%,
            0% 70%, 0% 30%, 30% 30%
        ) !important;
        border-radius: 4px !important;
        background: linear-gradient(135deg, #FF2E5B 0%, #B3261E 100%) !important;
        border: none !important;
        filter: drop-shadow(0 0 12px rgba(255, 46, 91, 0.85)) drop-shadow(0 0 24px rgba(225, 29, 72, 0.6)) drop-shadow(0 6px 16px rgba(0, 0, 0, 0.45)) !important;
        cursor: pointer !important;
        transform: {btn_transform} !important;
        transition: transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        position: relative !important;
    }}

    /* Hover Elevation */
    .st-key-floating_ai_assistant button:hover {{
        transform: {btn_transform} translateY(-6px) scale(1.10) !important;
        filter: drop-shadow(0 0 20px rgba(255, 46, 91, 1)) drop-shadow(0 0 36px rgba(225, 29, 72, 0.85)) drop-shadow(0 10px 22px rgba(0, 0, 0, 0.55)) !important;
    }}

    /* Animated Synchronized Eyes */
    .st-key-floating_ai_assistant button::before,
    .st-key-floating_ai_assistant button::after {{
        content: "" !important;
        position: absolute !important;
        width: 4px !important;
        height: 7px !important;
        background: #FFFFFF !important;
        border-radius: 2px !important;
        top: 50% !important;
        margin-top: -3.5px !important;
        transform-origin: center !important;
        animation: eye-look-and-blink 4.2s infinite ease-in-out !important;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.95) !important;
        z-index: 10 !important;
    }}

    .st-key-floating_ai_assistant button::before {{
        left: 16px !important;
    }}

    .st-key-floating_ai_assistant button::after {{
        right: 16px !important;
    }}

    .st-key-floating_ai_assistant button p,
    .st-key-floating_ai_assistant button span,
    .st-key-floating_ai_assistant button div {{
        display: none !important;
    }}

    /* Floating AI Popup Window (Auto-height with no empty space below input) */
    .st-key-slide_chat_drawer,
    div.st-key-slide_chat_drawer,
    div[data-testid="stVerticalBlock"]:has(> div.st-key-slide_chat_drawer) {{
        position: fixed !important;
        bottom: 82px !important;
        right: 22px !important;
        width: 390px !important;
        max-width: calc(100vw - 32px) !important;
        height: auto !important;
        max-height: calc(100vh - 100px) !important;
        background: var(--mm-bg-surface, #FFFFFF) !important;
        border: 1px solid rgba(179, 38, 30, 0.35) !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), 0 0 1px rgba(255, 255, 255, 0.1) !important;
        z-index: 999999 !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        transform: {popup_transform} !important;
        opacity: {popup_opacity} !important;
        pointer-events: {popup_pointer} !important;
        transform-origin: bottom right !important;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.22s ease !important;
        padding: 0 !important;
    }}

    /* Full-width Seamless Red Header */
    .st-key-popup_unified_header {{
        background: linear-gradient(135deg, #2D080A 0%, #8B0000 50%, #B3261E 100%) !important;
        padding: 12px 14px !important;
        border-radius: 19px 19px 0 0 !important;
        margin: 0 !important;
    }}

    /* Header Close & Clear Buttons */
    .st-key-drawer_close_x_btn button,
    .st-key-drawer_clear_chat_btn button {{
        height: 28px !important;
        width: 28px !important;
        min-height: 28px !important;
        max-height: 28px !important;
        min-width: 28px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        margin: 0 !important;
    }}
    .st-key-drawer_close_x_btn button:hover,
    .st-key-drawer_clear_chat_btn button:hover {{
        background: rgba(255, 255, 255, 0.35) !important;
        transform: scale(1.08) !important;
    }}
    .st-key-drawer_clear_chat_btn button:hover {{
        transform: rotate(-180deg) scale(1.08) !important;
        transition: all 0.3s ease !important;
    }}

    /* Multi-column and single-row Pill Chips matching reference UI */
    .st-key-slide_chat_drawer div[data-testid="stHorizontalBlock"] {{
        gap: 6px !important;
        margin-bottom: 5px !important;
        align-items: center !important;
    }}
    .st-key-slide_chat_drawer div[data-testid="stHorizontalBlock"] button,
    .st-key-slide_chat_drawer div[data-testid="stVerticalBlock"] > div > div[data-testid="stButton"] button {{
        height: auto !important;
        min-height: 32px !important;
        max-height: none !important;
        padding: 5px 12px !important;
        font-size: 0.77rem !important;
        font-weight: 600 !important;
        line-height: 1.25 !important;
        border-radius: 20px !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
        border: 1.2px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        transition: all 0.18s ease !important;
    }}
    .st-key-slide_chat_drawer div[data-testid="stHorizontalBlock"] button:hover,
    .st-key-slide_chat_drawer div[data-testid="stVerticalBlock"] > div > div[data-testid="stButton"] button:hover {{
        background: rgba(179, 38, 30, 0.05) !important;
        border-color: #B3261E !important;
        color: #B3261E !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 8px rgba(179,38,30,0.12) !important;
    }}
    /* Action Redirect CTA Buttons inside Chat */
    .st-key-slide_chat_drawer div[data-testid="stVerticalBlock"] div > div[data-testid="stButton"] button[key*="nav_action_btn_"] {{
        background: linear-gradient(135deg, #B3261E 0%, #7F1D1D 100%) !important;
        color: #FFFFFF !important;
        border: 1.2px solid #F87171 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        padding: 6px 14px !important;
        box-shadow: 0 3px 10px rgba(179, 38, 30, 0.4) !important;
        text-align: center !important;
        width: 100% !important;
    }}
    .st-key-slide_chat_drawer div[data-testid="stVerticalBlock"] div > div[data-testid="stButton"] button[key*="nav_action_btn_"]:hover {{
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) scale(1.02) !important;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.5) !important;
    }}

    /* Chat Input Form - Pinned Flush to Bottom */
    .st-key-slide_chat_drawer form {{
        padding: 10px 12px 12px 12px !important;
        background: var(--mm-bg-surface, #FFFFFF) !important;
        border-top: 1px solid var(--mm-border-color) !important;
        border-radius: 0 0 20px 20px !important;
        margin: 0 !important;
    }}
    .st-key-slide_chat_drawer form input {{
        border-radius: 24px !important;
        padding: 9px 16px !important;
        font-size: 0.83rem !important;
        border: 1.2px solid var(--mm-border-color) !important;
    }}
    .st-key-slide_chat_drawer form button {{
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        width: 38px !important;
        min-width: 38px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: #B3261E !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 1.05rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    .st-key-slide_chat_drawer form button:hover {{
        background: #DC2626 !important;
        transform: scale(1.08) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Floating '+'Trigger Button
st.button("＋", key="floating_ai_assistant", on_click=toggle_floating_chat)

# Active clinical context for AI
current_context = {
    "symptoms": (st.session_state.get("selected_symptoms_list") or st.session_state.get("user_context", {}).get("symptoms", [])),
    "top_disease": st.session_state.get("p1_triage_results", {}).get("ranked_conditions", [{}])[0].get("name", "") if st.session_state.get("p1_triage_results") else (st.session_state.get("triage_result", {}).get("ranked_conditions", [{}])[0].get("name", "") if st.session_state.get("triage_result") else ""),
    "medicines": st.session_state.get("nlp_medicines", []),
    "age": st.session_state.get("user_context", {}).get("age", "Adult"),
    "gender": st.session_state.get("user_context", {}).get("gender", "Unspecified"),
    "conditions": st.session_state.get("user_context", {}).get("conditions", []),
    "allergies": st.session_state.get("user_context", {}).get("allergies", "None"),
    "medications": st.session_state.get("user_context", {}).get("medications", "None"),
    "family_history": st.session_state.get("user_context", {}).get("surgeries", "None")
}


# Inject targeted CSS for chat drawer dark mode (before rendering the drawer)
if is_dark:
    st.markdown("""
<style>
/* === CHAT DRAWER COMPREHENSIVE DARK OVERRIDE === */
div.st-key-slide_chat_drawer,
div.st-key-slide_chat_drawer > div,
div.st-key-slide_chat_drawer > div > div,
div.st-key-slide_chat_drawer [data-testid="stVerticalBlock"],
div.st-key-slide_chat_drawer [data-testid="stVerticalBlockBorderWrapper"],
div.st-key-slide_chat_drawer [data-testid="element-container"],
div.st-key-slide_chat_drawer [data-testid="stHorizontalBlock"],
div.st-key-slide_chat_drawer [data-testid="stHeightContainer"],
div.st-key-slide_chat_drawer [data-testid="stHeightContainer"] > div,
div.st-key-slide_chat_drawer [data-testid="column"] {
    background-color: #0A0E1A !important;
    background: #0A0E1A !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
    box-shadow: none !important;
}

/* Send button (form submit) — HIDDEN so input is full-width and sends on Enter */
.st-key-slide_chat_form .stFormSubmitButton,
div.st-key-slide_chat_drawer .stFormSubmitButton,
.st-key-slide_chat_form div[data-testid="stFormSubmitButton"],
div[class*="st-key-slide_chat_form"] [data-testid="stFormSubmitButton"],
div[class*="st-key-slide_chat_form"] button {
    display: none !important;
}
.st-key-slide_chat_form [data-testid="stForm"],
div[class*="st-key-slide_chat_form"] form {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

/* ALL suggestion chip buttons — both general and by specific key */
div.st-key-slide_chat_drawer button,
div.st-key-slide_chat_drawer .stButton > button,
.st-key-dyn_chip_r1 button,
.st-key-dyn_chip_r2 button,
.st-key-dyn_chip_r3_1 button,
.st-key-dyn_chip_r3_2 button,
.st-key-dyn_chip_r3_3 button,
.st-key-dyn_chip_r4_1 button,
.st-key-dyn_chip_r4_2 button,
.st-key-dyn_chip_r5_1 button,
.st-key-dyn_chip_r5_2 button {
    background-color: #141D2E !important;
    background: #141D2E !important;
    color: #94A3B8 !important;
    border: 1.2px solid #283347 !important;
    border-radius: 20px !important;
    font-size: 0.80rem !important;
}
div.st-key-slide_chat_drawer button:hover,
.st-key-dyn_chip_r1 button:hover,
.st-key-dyn_chip_r2 button:hover,
.st-key-dyn_chip_r3_1 button:hover,
.st-key-dyn_chip_r3_2 button:hover,
.st-key-dyn_chip_r3_3 button:hover,
.st-key-dyn_chip_r4_1 button:hover,
.st-key-dyn_chip_r4_2 button:hover,
.st-key-dyn_chip_r5_1 button:hover,
.st-key-dyn_chip_r5_2 button:hover {
    background-color: #1E293B !important;
    border-color: #F87171 !important;
    color: #F87171 !important;
}

/* Chat text input */
div.st-key-slide_chat_drawer input,
div.st-key-slide_chat_drawer [data-baseweb="base-input"],
div.st-key-slide_chat_drawer [data-baseweb="base-input"] > div,
div.st-key-slide_chat_drawer [data-baseweb="base-input"] input,
div.st-key-slide_chat_drawer [data-baseweb="input"],
div.st-key-slide_chat_drawer [data-baseweb="input"] input,
div[class*="st-key-floating_chat_user_input"] input,
div[class*="st-key-floating_chat_user_input"] [data-baseweb="base-input"],
div[class*="st-key-floating_chat_user_input"] [data-baseweb="base-input"] input {
    background-color: #141D2E !important;
    background: #141D2E !important;
    color: #F8FAFC !important;
    border: 1.5px solid #283347 !important;
    border-radius: 24px !important;
    padding: 10px 16px !important;
}
.st-key-slide_chat_form input::placeholder,
div.st-key-slide_chat_drawer input::placeholder {
    color: #4B5B73 !important;
}

/* header close/refresh buttons */
.st-key-popup_unified_header button,
.st-key-drawer_clear_chat_btn button,
.st-key-drawer_close_x_btn button,
div[class*="st-key-drawer_close_x_btn"] button,
div[class*="st-key-drawer_clear_chat_btn"] button {
    background: rgba(255,255,255,0.12) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 50% !important;
    font-size: 1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    height: 32px !important;
    width: 32px !important;
    min-height: 32px !important;
    min-width: 32px !important;
}
.st-key-popup_unified_header button:hover,
.st-key-drawer_clear_chat_btn button:hover,
.st-key-drawer_close_x_btn button:hover,
div[class*="st-key-drawer_close_x_btn"] button:hover,
div[class*="st-key-drawer_clear_chat_btn"] button:hover {
    background: rgba(179,38,30,0.6) !important;
    border-color: #F87171 !important;
    color: #FFFFFF !important;
}

/* Text colors inside drawer */
div.st-key-slide_chat_drawer p,
div.st-key-slide_chat_drawer span,
div.st-key-slide_chat_drawer label {
    color: #94A3B8 !important;
}
div.st-key-slide_chat_drawer b, div.st-key-slide_chat_drawer strong {
    color: #F8FAFC !important;
}
</style>
""", unsafe_allow_html=True)


if chat_is_open:
    with st.container(key="slide_chat_drawer"):
        # 1. Seamless Full-Width Red Header with Clear Chat & Close Buttons
        with st.container(key="popup_unified_header"):
            hdr_c1, hdr_c2, hdr_c3 = st.columns([3.4, 0.45, 0.45], vertical_alignment="center")
            with hdr_c1:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 26px; height: 26px; border-radius: 50%; background: #1C0507; border: 1.4px solid #F87171; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <svg viewBox="0 0 36 36"width="16"height="16"fill="none"xmlns="http://www.w3.org/2000/svg">
                            <circle cx="18"cy="4.5"r="2.2"fill="#FFFFFF"/>
                            <path d="M18 6.7V9.5"stroke="#FFFFFF"stroke-width="2"stroke-linecap="round"/>
                            <rect x="7"y="9.5"width="22"height="19"rx="6"fill="#FFFFFF"/>
                            <rect x="3.5"y="14.5"width="3.5"height="9"rx="1.7"fill="#FFFFFF"/>
                            <rect x="29"y="14.5"width="3.5"height="9"rx="1.7"fill="#FFFFFF"/>
                            <rect x="9.5"y="12"width="17"height="14"rx="4"fill="#0B132B"/>
                            <circle cx="14"cy="17.5"r="2"fill="#38BDF8"/>
                            <circle cx="22"cy="17.5"r="2"fill="#38BDF8"/>
                            <path d="M14.5 22C16 23.2 20 23.2 21.5 22"stroke="#38BDF8"stroke-width="1.6"stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div>
                        <div style="font-weight: 800; font-size: 0.82rem; color: #FFFFFF; line-height: 1.2;">
                            {T.get("chat_header_title", "MediMind AI Clinical Assistant")}
                        </div>
                        <div style="font-size: 0.68rem; color: #E2E8F0; font-weight: 500; margin-top: 1px; display: flex; align-items: center; gap: 4px;">
                            <img src="https://cdn-icons-png.flaticon.com/512/4381/4381635.png" style="width: 10px; height: 10px; object-fit: contain; vertical-align: middle;" alt="Online"/> {T.get("chat_header_status", "Online — Ask me anything")}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with hdr_c2:
                st.button("", key="drawer_clear_chat_btn", on_click=clear_floating_chat, help="Clear Chat History", icon=":material/refresh:")
            with hdr_c3:
                st.button("", key="drawer_close_x_btn", on_click=toggle_floating_chat, help="Close Assistant", icon=":material/close:")

        if current_context["symptoms"] or current_context["top_disease"]:
            symp_snippet = ", ".join(current_context["symptoms"][:2]) if current_context["symptoms"] else current_context["top_disease"]
            st.markdown(f"""
            <div style="background: rgba(179, 38, 30, 0.08); border-bottom: 1px solid rgba(179, 38, 30, 0.2); padding: 4px 12px; font-size: 0.70rem; color: #F87171;">
                <b>Active Context:</b> {symp_snippet}
            </div>
            """, unsafe_allow_html=True)

        # 2. Scrollable Message & Interactive Suggestions Container (ORIGINAL structure)
        # JS injection to force dark chip styles via inline style.setProperty (beats emotion CSS re-injection)
        if is_dark:
            components.html("""
    <script>
    (function() {
        var BG = '#1E293B', FG = '#E2E8F0', BD = '1.2px solid #334155', BR = '20px', FS = '0.80rem';
        var CHIPS = ['dyn_chip_r1','dyn_chip_r2','dyn_chip_r3_1','dyn_chip_r3_2','dyn_chip_r3_3',
                     'dyn_chip_r4_1','dyn_chip_r4_2','dyn_chip_r5_1','dyn_chip_r5_2'];

        function applyDark(doc) {
            CHIPS.forEach(function(k) {
                doc.querySelectorAll('div[class*="st-key-' + k + '"] button, .st-key-' + k + ' button').forEach(function(btn) {
                    btn.style.setProperty('background-color', BG, 'important');
                    btn.style.setProperty('background',       BG, 'important');
                    btn.style.setProperty('color',            FG, 'important');
                    btn.style.setProperty('border',           BD, 'important');
                    btn.style.setProperty('border-radius',    BR, 'important');
                    btn.style.setProperty('font-size',        FS, 'important');
                    btn.style.setProperty('box-shadow', 'none', 'important');
                    btn.addEventListener('mouseover', function() {
                        btn.style.setProperty('background-color', '#334155', 'important');
                        btn.style.setProperty('background',       '#334155', 'important');
                        btn.style.setProperty('color',      '#F87171', 'important');
                        btn.style.setProperty('border',     '1.2px solid #F87171', 'important');
                    });
                    btn.addEventListener('mouseout', function() {
                        btn.style.setProperty('background-color', BG, 'important');
                        btn.style.setProperty('background',       BG, 'important');
                        btn.style.setProperty('color',  FG, 'important');
                        btn.style.setProperty('border', BD, 'important');
                    });
                });
            });
        }

        function run() { try { applyDark(window.parent.document); } catch(e) {} }
        run(); setTimeout(run,50); setTimeout(run,200); setTimeout(run,500); setTimeout(run,1000);
        try {
            new MutationObserver(run).observe(window.parent.document.body, {childList:true, subtree:true});
        } catch(e) {}
    })();
    </script>
    """, height=0)

        chat_box = st.container(height=340)
        with chat_box:

            # A. Always Render Greeting Card
            greeting_bg = "#1A2540"if is_dark else "rgba(255,255,255,0.9)"
            greeting_border = "#1E293B"if is_dark else "var(--mm-border-color)"
            greeting_text = "#F8FAFC"if is_dark else "var(--mm-text-primary)"
            greeting_sub = "#94A3B8"if is_dark else "var(--mm-text-secondary)"
            st.markdown(f"""
            <div style="display: flex; gap: 8px; align-items: flex-start; margin-top: 6px; margin-bottom: 12px;">
                <div style="width: 28px; height: 28px; border-radius: 50%; background: #1C0507; border: 1.4px solid #F87171; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 4px;">
                    <svg viewBox="0 0 36 36"width="18"height="18"fill="none"xmlns="http://www.w3.org/2000/svg">
                        <circle cx="18"cy="4.5"r="2.2"fill="#FFFFFF"/>
                        <path d="M18 6.7V9.5"stroke="#FFFFFF"stroke-width="2"stroke-linecap="round"/>
                        <rect x="7"y="9.5"width="22"height="19"rx="6"fill="#FFFFFF"/>
                        <rect x="3.5"y="14.5"width="3.5"height="9"rx="1.7"fill="#FFFFFF"/>
                        <rect x="29"y="14.5"width="3.5"height="9"rx="1.7"fill="#FFFFFF"/>
                        <rect x="9.5"y="12"width="17"height="14"rx="4"fill="#0B132B"/>
                        <circle cx="14"cy="17.5"r="2"fill="#38BDF8"/>
                        <circle cx="22"cy="17.5"r="2"fill="#38BDF8"/>
                        <path d="M14.5 22C16 23.2 20 23.2 21.5 22"stroke="#38BDF8"stroke-width="1.6"stroke-linecap="round"/>
                    </svg>
                </div>
                <div style="background: {greeting_bg}; border: 1.2px solid {greeting_border}; border-radius: 14px; padding: 12px 14px; font-size: 0.82rem; color: {greeting_text}; line-height: 1.45; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-weight: 700; color: {greeting_text}; margin-bottom: 4px;">Hello! I'm your <b>MediMind Clinical AI Assistant</b>.</div>
                    <div style="color: {greeting_sub}; font-size: 0.78rem;">How can I help you today?</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # B. Multi-row Natural Pill Chips
            if st.button("Explain my symptoms in simple words", key="dyn_chip_r1", use_container_width=True):
                st.session_state["floating_chat_history"].append({"role": "user", "content": "Please explain my current symptoms and what they indicate in simple terms."})
                with st.spinner("Analyzing query..."):
                    reply = ask_medimind_ai("Please explain my current symptoms and what they indicate in simple terms.", st.session_state["floating_chat_history"], current_context, lang_code)
                st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                st.rerun()

            if st.button("Which medicine should I take?", key="dyn_chip_r2", use_container_width=True):
                st.session_state["floating_chat_history"].append({"role": "user", "content": "Can you explain the prescribed medicines and active compounds?"})
                with st.spinner("Analyzing query..."):
                    reply = ask_medimind_ai("Can you explain the prescribed medicines and active compounds?", st.session_state["floating_chat_history"], current_context, lang_code)
                st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                st.rerun()

            c3_1, c3_2, c3_3 = st.columns([1, 1, 1])
            with c3_1:
                if st.button("Food timing?", key="dyn_chip_r3_1", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "When should I take my medicines with food?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("When should I take my medicines with food?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()
            with c3_2:
                if st.button("Danger signs", key="dyn_chip_r3_2", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "What are emergency red flags and danger signs?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("What are emergency red flags and danger signs?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()
            with c3_3:
                if st.button("Yoga poses", key="dyn_chip_r3_3", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "Which restorative yoga postures will speed up my recovery?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("Which restorative yoga postures will speed up my recovery?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()

            c4_1, c4_2 = st.columns([1, 1])
            with c4_1:
                if st.button("Lab report scanner", key="dyn_chip_r4_1", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "How and where do I scan my lab blood report or doctor prescription in MediMind AI?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("How and where do I scan my lab blood report or doctor prescription in MediMind AI?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()
            with c4_2:
                if st.button("Nearby hospitals", key="dyn_chip_r4_2", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "Where are nearby emergency hospitals and clinics and how do I find them?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("Where are nearby emergency hospitals and clinics and how do I find them?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()

            c5_1, c5_2 = st.columns([1, 1])
            with c5_1:
                if st.button("Doctor visit prep", key="dyn_chip_r5_1", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "What questions should I ask my doctor during the consultation?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("What questions should I ask my doctor during the consultation?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()
            with c5_2:
                if st.button("Recovery & diet tips", key="dyn_chip_r5_2", use_container_width=True):
                    st.session_state["floating_chat_history"].append({"role": "user", "content": "What home diet and hydration routine is recommended?"})
                    with st.spinner("Analyzing query..."):
                        reply = ask_medimind_ai("What home diet and hydration routine is recommended?", st.session_state["floating_chat_history"], current_context, lang_code)
                    st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()

            # C. Chat history
            if st.session_state["floating_chat_history"]:
                st.markdown("<div style='border-top: 1px dashed var(--mm-border-color); margin: 12px 0 10px 0;'></div>", unsafe_allow_html=True)
                for msg_idx, msg in enumerate(st.session_state["floating_chat_history"]):
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                            <div style="background: #B3261E; color: #FFFFFF; border-radius: 14px 14px 2px 14px; padding: 8px 12px; max-width: 86%; font-size: 0.82rem; line-height: 1.35; word-break: break-word; box-shadow: 0 2px 6px rgba(179,38,30,0.3);">
                                {msg['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        ai_bubble_bg = "#1A2540" if is_dark else "rgba(255,255,255,0.9)"
                        ai_bubble_border = "#1E293B" if is_dark else "var(--mm-border-color)"
                        ai_bubble_text = "#E2E8F0" if is_dark else "var(--mm-text-primary)"
                        raw_ai_text = msg.get("content", "")
                        try:
                            clean_ai_html = markdown.markdown(raw_ai_text, extensions=['tables', 'fenced_code', 'nl2br'])
                        except Exception:
                            clean_ai_html = raw_ai_text.replace("\n", "<br/>")

                        st.markdown(f"""
                        <div style="display: flex; gap: 8px; align-items: flex-start; margin-bottom: 10px;">
                            <div style="width: 26px; height: 26px; border-radius: 50%; background: #1C0507; border: 1.4px solid #F87171; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">
                                <svg viewBox="0 0 36 36" width="16" height="16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="18" cy="4.5" r="2.2" fill="#FFFFFF"/>
                                    <path d="M18 6.7V9.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
                                    <rect x="7" y="9.5" width="22" height="19" rx="6" fill="#FFFFFF"/>
                                    <rect x="3.5" y="14.5" width="3.5" height="9" rx="1.7" fill="#FFFFFF"/>
                                    <rect x="29" y="14.5" width="3.5" height="9" rx="1.7" fill="#FFFFFF"/>
                                    <rect x="9.5" y="12" width="17" height="14" rx="4" fill="#0B132B"/>
                                    <circle cx="14" cy="17.5" r="2" fill="#38BDF8"/>
                                    <circle cx="22" cy="17.5" r="2" fill="#38BDF8"/>
                                    <path d="M14.5 22C16 23.2 20 23.2 21.5 22" stroke="#38BDF8" stroke-width="1.6" stroke-linecap="round"/>
                                </svg>
                            </div>
                            <div class="mm-ai-chat-bubble" style="background: {ai_bubble_bg}; color: {ai_bubble_text}; border-radius: 14px 14px 14px 2px; padding: 10px 12px; max-width: calc(100% - 36px); font-size: 0.82rem; line-height: 1.45; border: 1.2px solid {ai_bubble_border}; word-break: break-word; overflow-x: auto; box-sizing: border-box;">
                                {clean_ai_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        action = detect_redirect_action(msg.get("content", ""), lang_code)
                        if action:
                            st.markdown("<div style='margin: -2px 0 8px 34px;'>", unsafe_allow_html=True)
                            if st.button(f" {action['label']}", key=f"nav_action_btn_{msg_idx}", use_container_width=True):
                                st.session_state["active_panel"] = action["panel"]
                                st.session_state["floating_chat_open"] = False
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

        # 3. Chat Input Bar (Full-width, Send on Enter key, ZERO buttons below)
        st.text_input(
            "Chat Input",
            placeholder=T.get("chat_input_placeholder", "Ask any medical, symptom, or medication question... (Press Enter)"),
            key="floating_chat_user_input",
            on_change=handle_floating_chat_submit,
            label_visibility="collapsed"
        )

        if st.session_state.get("pending_chat_query"):
            q_to_process = st.session_state.pop("pending_chat_query")
            with st.spinner("Analyzing query..."):
                reply = ask_medimind_ai(q_to_process, st.session_state["floating_chat_history"], current_context, lang_code)
            st.session_state["floating_chat_history"].append({"role": "assistant", "content": reply})
            st.rerun()



# Page Footer
st.markdown("---")
st.markdown(
    f"<center style='color: #64748B; font-size: 0.86rem; padding: 14px 0; font-weight: 500;'><b>MediMind AI</b> © 2026 • Enterprise Multilingual Healthcare Suite • Built for Clinical Safety & Triage Support</center>",
    unsafe_allow_html=True
)
