"""
WiseCruit - AI Recruitment Intelligence Platform
Smart Role Fit Analysis & Automated Deep Shortlisting Engine
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
from datetime import datetime
import pytz
import time as time_module

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.loader import load_jd_text
from engine.jd_parser import parse_jd
from engine.ranker import WiseCruitRanker

st.set_page_config(
    page_title="WiseCruit | Cognitive Talent Intelligence",
    page_icon="🧠",
    layout="wide"
)

clock_placeholder = st.empty()


if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return now.strftime("%d %b %Y, %I:%M %p") + " IST"

def get_ist_greeting():
    ist = pytz.timezone('Asia/Kolkata')
    hrs = datetime.now(ist).hour
    if 5 <= hrs < 12: return "Good Morning ☀️"
    elif 12 <= hrs < 17: return "Good Afternoon 🌤️"
    elif 17 <= hrs < 19: return "Good Evening 🌅"
    else: return "Good Evening 🌙"

THEMES = {
    "dark": {
        "bg_main": "#0A0B10", "bg_card": "#13141c", "bg_card_hover": "#1a1b26",
        "border": "#1f2030", "text_primary": "#e2e8f0", "text_secondary": "#94a3b8",
        "text_muted": "#64748b", "accent": "#7c3aed", "accent2": "#a78bfa",
        "accent3": "#c084fc", "accent4": "#38bdf8", "progress_bg": "#1f2030",
        "sidebar_bg": "#0A0B10", "expander_bg": "#13141c", "metric_bg": "#13141c",
        "success_bg": "#0d3320", "success_text": "#4ade80", "tab_bg": "#13141c",
        "tab_active": "#1a1b26", "upload_bg": "#13141c",
        "badge_bg": "rgba(124,58,237,0.12)", "badge_text": "#c4b5fd",
        "badge_border": "rgba(124,58,237,0.25)", "glow": "rgba(124,58,237,0.15)",
        "header_bg": "linear-gradient(135deg, #1a0f30, #0c0e17, #06070a)",
        "header_border": "rgba(139,92,246,0.25)",
        "elite_bg": "rgba(74,222,128,0.12)", "elite_text": "#4ade80",
        "good_bg": "rgba(168,139,250,0.12)", "good_text": "#a78bfa",
        "avg_bg": "rgba(251,191,36,0.12)", "avg_text": "#fbbf24",
    },
    "light": {
        "bg_main": "#f8fafc", "bg_card": "#ffffff", "bg_card_hover": "#f5f3ff",
        "border": "#e2e8f0", "text_primary": "#0f172a", "text_secondary": "#334155",
        "text_muted": "#64748b", "accent": "#7c3aed", "accent2": "#8b5cf6",
        "accent3": "#a78bfa", "accent4": "#0ea5e9", "progress_bg": "#f1f5f9",
        "sidebar_bg": "#ffffff", "expander_bg": "#ffffff", "metric_bg": "#ffffff",
        "success_bg": "#f0fdf4", "success_text": "#16a34a", "tab_bg": "#f5f3ff",
        "tab_active": "#ffffff", "upload_bg": "#fafaff",
        "badge_bg": "rgba(124,58,237,0.08)", "badge_text": "#7c3aed",
        "badge_border": "rgba(124,58,237,0.2)", "glow": "rgba(124,58,237,0.06)",
        "header_bg": "linear-gradient(135deg, #f5f3ff, #faf5ff, #ffffff)",
        "header_border": "#ddd6fe",
        "elite_bg": "rgba(22,163,74,0.1)", "elite_text": "#16a34a",
        "good_bg": "rgba(124,58,237,0.1)", "good_text": "#7c3aed",
        "avg_bg": "rgba(217,119,6,0.1)", "avg_text": "#d97706",
    }
}

theme = THEMES[st.session_state.theme]

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    code {{ font-family: 'JetBrains Mono', monospace !important; }}
    .main {{ background: {theme['bg_main']}; }}
    .stApp {{ background: {theme['bg_main']}; }}
    
    .wise-header {{
        position: relative; overflow: hidden;
        background: {theme['header_bg']};
        border: 1px solid {theme['header_border']};
        border-radius: 24px; padding: 36px 40px; margin-bottom: 20px;
        box-shadow: 0 25px 70px -25px {theme['glow']};
        animation: fadeSlideUp 0.6s ease-out;
    }}
    .wise-glow {{
        position: absolute; top: -60px; right: -60px;
        width: 350px; height: 350px;
        background: {theme['glow']}; border-radius: 50%;
        filter: blur(80px); pointer-events: none;
    }}
    .wise-badge {{
        display: inline-flex; align-items: center; gap: 10px;
        padding: 10px 22px; border-radius: 30px;
        font-size: 3.5rem; font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: {theme['badge_bg']}; color: {theme['badge_text']};
        border: 1px solid {theme['badge_border']};
        margin-bottom: 14px; letter-spacing: 0.8px; text-transform: uppercase;
        animation: fadeIn 0.8s ease-out;
    }}
    .wise-greeting {{ font-size: 1.8rem; font-weight: 700; color: {theme['text_primary']}; line-height: 1.2; }}
    .wise-subtitle {{ font-size: 0.8rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; color: {theme['accent2']}; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }}
    .wise-tagline {{ font-size: 1.05rem; font-weight: 500; color: {theme['text_secondary']}; }}
    .light .wise-greeting {{ color: #0f172a; }}
    
    @keyframes fadeSlideUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    
    .stTabs [data-baseweb="tab-panel"] {{ animation: fadeSlideUp 0.4s ease-out; }}
    
    .results-card {{
        background: linear-gradient(135deg, {theme['accent']}10, {theme['accent4']}08);
        border: 1px solid {theme['border']};
        border-radius: 20px; padding: 24px 28px; margin-bottom: 16px;
        animation: fadeSlideUp 0.5s ease-out;
    }}
    
    .tier-pill {{
        display: inline-block; padding: 4px 12px; border-radius: 14px;
        font-size: 0.8rem; font-weight: 600;
    }}
    .tier-elite {{ background: {theme['elite_bg']}; color: {theme['elite_text']}; }}
    .tier-strong {{ background: {theme['good_bg']}; color: {theme['good_text']}; }}
    .tier-potential {{ background: {theme['avg_bg']}; color: {theme['avg_text']}; }}
    
    [data-testid="stSidebar"] {{ background: {theme['sidebar_bg']} !important; border-right: 1px solid {theme['border']} !important; }}
    [data-testid="stSidebar"] * {{ color: {theme['text_secondary']} !important; }}
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{ color: {theme['text_primary']} !important; }}
    [data-testid="stSidebar"] .stButton > button {{
        width: 42px !important; height: 42px !important; padding: 0 !important;
        font-size: 1.3rem !important; border-radius: 50% !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        background: {theme['bg_card']} !important; border: 1px solid {theme['border']} !important; box-shadow: none !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{ border-color: {theme['accent']} !important; background: {theme['bg_card_hover']} !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        background: {theme['tab_bg']}; border-radius: 12px 12px 0 0; padding: 14px 28px;
        color: {theme['text_secondary']} !important; border: 1px solid {theme['border']};
        border-bottom: none; font-weight: 600; font-size: 0.95rem; transition: all 0.2s;
    }}
    .stTabs [aria-selected="true"] {{ background: {theme['tab_active']}; color: {theme['accent']} !important; border-color: {theme['accent']}; box-shadow: 0 -2px 10px {theme['glow']}; }}
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{ color: {theme['text_primary']} !important; }}
    
    [data-testid="stMetric"] {{ background: {theme['metric_bg']}; border: 1px solid {theme['border']}; border-radius: 16px; padding: 18px !important; transition: all 0.2s; }}
    [data-testid="stMetric"]:hover {{ border-color: {theme['accent']}; transform: translateY(-1px); }}
    [data-testid="stMetric"] label {{ color: {theme['text_muted']} !important; font-size: 0.8rem; }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {theme['text_primary']} !important; font-weight: 700 !important; }}
    
    [data-testid="stExpander"] {{ background: {theme['expander_bg']}; border: 1px solid {theme['border']}; border-radius: 12px; margin-bottom: 8px; transition: all 0.2s; animation: fadeSlideUp 0.4s ease-out; }}
    [data-testid="stExpander"]:hover {{ border-color: {theme['accent']}50; }}
        [data-testid="stExpander"] summary {{ 
        color: {theme['text_primary']} !important; 
        font-weight: 600 !important; 
        font-size: 0.95rem; 
    }}
    [data-testid="stExpander"] summary svg {{ 
        animation: pulse 1.5s ease-in-out infinite;
        color: {theme['accent']} !important;
    }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.5; transform: scale(1.2); }} }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {theme['accent']}, {theme['accent3']}) !important;
        color: #ffffff !important; font-weight: 700 !important; border: none !important;
        border-radius: 12px !important; padding: 14px 32px !important;
        font-size: 1.05rem !important; letter-spacing: 0.3px; transition: all 0.2s;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }}
    .stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 35px {theme['glow']}; }}
    .stButton > button p {{ color: #ffffff !important; font-weight: 700 !important; }}
    
    .stProgress > div > div {{ background: linear-gradient(90deg, {theme['accent']}, {theme['accent3']}); border-radius: 10px; }}
    .stProgress > div {{ background: {theme['progress_bg']}; border-radius: 10px; }}
    
    [data-testid="stInfo"] {{ background: {theme['expander_bg']}; border-left: 4px solid {theme['accent']}; border-radius: 10px; }}
    [data-testid="stSuccess"] {{ background: {theme['success_bg']}; border-left: 4px solid {theme['success_text']}; border-radius: 10px; }}
    
    [data-testid="stFileUploader"] {{ background: {theme['upload_bg']}; border: 2px dashed {theme['border']}; border-radius: 16px; padding: 28px; transition: all 0.2s; }}
    [data-testid="stFileUploader"]:hover {{ border-color: {theme['accent']}; }}
    
    h1, h2, h3, h4 {{ color: {theme['text_primary']} !important; font-weight: 700 !important; }}
    p, li, label {{ color: {theme['text_secondary']} !important; }}
    .stCaption {{ color: {theme['text_muted']} !important; }}
    hr {{ border-color: {theme['border']}; }}
    a {{ color: {theme['accent']} !important; text-decoration: none; }}
    a:hover {{ color: {theme['accent4']} !important; }}
    
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {theme['border']}; border-radius: 4px; }}
    
    .feature-card {{ background: {theme['bg_card']}; padding: 24px; border-radius: 16px; border: 1px solid {theme['border']}; transition: all 0.2s; }}
    .feature-card:hover {{ border-color: {theme['accent']}50; box-shadow: 0 8px 25px -10px {theme['glow']}; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_jd():
    return parse_jd(load_jd_text("job_description.md"))

jd_requirements = get_jd()
greeting = get_ist_greeting()
ist_time = get_ist_time()

# HEADER
st.markdown(f"""
<div class="wise-header">
    <div class="wise-glow"></div>
    <div style="position:relative; z-index:2;">
        <span class="wise-badge">🧠 WiseCruit</span>
        <h1 class="wise-greeting">{greeting}</h1>
        <p class="wise-subtitle">AI-Driven Role Fit Analysis & Automated Deep Shortlisting Engine</p>
        <p class="wise-tagline">Hire Smarter. Hunt Less. Hit Gold. 🥇 &nbsp;|&nbsp; 🕐 {ist_time}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        icon = " 🌙 " if st.session_state.theme == "dark" else " ☀️ "
        if st.button(icon, key="theme_toggle", help="Switch theme", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center; font-size:1.7rem !important;'>📋 Active Role</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{theme['bg_card']}; padding:14px; border-radius:12px; border:1px solid {theme['border']}; font-size:1.5rem; line-height:1.8;'>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{theme['text_secondary']};'><strong>Role:</strong> Senior AI Engineer</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{theme['text_secondary']};'><strong>Company:</strong> Redrob AI</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{theme['text_secondary']};'><strong>Location:</strong> Pune/Noida</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{theme['text_secondary']};'><strong>Experience:</strong> 5-9 years</span>", unsafe_allow_html=True)
    st.markdown(f"</div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### 🎯 Key Requirements")
    for r in ["Production ML/ranking", "Embeddings & vector search", "Strong Python", "Product experience", "Startup mindset"]:
        st.markdown(f"🔹 {r}")
    
    st.divider()
    st.markdown("#### 🧬 Engine")
    for f in ["9-Dimensional Scoring", "23 Behavioral Signals", "Trust & Honeypot Detection", "Hidden Talent Radar", "Startup Mindset Analysis"]:
        st.markdown(f"✅ {f}")

# TABS
tab1, tab2 = st.tabs(["🔮 Discover Talent", "📖 How It Works"])

# TAB 2: HOW IT WORKS
with tab2:
    st.markdown("### 🧠 Cognitive Recruitment Intelligence")
    st.caption("WiseCruit evaluates every candidate through 9 independent dimensions — like an expert hiring committee, not a keyword filter.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.markdown(f"""<div class="feature-card"><span style="font-size:2.5rem;">🔍</span><h4 style="color:{theme['accent']} !important; margin-top:8px;">Hidden Talent Radar</h4><p style="color:{theme['text_secondary']}; line-height:1.6; font-size:0.9rem;">Detects expertise buried in career descriptions — skills candidates demonstrably possess but haven't explicitly listed.</p></div>""", unsafe_allow_html=True)
    with fc2:
        st.markdown(f"""<div class="feature-card"><span style="font-size:2.5rem;">🛡️</span><h4 style="color:{theme['accent4']} !important; margin-top:8px;">Authenticity Shield</h4><p style="color:{theme['text_secondary']}; line-height:1.6; font-size:0.9rem;">Identifies timeline inconsistencies, skill inflation & impossible profiles — blocking keyword stuffers automatically.</p></div>""", unsafe_allow_html=True)
    with fc3:
        st.markdown(f"""<div class="feature-card"><span style="font-size:2.5rem;">🚀</span><h4 style="color:{theme['accent3']} !important; margin-top:8px;">Startup Compass</h4><p style="color:{theme['text_secondary']}; line-height:1.6; font-size:0.9rem;">Measures agility, multi-role versatility & product-company exposure for founding team hires.</p></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Scoring Architecture")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"""<div class="feature-card"><h4 style="color:{theme['accent']} !important;">🔬 9-Dimensional Analysis</h4><table style="width:100%; color:{theme['text_secondary']}; font-size:0.9rem; border-collapse:collapse;"><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">🎯 Skill Synthesis</td><td style="text-align:right;"><strong>28%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">💼 Career Vector</td><td style="text-align:right;"><strong>23%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">📅 Experience Calibration</td><td style="text-align:right;"><strong>10%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">🏢 Company Pedigree</td><td style="text-align:right;"><strong>10%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">📡 Engagement Pulse</td><td style="text-align:right;"><strong>9%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">🎓 Academic Signal</td><td style="text-align:right;"><strong>5%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">📍 Geo Alignment</td><td style="text-align:right;"><strong>5%</strong></td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:8px 4px;">🛡️ Authenticity Index</td><td style="text-align:right;"><strong>5%</strong></td></tr><tr><td style="padding:8px 4px;">🚀 Startup Quotient</td><td style="text-align:right;"><strong>5%</strong></td></tr></table></div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class="feature-card"><h4 style="color:{theme['accent4']} !important;">⚡ Performance</h4><div style="color:{theme['text_secondary']}; font-size:0.9rem; line-height:2;"><p>📦 <strong>100,000 candidates</strong> processed</p><p>⏱️ <strong>Under 30 seconds</strong> ranking time</p><p>💻 <strong>CPU only</strong> — no GPU required</p><p>🔒 <strong>Zero network calls</strong> during ranking</p><p>📊 <strong>100% reproducible</strong> results</p><p>🛡️ <strong>Honeypot-aware</strong> architecture</p></div></div><br><div class="feature-card"><h4 style="color:{theme['accent3']} !important;">🧠 vs Traditional ATS</h4><table style="width:100%; color:{theme['text_secondary']}; font-size:0.85rem;"><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:6px;">Keyword matching</td><td style="color:{theme['accent4']};">→ Semantic reasoning</td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:6px;">Binary filter</td><td style="color:{theme['accent4']};">→ Multi-factor score</td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:6px;">Black box</td><td style="color:{theme['accent4']};">→ Full explainability</td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:6px;">Static profile</td><td style="color:{theme['accent4']};">→ 23 behavioral signals</td></tr><tr style="border-bottom:1px solid {theme['border']};"><td style="padding:6px;">No fraud check</td><td style="color:{theme['accent4']};">→ Honeypot detection</td></tr><tr><td style="padding:6px;">Generic approach</td><td style="color:{theme['accent4']};">→ JD-specific tuning</td></tr></table></div>""", unsafe_allow_html=True)

# TAB 1: DISCOVER TALENT
with tab1:
    st.markdown("### 🔮 Discover Top Talent")
    st.caption("Upload candidate profiles. Get cognitive rankings with complete explainability.")
    
    uploaded_file = st.file_uploader("📤 Upload Candidate Profiles", type=["json", "jsonl", "csv", "xlsx", "xls"], help="Supports JSON, JSONL, CSV, and Excel formats. Max 200MB.")
    
    if uploaded_file is not None:
        try:
            fname = uploaded_file.name.lower()
            if fname.endswith('.csv'):
                df_in = pd.read_csv(uploaded_file); candidates = df_in.to_dict('records')
            elif fname.endswith(('.xlsx', '.xls')):
                df_in = pd.read_excel(uploaded_file); candidates = df_in.to_dict('records')
            else:
                content = uploaded_file.read().decode("utf-8")
                try: candidates = json.loads(content)
                except: candidates = [json.loads(l) for l in content.split("\n") if l.strip()]
                if not isinstance(candidates, list): candidates = [candidates]
            
            st.success(f"✨ **{len(candidates)} profiles loaded** — Ready for analysis")
            
            if st.button("🔮 Reveal Top Talent", type="primary", use_container_width=True):
                with st.spinner("🧠 Running cognitive analysis across 9 dimensions..."):
                    if len(candidates) > 100: candidates = candidates[:100]
                    ranker = WiseCruitRanker(jd_requirements)
                    ranked = ranker.rank_candidates(candidates, top_n=min(20, len(candidates)))
                    df = ranker.to_dataframe(ranked)
                    top_score = df['score'].iloc[0]
                    avg_score = df['score'].mean()
                    
                    # Count tiers
                    elite_n = len(df[df['score'] >= 70])
                    strong_n = len(df[(df['score'] >= 50) & (df['score'] < 70)])
                    pot_n = len(df) - elite_n - strong_n
                    
                    st.divider()
                    
                    # Results header card
                    st.markdown(f"""<div class="results-card"><div style="display:flex; align-items:center; gap:14px;"><span style="font-size:2.5rem;">🏆</span><div><h3 style="margin:0; color:{theme['text_primary']} !important;">Cognitive Match Results</h3><p style="margin:0; color:{theme['text_muted']}; font-size:0.85rem;">👆 Click any candidate row to expand and see the full 9-dimensional breakdown</p></div></div></div>""", unsafe_allow_html=True)
                    
                    # Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("🏅 Top Match", f"{top_score:.1f}%")
                    m2.metric("📊 Average", f"{avg_score:.1f}%")
                    m3.metric("👥 Evaluated", len(df))
                    m4.metric("⚡ Speed", "Instant")
                    
                    # Tier pills
                    st.markdown(f"""<div style="display:flex; gap:10px; margin:8px 0 18px 0;">""" +
                        f"""<span class="tier-pill tier-elite">🥇 {elite_n} Elite</span>""" +
                        f"""<span class="tier-pill tier-strong">🥈 {strong_n} Strong</span>""" +
                        f"""<span class="tier-pill tier-potential">🥉 {pot_n} Potential</span></div>""", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Candidate rows
                    for _, row in df.iterrows():
                        sv = row['score']
                        if sv >= 70: medal, tier = "🥇", "Elite"
                        elif sv >= 50: medal, tier = "🥈", "Strong"
                        else: medal, tier = "🥉", "Potential"
                        
                        with st.expander(f"{medal} #{row['rank']} | {row['candidate_id']} | {tier} · {sv:.1f}%  ───  ▼"):
                            st.markdown(f"**🧠 Assessment:** {row['reasoning']}")
                            cand_data = next((c for c in candidates if str(c.get('candidate_id','')) == str(row['candidate_id'])), None)
                            if cand_data:
                                from engine.scorer import WiseCruitScorer
                                scorer = WiseCruitScorer(jd_requirements)
                                detail = scorer.score_candidate(cand_data)
                                st.markdown("---")
                                st.markdown("#### 🔬 Dimensional Breakdown")
                                cols = st.columns(3)
                                dims = [
                                    ("🎯 Skills","skill_match"),("💼 Career","career_match"),
                                    ("📅 Experience","experience_fit"),("🎓 Education","education_fit"),
                                    ("📍 Location","location_fit"),("🏢 Company","company_fit"),
                                    ("📡 Engagement","hiring_readiness"),("🛡️ Trust","trust_score"),
                                    ("🚀 Startup Fit","startup_mindset"),
                                ]
                                for i,(label,key) in enumerate(dims):
                                    val = detail.get(key,0)
                                    emoji = "🟢" if val>=70 else "🟡" if val>=40 else "🔴"
                                    with cols[i%3]:
                                        st.markdown(f"**{emoji} {label}**")
                                        st.progress(val/100)
                                        st.caption(f"{val:.1f}%")
                    
                    st.download_button("📥 Download Results (CSV)", data=df.to_csv(index=False), file_name="wisecruit_results.csv", mime="text/csv", use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
    else:
        st.info("👆 **Upload candidate profiles** (JSON, JSONL, CSV, or Excel) to start analysis.")
        if os.path.exists("sample_candidates.json"):
            st.markdown("---")
            st.markdown("### ⚡ Quick Demo")
            if st.button("🚀 Run Demo Analysis", use_container_width=True):
                with st.spinner("🧠 Analyzing sample profiles..."):
                    from engine.loader import load_sample_candidates
                    candidates = load_sample_candidates("sample_candidates.json")
                    ranker = WiseCruitRanker(jd_requirements)
                    ranked = ranker.rank_candidates(candidates, top_n=min(20, len(candidates)))
                    df = ranker.to_dataframe(ranked)
                    top_score = df['score'].iloc[0]
                    avg_score = df['score'].mean()
                    elite_n = len(df[df['score']>=70])
                    strong_n = len(df[(df['score']>=50)&(df['score']<70)])
                    pot_n = len(df)-elite_n-strong_n
                    
                    st.divider()
                    st.markdown(f"""<div class="results-card"><div style="display:flex; align-items:center; gap:14px;"><span style="font-size:2.5rem;">🏆</span><div><h3 style="margin:0; color:{theme['text_primary']} !important;">Cognitive Match Results</h3><p style="margin:0; color:{theme['text_muted']}; font-size:0.85rem;">👆 Click any candidate row to expand and see the full 9-dimensional breakdown</p></div></div></div>""", unsafe_allow_html=True)
                    
                    m1,m2,m3,m4 = st.columns(4)
                    m1.metric("🏅 Top Match",f"{top_score:.1f}%")
                    m2.metric("📊 Average",f"{avg_score:.1f}%")
                    m3.metric("👥 Evaluated",len(df))
                    m4.metric("⚡ Speed","Instant")
                    
                    st.markdown(f"""<div style="display:flex; gap:10px; margin:8px 0 18px 0;">""" +
                        f"""<span class="tier-pill tier-elite">🥇 {elite_n} Elite</span>""" +
                        f"""<span class="tier-pill tier-strong">🥈 {strong_n} Strong</span>""" +
                        f"""<span class="tier-pill tier-potential">🥉 {pot_n} Potential</span></div>""", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    for _,row in df.iterrows():
                        sv=row['score']
                        if sv>=70: medal,tier="🥇","Elite"
                        elif sv>=50: medal,tier="🥈","Strong"
                        else: medal,tier="🥉","Potential"
                        
                        with st.expander(f"{medal} #{row['rank']} | {row['candidate_id']} | {tier} · {sv:.1f}%  ─── ▼"):
                            st.markdown(f"**🧠 Assessment:** {row['reasoning']}")
                            cand_data=next((c for c in candidates if c.get('candidate_id')==row['candidate_id']),None)
                            if cand_data:
                                from engine.scorer import WiseCruitScorer
                                scorer=WiseCruitScorer(jd_requirements)
                                detail=scorer.score_candidate(cand_data)
                                st.markdown("---")
                                st.markdown("#### 🔬 Dimensional Breakdown")
                                cols=st.columns(3)
                                dims=[
                                    ("🎯 Skills","skill_match"),("💼 Career","career_match"),
                                    ("📅 Experience","experience_fit"),("🎓 Education","education_fit"),
                                    ("📍 Location","location_fit"),("🏢 Company","company_fit"),
                                    ("📡 Engagement","hiring_readiness"),("🛡️ Trust","trust_score"),
                                    ("🚀 Startup Fit","startup_mindset"),
                                ]
                                for i,(label,key) in enumerate(dims):
                                    val=detail.get(key,0)
                                    emoji="🟢" if val>=70 else "🟡" if val>=40 else "🔴"
                                    with cols[i%3]:
                                        st.markdown(f"**{emoji} {label}**")
                                        st.progress(val/100)
                                        st.caption(f"{val:.1f}%")
                    st.download_button("📥 Download Demo Results (CSV)",data=df.to_csv(index=False),file_name="wisecruit_demo.csv",mime="text/csv",use_container_width=True)

# FOOTER
st.divider()
st.markdown(f"""
<div style="text-align:center; padding:20px 0 10px 0;">
    <p style="font-size:1rem; color:{theme['text_muted']}; margin:0;">
        👩‍💻 <strong style="color:{theme['text_primary']};">Keya Das</strong> &nbsp;|&nbsp; 
        MCA (AI & Data Science)
    </p>
    <p style="font-size:0.9rem; margin:6px 0; color:{theme['text_muted']};">
        🔗 <a href="https://github.com/Keya3639" target="_blank">github.com/Keya3639</a> &nbsp;|&nbsp; 
        📧 <a href="mailto:keyakarunamoydas@gmail.com">keyakarunamoydas@gmail.com</a>
    </p>
    <p style="font-size:0.85rem; color:{theme['accent']}; margin-top:8px; font-weight:500;">
        Built with ❤️ using Streamlit & Python
    </p>
</div>
""", unsafe_allow_html=True)