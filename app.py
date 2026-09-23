import os
import sys
import asyncio
import streamlit as st

# Automatically load Streamlit secrets into os.environ for cloud deployment
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str) and k not in os.environ:
                os.environ[k] = v
except Exception:
    pass

# Ensure backend modules can be imported
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agent import generate_video

# Page Configuration
st.set_page_config(
    page_title="Reel — AI Video Generation Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for high contrast, modern premium dark aesthetic & readable text
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0d13 !important;
        color: #f3f4f6 !important;
    }

    /* Main headings & text */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f3f4f6;
    }
    
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1.25rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 0.75rem;
        color: #ffffff !important;
    }
    
    .hero-title-gradient {
        background: linear-gradient(135deg, #818cf8 0%, #ec4899 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #9ca3af !important;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }

    /* Example buttons / chips */
    div[data-testid="column"] .stButton > button {
        background-color: #1e2230 !important;
        color: #f3f4f6 !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 0.75rem !important;
        min-height: 54px !important;
        height: auto !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: left !important;
        line-height: 1.35 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background-color: #2b3248 !important;
        color: #ffffff !important;
        border-color: #818cf8 !important;
        transform: translateY(-1px);
    }
    div[data-testid="column"] .stButton > button p {
        color: #f3f4f6 !important;
    }

    /* Textarea input box */
    .stTextArea {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stTextArea textarea {
        background-color: #161924 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
        padding: 0.85rem !important;
        line-height: 1.5 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    }
    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.3) !important;
    }
    .stTextArea textarea::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }

    /* Primary Generate Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.5rem !important;
        margin-top: 0.5rem !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.1) !important;
        box-shadow: 0 6px 22px rgba(239, 68, 68, 0.55) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Status & Alerts */
    [data-testid="stStatusWidget"] {
        background-color: #161924 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    [data-testid="stStatusWidget"] * {
        color: #ffffff !important;
    }
    .stAlert {
        background-color: #161924 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    
    .scene-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .scene-card strong {
        color: #ffffff !important;
    }
    .scene-card small {
        color: #9ca3af !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for optional Key Settings
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("API keys are loaded from `.env` or Streamlit Secrets by default.")
    custom_gemini = st.text_input("Gemini API Key (optional override)", type="password")
    if custom_gemini:
        os.environ["GEMINI_API_KEY"] = custom_gemini
    st.caption("Reel Universal Technical Video Mode: Procedural 1080p mathematical, algorithmic, CAD, and engineering animations with zero avatars and synchronized captions.")

# Hero Header
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">
        Universal Technical Video Agent.<br/>
        <span class="hero-title-gradient">100% Subject-Focused.</span>
    </h1>
    <p class="hero-subtitle">
        Enter any engineering, mathematical, algorithmic, CAD, automotive, or scientific concept — Reel generates authentic 1080p technical animations with real temporal motion in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# Examples showcasing universal technical domains
EXAMPLES = [
    "Explain Gradient Descent",
    "Explain Binary Search",
    "Explain PID Control",
    "Explain CAN Bus arbitration",
    "Explain Command Finder in CATIA",
    "Explain EV Regenerative Braking",
    "Explain Neural Network Backprop",
    "Explain CNC Milling Toolpaths",
]

col_row1 = st.columns(4)
for i, ex in enumerate(EXAMPLES[:4]):
    with col_row1[i]:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["user_prompt"] = ex
            st.rerun()

col_row2 = st.columns(4)
for i, ex in enumerate(EXAMPLES[4:]):
    with col_row2[i]:
        if st.button(ex, key=f"ex_{i+4}", use_container_width=True):
            st.session_state["user_prompt"] = ex
            st.rerun()

# Input Box
if "user_prompt" not in st.session_state:
    st.session_state["user_prompt"] = ""

prompt = st.text_area(
    "Prompt",
    value=st.session_state["user_prompt"],
    placeholder="Describe the educational concept you want to teach (e.g. 'Explain Gradient Descent' or 'Explain Command Finder in CATIA')...",
    height=100,
    label_visibility="collapsed",
)

generate_clicked = st.button("🎬 Generate Video", type="primary", use_container_width=True, disabled=not prompt.strip())

# Stages
STAGE_LABELS = {
    "understanding": "Understanding your idea...",
    "planning": "Planning educational scenes with Director AI...",
    "quality_check": "Educational quality check & anti-metaphor inspection...",
    "scripting": "Writing technical narration & script...",
    "scenes": "Configuring scene composition & timing...",
    "visuals": "Generating high-definition visuals...",
    "audio": "Synthesizing voiceover audio...",
    "captions": "Generating lower-third captions...",
    "rendering": "Assembling MP4 with Ken Burns motion & transitions...",
    "done": "Video complete!",
}

if generate_clicked:
    st.session_state["result"] = None
    
    status_container = st.status("🎬 Starting pipeline...", expanded=True)
    
    async def run_pipeline():
        async def on_progress(stage: str):
            label = STAGE_LABELS.get(stage, stage)
            status_container.write(f"✓ {label}")
            status_container.update(label=f"🎬 {label}")
            
        return await generate_video(prompt, on_progress=on_progress)
    
    try:
        with st.spinner("Processing..."):
            result = asyncio.run(run_pipeline())
            st.session_state["result"] = result
            status_container.update(label="✅ Educational Video Generated Successfully!", state="complete", expanded=False)
    except Exception as exc:
        status_container.update(label="❌ Error Generating Video", state="error", expanded=True)
        st.error(f"Generation failed: {exc}")

# Display Results
if st.session_state.get("result"):
    res = st.session_state["result"]
    st.divider()
    
    col_left, col_right = st.columns([1.2, 1], gap="large")
    
    with col_left:
        st.subheader("🎥 Final Educational Video")
        if os.path.exists(res.video_path):
            with open(res.video_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
                
                st.download_button(
                    label="⬇️ Download 1080p MP4",
                    data=video_bytes,
                    file_name=f"{res.title.replace(' ', '_').lower()}.mp4",
                    mime="video/mp4",
                    type="primary",
                    use_container_width=True,
                )
    
    with col_right:
        content_type_badge = getattr(res, "content_type", "GENERAL_EDUCATIONAL").replace("_", " ").upper()
        validation_status = "✅ Verified Educational Standard (0 Metaphors)" if getattr(res, "validation_passed", True) else "⚠️ Refined by Director Validator"
        
        st.subheader(f"✨ {res.title}")
        st.markdown(f"""
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 0.5rem;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">{validation_status}</span>
            <span style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">📁 {content_type_badge}</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption(res.description)
        
        if getattr(res, "shared_visual_anchor", None):
            anchor = res.shared_visual_anchor
            pal = anchor.get("color_palette", [])
            pal_html = " ".join([f"<span style='background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; margin-right: 4px;'>{c}</span>" for c in pal]) if pal else ""
            st.markdown(f"""
            <div style="background: rgba(129, 140, 248, 0.08); border: 1px solid rgba(129, 140, 248, 0.25); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <strong style="color: #a5b4fc; font-size: 0.88rem;">🎨 Shared Visual Anchor:</strong>
                    <div>{pal_html}</div>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 0.2rem;"><strong>💡 Lighting:</strong> {anchor.get('lighting_setup', 'Workstation ambient lighting')}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>⚙️ Materials:</strong> {anchor.get('primary_material', 'High-detail technical surfaces')}</div>
            </div>
            """, unsafe_allow_html=True)
        elif getattr(res, "visual_direction", None):
            st.markdown(f"""
            <div style="background: rgba(129, 140, 248, 0.08); border: 1px solid rgba(129, 140, 248, 0.25); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
                <strong style="color: #a5b4fc;">🎨 Visual Direction:</strong>
                <p style="color: #e0e7ff; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{res.visual_direction}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📝 Technical Narration Script")
        st.info(res.script)
        
        st.markdown("### 🎞️ Educational Director Storyboard")
        for s in res.scenes:
            beat_label = s.get("beat_role", "SCENE").replace("_", " ")
            vtype = s.get("visual_type", "technical_scene").replace("_", " ").upper()
            stype = s.get("shot_type", "medium_shot").replace("_", " ").upper()
            action = s.get("action", "")
            tech_content = s.get("technical_content", "")
            val_stat = s.get("validation_status", "PASSED")
            
            st.markdown(f"""
            <div class="scene-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap; gap: 4px;">
                    <div>
                        <span style="background: rgba(129, 140, 248, 0.2); color: #c7d2fe; border: 1px solid rgba(129, 140, 248, 0.4); padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700; margin-right: 6px;">{beat_label}</span>
                        <strong>Scene {s['index'] + 1} ({s['duration']}s)</strong>
                    </div>
                    <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                        <span style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.4); padding: 1px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{vtype}</span>
                        <span style="background: rgba(168, 85, 247, 0.2); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); padding: 1px 6px; border-radius: 4px; font-size: 0.7rem;">{stype}</span>
                        <span style="background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; color: #f3f4f6;">{s.get('caption', '')}</span>
                    </div>
                </div>
                {f"<div style='font-size: 0.84rem; color: #38bdf8; margin-bottom: 0.25rem;'><strong>⚡ Concrete Action:</strong> {action}</div>" if action else ""}
                {f"<div style='font-size: 0.84rem; color: #a7f3d0; margin-bottom: 0.25rem;'><strong>🔬 Technical Elements:</strong> {tech_content}</div>" if tech_content else ""}
                {f"<div style='font-size: 0.82rem; color: #93c5fd; margin-bottom: 0.25rem;'><strong>🎥 Camera Motion:</strong> {s.get('camera_direction', '')}</div>" if s.get('camera_direction') else ""}
                <div style='font-size: 0.82rem; color: #9ca3af; margin-bottom: 0.25rem;'><strong>🎨 Visual Prompt:</strong> {s['visual_prompt']}</div>
                <div style='font-size: 0.82rem; color: #cbd5e1;'><strong>🎙️ Voiceover:</strong> &ldquo;{s.get('narration', '')}&rdquo;</div>
            </div>
            """, unsafe_allow_html=True)
