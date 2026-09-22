import os
import sys
import asyncio
import streamlit as st

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

# Custom CSS for modern premium dark aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0d13;
        color: #f3f4f6;
    }
    
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 0.75rem;
    }
    
    .hero-title-gradient {
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #9ca3af;
        line-height: 1.5;
        margin-bottom: 2rem;
    }
    
    .scene-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
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
    st.caption("Reel uses Google Gemini for planning, Flux/SD for scene imagery, Edge-TTS for voiceover, and FFmpeg for assembly.")

# Hero Header
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">
        Describe the video.<br/>
        <span class="hero-title-gradient">Reel builds it.</span>
    </h1>
    <p class="hero-subtitle">
        One sentence is enough — Reel plans the scenes, generates the visuals and voiceover, and renders a finished 1080p MP4.
    </p>
</div>
""", unsafe_allow_html=True)

# Examples
EXAMPLES = [
    "Create a 10-second educational video explaining how a gearbox works.",
    "Create a 10-second explanation of gradient descent.",
    "Create a cinematic 10-second video of a futuristic city at night.",
    "Explain how regenerative braking works in 10 seconds.",
]

col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)
for i, (col, ex) in enumerate(zip([col_ex1, col_ex2, col_ex3, col_ex4], EXAMPLES)):
    with col:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["user_prompt"] = ex

# Input Box
if "user_prompt" not in st.session_state:
    st.session_state["user_prompt"] = ""

prompt = st.text_area(
    "Prompt",
    value=st.session_state["user_prompt"],
    placeholder="Describe the video you want to create (e.g. 'Create a 10-second educational video explaining how a gearbox works.')...",
    height=100,
    label_visibility="collapsed",
)

generate_clicked = st.button("🎬 Generate Video", type="primary", use_container_width=True, disabled=not prompt.strip())

# Stages
STAGE_LABELS = {
    "understanding": "Understanding your idea...",
    "planning": "Planning the video with AI...",
    "scripting": "Writing scene narration & script...",
    "scenes": "Configuring scene timing...",
    "visuals": "Generating scene visuals...",
    "audio": "Synthesizing voiceover audio...",
    "captions": "Generating subtitles & captions...",
    "rendering": "Assembling final MP4 with FFmpeg...",
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
            status_container.update(label="✅ Video Generated Successfully!", state="complete", expanded=False)
    except Exception as exc:
        status_container.update(label="❌ Error Generating Video", state="error", expanded=True)
        st.error(f"Generation failed: {exc}")

# Display Results
if st.session_state.get("result"):
    res = st.session_state["result"]
    st.divider()
    
    col_left, col_right = st.columns([1.2, 1], gap="large")
    
    with col_left:
        st.subheader("🎥 Final Video")
        if os.path.exists(res.video_path):
            with open(res.video_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
                
                st.download_button(
                    label="⬇️ Download MP4",
                    data=video_bytes,
                    file_name=f"{res.title.replace(' ', '_').lower()}.mp4",
                    mime="video/mp4",
                    type="primary",
                    use_container_width=True,
                )
    
    with col_right:
        st.subheader(f"✨ {res.title}")
        st.caption(res.description)
        
        st.markdown("### 📝 Full Script")
        st.info(res.script)
        
        st.markdown("### 🎞️ Scenes")
        for s in res.scenes:
            st.markdown(f"""
            <div class="scene-card">
                <strong>Scene {s['index'] + 1} ({s['duration']}s)</strong>: {s['caption']}<br/>
                <small style="color: #9ca3af;">{s['visual_prompt']}</small>
            </div>
            """, unsafe_allow_html=True)
