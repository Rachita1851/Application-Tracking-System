import streamlit as st
import streamlit.components.v1 as components
import pdf2image
import re
import io
import json
import base64
import plotly.graph_objects as go
import google.generativeai as genai

# ── Gemini ──────────────────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HireLens – ATS Application Tracking System",
    page_icon="🔍",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0c0c0e !important;
    color: #e8e4d8 !important;
}
.stApp { background-color: #0c0c0e !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}
.stMainBlockContainer { padding: 0 !important; max-width: 100% !important; }

@keyframes hl-scroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}
.hl-marquee-track {
    display: flex;
    width: max-content;
    animation: hl-scroll 28s linear infinite;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #131318 !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 16px !important;
    padding: 30px 18px 26px !important;
    width: 100% !important;
    min-height: 175px !important;
    height: auto !important;
    color: #e8e4d8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .88rem !important;
    font-weight: 500 !important;
    text-align: center !important;
    white-space: pre-wrap !important;
    line-height: 1.6 !important;
    cursor: pointer !important;
    transition: transform .3s cubic-bezier(.2,.8,.3,1),
                box-shadow .3s ease, border-color .3s ease !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    transform: translateY(-6px) !important;
    box-shadow: 0 18px 45px rgba(0,0,0,.55), 0 0 28px rgba(201,168,76,.14) !important;
    border-color: rgba(201,168,76,.55) !important;
    color: #e8c96a !important;
    background: #17171e !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:focus {
    outline: none !important;
    border-color: rgba(201,168,76,.5) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,.15) !important;
}

.stTextArea > div > div > textarea {
    background: #111114 !important;
    border: 1px solid #26262f !important;
    border-radius: 14px !important;
    color: #e8e4d8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .95rem !important;
    padding: 16px 18px !important;
    line-height: 1.7 !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: rgba(201,168,76,.5) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,.07) !important;
    outline: none !important;
}
.stTextArea label { display: none !important; }

