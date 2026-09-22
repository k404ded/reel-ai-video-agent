import { useRef, useState } from "react";
import "./App.css";

const STAGES = [
  { key: "understanding", label: "Understanding your idea" },
  { key: "planning", label: "Planning the video" },
  { key: "scripting", label: "Writing the script" },
  { key: "scenes", label: "Creating scenes" },
  { key: "visuals", label: "Generating visuals" },
  { key: "audio", label: "Adding audio" },
  { key: "captions", label: "Adding captions" },
  { key: "rendering", label: "Rendering video" },
];

const EXAMPLES = [
  "Explain how regenerative braking works in 10 seconds.",
  "Create a cinematic video of a futuristic city at night.",
  "Make a short educational video explaining gradient descent.",
  "Explain how a BLDC motor works.",
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
          Reel
        </div>
        <span className="topbar-note">prompt in, video out</span>
      </header>

      <main className="hero">
        <h1 className="hero-title">
          Describe the video.
          <br />
          <span className="hero-title-accent">Reel builds it.</span>
        </h1>
        <p className="hero-sub">
          One sentence is enough — Reel plans the scenes, generates the visuals and
          voiceover, and renders a finished MP4.
        </p>

        <div className="prompt-shell">
          <textarea
            className="prompt-box"
            placeholder="Describe the video you want to create…"
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
              <h2>{result.title}</h2>
              <p className="result-desc">{result.description}</p>

              <h3>Script</h3>
              <p className="result-script">{result.script}</p>

              <h3>Scenes</h3>
              <ul className="scene-list">
                {result.scenes.map((s) => (
                  <li key={s.index}>
                    <span className="scene-caption">{s.caption}</span>
                    <span className="scene-duration">{s.duration}s</span>
                  </li>
                ))}
              </ul>

              <a className="download-btn" href={result.video_url} download>
                Download MP4
              </a>

              {(result.providers.llm_fallback ||
                result.providers.visual_fallback ||
                result.providers.tts_fallback) && (
                <p className="fallback-note">
                  Running without one or more API keys — using built-in local fallbacks for{" "}
                  {[
                    result.providers.llm_fallback && "planning",
                    result.providers.visual_fallback && "visuals",
                    result.providers.tts_fallback && "voice",
                  ]
                    .filter(Boolean)
                    .join(", ")}
                  . Add keys in backend/.env for the real thing.
                </p>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
