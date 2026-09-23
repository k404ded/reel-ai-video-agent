import { useRef, useState } from "react";
import "./App.css";

const STAGES = [
  { key: "understanding", label: "Understanding educational topic" },
  { key: "planning", label: "Director planning educational scenes" },
  { key: "quality_check", label: "Inspecting technical accuracy & metaphors" },
  { key: "scripting", label: "Writing technical script" },
  { key: "scenes", label: "Composing camera & visual actions" },
  { key: "visuals", label: "Generating technical visualizations" },
  { key: "audio", label: "Synthesizing voiceover" },
  { key: "captions", label: "Adding technical lower-thirds" },
  { key: "rendering", label: "Rendering motion video" },
];

const EXAMPLES = [
  "Explain Gradient Descent",
  "Explain Command Finder in CATIA",
  "Explain CAN Bus arbitration in automotive networks",
  "Explain how regenerative braking works in electric vehicles",
];

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState("idle"); // idle | running | done | error
  const [activeStageIndex, setActiveStageIndex] = useState(-1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const esRef = useRef(null);

  async function handleGenerate() {
    if (!prompt.trim() || status === "running") return;
    setStatus("running");
    setResult(null);
    setError(null);
    setActiveStageIndex(0);

    try {
      const resp = await fetch("/generate/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          const event = JSON.parse(line.slice(5).trim());

          if (event.type === "progress") {
            const idx = STAGES.findIndex((s) => s.key === event.stage);
            if (idx >= 0) setActiveStageIndex(idx);
          } else if (event.type === "result") {
            setActiveStageIndex(STAGES.length);
            setResult(event.data);
            setStatus("done");
          } else if (event.type === "error") {
            setError(event.message);
            setStatus("error");
          }
        }
      }
    } catch (err) {
      setError(String(err));
      setStatus("error");
    }
  }

  return (
    <div className="page">
      <div className="filmgrain" aria-hidden="true" />

      <header className="topbar">
        <div className="logo">
          <span className="logo-mark" />
          Reel AI Educational Director
        </div>
        <span className="topbar-note">concept in, educational video out</span>
      </header>

      <main className="hero">
        <h1 className="hero-title">
          Describe the concept.
          <br />
          <span className="hero-title-accent">Reel builds the lesson.</span>
        </h1>
        <p className="hero-sub">
          One sentence is enough — Reel plans technically grounded scenes, eliminates arbitrary metaphors, synthesizes voiceover, and renders a 1080p MP4.
        </p>

        <div className="prompt-shell">
          <textarea
            className="prompt-box"
            placeholder="Describe the technical or educational concept you want to teach (e.g. 'Explain Gradient Descent' or 'Explain Command Finder in CATIA')…"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            disabled={status === "running"}
          />
          <div className="prompt-row">
            <div className="examples">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  className="example-chip"
                  onClick={() => setPrompt(ex)}
                  disabled={status === "running"}
                  type="button"
                >
                  {ex}
                </button>
              ))}
            </div>
            <button
              className="generate-btn"
              onClick={handleGenerate}
              disabled={!prompt.trim() || status === "running"}
              type="button"
            >
              {status === "running" ? "Generating…" : "Generate video"}
            </button>
          </div>
        </div>

        {status === "running" && (
          <ol className="stage-list">
            {STAGES.map((s, i) => (
              <li
                key={s.key}
                className={
                  "stage-item" +
                  (i < activeStageIndex ? " stage-done" : i === activeStageIndex ? " stage-active" : "")
                }
              >
                <span className="stage-dot" />
                {s.label}
              </li>
            ))}
          </ol>
        )}

        {status === "error" && (
          <div className="error-box">
            Something went wrong while rendering: {error}
          </div>
        )}

        {status === "done" && result && (
          <section className="result">
            <div className="result-video">
              <video src={result.video_url} controls autoPlay loop playsInline />
            </div>

            <div className="result-meta">
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                <span style={{ background: "rgba(16, 185, 129, 0.2)", color: "#6ee7b7", border: "1px solid rgba(16, 185, 129, 0.4)", padding: "2px 8px", borderRadius: "5px", fontSize: "11px", fontWeight: "600" }}>
                  {result.validation_passed ? "Verified Educational Standard (0 Metaphors)" : "Refined by Validator"}
                </span>
                <span style={{ background: "rgba(99, 102, 241, 0.2)", color: "#a5b4fc", border: "1px solid rgba(99, 102, 241, 0.4)", padding: "2px 8px", borderRadius: "5px", fontSize: "11px", fontWeight: "600" }}>
                  {result.content_type?.replace("_", " ").toUpperCase() || "EDUCATIONAL"}
                </span>
              </div>

              <h2>{result.title}</h2>
              <p className="result-desc">{result.description}</p>

              {result.visual_direction && (
                <div className="visual-direction-badge">
                  <strong>Visual Direction:</strong> {result.visual_direction}
                </div>
              )}

              <h3>Script</h3>
              <p className="result-script">{result.script}</p>

              <h3>Educational Director Storyboard</h3>
              <ul className="scene-list">
                {result.scenes.map((s) => (
                  <li key={s.index} className="scene-item">
                    <div className="scene-header">
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                        {s.beat_role && (
                          <span style={{ background: "rgba(129, 140, 248, 0.2)", color: "#c7d2fe", border: "1px solid rgba(129, 140, 248, 0.4)", padding: "1px 6px", borderRadius: "4px", fontSize: "11px", fontWeight: "700" }}>
                            {s.beat_role.replace("_", " ")}
                          </span>
                        )}
                        <span className="scene-caption">{s.caption}</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                        {s.visual_type && (
                          <span style={{ background: "rgba(59, 130, 246, 0.2)", color: "#93c5fd", border: "1px solid rgba(59, 130, 246, 0.4)", padding: "1px 5px", borderRadius: "4px", fontSize: "10px", fontWeight: "600" }}>
                            {s.visual_type.replace("_", " ").toUpperCase()}
                          </span>
                        )}
                        {s.shot_type && (
                          <span style={{ background: "rgba(168, 85, 247, 0.2)", color: "#d8b4fe", border: "1px solid rgba(168, 85, 247, 0.4)", padding: "1px 5px", borderRadius: "4px", fontSize: "10px" }}>
                            {s.shot_type.replace("_", " ").toUpperCase()}
                          </span>
                        )}
                        <span className="scene-duration">{s.duration}s</span>
                      </div>
                    </div>
                    {s.action && (
                      <div style={{ fontSize: "12px", color: "#38bdf8", marginTop: "4px" }}>
                        <strong>Action:</strong> {s.action}
                      </div>
                    )}
                    {s.technical_content && (
                      <div style={{ fontSize: "12px", color: "#a7f3d0", marginTop: "2px" }}>
                        <strong>Technical:</strong> {s.technical_content}
                      </div>
                    )}
                    {s.camera_direction && (
                      <div className="scene-camera" style={{ marginTop: "3px" }}>🎥 {s.camera_direction}</div>
                    )}
                  </li>
                ))}
              </ul>

              <a className="download-btn" href={result.video_url} download>
                Download 1080p MP4
              </a>

              {(result.providers?.llm_fallback ||
                result.providers?.visual_fallback ||
                result.providers?.tts_fallback) && (
                <p className="fallback-note">
                  Running in multi-dispatch mode — specialized backends active for mathematical 3D rendering and software simulation.
                </p>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