[data-testid="stFileUploader"] > div {
    background: #111114 !important;
    border: 1.5px dashed #26262f !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(201,168,76,.5) !important;
    background: rgba(201,168,76,.04) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(201,168,76,.1) !important;
    border: 1px solid rgba(201,168,76,.4) !important;
    color: #c9a84c !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stMetric"] {
    background: #131318 !important;
    border: 1px solid #26262f !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: #e8c96a !important; }
[data-testid="stMetricLabel"] {
    color: #7a7870 !important;
    font-size: .68rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
}

.stSuccess { background: rgba(111,207,151,.07) !important; border-radius: 12px !important; }
.stInfo    { background: rgba(201,168,76,.07)  !important; border-radius: 12px !important; }
.stWarning { background: rgba(232,168,76,.07)  !important; border-radius: 12px !important; }

.stDownloadButton > button {
    background: rgba(201,168,76,.1) !important;
    border: 1px solid rgba(201,168,76,.45) !important;
    color: #e8c96a !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    width: auto !important;
    min-height: unset !important;
    padding: .65rem 1.6rem !important;
}

/* iframe embed gets dark bg */
iframe { background: #0c0c0e !important; border: none !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  NAV
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
    padding:20px 60px;border-bottom:1px solid #2a2a35;background:#0c0c0e;
    margin-left:calc(-50vw + 50%);margin-right:calc(-50vw + 50%);
    width:100vw;position:relative;">
  <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;
              color:#c9a84c;letter-spacing:.04em;">
    Hire<span style="color:#e8e4d8;">Lens</span>
  </div>
  <div style="font-size:.68rem;letter-spacing:.2em;color:#7a7870;text-transform:uppercase;">
    Resume Intelligence
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:64px 20px 0;
    background:radial-gradient(ellipse at 50% 0%, rgba(201,168,76,0.10) 0%, transparent 60%);">
  <div style="display:inline-block;font-size:.63rem;letter-spacing:.24em;text-transform:uppercase;
      color:#c9a84c;border:1px solid rgba(201,168,76,.35);padding:5px 18px;border-radius:20px;
      background:rgba(201,168,76,.06);margin-bottom:24px;font-family:'DM Sans',sans-serif;">
    ATS Application Tracking System
  </div>
  <div style="font-family:'Playfair Display',serif;font-size:clamp(3rem,7vw,5rem);
      font-weight:900;line-height:1.06;color:#ffffff;letter-spacing:-.02em;margin-bottom:18px;">
    Hire<span style="background:linear-gradient(135deg,#c9a84c 0%,#e8c96a 60%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Lens</span>
  </div>
  <div style="font-size:1.1rem;color:#7a7870;font-weight:300;letter-spacing:.02em;
      font-family:'DM Sans',sans-serif;padding-bottom:4px;">
    See your resume the way recruiters do.
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  MARQUEE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="width:100%;overflow:hidden;margin:40px 0 48px;
    border-top:1px solid #2a2a35;border-bottom:1px solid #2a2a35;
    padding:12px 0;background:rgba(201,168,76,.025);">
  <div class="hl-marquee-track">
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Smart analysis</strong>&nbsp;for smarter careers</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Turn resumes</strong>&nbsp;into insights</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Analyze.</strong>&nbsp;Improve.&nbsp;<strong style="color:#c9a84c;">Get hired.</strong></div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Smart analysis</strong>&nbsp;for smarter careers</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Turn resumes</strong>&nbsp;into insights</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Analyze.</strong>&nbsp;Improve.&nbsp;<strong style="color:#c9a84c;">Get hired.</strong></div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Smart analysis</strong>&nbsp;for smarter careers</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Turn resumes</strong>&nbsp;into insights</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Analyze.</strong>&nbsp;Improve.&nbsp;<strong style="color:#c9a84c;">Get hired.</strong></div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Smart analysis</strong>&nbsp;for smarter careers</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Turn resumes</strong>&nbsp;into insights</div>
    <div style="display:flex;align-items:center;gap:28px;padding:0 52px;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#5a5858;white-space:nowrap;font-family:'DM Sans',sans-serif;"><span style="width:4px;height:4px;border-radius:50%;background:#c9a84c;opacity:.65;flex-shrink:0;display:inline-block;"></span><strong style="color:#c9a84c;">Analyze.</strong>&nbsp;Improve.&nbsp;<strong style="color:#c9a84c;">Get hired.</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  INPUTS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="max-width:880px;margin:0 auto;padding:0 32px;">
  <span style="font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;
               color:#7a7870;display:block;margin-bottom:10px;font-family:'DM Sans',sans-serif;">
    Job Description
  </span>
</div>
""", unsafe_allow_html=True)

_, col_main, _ = st.columns([1, 8, 1])
with col_main:
    jd_input = st.text_area(
        label="jd", label_visibility="collapsed",
        height=155,
        placeholder="Paste the job description here…\ne.g. Role Category: DevOps\nEducation: UG: Any Graduate / PG: Any Postgraduate",
        key="jd_input",
    )

st.markdown("""
<div style="max-width:880px;margin:0 auto;padding:0 32px 10px;">
  <span style="font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;
               color:#7a7870;display:block;margin-top:18px;margin-bottom:10px;
               font-family:'DM Sans',sans-serif;">
    Upload Your Resume (PDF)
  </span>
</div>
""", unsafe_allow_html=True)

_, col_main2, _ = st.columns([1, 8, 1])
with col_main2:
    uploaded_file = st.file_uploader(label="up", label_visibility="collapsed", type=["pdf"])

if "resume_bytes" not in st.session_state:
    st.session_state.resume_bytes = None

if uploaded_file is not None:
    st.session_state.resume_bytes = uploaded_file.read()
    _, sc, _ = st.columns([1, 8, 1])
    with sc:
        st.success("✓  PDF Uploaded Successfully")

st.markdown('<hr style="border:none;border-top:1px solid #2a2a35;margin:32px 0;"/>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  6 FEATURE CARDS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;
            color:#5a5858;text-align:center;margin:0 0 22px;font-family:'DM Sans',sans-serif;">
  Choose an Analysis Tool
</div>
""", unsafe_allow_html=True)

_, card_col, _ = st.columns([1, 14, 1])
with card_col:
    r1c1, r1c2, r1c3 = st.columns(3, gap="medium")
    with r1c1:
        btn_resume_lens = st.button("🔍\n\nResume Lens\n\nDeep-dive into your resume through a recruiter's eye", key="btn_resume_lens", use_container_width=True)
    with r1c2:
        btn_keywords = st.button("🏷️\n\nGet Keywords\n\nExtract high-impact ATS keywords from the job description", key="btn_keywords", use_container_width=True)
    with r1c3:
        btn_pct = st.button("📊\n\nPercentage Match\n\nSee how well your resume matches the job requirements", key="btn_pct", use_container_width=True)

    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")
    with r2c1:
        btn_rewriter = st.button("✍️\n\nResume Rewriter\n\nAI rewrites your resume to be ATS-optimised and impactful", key="btn_rewriter", use_container_width=True)
    with r2c2:
        btn_skill = st.button("⚡\n\nSkill Matching\n\nMap your skills against what the role actually demands", key="btn_skill", use_container_width=True)
    with r2c3:
        btn_visual = st.button("📈\n\nVisual Analyzer\n\nVisualise resume structure, gaps, and formatting quality", key="btn_visual", use_container_width=True)

st.markdown('<hr style="border:none;border-top:1px solid #2a2a35;margin:32px 0;"/>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  ACTIVE TOOL STATE
# ═══════════════════════════════════════════════════════════════════════════
if btn_resume_lens: st.session_state["active_tool"] = "resume-lens"
if btn_keywords:    st.session_state["active_tool"] = "get-keywords"
if btn_pct:         st.session_state["active_tool"] = "percentage-match"
if btn_rewriter:    st.session_state["active_tool"] = "resume-rewriter"
if btn_skill:       st.session_state["active_tool"] = "skill-matching"
if btn_visual:      st.session_state["active_tool"] = "visual-analyzer"

active = st.session_state.get("active_tool", "")


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def input_pdf_setup(file_bytes: bytes):
    poppler_path = r"C:\Users\Rachita\Desktop\poppler\poppler-25.12.0\Library\bin"
    images = pdf2image.convert_from_bytes(file_bytes, poppler_path=poppler_path)
    buf = io.BytesIO()
    images[0].save(buf, format="JPEG")
    return [{"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}]

@st.cache_data(show_spinner=False)
def gemini_text(system_prompt: str, pdf_parts: list, jd: str) -> str:
    r = model.generate_content([system_prompt, pdf_parts[0], jd])
    return r.text

@st.cache_data(show_spinner=False)
def gemini_json(system_prompt: str, pdf_parts: list, jd: str):
    r = model.generate_content([system_prompt, pdf_parts[0], jd])
    raw = re.sub(r"^```[a-z]*\n?", "", r.text.strip())
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)

def check_inputs():
    if st.session_state.resume_bytes is None:
        st.warning("⚠️  Please upload your resume first.")
        return False
    if not jd_input.strip():
        st.warning("⚠️  Please paste a job description first.")
        return False
    return True

def section_header(title):
    st.markdown(f"""
    <div style="font-family:'Playfair Display',serif;font-size:1.55rem;font-weight:700;
                color:#e8e4d8;margin:1.8rem 0 1rem;border-left:3px solid #c9a84c;
                padding-left:.8rem;line-height:1.2;">{title}</div>""",
    unsafe_allow_html=True)

def response_card(text):
    st.markdown(f"""
    <div style="background:#111114;border:1px solid #252530;border-radius:16px;
                padding:1.8rem 2rem;margin-top:.8rem;line-height:1.85;
                color:#d8d4c8;font-size:.95rem;font-family:'DM Sans',sans-serif;">{text}</div>""",
    unsafe_allow_html=True)

GOLD    = "#c9a84c"
GOLD_L  = "#e8c96a"
VIBRANT = ["#c9a84c","#e05c8a","#4ecdc4","#45b7d1","#96ceb4","#ffeaa7","#fd79a8","#a29bfe","#00cec9","#fdcb6e"]

def base_layout(title="", height=420):
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=17, color="#e8e4d8"), x=0.02),
        paper_bgcolor="#131318", plot_bgcolor="#0c0c0e",
        font=dict(family="DM Sans", color="#e8e4d8"),
        height=height, margin=dict(l=16, r=16, t=50, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8e4d8")),
    )


# ═══════════════════════════════════════════════════════════════════════════
#  PROMPTS
# ═══════════════════════════════════════════════════════════════════════════
PROMPT_RESUME_LENS = """
You are an experienced Technical Human Resource Manager. Review the provided resume
against the job description. Give a professional evaluation on whether the candidate's
profile aligns with the role. Highlight strengths and weaknesses clearly with bullet points.
"""

PROMPT_KEYWORDS = """
You are an expert ATS scanner. Evaluate the resume against the job description.
Respond ONLY with valid JSON — no markdown fences, no extra text:
{"Technical Skills":["..."],"Analytical Skills":["..."],"Soft Skills":["..."]}
Only use skills actually present in the job description.
"""

PROMPT_PERCENTAGE = """
You are a skilled ATS scanner. Evaluate the resume against the job description.
Respond ONLY with valid JSON — no markdown fences, no extra text:
{
  "match_percentage": 74,
  "missing_keywords": ["Jenkins","CircleCI","Azure","PowerShell","communication","documentation"],
  "existing_skills": ["Python","Docker","Kubernetes","AWS","GCP","CI/CD","Bash","Linux","Git"],
  "final_thoughts": "Your resume presents a strong foundational match. To further enhance alignment, add keywords related to documentation and soft skills."
}
Base ALL values on the actual resume and JD provided.
"""

PROMPT_REWRITER = """
You are a professional resume writer and ATS expert.
Rewrite the entire resume to be ATS-optimised for the provided job description.
- Incorporate relevant keywords naturally
- Use strong action verbs; quantify achievements where possible
- Keep truthful — do not fabricate facts
- Format: Summary, Skills, Experience, Projects, Education
- Output only the rewritten resume, no commentary
"""

PROMPT_SKILL_MATCH = """
You are a career coach and ATS expert. Analyse the resume against the job description.
Score each resume section out of 10. Give improvement tips and 15-20 interview questions.
Respond ONLY with valid JSON — no markdown fences:
{
  "scores": {"Summary":7,"Skills":6,"Experience":8,"Projects":5,"Education":7},
  "improvement_tips": ["tip1","tip2"],
  "interview_questions": ["Q1?","Q2?"]
}
"""

PROMPT_VISUAL = """
You are an ATS and resume expert. Analyse the resume against the job description.
Respond ONLY with valid JSON — no markdown fences:
{
  "missing_skills": [{"skill":"Python","gap_pct":80},{"skill":"SQL","gap_pct":55}],
  "ats_breakdown": {"Keyword Match":35,"Skills Match":22,"Experience Match":18,"Education Match":8,"Formatting":9},
  "ats_summary": "One to two sentence summary of ATS performance.",
  "readability": {"score":72,"avg_sentence_length":18,"action_verbs_used":12,"passive_voice_pct":14},
  "job_role_compatibility": [{"role":"Data Engineer","score":82},{"role":"Backend Developer","score":65}],
  "skill_category_distribution": {"Programming":38,"Data Analysis":25,"Machine Learning":17,"Tools & Platforms":20},
  "learning_path": [{"item":"Learn SQL","priority":90},{"item":"Learn Power BI","priority":72}]
}
Base ALL values on the actual resume and JD — do not use placeholder numbers.
"""


# ═══════════════════════════════════════════════════════════════════════════
#  RESULTS
# ═══════════════════════════════════════════════════════════════════════════
_, res_col, _ = st.columns([1, 8, 1])

# ── 1. RESUME LENS ──────────────────────────────────────────────────────────
if active == "resume-lens":
    with res_col:
        if check_inputs():
            with st.spinner("Analysing your resume through a recruiter's eye…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                response = gemini_text(PROMPT_RESUME_LENS, pdf, jd_input)
            section_header("🔍 Resume Lens")
            response_card(response)

# ── 2. GET KEYWORDS ─────────────────────────────────────────────────────────
elif active == "get-keywords":
    with res_col:
        if check_inputs():
            with st.spinner("Extracting ATS keywords…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                data = gemini_json(PROMPT_KEYWORDS, pdf, jd_input)
            section_header("🏷️ ATS Keywords")
            for category, skills in data.items():
                if skills:
                    st.markdown(f"**{category}**")
                    pills = "".join(
                        f'<span style="background:rgba(201,168,76,.09);border:1px solid rgba(201,168,76,.28);'
                        f'border-radius:20px;padding:5px 16px;font-size:.8rem;color:#e8c96a;'
                        f'font-weight:500;margin:3px;display:inline-block;">{s}</span>'
                        for s in skills
                    )
                    st.markdown(f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;margin:.6rem 0 1.2rem;">{pills}</div>', unsafe_allow_html=True)

# ── 3. PERCENTAGE MATCH — FULL INTERACTIVE ──────────────────────────────────
elif active == "percentage-match":
    with res_col:
        if check_inputs():
            with st.spinner("Calculating match percentage…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                data = gemini_json(PROMPT_PERCENTAGE, pdf, jd_input)

            pct_val        = data.get("match_percentage", 0)
            missing_kws    = data.get("missing_keywords", [])
            existing_skills= data.get("existing_skills", [])
            final_thoughts = data.get("final_thoughts", "")

            section_header("📊 Percentage Match")

            # ── big percentage line ──────────────────────────────────────
            color = "#e05c8a" if pct_val < 50 else "#c9a84c" if pct_val < 75 else "#4ecdc4"
            label = "Needs Work" if pct_val < 50 else "Good Match" if pct_val < 75 else "Strong Match"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:20px;
                        padding:24px 28px;margin:12px 0 28px;
                        background:linear-gradient(135deg,#131318 0%,#1a1a22 100%);
                        border:1px solid {color}44;border-radius:18px;
                        box-shadow:0 0 30px {color}18;">
              <div style="font-family:'Playfair Display',serif;font-size:4.5rem;
                          font-weight:900;color:{color};line-height:1;letter-spacing:-.03em;">
                {pct_val}%
              </div>
              <div>
                <div style="font-family:'DM Sans',sans-serif;font-size:.7rem;
                            letter-spacing:.2em;text-transform:uppercase;color:#7a7870;
                            margin-bottom:6px;">ATS Match Score</div>
                <div style="display:inline-block;background:{color}22;border:1px solid {color}55;
                            border-radius:20px;padding:4px 14px;font-size:.82rem;
                            color:{color};font-weight:600;font-family:'DM Sans',sans-serif;">
                  {label}
                </div>
                <div style="font-family:'DM Sans',sans-serif;font-size:.88rem;
                            color:#a0a0a0;margin-top:10px;line-height:1.6;">
                  {final_thoughts}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Full interactive What-If component ───────────────────────
            missing_json  = json.dumps(missing_kws)
            existing_json = json.dumps(existing_skills)

            html_component = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    background:#0c0c0e; color:#e8e4d8;
    font-family:'DM Sans',sans-serif;
    padding:0 4px 24px;
  }}

  /* ── section labels ── */
  .sec-label {{
    font-size:.62rem; letter-spacing:.2em; text-transform:uppercase;
    color:#7a7870; margin-bottom:12px; font-weight:500;
  }}
  .sec-title {{
    font-family:'Playfair Display',serif; font-size:1.25rem;
    font-weight:700; color:#e8e4d8; margin-bottom:6px;
    border-left:3px solid #c9a84c; padding-left:10px;
  }}

  /* ── keyword chips ── */
  .chip {{
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(224,92,138,.12); border:1px solid rgba(224,92,138,.4);
    border-radius:20px; padding:6px 14px;
    font-size:.8rem; color:#e05c8a; font-weight:500;
    cursor:grab; user-select:none;
    transition:transform .2s, box-shadow .2s, background .2s;
    margin:4px;
  }}
  .chip:hover {{
    transform:translateY(-2px);
    box-shadow:0 6px 20px rgba(224,92,138,.25);
    background:rgba(224,92,138,.22);
  }}
  .chip:active {{ cursor:grabbing; }}
  .chip.dragging {{ opacity:.45; transform:scale(.94); }}

  /* ── missing keywords box ── */
  .missing-box {{
    background:#111114; border:1px solid #252530;
    border-radius:14px; padding:18px 18px 14px;
    margin-bottom:24px;
  }}
  .missing-pool {{
    display:flex; flex-wrap:wrap; gap:4px; min-height:48px;
  }}

  /* ── simulator box ── */
  .sim-box {{
    background:linear-gradient(135deg,#131318 0%,#16161e 100%);
    border:1px solid #2a2a35; border-radius:16px;
    padding:20px; margin-bottom:20px;
  }}
  .sim-header {{
    display:flex; align-items:center; gap:10px; margin-bottom:16px;
  }}
  .sim-icon {{
    width:36px; height:36px; border-radius:10px;
    background:rgba(201,168,76,.12); display:flex; align-items:center;
    justify-content:center; font-size:1.1rem;
  }}

  /* ── existing skills display ── */
  .skill-chip {{
    display:inline-block; background:rgba(78,205,196,.1);
    border:1px solid rgba(78,205,196,.3); border-radius:20px;
    padding:5px 12px; font-size:.75rem; color:#4ecdc4;
    margin:3px;
  }}

  /* ── drop zone ── */
  .drop-zone {{
    border:2px dashed #3a3a48; border-radius:14px;
    padding:18px; min-height:80px;
    display:flex; flex-wrap:wrap; align-items:flex-start;
    gap:6px; content:align; position:relative;
    transition:border-color .25s, background .25s;
    background:rgba(201,168,76,.02);
  }}
  .drop-zone.over {{
    border-color:#c9a84c;
    background:rgba(201,168,76,.07);
    box-shadow:0 0 20px rgba(201,168,76,.1);
  }}
  .drop-zone-hint {{
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    color:#3a3a50; font-size:.82rem; letter-spacing:.08em;
    pointer-events:none; white-space:nowrap;
    transition:opacity .25s;
  }}

  /* ── added skill pill (in drop zone) ── */
  .added-pill {{
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(201,168,76,.15); border:1px solid rgba(201,168,76,.45);
    border-radius:20px; padding:6px 8px 6px 14px;
    font-size:.8rem; color:#e8c96a; font-weight:500;
    animation:popIn .25s ease;
  }}
  @keyframes popIn {{
    from {{ transform:scale(.7); opacity:0; }}
    to   {{ transform:scale(1); opacity:1; }}
  }}
  .remove-btn {{
    width:20px; height:20px; border-radius:50%;
    background:rgba(224,92,138,.2); border:1px solid rgba(224,92,138,.4);
    color:#e05c8a; font-size:.75rem; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    transition:background .2s;
    flex-shrink:0;
  }}
  .remove-btn:hover {{ background:rgba(224,92,138,.45); }}

  /* ── meter ── */
  .meter-wrap {{
    background:linear-gradient(135deg,#111114 0%,#161620 100%);
    border:1px solid #252530; border-radius:16px;
    padding:22px; margin-top:8px;
  }}
  .meter-label {{
    font-family:'Playfair Display',serif; font-size:1rem; color:#7a7870;
    margin-bottom:16px; text-align:center; letter-spacing:.04em;
  }}
  .meter-label span {{ color:#c9a84c; font-weight:700; }}
  .score-display {{
    text-align:center; margin-bottom:18px;
  }}
  .score-number {{
    font-family:'Playfair Display',serif; font-size:3.8rem;
    font-weight:900; line-height:1; letter-spacing:-.03em;
    transition:color .5s;
  }}
  .score-badge {{
    display:inline-block; border-radius:20px; padding:4px 16px;
    font-size:.8rem; font-weight:600; margin-top:8px;
    transition:background .5s, color .5s, border-color .5s;
  }}
  .arc-bar-track {{
    width:100%; height:14px; background:#1e1e28;
    border-radius:8px; overflow:hidden; margin-bottom:10px;
  }}
  .arc-bar-fill {{
    height:100%; border-radius:8px;
    transition:width .6s cubic-bezier(.4,0,.2,1), background .6s;
  }}
  .meter-ticks {{
    display:flex; justify-content:space-between;
    font-size:.65rem; color:#4a4a58; letter-spacing:.05em;
  }}

  /* ── skill contribution list ── */
  .contrib-wrap {{
    margin-top:18px; border-top:1px solid #252530; padding-top:16px;
  }}
  .contrib-title {{
    font-size:.7rem; letter-spacing:.16em; text-transform:uppercase;
    color:#7a7870; margin-bottom:10px;
  }}
  .contrib-row {{
    display:flex; align-items:center; gap:10px;
    margin-bottom:8px;
  }}
  .contrib-name {{
    font-size:.82rem; color:#e8c96a; min-width:120px;
  }}
  .contrib-bar-track {{
    flex:1; height:6px; background:#1e1e28; border-radius:4px; overflow:hidden;
  }}
  .contrib-bar-fill {{
    height:100%; border-radius:4px; background:#c9a84c;
    transition:width .5s ease;
  }}
  .contrib-val {{
    font-size:.75rem; color:#c9a84c; min-width:36px; text-align:right;
  }}
</style>
</head>
<body>

<!-- ── MISSING KEYWORDS DASHBOARD ── -->
<div class="sec-title" style="margin-bottom:4px;">🎯 Missing Keywords Dashboard</div>
<div class="sec-label" style="margin-bottom:14px;">Drag any keyword into the What If Calculator below</div>
<div class="missing-box">
  <div class="sec-label">Missing from your resume</div>
  <div class="missing-pool" id="missingPool"></div>
</div>

<!-- ── WHAT IF SIMULATOR ── -->
<div class="sim-box">
  <div class="sim-header">
    <div class="sim-icon">🧪</div>
    <div>
      <div style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:#e8e4d8;">
        What If Calculator
      </div>
      <div style="font-size:.75rem;color:#7a7870;margin-top:2px;">
        See how learning new skills before your interview boosts your ATS score
      </div>
    </div>
  </div>

  <!-- existing skills -->
  <div class="sec-label" style="margin-bottom:8px;">Your existing skills</div>
  <div id="existingSkills" style="margin-bottom:18px;"></div>

  <!-- drop zone -->
  <div class="sec-label" style="margin-bottom:8px;">
    ✨ What if you add these skills?
    <span style="color:#5a5858;font-size:.7rem;"> — drag keywords here or click them above</span>
  </div>
  <div class="drop-zone" id="dropZone">
    <span class="drop-zone-hint" id="dzHint">Drop missing keywords here…</span>
  </div>
</div>

<!-- ── WHAT IF METER ── -->
<div class="meter-wrap" id="meterWrap">
  <div class="meter-label">
    <span>WHAT IF YOU ARE MORE SKILLED TILL YOUR INTERVIEW</span>
  </div>
  <div class="score-display">
    <div class="score-number" id="newScoreNum" style="color:#c9a84c;">{pct_val}%</div>
    <div class="score-badge" id="scoreBadge" style="background:rgba(201,168,76,.15);
         border:1px solid rgba(201,168,76,.4);color:#c9a84c;">Current Score</div>
  </div>
  <div class="arc-bar-track">
    <div class="arc-bar-fill" id="arcFill" style="width:{pct_val}%;background:#c9a84c;"></div>
  </div>
  <div class="meter-ticks">
    <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
  </div>

  <!-- contribution breakdown -->
  <div class="contrib-wrap" id="contribWrap" style="display:none;">
    <div class="contrib-title">Skill contribution breakdown</div>
    <div id="contribList"></div>
    <div style="margin-top:14px;padding:12px 16px;background:rgba(78,205,196,.07);
                border:1px solid rgba(78,205,196,.2);border-radius:10px;
                font-size:.84rem;color:#4ecdc4;line-height:1.6;" id="tipsBox"></div>
  </div>
</div>

<script>
const BASE_SCORE   = {pct_val};
const MISSING_KWS  = {missing_json};
const EXIST_SKILLS = {existing_json};

// Each missing keyword boosts score by a weighted amount (max total ~25pts headroom)
function skillBoost(skill) {{
  // Simple heuristic: spread remaining headroom evenly with some variance
  const headroom = Math.max(0, 98 - BASE_SCORE);
  const base = headroom / Math.max(MISSING_KWS.length, 1);
  // Add variance by keyword length
  const variance = (skill.length % 5) * 0.4;
  return Math.min(Math.round((base + variance) * 10) / 10, headroom);
}}

let addedSkills = []; // {{ name, boost }}

// ── Render missing pool ──────────────────────────────────────────────────
function renderPool() {{
  const pool = document.getElementById('missingPool');
  pool.innerHTML = '';
  MISSING_KWS.forEach(kw => {{
    if (addedSkills.find(s => s.name === kw)) return; // already added
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.draggable = true;
    chip.textContent = kw;
    chip.dataset.skill = kw;

    chip.addEventListener('dragstart', e => {{
      e.dataTransfer.setData('text/plain', kw);
      chip.classList.add('dragging');
    }});
    chip.addEventListener('dragend', () => chip.classList.remove('dragging'));

    // click to add directly
    chip.addEventListener('click', () => addSkill(kw));

    pool.appendChild(chip);
  }});
}}

// ── Render existing skills ────────────────────────────────────────────────
function renderExisting() {{
  const el = document.getElementById('existingSkills');
  el.innerHTML = EXIST_SKILLS.map(s =>
    `<span class="skill-chip">${{s}}</span>`
  ).join('');
}}

// ── Drop zone ─────────────────────────────────────────────────────────────
const dz = document.getElementById('dropZone');
const dzHint = document.getElementById('dzHint');

dz.addEventListener('dragover', e => {{ e.preventDefault(); dz.classList.add('over'); }});
dz.addEventListener('dragleave', () => dz.classList.remove('over'));
dz.addEventListener('drop', e => {{
  e.preventDefault();
  dz.classList.remove('over');
  const skill = e.dataTransfer.getData('text/plain');
  if (skill) addSkill(skill);
}});

function addSkill(name) {{
  if (addedSkills.find(s => s.name === name)) return;
  const boost = skillBoost(name);
  addedSkills.push({{ name, boost }});
  renderDropZone();
  renderPool();
  updateMeter();
}}

function removeSkill(name) {{
  addedSkills = addedSkills.filter(s => s.name !== name);
  renderDropZone();
  renderPool();
  updateMeter();
}}

function renderDropZone() {{
  // Clear only added pills (keep hint)
  Array.from(dz.querySelectorAll('.added-pill')).forEach(el => el.remove());

  if (addedSkills.length === 0) {{
    dzHint.style.opacity = '1';
  }} else {{
    dzHint.style.opacity = '0';
    addedSkills.forEach(s => {{
      const pill = document.createElement('div');
      pill.className = 'added-pill';
      pill.innerHTML = `
        ${{s.name}}
        <button class="remove-btn" title="Remove" onclick="removeSkill('${{s.name}}')">✕</button>
      `;
      dz.appendChild(pill);
    }});
  }}
}}

// ── Update meter ──────────────────────────────────────────────────────────
function updateMeter() {{
  const totalBoost = addedSkills.reduce((sum, s) => sum + s.boost, 0);
  const newScore   = Math.min(Math.round(BASE_SCORE + totalBoost), 99);

  const numEl    = document.getElementById('newScoreNum');
  const fillEl   = document.getElementById('arcFill');
  const badgeEl  = document.getElementById('scoreBadge');
  const cwEl     = document.getElementById('contribWrap');
  const listEl   = document.getElementById('contribList');
  const tipsEl   = document.getElementById('tipsBox');

  // color
  let col, bgc, bdc, label;
  if (newScore < 50) {{
    col='#e05c8a'; bgc='rgba(224,92,138,.15)'; bdc='rgba(224,92,138,.4)'; label='Needs Work';
  }} else if (newScore < 75) {{
    col='#c9a84c'; bgc='rgba(201,168,76,.15)'; bdc='rgba(201,168,76,.4)'; label='Good Match';
  }} else {{
    col='#4ecdc4'; bgc='rgba(78,205,196,.15)'; bdc='rgba(78,205,196,.4)'; label='Strong Match';
  }}

  numEl.textContent  = newScore + '%';
  numEl.style.color  = col;
  fillEl.style.width = newScore + '%';
  fillEl.style.background = col;

  if (addedSkills.length > 0) {{
    const gained = newScore - BASE_SCORE;
    badgeEl.textContent = `+${{gained}}% boost · ${{label}}`;
    badgeEl.style.background   = bgc;
    badgeEl.style.borderColor  = bdc;
    badgeEl.style.color        = col;

    cwEl.style.display = 'block';
    listEl.innerHTML = addedSkills.map(s => `
      <div class="contrib-row">
        <div class="contrib-name">${{s.name}}</div>
        <div class="contrib-bar-track">
          <div class="contrib-bar-fill" style="width:${{Math.min(s.boost * 3, 100)}}%"></div>
        </div>
        <div class="contrib-val">+${{s.boost.toFixed(1)}}%</div>
      </div>
    `).join('');

    const skillNames = addedSkills.map(s => s.name).join(', ');
    tipsEl.innerHTML = `
      <strong style="color:#e8e4d8;">📌 Interview Tip:</strong>
      By adding <strong style="color:#e8c96a;">${{skillNames}}</strong> to your skill set,
      your ATS compatibility rises from <strong>${{BASE_SCORE}}%</strong> to
      <strong style="color:${{col}}">${{newScore}}%</strong>.
      Mention these skills explicitly in your resume summary and experience section
      with real project examples to maximise impact.
    `;
  }} else {{
    badgeEl.textContent = 'Current Score';
    badgeEl.style.background  = 'rgba(201,168,76,.15)';
    badgeEl.style.borderColor = 'rgba(201,168,76,.4)';
    badgeEl.style.color       = '#c9a84c';
    cwEl.style.display = 'none';
  }}
}}

// ── Init ──────────────────────────────────────────────────────────────────
renderPool();
renderExisting();
</script>
</body>
</html>
"""
            components.html(html_component, height=1100, scrolling=True)

# ── 4. RESUME REWRITER ──────────────────────────────────────────────────────
elif active == "resume-rewriter":
    with res_col:
        if check_inputs():
            with st.spinner("Rewriting your resume for ATS optimisation…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                response = gemini_text(PROMPT_REWRITER, pdf, jd_input)
            section_header("✍️ ATS-Optimised Resume")
            st.info("💡 Review carefully before using. All facts preserved from your original resume.")
            response_card(response)
            st.download_button(
                label="⬇️  Download Rewritten Resume (.txt)",
                data=response,
                file_name="hirelens_rewritten_resume.txt",
                mime="text/plain",
            )

# ── 5. SKILL MATCHING ───────────────────────────────────────────────────────
elif active == "skill-matching":
    with res_col:
        if check_inputs():
            with st.spinner("Scoring resume sections and generating interview questions…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                data = gemini_json(PROMPT_SKILL_MATCH, pdf, jd_input)
            section_header("⚡ Skill Matching & Section Scores")
            scores = data.get("scores", {})
            if scores:
                sections = list(scores.keys())
                vals     = list(scores.values())
                colors   = [GOLD if v >= 7 else "#e05c8a" if v < 5 else "#4ecdc4" for v in vals]
                fig = go.Figure(go.Bar(
                    x=sections, y=vals, marker_color=colors,
                    text=[f"{v}/10" for v in vals],
                    textposition="outside",
                    textfont=dict(color="#e8e4d8", size=13),
                ))
                fig.update_layout(
                    **base_layout("Resume Section Scores (out of 10)", height=360),
                    yaxis=dict(range=[0,11], gridcolor="#2a2a35", color="#7a7870"),
                    xaxis=dict(color="#7a7870"), bargap=0.35,
                )
                st.plotly_chart(fig, use_container_width=True)
                cols = st.columns(len(scores))
                for i, (sec, score) in enumerate(scores.items()):
                    with cols[i]:
                        st.metric(label=sec, value=f"{score}/10")
            tips = data.get("improvement_tips", [])
            if tips:
                section_header("How to Improve")
                for tip in tips:
                    st.markdown(f"- {tip}")
            questions = data.get("interview_questions", [])
            if questions:
                section_header("Top Interview Questions")
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**Q{i}.** {q}")

# ── 6. VISUAL ANALYZER ──────────────────────────────────────────────────────
elif active == "visual-analyzer":
    with res_col:
        if check_inputs():
            with st.spinner("Building your visual resume dashboard…"):
                pdf = input_pdf_setup(st.session_state.resume_bytes)
                data = gemini_json(PROMPT_VISUAL, pdf, jd_input)
            section_header("📈 Visual Resume Dashboard")

    if active == "visual-analyzer" and st.session_state.resume_bytes and jd_input.strip():
        r1c1, r1c2 = st.columns(2, gap="medium")
        with r1c1:
            missing = data.get("missing_skills", [])
            if missing:
                skills = [m["skill"] for m in missing]
                gaps   = [m["gap_pct"] for m in missing]
                fig = go.Figure(go.Bar(
                    y=skills, x=gaps, orientation="h",
                    marker=dict(color=gaps, colorscale="Plasma", showscale=True,
                                colorbar=dict(title=dict(text="Gap %", font=dict(color="#e8e4d8")),
                                             tickfont=dict(color="#e8e4d8"))),
                    text=[f"{g}%" for g in gaps], textposition="outside",
                    textfont=dict(color="#e8e4d8", size=12),
                ))
                fig.update_layout(**base_layout("Missing Skills Heatmap", height=380),
                                  xaxis=dict(range=[0,110], gridcolor="#2a2a35", color="#7a7870"),
                                  yaxis=dict(color="#e8e4d8"))
                st.plotly_chart(fig, use_container_width=True)
        with r1c2:
            ats_bd  = data.get("ats_breakdown", {})
            summary = data.get("ats_summary", "")
            if ats_bd:
                fig = go.Figure(go.Pie(
                    labels=list(ats_bd.keys()), values=list(ats_bd.values()), hole=0.45,
                    marker=dict(colors=VIBRANT[:len(ats_bd)], line=dict(color="#0c0c0e", width=2)),
                    textfont=dict(size=12, color="#e8e4d8"),
                ))
                fig.update_layout(**base_layout("ATS Score Breakdown", height=380))
                st.plotly_chart(fig, use_container_width=True)
                if summary: st.caption(f"💡 {summary}")

        r2c1, r2c2 = st.columns(2, gap="medium")
        with r2c1:
            readability = data.get("readability", {})
            if readability:
                score = readability.get("score", 70)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta", value=score,
                    delta={"reference":70,"increasing":{"color":"#4ecdc4"}},
                    number={"suffix":"/100","font":{"size":32,"color":GOLD}},
                    gauge={"axis":{"range":[0,100],"tickcolor":"#7a7870"},
                           "bar":{"color":GOLD},"bgcolor":"#1a1a20","bordercolor":"#2a2a35",
                           "steps":[{"range":[0,50],"color":"#2d1a1a"},{"range":[50,75],"color":"#1a1a20"},{"range":[75,100],"color":"#1a2a1a"}],
                           "threshold":{"line":{"color":"#e05c8a","width":3},"value":70}},
                ))
                fig.update_layout(**base_layout("Resume Readability Score", height=300))
                st.plotly_chart(fig, use_container_width=True)
                m1,m2,m3 = st.columns(3)
                m1.metric("Avg Sentence Length", f"{readability.get('avg_sentence_length','—')} wds")
                m2.metric("Action Verbs Used", readability.get("action_verbs_used","—"))
                m3.metric("Passive Voice", f"{readability.get('passive_voice_pct','—')}%")
        with r2c2:
            compat = data.get("job_role_compatibility", [])
            if compat:
                roles  = [c["role"]  for c in compat]
                scores = [c["score"] for c in compat]
                fig = go.Figure(go.Bar(
                    y=roles, x=scores, orientation="h",
                    marker=dict(color=scores, colorscale="Teal", showscale=False),
                    text=[f"{s}%" for s in scores], textposition="outside",
                    textfont=dict(color="#e8e4d8", size=12),
                ))
                fig.update_layout(**base_layout("Job Role Compatibility", height=360),
                                  xaxis=dict(range=[0,110], gridcolor="#2a2a35", color="#7a7870"),
                                  yaxis=dict(autorange="reversed", color="#e8e4d8"))
                st.plotly_chart(fig, use_container_width=True)

        r3c1, r3c2 = st.columns(2, gap="medium")
        with r3c1:
            skill_dist = data.get("skill_category_distribution", {})
            if skill_dist:
                fig = go.Figure(go.Pie(
                    labels=list(skill_dist.keys()), values=list(skill_dist.values()), hole=0.35,
                    marker=dict(colors=["#c9a84c","#e05c8a","#4ecdc4","#a29bfe"],
                                line=dict(color="#0c0c0e", width=2)),
                    textfont=dict(size=12, color="#e8e4d8"),
                ))
                fig.update_layout(**base_layout("Skill Category Distribution", height=340))
                st.plotly_chart(fig, use_container_width=True)
        with r3c2:
            learning = data.get("learning_path", [])
            if learning:
                items    = [l["item"]     for l in learning]
                priority = [l["priority"] for l in learning]
                bar_clrs = ["#c9a84c","#e05c8a","#4ecdc4","#a29bfe","#fdcb6e","#00cec9"][:len(items)]
                fig = go.Figure(go.Bar(
                    y=items, x=priority, orientation="h",
                    marker=dict(color=bar_clrs),
                    text=[f"{p}%" for p in priority], textposition="outside",
                    textfont=dict(color="#e8e4d8", size=12),
                ))
                fig.update_layout(
                    **base_layout("Learning Path – To Increase Match Score", height=340),
                    xaxis=dict(range=[0,110], gridcolor="#2a2a35", color="#7a7870",
                               title=dict(text="Priority %", font=dict(color="#7a7870"))),
                    yaxis=dict(autorange="reversed", color="#e8e4d8"), bargap=0.3,
                )
                st.plotly_chart(fig, use_container_width=True)
