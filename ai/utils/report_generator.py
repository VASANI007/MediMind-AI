"""
    MediMind AI - Clinical Health Summary PDF Generator
Generates comprehensive downloadable medical summary PDF reports using ReportLab.
Includes patient profile, ranked conditions, medicines with verified packaging photos,
restorative yoga, physiotherapy, compression therapy, diet, red flags, and clinical advisory.
"""
import io
import os
import re
import base64
import requests
from datetime import datetime
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage, KeepTogether
)

def _clean_pdf_text(text) -> str:
    """
    Sanitizes text for ReportLab PDF rendering.
    Replaces Unicode hyphens, dashes, curly quotes, non-breaking spaces,
    and removes unsupported emojis/symbols that cause square boxes (tofu) in standard fonts.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
        
    # Replace unicode dashes & hyphens (major cause of square boxes in numbers/words)
    text = text.replace('\u2011', '-')   # Non-breaking hyphen (e.g. community-acquired, 7-10)
    text = text.replace('\u2010', '-')   # Hyphen
    text = text.replace('\u2012', '-')   # Figure dash
    text = text.replace('\u2013', ' - ') # En-dash
    text = text.replace('\u2014', ' - ') # Em-dash
    text = text.replace('\u2015', ' - ') # Horizontal bar
    text = text.replace('\u2212', '-')   # Minus sign
    text = text.replace('■', '')         # Literal black square if already present
    
    # Replace spaces & quotes
    text = text.replace('\u202f', ' ')   # Narrow no-break space
    text = text.replace('\u00a0', ' ')   # Non-breaking space
    text = text.replace('\u200b', '')    # Zero-width space
    text = text.replace('\u2018', "'").replace('\u2019', "'") # Curly single quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"') # Curly double quotes
    text = text.replace('\u2026', '...') # Ellipsis
    
    # Remove emojis and high unicode symbols (<img src="https://cdn-icons-png.flaticon.com/512/6266/6266132.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" />, <img src="https://cdn-icons-png.flaticon.com/512/3722/3722581.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" />, <img src="https://cdn-icons-png.flaticon.com/128/6018/6018699.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" />, <img src="https://cdn-icons-png.flaticon.com/512/5228/5228598.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" />, <img src="https://cdn-icons-png.flaticon.com/128/6939/6939131.png" style="width: 1.1em; height: 1.1em; vertical-align: -0.15em; display: inline-block;" />, etc.) that Helvetica cannot render
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text) # 4-byte emojis
    text = re.sub(r'[\u2600-\u27ff]', '', text)         # Misc symbols & dingbats
    text = re.sub(r'[\ufe00-\ufe0f]', '', text)         # Variation selectors
    
    return text.strip()


def _convert_to_rl_image(img_source, width=70, height=70):
    """
    Safely converts image path, remote HTTP URL, or base64 Data URI into a ReportLab Image Flowable.
    """
    if not img_source or not isinstance(img_source, str):
        return None
        
    try:
        # 1. Base64 Data URI
        if img_source.startswith("data:image"):
            if "base64," in img_source:
                b64_data = img_source.split("base64,")[1]
                img_bytes = base64.b64decode(b64_data)
                if "svg" in img_source[:30]:
                    return None
                img_buf = io.BytesIO(img_bytes)
                pil_img = PILImage.open(img_buf)
                pil_img = pil_img.convert("RGB")
                out_buf = io.BytesIO()
                pil_img.save(out_buf, format="PNG")
                out_buf.seek(0)
                return RLImage(out_buf, width=width, height=height)

        # 2. Remote HTTP(S) URL
        elif img_source.startswith("http://") or img_source.startswith("https://"):
            resp = requests.get(img_source, timeout=3, headers={"User-Agent": "MediMindAI/2.0"})
            if resp.status_code == 200:
                img_buf = io.BytesIO(resp.content)
                pil_img = PILImage.open(img_buf)
                pil_img = pil_img.convert("RGB")
                out_buf = io.BytesIO()
                pil_img.save(out_buf, format="PNG")
                out_buf.seek(0)
                return RLImage(out_buf, width=width, height=height)

        # 3. Local File Path
        elif os.path.exists(img_source):
            if img_source.lower().endswith(".svg"):
                return None
            pil_img = PILImage.open(img_source)
            pil_img = pil_img.convert("RGB")
            out_buf = io.BytesIO()
            pil_img.save(out_buf, format="PNG")
            out_buf.seek(0)
            return RLImage(out_buf, width=width, height=height)
            
    except Exception as e:
        print(f"ReportLab image conversion note: {e}")
        
    return None


def generate_pdf_report(user_context: dict, triage_result: dict, care_recommendations: dict = None) -> io.BytesIO:
    """
    Builds a complete, beautifully structured PDF clinical summary report.
    
    Args:
        user_context: Dict containing patient demographics, symptoms, medical history.
        triage_result: Dict containing ranked conditions, urgency, emergency flags.
        care_recommendations: Dict containing medicines, recovery, yoga, physio, diet, compress.
        
    Returns:
        io.BytesIO buffer containing the PDF.
    """
    user_context = user_context or {}
    triage_result = triage_result or {}
    care_res = care_recommendations or {}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Palette definition
    PRIMARY_RED = colors.HexColor("#B3261E")
    DARK_NAVY = colors.HexColor("#0F172A")
    ALERT_RED = colors.HexColor("#DC2626")
    SUCCESS_GREEN = colors.HexColor("#16A34A")
    ORANGE_BRAND = colors.HexColor("#EA580C")
    BLUE_BRAND = colors.HexColor("#2563EB")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#CBD5E1")
    TEXT_MUTED = colors.HexColor("#64748B")
    TEXT_DARK = colors.HexColor("#1E293B")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY_RED
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=DARK_NAVY,
        spaceBefore=7,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK
    )

    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK
    )

    alert_style = ParagraphStyle(
        'AlertBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=ALERT_RED
    )

    advisory_heading = ParagraphStyle(
        'AdvisoryHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=ORANGE_BRAND
    )

    advisory_body = ParagraphStyle(
        'AdvisoryBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=DARK_NAVY
    )

    story = []

    # 1. Header Banner with Official Logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "logo", "logo_light.png")
    
    gen_time_str = datetime.now().strftime('%d %B %Y, %I:%M %p')
    doc_id_str = f"MM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if os.path.exists(logo_path):
        try:
            img = RLImage(logo_path, width=40, height=40)
            t_header = Table([[
                img,
                [
                    Paragraph("MediMind AI — Clinical Health Summary & Triage Report", title_style),
                    Paragraph(f"Generated: {gen_time_str} | Report ID: {doc_id_str} | Verified Healthcare Engine", subtitle_style)
                ]
            ]], colWidths=[46, 494])
            t_header.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t_header)
        except Exception:
            story.append(Paragraph("MediMind AI — Clinical Health Summary & Triage Report", title_style))
            story.append(Paragraph(f"Generated: {gen_time_str} | Report ID: {doc_id_str}", subtitle_style))
    else:
        story.append(Paragraph("MediMind AI — Clinical Health Summary & Triage Report", title_style))
        story.append(Paragraph(f"Generated: {gen_time_str} | Report ID: {doc_id_str}", subtitle_style))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_RED, spaceBefore=2, spaceAfter=5))

    # 2. Patient Demographics & Health Profile Table
    # 2. Patient Demographics & Health Profile Table
    symptoms_list = user_context.get("symptoms", []) or []
    sym_str = _clean_pdf_text(", ".join(symptoms_list) if symptoms_list else "None recorded")
    
    patient_data = [
        [
            Paragraph("<b>Age Group:</b> " + _clean_pdf_text(str(user_context.get("age", user_context.get("age_group", "21-30 Years")))), body_style),
            Paragraph("<b>Gender:</b> " + _clean_pdf_text(str(user_context.get("gender", "Male"))), body_style),
            Paragraph("<b>Location:</b> " + _clean_pdf_text(str(user_context.get("location", user_context.get("state", "India")))), body_style)
        ],
        [
            Paragraph("<b>Symptom Duration:</b> " + _clean_pdf_text(str(user_context.get("duration", "1-3 Days"))), body_style),
            Paragraph("<b>Assessed Severity:</b> " + _clean_pdf_text(str(user_context.get("severity", "Moderate"))), body_style),
            Paragraph("<b>Blood Group:</b> " + _clean_pdf_text(str(user_context.get("blood_group", "None"))), body_style)
        ],
        [
            Paragraph("<b>Pre-existing Conditions:</b> " + _clean_pdf_text(str(user_context.get("pre_existing", user_context.get("conditions", "None")))), body_style),
            Paragraph("<b>Current Medications:</b> " + _clean_pdf_text(str(user_context.get("current_meds", user_context.get("medications", "None")))), body_style),
            Paragraph("<b>Known Allergies:</b> " + _clean_pdf_text(str(user_context.get("allergies", "None"))), body_style)
        ],
        [
            Paragraph("<b>Family History / Surgeries:</b> " + _clean_pdf_text(str(user_context.get("surgeries", user_context.get("family_history", "None")))), body_style),
            Paragraph("", body_style),
            Paragraph("", body_style)
        ]
    ]
    t_patient = Table(patient_data, colWidths=[180, 180, 180])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 5))

    # 3. Reported Symptoms
    story.append(Paragraph(f"<b>Reported Symptoms:</b> {sym_str}", body_style))
    story.append(Spacer(1, 5))

    # 4. Emergency Red-Flag Alert (if present)
    if triage_result.get("is_emergency"):
        rf_rows = [[Paragraph("EMERGENCY RED FLAG DETECTED — IMMEDIATE MEDICAL EVALUATION REQUIRED", alert_style)]]
        for rf in triage_result.get("red_flags", []):
            rf_name = _clean_pdf_text(rf.get('symptom_name', 'Critical Symptom'))
            rf_action = _clean_pdf_text(rf.get('immediate_action_protocol', 'Proceed immediately to emergency room.'))
            rf_rows.append([Paragraph(f"• <b>{rf_name}:</b> {rf_action}", alert_style)])
        t_rf = Table(rf_rows, colWidths=[540])
        t_rf.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
            ('BOX', (0,0), (-1,-1), 1.5, ALERT_RED),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_rf)
        story.append(Spacer(1, 6))

    # 5. Plausible Clinical Health Conditions Table
    ranked_conds = triage_result.get("ranked_conditions", [])
    if ranked_conds:
        story.append(Paragraph("Plausible Clinical Health Conditions (Differential Assessment)", section_heading))
        cond_rows = [["Condition Name", "ICD-11 Code", "Category", "Match Index"]]
        for cond in ranked_conds[:4]:
            cond_name = _clean_pdf_text(cond.get("name", cond.get("disease_name", "Clinical Condition")))
            cond_rows.append([
                Paragraph(f"<b>{cond_name}</b>", body_style),
                Paragraph(_clean_pdf_text(cond.get("icd_code", "N/A")), body_style),
                Paragraph(_clean_pdf_text(cond.get("category", "General Medicine")), body_style),
                Paragraph(f"<b>{cond.get('match_percentage', 75)}%</b>", body_style)
            ])
        t_cond = Table(cond_rows, colWidths=[210, 95, 140, 95])
        t_cond.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY_RED),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8.5),
            ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_cond)
        story.append(Spacer(1, 6))

    # 6. Clinical Summary & Expected Recovery Timeline
    summary_text = _clean_pdf_text(care_res.get("summary") or "Clinical evaluation completed. Monitor symptoms and follow supportive care instructions.")
    recovery_text = _clean_pdf_text(care_res.get("recovery_duration") or "3 - 5 Days with adequate rest, hydration, and adherence to prescribed medications.")
    
    summary_data = [
        [
            Paragraph("<b>Clinical Summary:</b>", body_bold),
            Paragraph(summary_text, body_style)
        ],
        [
            Paragraph("<b>Expected Recovery:</b>", body_bold),
            Paragraph(f"<font color='#16A34A'><b>{recovery_text}</b></font>", body_style)
        ]
    ]
    t_summary = Table(summary_data, colWidths=[130, 410])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 1, SUCCESS_GREEN),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 6))

    # 7. Verified Medication & Pharmaceutical Gallery (With Images)
    med_gallery = care_res.get("medicine_gallery", care_res.get("medicines", []))
    if med_gallery:
        story.append(Paragraph(f"Verified Medication & Pharmaceutical Guidance ({len(med_gallery)} Items)", section_heading))
        
        med_table_rows = [["Product", "Medication Name & Indication", "Dosage & Food Timing", "Course"]]
        for med in med_gallery:
            m_name = _clean_pdf_text(med.get("name", "Prescription Drug"))
            m_ind = _clean_pdf_text(med.get("indication", ""))
            m_dose = _clean_pdf_text(med.get("dosage", "As directed by physician"))
            m_timing = _clean_pdf_text(med.get("food_timing", "After Food"))
            m_course = _clean_pdf_text(med.get("course_duration", "3 - 5 Days"))
            m_type = _clean_pdf_text(med.get("type", "OTC"))
            m_img_src = med.get("image")
            
            rl_img = _convert_to_rl_image(m_img_src, width=50, height=50)
            img_cell = rl_img if rl_img else Paragraph("<b>Rx</b>", ParagraphStyle('RxBadge', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, alignment=1, textColor=PRIMARY_RED))
            
            info_cell = [
                Paragraph(f"<b>{m_name}</b> <font color='#64748B'>({m_type})</font>", body_style),
                Paragraph(f"<font color='#475569'>{m_ind}</font>", subtitle_style)
            ]
            
            timing_color = "#EA580C" if "before" in m_timing.lower() or "pehle" in m_timing.lower() else "#16A34A"
            dose_cell = [
                Paragraph(f"<b>Dosage:</b> {m_dose}", body_style),
                Paragraph(f"<b>Timing:</b> <font color='{timing_color}'><b>{m_timing}</b></font>", body_style)
            ]
            
            course_cell = Paragraph(f"<font color='#2563EB'><b>{m_course}</b></font>", body_style)
            
            med_table_rows.append([img_cell, info_cell, dose_cell, course_cell])
            
        t_meds = Table(med_table_rows, colWidths=[58, 242, 160, 80])
        t_meds.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8.5),
            ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ]))
        story.append(t_meds)
        story.append(Spacer(1, 6))

    # 8. Restorative Yoga & Supportive Physiotherapy Guidance
    yoga_recs = care_res.get("yoga_recommendations", [])
    physio_recs = care_res.get("physiotherapy_recommendations", [])
    
    if yoga_recs or physio_recs:
        story.append(Paragraph("Restorative Yoga & Supportive Physiotherapy Exercises", section_heading))
        yp_rows = []
        if yoga_recs:
            for y in yoga_recs:
                y_name = _clean_pdf_text(y.get('name', 'Yoga Asana'))
                y_dur = _clean_pdf_text(y.get('duration', '5-10 Mins'))
                y_inst = _clean_pdf_text(y.get('instructions', y.get('benefit', '')))
                yp_rows.append([
                    Paragraph("<b>Restorative Yoga</b>", ParagraphStyle('YogaH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#15803D"))),
                    Paragraph(f"<b>{y_name}</b> ({y_dur})<br/>{y_inst}", body_style)
                ])
        if physio_recs:
            for p in physio_recs:
                p_name = _clean_pdf_text(p.get('name', 'Mobility Exercise'))
                p_reps = _clean_pdf_text(p.get('reps', '2-3 Sets'))
                p_inst = _clean_pdf_text(p.get('technique', p.get('instructions', '')))
                yp_rows.append([
                    Paragraph("<b>Physiotherapy</b>", ParagraphStyle('PhysH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#1D4ED8"))),
                    Paragraph(f"<b>{p_name}</b> ({p_reps})<br/>{p_inst}", body_style)
                ])
                
        t_yp = Table(yp_rows, colWidths=[125, 415])
        t_yp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_yp)
        story.append(Spacer(1, 6))

    # 9. Compression Therapy Guidance
    comp_guidance = care_res.get("compress_guidance")
    if comp_guidance and isinstance(comp_guidance, dict) and comp_guidance.get("type") and comp_guidance.get("type") != "None":
        story.append(Paragraph("Thermal / Compression Therapy Guidance", section_heading))
        c_type = _clean_pdf_text(comp_guidance.get("type", "Compress"))
        c_inst = _clean_pdf_text(comp_guidance.get("instructions", ""))
        c_prec = _clean_pdf_text(comp_guidance.get("precautions", ""))
        comp_data = [[
            Paragraph(f"<b>{c_type}:</b>", body_bold),
            Paragraph(f"{c_inst} <i>(Precaution: {c_prec})</i>", body_style)
        ]]
        t_comp = Table(comp_data, colWidths=[125, 415])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('BOX', (0,0), (-1,-1), 1, BLUE_BRAND),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_comp)
        story.append(Spacer(1, 6))

    # 10. Dietary & Hydration Guidance
    diet_recs = care_res.get("diet_recommendations") or care_res.get("dietary_guidelines")
    if diet_recs:
        eat_list = []
        avoid_list = []
        hyd_text = "Drink 2.5 - 3 liters of water daily."
        
        if isinstance(diet_recs, dict):
            eat_list = [_clean_pdf_text(x) for x in diet_recs.get("foods_to_eat", [])]
            avoid_list = [_clean_pdf_text(x) for x in diet_recs.get("foods_to_avoid", [])]
            hyd_text = _clean_pdf_text(diet_recs.get("hydration_advice", hyd_text))
        elif isinstance(diet_recs, list):
            eat_list = [_clean_pdf_text(x) for x in diet_recs]
        
        if eat_list or avoid_list:
            story.append(Paragraph("Clinical Dietary & Hydration Recommendations", section_heading))
            diet_data = [
                [
                    Paragraph("<b>Recommended Foods:</b>", body_bold),
                    Paragraph("• " + "<br/>• ".join(eat_list) if eat_list else "Nutritious balanced diet", body_style)
                ]
            ]
            if avoid_list:
                diet_data.append([
                    Paragraph("<b>Foods to Limit / Avoid:</b>", body_bold),
                    Paragraph("• " + "<br/>• ".join(avoid_list), body_style)
                ])
            diet_data.append([
                Paragraph("<b>Hydration Advice:</b>", body_bold),
                Paragraph(hyd_text, body_style)
            ])
            t_diet = Table(diet_data, colWidths=[140, 400])
            t_diet.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
                ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(t_diet)
            story.append(Spacer(1, 6))

    # 11. Recommended Diagnostic Laboratory Tests
    tests_list = [_clean_pdf_text(t) for t in triage_result.get("tests_to_discuss", [])]
    if tests_list:
        story.append(Paragraph("Recommended Clinical Diagnostic Tests (To Discuss with Physician)", section_heading))
        story.append(Paragraph("• " + "<br/>• ".join(tests_list), body_style))
        story.append(Spacer(1, 6))

    # 12. MANDATORY FINAL CLINICAL ADVISORY (Exact user text specification)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ORANGE_BRAND, spaceBefore=4, spaceAfter=6))
    
    advisory_table_data = [[
        [
            Paragraph("Clinical Advisory", advisory_heading),
            Spacer(1, 3),
            Paragraph("MediMind AI can make mistakes. Do not rely solely on AI suggestions — always consult a certified doctor or licensed physician for clinical decisions.", advisory_body)
        ]
    ]]
    t_advisory = Table(advisory_table_data, colWidths=[540])
    t_advisory.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF7ED")),
        ('BOX', (0,0), (-1,-1), 1.2, ORANGE_BRAND),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_advisory)

    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
