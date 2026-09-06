# -*- coding: utf-8 -*-
"""
    MediMind AI - Clinical Red Design System & Theme Engine
Enterprise Clinical UI/UX Layer for Hospital-Grade Healthcare Platforms.
"""

CUSTOM_CSS = """
    <style>
/* ==========================================================================
   1. TYPOGRAPHY & CORE DESIGN TOKENS
   ========================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --mm-brand-primary: #B3261E;
    --mm-brand-hover: #8C1F19;
    --mm-brand-active: #731914;
    --mm-brand-subtle: #FCEAE9;
    --mm-brand-border: #F8DAD8;
    
    --mm-bg-base: #F7F8FA;
    --mm-bg-surface: #FFFFFF;
    --mm-bg-sidebar: #111827;
    
    --mm-text-primary: #1A1D21;
    --mm-text-secondary: #5B616E;
    --mm-text-muted: #8A909D;
    
    --mm-border-color: #E7E9EC;
    --mm-border-light: #F0F2F5;
    
    --mm-status-critical: #D32F2F;
    --mm-status-critical-bg: #FDECEA;
    --mm-status-warning: #D97706;
    --mm-status-warning-bg: #FEF6E7;
    --mm-status-success: #1E7A4C;
    --mm-status-success-bg: #E8F5EC;
    --mm-status-info: #2563A6;
    --mm-status-info-bg: #EAF2FB;
    
    --mm-radius-sm: 6px;
    --mm-radius-md: 8px;
    --mm-radius-lg: 12px;
    --mm-radius-xl: 16px;
    
    --mm-shadow-subtle: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    --mm-shadow-card: 0 2px 6px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
    --mm-shadow-hover: 0 6px 16px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
}

/* ============================================================
   DARK MODE -- activated when data-theme="dark"is set on root
   ============================================================ */
[data-theme="dark"],
[data-theme="dark"] .stApp,
[data-theme="dark"] body {
    --mm-bg-base: #0B0F19 !important;
    --mm-bg-surface: #111827 !important;
    --mm-bg-sidebar: #070B14 !important;
    --mm-text-primary: #F8FAFC !important;
    --mm-text-secondary: #94A3B8 !important;
    --mm-text-muted: #64748B !important;
    --mm-border-color: #1E293B !important;
    --mm-border-light: #162032 !important;
    --mm-brand-subtle: #2D1B1A !important;
    --mm-brand-border: #4A1C1A !important;
    --mm-status-success-bg: #0F2D1E !important;
    --mm-status-info-bg: #0D1F3C !important;
    --mm-status-critical-bg: #2D1215 !important;
    --mm-status-warning-bg: #2D1C00 !important;
    --mm-shadow-card: 0 2px 8px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.3) !important;
    --mm-shadow-hover: 0 6px 20px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.4) !important;
}

[data-theme="dark"] html,
[data-theme="dark"] body,
[data-theme="dark"] .stApp,
[data-theme="dark"] [class*="css"],
[data-theme="dark"] .stMainBlockContainer,
[data-theme="dark"] .main,
[data-theme="dark"] section.main {
    background-color: #0B0F19 !important;
    color: #F8FAFC !important;
}

[data-theme="dark"] .mm-card,
[data-theme="dark"] .mm-hospital-card,
[data-theme="dark"] .stContainer,
[data-theme="dark"] [data-testid="stVerticalBlockBorderWrapper"],
[data-theme="dark"] [data-testid="stHorizontalBlock"] > div,
[data-theme="dark"] [data-testid="element-container"] > div {
    background-color: #111827 !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}

[data-theme="dark"] .mm-hospital-card {
    background: #111827 !important;
    border-color: #1E293B !important;
}

[data-theme="dark"] h1,
[data-theme="dark"] h2,
[data-theme="dark"] h3,
[data-theme="dark"] h4,
[data-theme="dark"] h5,
[data-theme="dark"] h6,
[data-theme="dark"] p,
[data-theme="dark"] span,
[data-theme="dark"] label,
[data-theme="dark"] div {
    color: #F8FAFC !important;
}

/* ==========================================================================
   CODE & PRE INLINE BLOCKS (LIGHT & DARK MODE HIGH CONTRAST)
   ========================================================================== */
code,
[data-testid="stMarkdownContainer"] code,
.stMarkdown code,
p code,
li code,
span code,
div code,
td code {
    background-color: #F1F5F9 !important;
    background: #F1F5F9 !important;
    color: #B3261E !important;
    -webkit-text-fill-color: #B3261E !important;
    border: 1px solid #CBD5E1 !important;
    padding: 2px 7px !important;
    border-radius: 6px !important;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace !important;
    font-size: 0.86em !important;
    font-weight: 600 !important;
    display: inline-block !important;
    line-height: 1.35 !important;
}

[data-theme="dark"] code,
[data-theme="dark"] pre code,
[data-theme="dark"] [data-testid="stMarkdownContainer"] code,
[data-theme="dark"] .stMarkdown code,
[data-theme="dark"] .element-container code,
[data-theme="dark"] p code,
[data-theme="dark"] li code,
[data-theme="dark"] span code,
[data-theme="dark"] div code,
[data-theme="dark"] td code,
[data-theme="dark"] .mm-card code,
[data-theme="dark"] div[class*="mm-"] code {
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #FCA5A5 !important;
    -webkit-text-fill-color: #FCA5A5 !important;
    border: 1px solid #334155 !important;
    padding: 2px 7px !important;
    border-radius: 6px !important;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace !important;
    font-size: 0.86em !important;
    font-weight: 600 !important;
    display: inline-block !important;
    line-height: 1.35 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
}

[data-theme="dark"] pre,
[data-theme="dark"] pre[data-testid="stCodeBlock"] {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
}

/* Dark Mode Form Inputs (Inputs, TextAreas, Dropdowns) */
[data-theme="dark"] input,
[data-theme="dark"] textarea,
[data-theme="dark"] [data-baseweb="input"],
[data-theme="dark"] [data-baseweb="base-input"],
[data-theme="dark"] [data-baseweb="input"] input,
[data-theme="dark"] [data-baseweb="base-input"] input,
[data-theme="dark"] [data-baseweb="base-input"] textarea,
[data-theme="dark"] .stTextInput input,
[data-theme="dark"] .stTextInput > div > div,
[data-theme="dark"] .stTextArea textarea,
[data-theme="dark"] .stTextArea > div > div,
[data-theme="dark"] .stSelectbox > div > div,
[data-theme="dark"] [data-baseweb="select"] > div {
    background-color: #111827 !important;
    background: #111827 !important;
    border-color: #1E2E4E !important;
    color: #F8FAFC !important;
}

[data-theme="dark"] input::placeholder,
[data-theme="dark"] textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
}

/* Dark Mode File Uploader Dropzone & Controls */
[data-theme="dark"] [data-testid="stFileUploader"],
[data-theme="dark"] [data-testid="stFileUploadDropzone"],
[data-theme="dark"] section[data-testid="stFileUploadDropzone"],
[data-theme="dark"] .stFileUploader,
[data-theme="dark"] .stFileUploader > div,
[data-theme="dark"] .stFileUploader section,
[data-theme="dark"] div[data-testid="stFileUploadDropzone"] {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1.5px dashed #334155 !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
}

[data-theme="dark"] [data-testid="stFileUploadDropzone"]:hover,
[data-theme="dark"] section[data-testid="stFileUploadDropzone"]:hover {
    border-color: #B3261E !important;
    background-color: #1E293B !important;
    background: #1E293B !important;
}

[data-theme="dark"] [data-testid="stFileUploadDropzone"] div,
[data-theme="dark"] [data-testid="stFileUploadDropzone"] span,
[data-theme="dark"] [data-testid="stFileUploadDropzone"] small,
[data-theme="dark"] [data-testid="stFileUploadDropzone"] p,
[data-theme="dark"] [data-testid="stFileUploadDropzone"] label,
[data-theme="dark"] section[data-testid="stFileUploadDropzone"] * {
    color: #94A3B8 !important;
}

[data-theme="dark"] [data-testid="stFileUploadDropzone"] svg {
    fill: #94A3B8 !important;
    stroke: #94A3B8 !important;
}

[data-theme="dark"] [data-testid="stFileUploadDropzone"] button,
[data-theme="dark"] [data-testid="stFileUploader"] button,
[data-theme="dark"] [data-testid="stFileUploadDropzone"] [data-testid="baseButton-secondary"],
[data-theme="dark"] [data-testid="stFileUploadDropzone"] button[data-testid="baseButton-secondary"] {
    background-color: #1E293B !important;
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
}

[data-theme="dark"] [data-testid="stFileUploadDropzone"] button:hover {
    background-color: #334155 !important;
    border-color: #B3261E !important;
    color: #FFFFFF !important;
}

[data-theme="dark"] [data-testid="stFileUploaderFileData"],
[data-theme="dark"] [data-testid="stFileUploaderDeleteBtn"],
[data-theme="dark"] [data-testid="stFileUploaderFile"] {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
}

/* Dark Mode Text Area (Disabled OCR Stream & Normal) */
[data-theme="dark"] textarea,
[data-theme="dark"] textarea:disabled,
[data-theme="dark"] .stTextArea textarea,
[data-theme="dark"] .stTextArea textarea:disabled,
[data-theme="dark"] [data-baseweb="textarea"],
[data-theme="dark"] [data-baseweb="textarea"]:disabled,
[data-theme="dark"] [data-baseweb="base-input"],
[data-theme="dark"] [data-baseweb="base-input"]:disabled,
[data-theme="dark"] .stTextArea > div,
[data-theme="dark"] .stTextArea > div > div {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1px solid #1E2E4E !important;
    color: #E2E8F0 !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace !important;
    border-radius: 10px !important;
    -webkit-text-fill-color: #E2E8F0 !important;
    opacity: 1 !important;
}

/* Dark Mode Chat Input */
[data-theme="dark"] [data-testid="stChatInput"],
[data-theme="dark"] [data-testid="stChatInput"] > div,
[data-theme="dark"] [data-testid="stChatInputContainer"],
[data-theme="dark"] [data-testid="stBottomBlockContainer"] {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
}

[data-theme="dark"] [data-testid="stChatInput"] [data-baseweb="base-input"],
[data-theme="dark"] [data-testid="stChatInput"] [data-baseweb="input"],
[data-theme="dark"] [data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1.5px solid #1E2E4E !important;
    border-radius: 24px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
}

[data-theme="dark"] [data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    background: transparent !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border: none !important;
    font-size: 0.90rem !important;
    font-family: 'Inter', sans-serif !important;
}

[data-theme="dark"] [data-testid="stChatInput"] textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
}

[data-theme="dark"] [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #B3261E, #E11D48) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 50% !important;
    box-shadow: 0 2px 8px rgba(179, 38, 30, 0.4) !important;
}

[data-theme="dark"] [data-testid="stChatInput"] button svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
}

/* Dark Mode Chat Messages */
[data-theme="dark"] [data-testid="stChatMessage"],
[data-theme="dark"] .stChatMessage {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    margin-bottom: 8px !important;
}

[data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
[data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
[data-theme="dark"] [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em {
    color: #E2E8F0 !important;
}

/* Dark Mode Status Widget / Progress Spinners */
[data-theme="dark"] [data-testid="stStatusWidget"],
[data-theme="dark"] details[data-testid="stExpander"] {
    background-color: #111827 !important;
    background: #111827 !important;
    border: 1px solid #1E2E4E !important;
    color: #F8FAFC !important;
    border-radius: 12px !important;
}
[data-theme="dark"] [data-testid="stStatusWidget"] * {
    color: #F8FAFC !important;
}

/* Dark Mode Medication Dialog / Modal */
[data-theme="dark"] div[data-testid="stDialog"] > div,
[data-theme="dark"] div[role="dialog"],
[data-theme="dark"] [data-testid="stModal"] {
    background-color: #0B0F19 !important;
    background: #0B0F19 !important;
    border: 1.5px solid #1E2E4E !important;
    color: #F8FAFC !important;
    border-radius: 16px !important;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7) !important;
}
[data-theme="dark"] div[data-testid="stDialog"] header,
[data-theme="dark"] div[role="dialog"] header {
    background-color: #0B0F19 !important;
    color: #F8FAFC !important;
    border-bottom: 1px solid #1E293B !important;
}
[data-theme="dark"] div[data-testid="stDialog"] h1,
[data-theme="dark"] div[data-testid="stDialog"] h2,
[data-theme="dark"] div[data-testid="stDialog"] h3,
[data-theme="dark"] div[data-testid="stDialog"] p,
[data-theme="dark"] div[data-testid="stDialog"] span,
[data-theme="dark"] div[data-testid="stDialog"] li,
[data-theme="dark"] div[data-testid="stDialog"] b,
[data-theme="dark"] div[data-testid="stDialog"] strong,
[data-theme="dark"] div[data-testid="stDialog"] em {
    color: #F1F5F9 !important;
}
[data-theme="dark"] div[data-testid="stDialog"] code {
    background-color: #1E293B !important;
    color: #38BDF8 !important;
    padding: 3px 7px !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

/* Quick Question Chip buttons inside Dialog */
[data-theme="dark"] div[data-testid="stDialog"] .stButton > button,
[data-theme="dark"] .st-key-p2_quick_q_0 button,
[data-theme="dark"] .st-key-p2_quick_q_1 button,
[data-theme="dark"] .st-key-p2_quick_q_2 button {
    background-color: #162032 !important;
    background: #162032 !important;
    color: #94A3B8 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    padding: 6px 10px !important;
    transition: all 0.2s ease !important;
}

[data-theme="dark"] div[data-testid="stDialog"] .stButton > button:hover,
[data-theme="dark"] .st-key-p2_quick_q_0 button:hover,
[data-theme="dark"] .st-key-p2_quick_q_1 button:hover,
[data-theme="dark"] .st-key-p2_quick_q_2 button:hover {
    background-color: #1E293B !important;
    border-color: #3B82F6 !important;
    color: #60A5FA !important;
    transform: translateY(-1px) !important;
}

[data-theme="dark"] .stButton > button {
    background-color: #1E293B !important;
    border-color: #334155 !important;
    color: #F8FAFC !important;
}


[data-theme="dark"] .mm-btn-primary {
    background: linear-gradient(135deg, #B3261E 0%, #8C1F19 100%) !important;
    color: #ffffff !important;
}

[data-theme="dark"] header[data-testid="stHeader"] {
    background-color: #0B0F19 !important;
    border-bottom-color: #B3261E !important;
}

[data-theme="dark"] .stRadio label,
[data-theme="dark"] .stCheckbox label {
    color: #CBD5E1 !important;
}

[data-theme="dark"] .stTabs [data-baseweb="tab-list"] {
    background-color: #111827 !important;
    border-bottom-color: #1E293B !important;
}

[data-theme="dark"] .stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
}

[data-theme="dark"] .stTabs [aria-selected="true"] {
    color: #B3261E !important;
    border-bottom-color: #B3261E !important;
}

/* ============================================================
   ANIMATED SUN & MOON DAY/NIGHT TOGGLE SWITCH (BaseWeb & Streamlit)
   ============================================================ */
div[data-testid="stToggle"],
.stToggle {
    display: inline-flex !important;
    align-items: center !important;
}

div[data-testid="stToggle"] label,
div[data-testid="stToggle"] [data-baseweb="checkbox"],
.stToggle label,
.stToggle [data-baseweb="checkbox"] {
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
}

/* Switch Outer Track (Day / Sky Blue in Light Mode) */
div[data-testid="stToggle"] label > div:first-of-type,
div[data-testid="stToggle"] [data-baseweb="checkbox"] > div:first-of-type,
div[data-testid="stToggle"] div[data-testid="stToggleSwitch"],
.stToggle label > div:first-of-type,
.stToggle [data-baseweb="checkbox"] > div:first-of-type {
    width: 64px !important;
    height: 32px !important;
    min-width: 64px !important;
    border-radius: 30px !important;
    background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), 0 2px 10px rgba(56, 189, 248, 0.4) !important;
    position: relative !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    overflow: visible !important;
}

/* Cloud icon in Day mode */
div[data-testid="stToggle"] label > div:first-of-type::after,
div[data-testid="stToggle"] [data-baseweb="checkbox"] > div:first-of-type::after,
div[data-testid="stToggle"] div[data-testid="stToggleSwitch"]::after,
.stToggle label > div:first-of-type::after,
.stToggle [data-baseweb="checkbox"] > div:first-of-type::after {
    content: "" !important;
    position: absolute !important;
    right: 6px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    font-size: 13px !important;
    line-height: 1 !important;
    opacity: 0.95 !important;
    pointer-events: none !important;
}

/* Night / Starry Track when checked (Dark Mode) */
div[data-testid="stToggle"]:has(input:checked) label > div:first-of-type,
div[data-testid="stToggle"]:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type,
div[data-testid="stToggle"] input:checked + div,
.stToggle:has(input:checked) label > div:first-of-type,
.stToggle:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type {
    background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5), 0 2px 10px rgba(99, 102, 241, 0.4) !important;
}

/* Star icon in Night mode */
div[data-testid="stToggle"]:has(input:checked) label > div:first-of-type::after,
div[data-testid="stToggle"]:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type::after,
div[data-testid="stToggle"] input:checked + div::after,
.stToggle:has(input:checked) label > div:first-of-type::after,
.stToggle:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type::after {
    content: "" !important;
    left: 7px !important;
    right: auto !important;
    font-size: 12px !important;
    line-height: 1 !important;
    opacity: 0.95 !important;
    pointer-events: none !important;
}

/* Sun Thumb (Light Mode) */
div[data-testid="stToggle"] label > div:first-of-type > div,
div[data-testid="stToggle"] [data-baseweb="checkbox"] > div:first-of-type > div,
div[data-testid="stToggle"] div[data-testid="stToggleSwitch"] > div,
.stToggle label > div:first-of-type > div,
.stToggle [data-baseweb="checkbox"] > div:first-of-type > div {
    width: 24px !important;
    height: 24px !important;
    border-radius: 50% !important;
    background: #FBBF24 !important;
    background-image: radial-gradient(circle at 35% 35%, #FEF08A 0%, #F59E0B 100%) !important;
    box-shadow: 0 0 10px #F59E0B, inset -1px -1px 2px rgba(0,0,0,0.2) !important;
    transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    position: relative !important;
    top: 2.5px !important;
    left: 3px !important;
}

/* Moon Thumb (Dark Mode) */
div[data-testid="stToggle"]:has(input:checked) label > div:first-of-type > div,
div[data-testid="stToggle"]:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type > div,
div[data-testid="stToggle"] input:checked + div > div,
.stToggle:has(input:checked) label > div:first-of-type > div,
.stToggle:has(input:checked) [data-baseweb="checkbox"] > div:first-of-type > div {
    background: #E2E8F0 !important;
    background-image: radial-gradient(circle at 35% 35%, #FFFFFF 0%, #94A3B8 100%) !important;
    box-shadow: 0 0 12px rgba(226, 232, 240, 0.8), inset -2px -2px 3px rgba(0,0,0,0.3) !important;
    transform: translateX(31px) !important;
}

/* Global resets & typography */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--mm-bg-base) !important;
    color: var(--mm-text-primary) !important;
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.3s ease, color 0.3s ease !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Manrope', 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: var(--mm-text-primary) !important;
    letter-spacing: -0.02em;
}

/* Hairline Top Brand Accent Bar */
header[data-testid="stHeader"] {
    background-color: var(--mm-bg-surface) !important;
    border-bottom: 2px solid var(--mm-brand-primary) !important;
    display: flex !important;
    align-items: center !important;
    z-index: 9999 !important;
}

/* Hide Streamlit deploy button, hamburger menu & cloud badges (Preserve header & sidebar controls) */
#MainMenu, footer, .stDeployButton, .stAppDeployButton, [data-testid="stAppDeployButton"], button[data-testid="stAppDeployButton"], .viewerBadge_container__r5tak, .viewerBadge_link__qRIco, div[class*="viewerBadge"], [data-testid="stStatusWidget"] { 
    display: none !important; 
    visibility: hidden !important; 
}

/* ==========================================================================
   1B. EQUAL HEIGHT CARDS & FLEX COLUMN ALIGNMENT IN ROWS
   When cards sit in columns (e.g. 3 cards in a row), all cards stretch to equal height.
   ========================================================================== */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}

[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 100% !important;
    height: 100% !important;
}

[data-testid="stHorizontalBlock"] > div[data-testid="column"] .mm-card {
    flex: 1 1 100% !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-sizing: border-box !important;
}

/* ==========================================================================
   1C. MULTI-COLUMN & RESPONSIVE LAYOUT SYSTEM
   ========================================================================== */

/* Button Groups & Chips wrap as an inline tag cloud */
[data-testid="stHorizontalBlock"]:has(.stButton),
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-pop_sym_chip_"]),
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-chip_"]),
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-p2_quick_q_"]),
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-qa_"]),
[data-testid="stHorizontalBlock"].mm-keep-horizontal {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 8px !important;
    width: 100% !important;
    overflow-x: visible !important;
}

[data-testid="stHorizontalBlock"]:has(.stButton) > div[data-testid="column"],
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-pop_sym_chip_"]) > div[data-testid="column"],
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-chip_"]) > div[data-testid="column"],
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-p2_quick_q_"]) > div[data-testid="column"],
[data-testid="stHorizontalBlock"]:has(div[class*="st-key-qa_"]) > div[data-testid="column"],
[data-testid="stHorizontalBlock"].mm-keep-horizontal > div[data-testid="column"] {
    flex: 0 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
}

/* Ensure chips display neatly as rounded pill chips with proper padding and no broken text */
div[class*="st-key-pop_sym_chip_"] button,
div[class*="st-key-chip_"] button,
div[class*="st-key-p2_quick_q_"] button {
    white-space: nowrap !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    font-size: 0.82rem !important;
    min-height: 38px !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Responsive behavior on mobile screens (< 768px) */
@media (max-width: 767px) {
    /* 1. Large major cards (File uploaders, OCR textareas, data cards, charts, bordered containers) stack vertically at FULL 100% WIDTH */
    [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"]),
    [data-testid="stHorizontalBlock"]:has(.stFileUploader),
    [data-testid="stHorizontalBlock"]:has(.stTextArea),
    [data-testid="stHorizontalBlock"]:has(.stPlotlyChart) {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: wrap !important;
        gap: 16px !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"]) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"]) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.stFileUploader) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has(.stFileUploader) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.stTextArea) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has(.stTextArea) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.stPlotlyChart) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has(.stPlotlyChart) > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        box-sizing: border-box !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    /* 2. Compact form input rows (Demographics 3-columns or 2-columns) fit neatly side-by-side */
    [data-testid="stHorizontalBlock"]:not(:has([data-testid="stVerticalBlockBorderWrapper"])):not(:has(.stFileUploader)):not(:has(.stTextArea)):not(:has(.stButton)):not(:has(iframe)) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"]:not(:has([data-testid="stVerticalBlockBorderWrapper"])):not(:has(.stFileUploader)):not(:has(.stTextArea)):not(:has(.stButton)):not(:has(iframe)) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:not(:has([data-testid="stVerticalBlockBorderWrapper"])):not(:has(.stFileUploader)):not(:has(.stTextArea)):not(:has(.stButton)):not(:has(iframe)) > [data-testid="stColumn"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        max-width: none !important;
    }

    /* Radio options wrap cleanly and don't get truncated */
    .stRadio div[role="radiogroup"] label {
        white-space: normal !important;
        word-break: break-word !important;
    }

    /* Integrated major disease selector row inside Clinical Symptoms */
    [data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_add_major_dis_syms"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_add_major_dis_syms"]) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_add_major_dis_syms"]) > [data-testid="stColumn"] {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    /* Compact form inputs & labels on phone */
    .stTextInput label,
    .stSelectbox label,
    .stMultiSelect label,
    .stRadio label,
    .stSlider label,
    .stFileUploader label,
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {
        font-size: 0.74rem !important;
        margin-bottom: 2px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .stTextInput input,
    [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div:first-child {
        font-size: 0.76rem !important;
        min-height: 34px !important;
        height: 34px !important;
        padding: 0 6px !important;
    }
    /* Proper height and padding for multi-line textareas (OCR stream, notes) */
    .stTextArea textarea {
        font-size: 0.82rem !important;
        min-height: 150px !important;
        height: auto !important;
        line-height: 1.45 !important;
        padding: 8px 10px !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] input {
        font-size: 0.76rem !important;
    }
    [data-baseweb="select"] svg {
        width: 14px !important;
        height: 14px !important;
    }

    /* Extra bottom clearance so floating emergency cross does not cover footer */
    .main .block-container,
    .stMainBlockContainer {
        padding-bottom: 72px !important;
    }
}

/* ==========================================================================
   2. SIDEBAR - TOGGLE BUTTONS & NAVIGATION PANEL
   ========================================================================== */

/* All Sidebar Open / Expand Toggle Controls */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
header button[kind="header"],
header button[kind="headerNoPadding"],
header button[data-testid*="Collapse"],
header button[data-testid*="Expand"],
header [data-testid="stSidebarNavCollapseButton"] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #B3261E !important;
    background-color: rgba(179, 38, 30, 0.08) !important;
    border: 1px solid rgba(179, 38, 30, 0.3) !important;
    border-radius: 6px !important;
    margin-left: 8px !important;
}

[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
header button[kind="header"] svg,
header button[kind="headerNoPadding"] svg {
    fill: #B3261E !important;
    color: #B3261E !important;
    width: 22px !important;
    height: 22px !important;
}

/* Sidebar Close Button inside Dark Sidebar */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button {
    color: #F8FAFC !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] svg {
    fill: #F8FAFC !important;
    color: #F8FAFC !important;
    width: 22px !important;
    height: 22px !important;
}

[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
    padding-top: 1rem !important;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] b {
    color: #F8FAFC !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #94A3B8 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* Sidebar Selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: var(--mm-radius-md) !important;
    color: #F8FAFC !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #94A3B8 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #F8FAFC !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #F8FAFC !important;
    font-weight: 500 !important;
}

/* Sidebar Radio Navigation Cards */
[data-testid="stSidebar"] [data-testid="stRadio"],
[data-testid="stSidebar"] .stRadio,
[data-testid="stSidebar"] div[role="radiogroup"] {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #141D2E !important;
    border: 1.2px solid #23324D !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    box-sizing: border-box !important;
    min-height: 44px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #1E293B !important;
    border-color: #38BDF8 !important;
    transform: translateX(3px) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(179, 38, 30, 0.35) 0%, rgba(225, 29, 72, 0.18) 100%) !important;
    border-left: 5px solid #B3261E !important;
    border-color: #B3261E !important;
    box-shadow: 0 4px 14px rgba(179, 38, 30, 0.30) !important;
}

/* Hide native radio input and SVG circle icon */
[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
    display: none !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label svg {
    display: none !important;
}

/* Hide radio circle dot wrapper (only when there are multiple child divs) */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child:not(:last-child) {
    display: none !important;
}

/* Text visibility inside sidebar navigation */
[data-testid="stSidebar"] div[role="radiogroup"] label,
[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] div[role="radiogroup"] label p,
[data-testid="stSidebar"] div[role="radiogroup"] label span,
[data-testid="stSidebar"] div[role="radiogroup"] label div {
    color: #F8FAFC !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Keep the theme toggle visually consistent with the rest of the
   sidebar (was floating with no card/spacing around it). */
[data-testid="stSidebar"] [data-testid="stToggle"] {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    padding: 8px 10px !important;
    width: 100% !important;
    margin-bottom: 6px !important;
}

[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 4px !important;
}

/* ==========================================================================
   3. STREAMLIT FORM CONTROLS & WIDGET RESTYLING
   ========================================================================== */

/* Buttons */
.stButton > button,
button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background-color: var(--mm-brand-primary) !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border: 1px solid var(--mm-brand-primary) !important;
    border-radius: var(--mm-radius-md) !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 1px 3px rgba(179, 38, 30, 0.25) !important;
    transition: all 0.18s ease-in-out !important;
}

.stButton > button:hover,
button[kind="primary"]:hover {
    background-color: var(--mm-brand-hover) !important;
    border-color: var(--mm-brand-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 10px rgba(179, 38, 30, 0.3) !important;
}

.stButton > button:active,
button[kind="primary"]:active {
    background-color: var(--mm-brand-active) !important;
    transform: translateY(0px) !important;
}

.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: var(--mm-brand-primary) !important;
    border: 1.5px solid var(--mm-brand-primary) !important;
    border-radius: var(--mm-radius-md) !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.18s ease !important;
}

.stDownloadButton > button:hover {
    background-color: var(--mm-brand-subtle) !important;
    color: var(--mm-brand-hover) !important;
    transform: translateY(-1px) !important;
}

/* Equal Action & Hospital Card Action Buttons */
div[data-testid="stColumn"] div[data-testid="stButton"] button,
div[data-testid="stColumn"] div[data-testid="stDownloadButton"] button,
div[data-testid="stColumn"] .stButton > button,
div[data-testid="stColumn"] .stDownloadButton > button,
div[data-testid="stColumn"] div[data-testid="stLinkButton"] a {
    min-height: 38px !important;
    height: 38px !important;
    max-height: 38px !important;
    padding: 0 12px !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    box-sizing: border-box !important;
    text-decoration: none !important;
    width: 100% !important;
    line-height: 1 !important;
}

div[data-testid="stColumn"] div[data-testid="stLinkButton"] a {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border: 1.5px solid #CBD5E1 !important;
}

div[data-testid="stColumn"] div[data-testid="stLinkButton"] a:hover {
    background-color: #F1F5F9 !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
    transform: translateY(-1px) !important;
}

/* -- Verified Healthcare Facility Card -- */
.mm-hospital-card {
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    min-height: 190px !important;
    height: 190px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
    overflow: hidden !important;
}

.mm-hospital-card:hover {
    border-color: #CBD5E1 !important;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08) !important;
}

/* Form Field Labels */
.stTextInput label,
.stSelectbox label,
.stMultiSelect label,
.stSlider label,
.stFileUploader label,
.stTextArea label {
    font-size: 0.84rem !important;
    color: #475569 !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
    letter-spacing: 0.01em !important;
}

/* Text Inputs, Selectboxes, Multiselects & Textareas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
[data-baseweb="select"] > div {
    background-color: var(--mm-bg-surface) !important;
    border: 1.5px solid var(--mm-border-color) !important;
    border-radius: 8px !important;
    color: var(--mm-text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 2px 6px !important;
}

/* Conditions Multiselect Custom Dropdown Styling */
div[class*="st-key-selected_conditions_widget"] input {
    caret-color: transparent !important;
    cursor: pointer !important;
}
div[class*="st-key-selected_conditions_widget"] input::placeholder {
    color: transparent !important;
    opacity: 0 !important;
}

/* Header Compact Pill Language Dropdown (Rounded on Both Sides) */
div[class*="st-key-hdr_lang_"] [data-baseweb="select"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[class*="st-key-hdr_lang_"] [data-baseweb="select"] > div {
    border-radius: 9999px !important;
    min-height: 36px !important;
    height: 36px !important;
    font-size: 0.82rem !important;
    padding: 0 10px 0 14px !important;
    border: 1.5px solid var(--mm-border-color) !important;
    background: var(--mm-bg-surface) !important;
    color: var(--mm-text-primary) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    display: flex !important;
    align-items: center !important;
}

div[class*="st-key-hdr_lang_"] [data-baseweb="select"] span {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--mm-text-primary) !important;
}

div[class*="st-key-hdr_lang_"] {
    width: 100% !important;
    max-width: 160px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}
div[class*="st-key-hdr_lang_"] .stSelectbox {
    margin: 0 !important;
    padding: 0 !important;
}

/* Modal Dialog Horizontal Large Layout */
div[data-testid="stDialog"] > div[role="dialog"],
div[role="dialog"] {
    max-width: 880px !important;
    width: min(880px, 92vw) !important;
    border-radius: 20px !important;
    padding: 24px 28px !important;
    background: var(--mm-bg-surface) !important;
    border: 1.5px solid var(--mm-border-color) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35) !important;
}

.mm-badge-online-pill {
    background: #F0FDF4 !important;
    color: #166534 !important;
    border: 1.5px solid #DCFCE7 !important;
    border-radius: 9999px !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    padding: 0 14px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    white-space: nowrap !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    height: 36px !important;
    line-height: 36px !important;
    box-sizing: border-box !important;
}

/* Unified Top Header Card Container */
div[class*="st-key-mm_top_header_card"] {
    background: var(--mm-bg-surface) !important;
    border: 1.5px solid var(--mm-border-color) !important;
    border-radius: 20px !important;
    padding: 20px 28px !important;
    box-shadow: var(--mm-shadow-card) !important;
    margin-bottom: 20px !important;
    min-height: 92px !important;
    display: flex !important;
    align-items: center !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 14px !important;
    width: 100% !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stColumn"],
div[class*="st-key-mm_top_header_card"] [data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: stretch !important;
    margin: auto 0 !important;
    padding: 0 !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stVerticalBlockBorderWrapper"],
div[class*="st-key-mm_top_header_card"] [data-testid="stColumn"] > div,
div[class*="st-key-mm_top_header_card"] [data-testid="column"] > div {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: stretch !important;
    height: 100% !important;
    margin: auto 0 !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stColumn"] [data-testid="stVerticalBlock"],
div[class*="st-key-mm_top_header_card"] [data-testid="column"] [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    height: 100% !important;
    gap: 0 !important;
    padding: 0 !important;
    margin: auto 0 !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"],
div[class*="st-key-mm_top_header_card"] [data-testid="column"]:first-child [data-testid="stVerticalBlock"] {
    align-items: flex-start !important;
    justify-content: center !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="element-container"],
div[class*="st-key-mm_top_header_card"] .element-container {
    margin: auto 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stColumn"]:first-child [data-testid="element-container"],
div[class*="st-key-mm_top_header_card"] [data-testid="column"]:first-child [data-testid="element-container"] {
    justify-content: flex-start !important;
}

div[class*="st-key-mm_top_header_card"] [data-testid="stCustomComponentV1"],
div[class*="st-key-hdr_sun_moon_"] [data-testid="stCustomComponentV1"],
div[class*="st-key-hdr_sun_moon_"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 38px !important;
    min-height: 38px !important;
    max-height: 38px !important;
    width: 100% !important;
    margin: auto 0 !important;
    padding: 0 !important;
}

div[class*="st-key-mm_top_header_card"] iframe,
div[class*="st-key-hdr_sun_moon_"] iframe {
    height: 38px !important;
    min-height: 38px !important;
    max-height: 38px !important;
    border: none !important;
    display: block !important;
    margin: auto !important;
    padding: 0 !important;
    vertical-align: middle !important;
}

@media (max-width: 767px) {
    div[class*="st-key-mm_top_header_card"] {
        padding: 14px 16px !important;
        border-radius: 16px !important;
        margin-bottom: 14px !important;
    }
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 10px 8px !important;
        width: 100% !important;
    }
    /* Row 1: Title & Icon takes full width */
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
        margin-bottom: 4px !important;
    }
    div[class*="st-key-mm_top_header_card"] img {
        width: 44px !important;
        height: 44px !important;
        padding: 4px !important;
        border-radius: 12px !important;
        flex-shrink: 0 !important;
    }
    div[class*="st-key-mm_top_header_card"] div[style*="font-size: 1.45rem"] {
        font-size: 1.15rem !important;
        line-height: 1.25 !important;
        font-weight: 800 !important;
    }
    div[class*="st-key-mm_top_header_card"] div[style*="font-size: 0.85rem"] {
        font-size: 0.76rem !important;
        line-height: 1.2 !important;
        margin-top: 2px !important;
        display: block !important;
    }

    /* Row 2: Controls row (Badge on left, Language & Theme Switch on right) */
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2),
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    div[class*="st-key-mm_top_header_card"] .mm-badge,
    div[class*="st-key-mm_top_header_card"] .mm-badge-brand,
    div[class*="st-key-mm_top_header_card"] .mm-badge-online-pill {
        font-size: 0.70rem !important;
        font-weight: 700 !important;
        padding: 0 10px !important;
        height: 34px !important;
        line-height: 34px !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
    }

    /* Language selector - pushed to the right alongside theme toggle */
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3),
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
        flex: 0 0 86px !important;
        width: 86px !important;
        min-width: 86px !important;
        margin-left: auto !important;
    }
    div[class*="st-key-mm_top_header_card"] .stSelectbox [data-baseweb="select"] > div:first-child {
        min-height: 34px !important;
        height: 34px !important;
        padding: 0 6px !important;
        font-size: 0.78rem !important;
    }

    /* Sun / Moon switch - full 78px width to match 76px custom toggle widget */
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4),
    div[class*="st-key-mm_top_header_card"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) {
        flex: 0 0 78px !important;
        width: 78px !important;
        min-width: 78px !important;
    }
    div[class*="st-key-mm_top_header_card"] [data-testid="stCustomComponentV1"],
    div[class*="st-key-mm_top_header_card"] iframe {
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        width: 78px !important;
        min-width: 78px !important;
        border: none !important;
        display: block !important;
        margin: 0 auto !important;
    }
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
[data-baseweb="select"]:focus-within > div {
    border-color: #B3261E !important;
    box-shadow: 0 0 0 3.5px rgba(179, 38, 30, 0.12) !important;
}

/* Read-only & Disabled Text Areas for OCR Stream */
.stTextArea textarea:disabled,
.stTextArea textarea[disabled],
[data-baseweb="textarea"] textarea:disabled,
[data-baseweb="textarea"] textarea[disabled] {
    opacity: 1 !important;
    cursor: text !important;
    user-select: text !important;
    -webkit-text-fill-color: var(--mm-text-primary) !important;
    color: var(--mm-text-primary) !important;
    background-color: rgba(248, 250, 252, 0.7) !important;
    border-color: #CBD5E1 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.84rem !important;
    line-height: 1.5 !important;
}
[data-theme="dark"] .stTextArea textarea:disabled,
[data-theme="dark"] .stTextArea textarea[disabled],
[data-dark-mode="true"] .stTextArea textarea:disabled,
[data-dark-mode="true"] .stTextArea textarea[disabled] {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border-color: #1E2E4E !important;
}

/* Multiselect Tag Chips */
[data-baseweb="tag"] {
    background-color: var(--mm-brand-subtle) !important;
    border: 1px solid rgba(179, 38, 30, 0.3) !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
}

[data-baseweb="tag"] span {
    color: var(--mm-brand-primary) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* Sliders */
.stSlider div[data-baseweb="slider"] div[role="slider"] {
    background-color: var(--mm-brand-primary) !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 0 0 2px var(--mm-brand-primary) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid var(--mm-border-color) !important;
    gap: 8px !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    flex-wrap: nowrap !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    position: relative !important;
    max-width: 100% !important;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: var(--mm-text-secondary) !important;
    padding: 10px 18px !important;
    border-radius: var(--mm-radius-md) var(--mm-radius-md) 0 0 !important;
    transition: all 0.18s ease !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    min-height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--mm-brand-primary) !important;
    background-color: rgba(179, 38, 30, 0.04) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--mm-brand-primary) !important;
    border-bottom: 3px solid var(--mm-brand-primary) !important;
}

@media (max-width: 767px) {
    .stTabs [data-baseweb="tab-list"] {
        padding-bottom: 2px !important;
        mask-image: linear-gradient(to right, black calc(100% - 28px), transparent 100%);
        -webkit-mask-image: linear-gradient(to right, black calc(100% - 28px), transparent 100%);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 0.82rem !important;
        min-height: 44px !important;
    }
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: var(--mm-bg-surface) !important;
    border: 1px solid var(--mm-border-color) !important;
    border-radius: var(--mm-radius-lg) !important;
    padding: 16px 20px !important;
    box-shadow: var(--mm-shadow-subtle) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--mm-text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.03em !important;
}

[data-testid="stMetricValue"] {
    color: var(--mm-text-primary) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: var(--mm-bg-surface) !important;
    border: 1px solid var(--mm-border-color) !important;
    border-radius: var(--mm-radius-md) !important;
    font-weight: 600 !important;
    color: var(--mm-text-primary) !important;
    padding: 12px 18px !important;
}

.streamlit-expanderContent {
    background-color: var(--mm-bg-surface) !important;
    border: 1px solid var(--mm-border-color) !important;
    border-top: none !important;
    border-radius: 0 0 var(--mm-radius-md) var(--mm-radius-md) !important;
    padding: 18px !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background-color: var(--mm-bg-surface) !important;
    border: 1.5px dashed var(--mm-border-color) !important;
    border-radius: var(--mm-radius-lg) !important;
    padding: 16px !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--mm-brand-primary) !important;
}

/* ==========================================================================
   4. CUSTOM ENTERPRISE CLINICAL CARDS & UI COMPONENTS (.mm-*)
   ========================================================================== */

/* Top Breadcrumb / Header Bar */
.mm-header-bar {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 16px;
    padding: 16px 22px;
    margin-bottom: 20px;
    box-shadow: var(--mm-shadow-card);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.mm-header-title {
    margin: 0;
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--mm-text-primary);
    display: flex;
    align-items: center;
    gap: 10px;
}

.mm-header-subtitle {
    margin: 4px 0 0 0;
    font-size: 0.88rem;
    color: var(--mm-text-secondary);
}

/* -- Modern Stepper Component -- */
.mm-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 16px;
    padding: 14px 24px;
    margin-bottom: 22px;
    box-shadow: var(--mm-shadow-subtle);
}

.mm-step-item {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    flex: 1;
}

.mm-step-num {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    font-weight: 800;
    background: rgba(59, 130, 246, 0.12);
    color: #3B82F6;
    border: 1.5px solid rgba(59, 130, 246, 0.3);
    flex-shrink: 0;
    transition: all 0.2s ease;
}

.mm-step-num.active {
    background: linear-gradient(135deg, #B3261E 0%, #E11D48 100%);
    color: #FFFFFF;
    border-color: #B3261E;
    box-shadow: 0 4px 12px rgba(225, 29, 72, 0.35);
}

.mm-step-num.done {
    background: #10B981;
    color: #FFFFFF;
    border-color: #059669;
}

.mm-step-text-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--mm-text-primary);
    line-height: 1.2;
}

.mm-step-text-title.active {
    color: #B3261E;
}

.mm-step-text-sub {
    font-size: 0.74rem;
    color: var(--mm-text-secondary);
    margin-top: 2px;
}

.mm-step-arrow {
    color: var(--mm-text-muted);
    font-size: 1.1rem;
    padding: 0 12px;
    flex-shrink: 0;
}

@media (max-width: 767px) {
    .mm-stepper {
        padding: 8px 10px !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        gap: 4px !important;
        justify-content: space-between !important;
        scrollbar-width: none !important;
        margin-bottom: 14px !important;
    }
    .mm-stepper::-webkit-scrollbar {
        display: none !important;
    }
    .mm-step-item {
        flex: 1 1 auto !important;
        gap: 5px !important;
        min-width: 0 !important;
    }
    .mm-step-text-sub {
        display: none !important;
    }
    .mm-step-text-title {
        font-size: 0.72rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .mm-step-num {
        width: 24px !important;
        height: 24px !important;
        font-size: 0.75rem !important;
        flex-shrink: 0 !important;
    }
    .mm-step-arrow {
        font-size: 0.70rem !important;
        padding: 0 2px !important;
        flex-shrink: 0 !important;
    }
}

/* -- Panel Card Surface -- */
.mm-card {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 20px;
    box-shadow: var(--mm-shadow-card);
    color: var(--mm-text-primary);
}

.mm-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1.5px solid var(--mm-border-color);
}

.mm-card-title {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--mm-text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* -- Panel 1 Robot Assistant Widget Card -- */
.mm-robot-card {
    background: linear-gradient(145deg, #0A1128 0%, #101F42 60%, #0F172A 100%);
    border: 1.5px solid #1E293B;
    border-radius: 18px;
    padding: 20px;
    color: #FFFFFF;
    margin-bottom: 18px;
    box-shadow: 0 12px 30px rgba(10, 17, 40, 0.4);
    position: relative;
    overflow: hidden;
}

.mm-robot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.mm-speech-bubble {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 14px 16px;
    color: #F1F5F9;
    font-size: 0.85rem;
    line-height: 1.45;
    margin: 12px 0 16px 0;
    backdrop-filter: blur(8px);
}

/* -- Quick Action Cards -- */
.mm-quick-action-item {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
    cursor: pointer;
    text-decoration: none;
    color: var(--mm-text-primary);
}

.mm-quick-action-item:hover {
    border-color: #3B82F6;
    background: var(--mm-border-light);
    transform: translateX(3px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}

/* -- Document Type Pill Selector (Panel 2) -- */
.mm-doc-selector-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}

.mm-doc-pill {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 14px;
    padding: 14px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    color: var(--mm-text-primary);
}

.mm-doc-pill.active {
    border-color: #B3261E;
    background: var(--mm-brand-subtle);
    box-shadow: 0 0 0 2px rgba(179, 38, 30, 0.2);
}

/* -- OCR Text Stream Box -- */
.mm-ocr-box {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 12px;
    padding: 14px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.82rem;
    color: var(--mm-text-primary);
    line-height: 1.5;
    min-height: 180px;
}

/* -- BioPortal Ontology Badges -- */
.mm-ontology-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    margin-top: 12px;
}

.mm-ontology-pill {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--mm-text-primary);
}

/* -- Facility / Hospital Cards Grid (Panel 3) -- */
.mm-hospital-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 14px;
}

.mm-hospital-card {
    background: var(--mm-bg-surface);
    border: 1.5px solid var(--mm-border-color);
    border-radius: 14px;
    padding: 16px;
    box-shadow: var(--mm-shadow-card);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease;
    color: var(--mm-text-primary);
}

.mm-hospital-card:hover {
    border-color: #B3261E;
    transform: translateY(-2px);
    box-shadow: var(--mm-shadow-hover);
}

/* -- Trust & Compliance Bottom Footer Bar -- */
.mm-footer-trust-bar {
    background: var(--mm-bg-surface);
    border: 1.2px solid var(--mm-border-color);
    border-radius: 12px;
    padding: 12px 24px;
    margin-top: 24px;
    margin-bottom: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
    color: var(--mm-text-secondary);

    width: 100%;
}
.mm-footer-trust-items {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 20px;
    width: 100%;
}
.mm-trust-item {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.80rem;
    color: #475569;
    font-weight: 600;
    letter-spacing: 0.01em;
}
.mm-trust-icon {
    font-size: 0.90rem;
}
.mm-trust-dot {
    color: #CBD5E1;
    font-size: 0.75rem;
}

/* -- Panel 1 Form & Tool Box Polish -- */
.st-key-btn_describe_words button {
    background: #FFFFFF !important;
    color: #3B82F6 !important;
    border: 1.5px solid #BFDBFE !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    height: 42px !important;
    min-height: 42px !important;
    padding: 0 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.st-key-btn_describe_words button:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
    color: #1D4ED8 !important;
}

/* Popular Symptoms Pills */
.st-key-pop_btn_0 button, .st-key-pop_btn_1 button, .st-key-pop_btn_2 button, .st-key-pop_btn_3 button,
.st-key-pop_btn_4 button, .st-key-pop_btn_5 button, .st-key-pop_btn_6 button, .st-key-pop_btn_7 button {
    background: #F8FAFC !important;
    color: #1E293B !important;
    border: 1.2px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 4px 10px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    min-height: 32px !important;
    height: 32px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
}

.st-key-pop_btn_0 button:hover, .st-key-pop_btn_1 button:hover, .st-key-pop_btn_2 button:hover, .st-key-pop_btn_3 button:hover,
.st-key-pop_btn_4 button:hover, .st-key-pop_btn_5 button:hover, .st-key-pop_btn_6 button:hover, .st-key-pop_btn_7 button:hover {
    background: #EFF6FF !important;
    border-color: #3B82F6 !important;
    color: #1D4ED8 !important;
    transform: translateY(-1px) !important;
}

/* Clear All Button */
.st-key-clear_all_sym_btn button {
    background: #FFF1F2 !important;
    color: #E11D48 !important;
    border: 1px solid #FFE4E6 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    padding: 4px 10px !important;
    min-height: 30px !important;
    height: 30px !important;
    box-shadow: none !important;
}

/* Previous Navigation Button */
.st-key-p1_prev_btn button {
    background: #FFFFFF !important;
    color: #475569 !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

.st-key-p1_prev_btn button:hover {
    background: #F1F5F9 !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}

/* Quick Actions List Items */
.st-key-qa_upload_presc button,
.st-key-qa_find_hosp button,
.st-key-qa_health_tips button {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important;
    text-align: left !important;
    padding: 12px 14px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    min-height: 54px !important;
    height: auto !important;
    margin-bottom: 8px !important;
    line-height: 1.35 !important;
    transition: all 0.2s ease !important;
}

.st-key-qa_upload_presc button:hover,
.st-key-qa_find_hosp button:hover,
.st-key-qa_health_tips button:hover {
    background: #F8FAFC !important;
    border-color: #3B82F6 !important;
    color: #1D4ED8 !important;
    transform: translateX(2px) !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.12) !important;
}

/* Badges & Status Pills */
.mm-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.mm-badge-brand {
    background-color: var(--mm-brand-subtle);
    color: var(--mm-brand-primary);
    border: 1px solid var(--mm-brand-border);
}

.mm-badge-critical {
    background-color: var(--mm-status-critical-bg);
    color: var(--mm-status-critical);
    border: 1px solid #F5C6CB;
}

.mm-badge-warning {
    background-color: var(--mm-status-warning-bg);
    color: var(--mm-status-warning);
    border: 1px solid #FFEBAA;
}

.mm-badge-success {
    background-color: var(--mm-status-success-bg);
    color: var(--mm-status-success);
    border: 1px solid #C3E6CB;
}

.mm-badge-info {
    background-color: var(--mm-status-info-bg);
    color: var(--mm-status-info);
    border: 1px solid #B8DAFF;
}

/* Clinical Alert Banners */
.mm-alert-banner {
    border-radius: var(--mm-radius-lg);
    padding: 16px 20px;
    margin: 18px 0;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.mm-alert-critical {
    background-color: var(--mm-status-critical-bg);
    border: 1px solid #F5C6CB;
    border-left: 5px solid var(--mm-status-critical);
    color: #721C24;
}

.mm-alert-warning {
    background-color: var(--mm-status-warning-bg);
    border: 1px solid #FFEBAA;
    border-left: 5px solid var(--mm-status-warning);
    color: #856404;
}

.mm-alert-info {
    background-color: var(--mm-status-info-bg);
    border: 1px solid #B8DAFF;
    border-left: 5px solid var(--mm-status-info);
    color: #004085;
}

/* Sidebar Brand Card */
.mm-sidebar-brand {
    background: linear-gradient(180deg, rgba(179, 38, 30, 0.15) 0%, rgba(17, 24, 39, 0) 100%);
    border: 1px solid rgba(179, 38, 30, 0.3);
    border-radius: var(--mm-radius-lg);
    padding: 18px;
    margin-bottom: 20px;
    text-align: center;
}

.mm-sidebar-trust {
    background: #1A2234;
    border: 1px solid #28334E;
    border-radius: var(--mm-radius-md);
    padding: 14px;
    font-size: 0.8rem;
    color: #9CA3AF;
    line-height: 1.4;
    margin-top: 24px;
}

/* Section Header Typography */
.mm-section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--mm-text-primary);
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1.5px solid var(--mm-border-color);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Context Chip */
.mm-chip {
    display: inline-block;
    background: #F1F3F6;
    color: var(--mm-text-secondary);
    font-size: 0.82rem;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 4px;
    margin-right: 6px;
}
</style>
"""
DARK_CSS_OVERRIDE = """
<style>
/* ============================================================
   MEDIMIND AI -- COMPLETE CLINICAL DARK MODE SYSTEM OVERRIDE
   ============================================================ */

/* -- 1. Root Variable Tokens for Dark Mode -- */
:root {
    --mm-brand-primary: #B3261E !important;
    --mm-brand-hover: #D32F2F !important;
    --mm-brand-active: #991B1B !important;
    --mm-brand-subtle: #2D1B1A !important;
    --mm-brand-border: #4A1C1A !important;

    --mm-bg-base: #0B0F19 !important;
    --mm-bg-surface: #111827 !important;
    --mm-bg-sidebar: #070B14 !important;

    --mm-text-primary: #F8FAFC !important;
    --mm-text-secondary: #94A3B8 !important;
    --mm-text-muted: #64748B !important;

    --mm-border-color: #1E293B !important;
    --mm-border-light: #162032 !important;

    --mm-status-critical: #EF4444 !important;
    --mm-status-critical-bg: #2D1215 !important;
    --mm-status-warning: #F59E0B !important;
    --mm-status-warning-bg: #2D1C00 !important;
    --mm-status-success: #22C55E !important;
    --mm-status-success-bg: #0F2D1E !important;
    --mm-status-info: #38BDF8 !important;
    --mm-status-info-bg: #0D1F3C !important;

    --mm-shadow-subtle: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    --mm-shadow-card: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
    --mm-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.65) !important;
}

/* -- 2. Core App Background & Base Layout -- */
html, body, .stApp, section.main, .stMainBlockContainer, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], .block-container {
    background-color: #0B0F19 !important;
    background: #0B0F19 !important;
    color: #F8FAFC !important;
}

/* -- 3. Typography & Global Elements -- */
h1, h2, h3, h4, h5, h6, b, strong, .mm-card-title, .mm-step-text-title, .mm-header-title {
    color: #F8FAFC !important;
}
p, span, div {
    color: #CBD5E1 !important;
}
.mm-section-header {
    color: #F8FAFC !important;
    border-bottom-color: #1E293B !important;
}
.mm-header-subtitle,
.mm-step-text-sub {
    color: #94A3B8 !important;
}

/* -- 4. Top Header Cards (All Panels) -- */
div[class*="st-key-mm_top_header_card"] {
    background: #111827 !important;
    background-color: #111827 !important;
    border-color: #1E293B !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
}
div[class*="st-key-mm_top_header_card"] div {
    color: #F8FAFC !important;
}
div[class*="st-key-mm_top_header_card"] .mm-badge-brand {
    background: #2D1215 !important;
    color: #F87171 !important;
    border-color: #4A1A1E !important;
}
div[class*="st-key-mm_top_header_card"] .mm-badge-online-pill {
    background: #0F2D1E !important;
    color: #4ADE80 !important;
    border-color: #14532D !important;
}

/* Header Language Selector (Pill Dropdown) */
div[class*="st-key-hdr_lang_"] [data-baseweb="select"] > div {
    background: #1E293B !important;
    background-color: #1E293B !important;
    border-color: #334155 !important;
    color: #F8FAFC !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
}
div[class*="st-key-hdr_lang_"] [data-baseweb="select"] span {
    color: #F8FAFC !important;
}
div[class*="st-key-hdr_lang_"] [data-baseweb="select"] svg {
    fill: #CBD5E1 !important;
}

/* -- 5. Cards, Containers & Custom Badges -- */
.mm-card,
.mm-hospital-card,
.mm-header-bar,
.mm-quick-action-item,
.mm-ocr-box,
.mm-footer-trust-bar,
.stContainer,
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827 !important;
    background-color: #111827 !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}
.mm-card:hover,
.mm-hospital-card:hover {
    border-color: rgba(225,29,72,0.35) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.55), 0 0 14px rgba(179,38,30,0.22) !important;
}
.mm-card * { color: #F8FAFC !important; }
.mm-card p, .mm-card span, .mm-card div { color: #CBD5E1 !important; }

.mm-doc-pill,
.mm-ontology-pill {
    background: #111827 !important;
    border-color: #1E293B !important;
    color: #E2E8F0 !important;
}
.mm-doc-pill.active {
    background: #3B0A0A !important;
    border-color: #B3261E !important;
}
.mm-chip {
    background: #1E293B !important;
    color: #CBD5E1 !important;
}

/* -- 6. Clinical Stepper -- */
.mm-stepper {
    background: #111827 !important;
    background-color: #111827 !important;
    border-color: #1E293B !important;
}
.mm-stepper .mm-step-text-title { color: #F1F5F9 !important; }
.mm-stepper .mm-step-text-title.active { color: #F87171 !important; }
.mm-stepper .mm-step-text-sub { color: #94A3B8 !important; }
.mm-stepper .mm-step-arrow { color: #64748B !important; }
.mm-stepper .mm-step-num {
    background: #1E293B !important;
    color: #94A3B8 !important;
    border-color: #334155 !important;
}
.mm-stepper .mm-step-num.active {
    background: linear-gradient(135deg, #B3261E 0%, #E11D48 100%) !important;
    color: #FFFFFF !important;
    border-color: #B3261E !important;
    box-shadow: 0 0 14px rgba(179, 38, 30, 0.5) !important;
}
.mm-stepper .mm-step-num.done {
    background: #10B981 !important;
    color: #FFFFFF !important;
    border-color: #059669 !important;
}

/* -- 7. Form Labels, Inputs & Textboxes -- */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stMultiSelect label,
.stRadio label,
.stCheckbox label,
.stSlider label,
.stFileUploader label,
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label p,
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] label p {
    color: #CBD5E1 !important;
}

/* Radio circle inner styles */
div[data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    background-color: #0F172A !important;
    border-color: #475569 !important;
}

input,
textarea,
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="base-input"] textarea,
.stTextInput input,
.stTextInput > div,
.stTextInput > div > div,
.stTextArea textarea,
.stTextArea > div,
.stTextArea > div > div,
.stSelectbox > div,
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1.5px solid #1E2E4E !important;
    border-color: #1E2E4E !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
}

input:focus,
textarea:focus,
[data-baseweb="input"]:focus-within,
[data-baseweb="select"]:focus-within > div,
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: #B3261E !important;
    box-shadow: 0 0 0 2px rgba(179, 38, 30, 0.3) !important;
}

input::placeholder,
textarea::placeholder,
[data-baseweb="select"] input::placeholder,
[data-baseweb="select"] div[class*="Placeholder"],
[data-baseweb="select"] div[class*="placeholder"],
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
}

/* MultiSelect Selected Badges/Tags */
[data-baseweb="tag"] {
    background-color: rgba(179,38,30,0.25) !important;
    background: rgba(179,38,30,0.25) !important;
    border: 1px solid rgba(179,38,30,0.55) !important;
}
[data-baseweb="tag"] span,
[data-baseweb="tag"] svg {
    color: #FCA5A5 !important;
    fill: #FCA5A5 !important;
}

/* Dropdown Menu Popovers */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] li,
[role="listbox"],
[role="option"],
ul[role="listbox"],
div[data-testid="stSelectboxVirtualDropdown"],
ul[data-testid="stVirtualDropdown"] {
    background-color: #111827 !important;
    background: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid #1E293B !important;
}

li[role="option"],
div[role="option"],
[data-baseweb="menu"] li {
    color: #F8FAFC !important;
    border-bottom: 1px solid #1E293B !important;
}
li[role="option"] *,
div[role="option"] *,
[data-baseweb="menu"] li * {
    color: #F8FAFC !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"],
li[role="option"]:focus,
div[role="option"]:focus,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #F87171 !important;
}
li[role="option"]:hover *,
div[role="option"]:hover *,
li[role="option"][aria-selected="true"] *,
div[role="option"][aria-selected="true"] * {
    color: #F87171 !important;
}

/* -- 8. File Uploader Dropzone -- */
[data-testid="stFileUploader"],
[data-testid="stFileUploadDropzone"],
section[data-testid="stFileUploadDropzone"],
.stFileUploader,
.stFileUploader > div,
.stFileUploader section,
div[data-testid="stFileUploadDropzone"] {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border-color: #334155 !important;
    color: #F8FAFC !important;
}
[data-testid="stFileUploadDropzone"]:hover,
section[data-testid="stFileUploadDropzone"]:hover {
    border-color: #B3261E !important;
    background-color: #1E293B !important;
    background: #1E293B !important;
}
[data-testid="stFileUploadDropzone"] div,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] small,
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] label,
section[data-testid="stFileUploadDropzone"] * {
    color: #94A3B8 !important;
}
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploader"] button {
    background-color: #1E293B !important;
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #F8FAFC !important;
}

/* -- 9. Buttons & Interactive Elements -- */
.stButton > button {
    background-color: #1E293B !important;
    background: #1E293B !important;
    border-color: #334155 !important;
    color: #F1F5F9 !important;
}
.stButton > button:hover {
    background-color: #27354A !important;
    border-color: #475569 !important;
    color: #FFFFFF !important;
}
button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #B3261E 0%, #E11D48 100%) !important;
    color: #FFFFFF !important;
    border-color: #B3261E !important;
    box-shadow: 0 4px 14px rgba(179,38,30,0.4) !important;
}

/* Quick Action / Symptom Chips */
.st-key-pop_sym_chip_0 button, .st-key-pop_sym_chip_1 button,
.st-key-pop_sym_chip_2 button, .st-key-pop_sym_chip_3 button,
.st-key-pop_sym_chip_4 button, .st-key-pop_sym_chip_5 button,
.st-key-pop_sym_chip_6 button {
    background: #1E293B !important;
    color: #CBD5E1 !important;
    border-color: #334155 !important;
}
.st-key-pop_sym_chip_0 button:hover, .st-key-pop_sym_chip_1 button:hover,
.st-key-pop_sym_chip_2 button:hover, .st-key-pop_sym_chip_3 button:hover,
.st-key-pop_sym_chip_4 button:hover, .st-key-pop_sym_chip_5 button:hover,
.st-key-pop_sym_chip_6 button:hover {
    background: #27354A !important;
    border-color: #38BDF8 !important;
    color: #38BDF8 !important;
}

.st-key-btn_describe_words button,
.st-key-qa_upload_presc button,
.st-key-qa_find_hosp button,
.st-key-qa_health_tips button {
    background: #1E293B !important;
    color: #93C5FD !important;
    border-color: #334155 !important;
}
.st-key-btn_describe_words button:hover,
.st-key-qa_upload_presc button:hover,
.st-key-qa_find_hosp button:hover,
.st-key-qa_health_tips button:hover {
    background: #27354A !important;
    border-color: #38BDF8 !important;
    color: #38BDF8 !important;
}
.st-key-clear_all_sym_btn button {
    background: #2D1215 !important;
    color: #FCA5A5 !important;
    border-color: #4A1C1A !important;
}

/* -- 10. Sidebar Navigation (Dark Mode Colors) -- */
[data-testid="stSidebar"] {
    background-color: #070B14 !important;
    border-right-color: #1E293B !important;
}
[data-testid="stSidebar"] * { color: #F8FAFC !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #94A3B8 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #111827 !important;
    border-color: #1E293B !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #141D2E !important;
    border-color: #23324D !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #1E293B !important;
    border-color: #38BDF8 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(179, 38, 30, 0.35) 0%, rgba(225, 29, 72, 0.18) 100%) !important;
    border-left: 5px solid #B3261E !important;
    border-color: #B3261E !important;
    box-shadow: 0 4px 14px rgba(179, 38, 30, 0.30) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label,
[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] div[role="radiogroup"] label p,
[data-testid="stSidebar"] div[role="radiogroup"] label span,
[data-testid="stSidebar"] div[role="radiogroup"] label div {
    color: #F8FAFC !important;
}

/* -- 11. Tabs & Navigation -- */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111827 !important;
    border-bottom-color: #1E293B !important;
}
.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
}
.stTabs [aria-selected="true"] {
    color: #F87171 !important;
    border-bottom-color: #B3261E !important;
}

/* -- 12. Expanders, Metrics & Uploaders -- */
[data-testid="stMetric"] {
    background: #111827 !important;
    border-color: #1E293B !important;
}
[data-testid="stMetricLabel"] { color: #94A3B8 !important; }
[data-testid="stMetricValue"] { color: #F8FAFC !important; }

.streamlit-expanderHeader,
details[data-testid="stExpander"] {
    background: #111827 !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}
.streamlit-expanderContent {
    background: #0F172A !important;
    border-color: #1E293B !important;
    color: #CBD5E1 !important;
}

/* -- 13. Floating Chatbot Drawer & Suggestion Chips -- */
.floating-chat-container,
div[class*="st-key-slide_chat_drawer"],
div.st-key-slide_chat_drawer,
.st-key-slide_chat_drawer {
    background: #0A0E1A !important;
    background-color: #0A0E1A !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}
div.st-key-slide_chat_drawer [data-testid="stVerticalBlock"],
div.st-key-slide_chat_drawer [data-testid="stHorizontalBlock"],
div.st-key-slide_chat_drawer [data-testid="element-container"],
div.st-key-slide_chat_drawer [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
}
div.st-key-slide_chat_drawer [data-testid="stHeightContainer"] {
    background: #0A0E1A !important;
    border-color: #1E293B !important;
}
div[class*="st-key-floating_chat_user_input"] [data-baseweb="base-input"],
div[class*="st-key-floating_chat_user_input"] [data-baseweb="input"],
div[class*="st-key-floating_chat_user_input"] [data-baseweb="base-input"] input,
div[class*="st-key-floating_chat_user_input"] .stTextInput > div > div,
div[class*="st-key-floating_chat_user_input"] .stTextInput > div > div > input,
.st-key-slide_chat_form [data-baseweb="base-input"],
.st-key-slide_chat_form [data-baseweb="input"],
.st-key-slide_chat_form [data-baseweb="base-input"] input,
.st-key-slide_chat_form .stTextInput > div > div,
.st-key-slide_chat_form .stTextInput > div > div > input {
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #F8FAFC !important;
    border-color: #334155 !important;
}
div[class*="st-key-popup_unified_header"] {
    background: linear-gradient(135deg, #2D080A 0%, #8B0000 50%, #B3261E 100%) !important;
}
div[class*="st-key-dyn_chip_"] button,
div[class*="st-key-dyn_chip_"] [data-testid="baseButton-secondary"],
.floating-chat-container div[class*="st-key-dyn_chip_"] button {
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #E2E8F0 !important;
    border-color: #334155 !important;
}
div[class*="st-key-dyn_chip_"] button:hover,
div[class*="st-key-dyn_chip_"] [data-testid="baseButton-secondary"]:hover {
    background-color: #334155 !important;
    border-color: #F87171 !important;
    color: #F87171 !important;
}
div[class*="st-key-drawer_clear_chat_btn"] button,
div[class*="st-key-drawer_close_x_btn"] button,
.st-key-drawer_clear_chat_btn button,
.st-key-drawer_close_x_btn button {
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #CBD5E1 !important;
    border-color: #334155 !important;
}
div[class*="st-key-drawer_clear_chat_btn"] button:hover,
div[class*="st-key-drawer_close_x_btn"] button:hover,
.st-key-drawer_clear_chat_btn button:hover,
.st-key-drawer_close_x_btn button:hover {
    background-color: #334155 !important;
    border-color: #F87171 !important;
    color: #F87171 !important;
}

/* Chat Messages */
[data-testid="stChatMessage"],
.stChatMessage {
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    color: #F8FAFC !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em {
    color: #E2E8F0 !important;
}

/* -- 14. Dialogs, Modals & Quick Question Buttons -- */
[data-testid="stModal"],
div[data-testid="stDialog"] > div,
div[role="dialog"] {
    background-color: #0B0F19 !important;
    background: #0B0F19 !important;
    border-color: #1E2E4E !important;
    color: #F8FAFC !important;
}
div[data-testid="stDialog"] header,
div[role="dialog"] header {
    background-color: #0B0F19 !important;
    color: #F8FAFC !important;
    border-bottom-color: #1E293B !important;
}
div[data-testid="stDialog"] .stButton > button,
.st-key-p2_quick_q_0 button,
.st-key-p2_quick_q_1 button,
.st-key-p2_quick_q_2 button {
    background-color: #162032 !important;
    background: #162032 !important;
    color: #94A3B8 !important;
    border-color: #1E293B !important;
}
div[data-testid="stDialog"] .stButton > button:hover,
.st-key-p2_quick_q_0 button:hover,
.st-key-p2_quick_q_1 button:hover,
.st-key-p2_quick_q_2 button:hover {
    background-color: #1E293B !important;
    border-color: #3B82F6 !important;
    color: #60A5FA !important;
}
div[data-testid="stStatusWidget"] {
    background: #111827 !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}
</style>
"""


def apply_theme(dark_mode: bool = False):
    """
    Injects the Clinical Red enterprise medical stylesheet into the Streamlit app.
    Dynamically applies dark mode or light mode styles.
    """
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    if dark_mode:
        st.markdown(DARK_CSS_OVERRIDE, unsafe_allow_html=True)
