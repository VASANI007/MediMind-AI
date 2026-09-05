import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')
import json
from dotenv import load_dotenv
load_dotenv()

from ai.disease_prediction.predict import SymptomTriageEngine
from ai.utils.care_recommendations import get_dynamic_clinical_recommendations
from ai.utils.report_generator import generate_pdf_report

engine = SymptomTriageEngine()

symptoms = ["Cough", "Nausea", "Fatigue", "Groin Pain"]

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

selected_ids = []
for s in symptoms:
    s_l = s.strip().lower()
    if s_l in symptom_ontology_map:
        selected_ids.extend(symptom_ontology_map[s_l])

patient_history_with_sugar = {
    "age": "31 - 35",
    "age_group": "31 - 35 Years",
    "gender": "Male",
    "duration": "1 - 2 Weeks",
    "severity": "Moderate",
    "conditions": ["None"],
    "location": "Ahmedabad, Gujarat",
    "medications": "None",
    "allergies": "None",
    "surgeries": "Father has diabetes (sugar)",
    "details": ""
}

patient_history_without_sugar = {
    "age": "31 - 35",
    "age_group": "31 - 35 Years",
    "gender": "Male",
    "duration": "1 - 2 Weeks",
    "severity": "Moderate",
    "conditions": ["None"],
    "location": "Ahmedabad, Gujarat",
    "medications": "None",
    "allergies": "None",
    "surgeries": "None",
    "details": ""
}

print("=================================================================")
print("RUNNING REAL TEST 1: TRIAGE EVALUATION (DISEASE MATCHING)")
print("=================================================================")
triage_res = engine.evaluate_triage(reported_symptom_ids=selected_ids, patient_history=patient_history_with_sugar)
print("Urgency Level:", triage_res.get("urgency_level"))
print("Ranked Conditions:")
for c in triage_res.get("ranked_conditions", []):
    print(f" - {c.get('name')} | Match: {c.get('match_percentage')}% | Category: {c.get('category')}")
print("Lab Tests to Discuss:", triage_res.get("tests_to_discuss"))

top_cond = triage_res["ranked_conditions"][0]["name"] if triage_res.get("ranked_conditions") else "Acute Illness"

print("\n=================================================================")
print("RUNNING REAL TEST 2: LIVE AI CARE RECOMMENDATIONS (WITH FATHER DIABETES)")
print("=================================================================")
care_res_with_sugar = get_dynamic_clinical_recommendations(
    symptoms=symptoms,
    user_context=patient_history_with_sugar,
    top_condition=top_cond,
    lang_code="en"
)
print("API Source:", care_res_with_sugar.get("api_source"))
print("Summary:", care_res_with_sugar.get("summary"))
print("Recovery Duration:", care_res_with_sugar.get("recovery_duration"))
print("Diet Guidelines:", care_res_with_sugar.get("dietary_guidelines"))
print("Medicines:")
for m in care_res_with_sugar.get("medicine_gallery", []):
    name = str(m.get('name')).encode('ascii', 'replace').decode('ascii')
    ind = str(m.get('indication')).encode('ascii', 'replace').decode('ascii')
    dos = str(m.get('dosage')).encode('ascii', 'replace').decode('ascii')
    war = str(m.get('warnings')).encode('ascii', 'replace').decode('ascii')
    print(f" - {name} | Indication: {ind} | Dosage: {dos} | Warnings: {war}")

print("\n=================================================================")
print("RUNNING REAL TEST 3: LIVE AI CARE RECOMMENDATIONS (WITHOUT FATHER DIABETES)")
print("=================================================================")
care_res_without = get_dynamic_clinical_recommendations(
    symptoms=symptoms,
    user_context=patient_history_without_sugar,
    top_condition=top_cond,
    lang_code="en"
)
sum_wo = str(care_res_without.get("summary")).encode('ascii', 'replace').decode('ascii')
print("Summary without family history:", sum_wo)
print("Diet Guidelines without family history:", care_res_without.get("dietary_guidelines"))

print("\n=================================================================")
print("RUNNING REAL TEST 4: PDF GENERATION CHECK")
print("=================================================================")
pdf_io = generate_pdf_report(user_context=patient_history_with_sugar, triage_result=triage_res, care_recommendations=care_res_with_sugar)
print("PDF Generated successfully! Size:", len(pdf_io.getvalue()), "bytes")
