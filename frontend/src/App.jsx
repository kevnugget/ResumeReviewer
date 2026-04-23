import { useState } from "react";

// converts **text** to <strong> and renders each line with spacing
function renderFeedback(text) {
  return text.split("\n").filter(line => line.trim()).map((line, i) => {
    const cleaned = line.replace(/^[\*\-]\s+/, "• ");  // replace * or - bullets with a real bullet
    const parts = cleaned.split(/\*\*(.*?)\*\*/g);
    return (
      <p key={i} style={{ margin: "0 0 0.6rem 0", lineHeight: "1.6", fontSize: "0.9rem" }}>
        {parts.map((part, j) => j % 2 === 1 ? <strong key={j}>{part}</strong> : part)}
      </p>
    );
  });
}

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resumeContext, setResumeContext] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [answerIsWarning, setAnswerIsWarning] = useState(false);
  const [askLoading, setAskLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setText("");
    setStatus("");
    setFeedback(null);
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    setFile(null);
    setStatus("");
    setFeedback(null);
  };

  const submitResume = async () => {
    if (!file && !text.trim()) {
      setStatus("Please upload a file or paste resume text before submitting.");
      return;
    }

    setLoading(true);
    setStatus("Reviewing your resume...");
    setFeedback(null);

    // build a form payload since the backend expects multipart/form-data
    const formData = new FormData();
    if (file) {
      formData.append("file", file);
    } else {
      formData.append("text", text);
    }

    try {
      const res = await fetch("http://localhost:8000/review", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        setStatus(`Error: ${err.detail}`);
        return;
      }

      const data = await res.json();
      setFeedback(data.sections);
      setResumeContext(file ? `File: ${file.name}` : text);  // save resume for follow-up questions
      setStatus(`Reviewed ${Object.keys(data.sections).length} sections.`);
    } catch (err) {
      setStatus("Could not connect to the backend. Make sure it is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const askLLM = async () => {
    if (!question.trim()) return;
    setAskLoading(true);
    setAnswer("");
    setAnswerIsWarning(false);

    const formData = new FormData();
    formData.append("question", question);
    formData.append("context", resumeContext);

    try {
      const res = await fetch("http://localhost:8000/ask", { method: "POST", body: formData });
      const data = await res.json();
      const isOffTopic = data.answer?.toLowerCase().includes("please ask a question related to your resume");
      setAnswerIsWarning(isOffTopic);
      setAnswer(data.answer);
    } catch {
      setAnswer("Could not reach the backend.");
    } finally {
      setAskLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f5f5f5", fontFamily: "'Segoe UI', Arial, sans-serif" }}>

      {/* header */}
      <div style={{ backgroundColor: "#1a1a2e", padding: "2.5rem 1rem", textAlign: "center" }}>
        <h1 style={{ color: "white", margin: 0, fontSize: "2.2rem", fontWeight: 700 }}>AI Resume Reviewer</h1>
        <p style={{ color: "#a0a8c0", marginTop: "0.5rem", fontSize: "1rem" }}>
          Upload your resume and get section-by-section AI feedback
        </p>
      </div>

      <div style={{ maxWidth: 780, margin: "2rem auto", padding: "0 1rem" }}>

        {/* upload card */}
        <div style={{ backgroundColor: "white", borderRadius: 10, padding: "1.5rem", marginBottom: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem", color: "#1a1a2e", textAlign: "center" }}>Upload Resume</h2>
          <div style={{ textAlign: "center" }}>
          <label style={{
            display: "inline-block",
            padding: "0.6rem 1.2rem",
            backgroundColor: "#2563eb",
            color: "white",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: "0.9rem",
            fontWeight: 600,
            marginBottom: "0.5rem",
          }}>
            {file ? "Change File" : "Choose File"}
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
          </label>
          {file && <p style={{ color: "#555", fontSize: "0.85rem", marginTop: "0.4rem" }}>Selected: <strong>{file.name}</strong></p>}
          </div>

          <div style={{ textAlign: "center", color: "#aaa", margin: "1rem 0", fontSize: "0.85rem" }}>— or paste text below —</div>

          <textarea
            value={text}
            onChange={handleTextChange}
            placeholder="Paste your resume text here..."
            rows={10}
            style={{ width: "100%", padding: "0.75rem", fontSize: "0.9rem", border: "1px solid #ddd", borderRadius: 6, boxSizing: "border-box", resize: "vertical" }}
          />
        </div>

        {/* submit button */}
        <button
          onClick={submitResume}
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.9rem",
            fontSize: "1rem",
            fontWeight: "bold",
            color: "white",
            backgroundColor: loading ? "#7a9fcc" : "#2563eb",
            border: "none",
            borderRadius: 8,
            cursor: loading ? "not-allowed" : "pointer",
            marginBottom: "1.5rem",
            transition: "background-color 0.2s",
          }}
        >
          {loading ? "Reviewing..." : "Review My Resume"}
        </button>

        {/* status */}
        {status && (
          <p style={{ textAlign: "center", color: "#555", marginBottom: "1rem", fontSize: "0.9rem" }}>
            {status}
          </p>
        )}

        {/* feedback cards */}
        {feedback && Object.entries(feedback).sort(([a], [b]) => a === "other" ? 1 : b === "other" ? -1 : 0).map(([section, sectionText]) => (
          <div key={section} style={{ backgroundColor: "white", borderRadius: 10, padding: "1.5rem", marginBottom: "1rem", boxShadow: "0 2px 8px rgba(0,0,0,0.08)", borderLeft: "4px solid #2563eb" }}>
            <h3 style={{ marginTop: 0, textTransform: "capitalize", color: "#1a1a2e", fontSize: "1rem" }}>{section}</h3>
            <div>{renderFeedback(sectionText)}</div>
          </div>
        ))}

        {/* suggestion box — only show after a review is done */}
        {feedback && (
          <div style={{ backgroundColor: "white", borderRadius: 10, padding: "1.5rem", marginTop: "1rem", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
            <h3 style={{ marginTop: 0, color: "#1a1a2e", fontSize: "1rem" }}>Ask a follow-up question</h3>
            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="e.g. How can I improve my experience section?"
              rows={3}
              style={{ width: "100%", padding: "0.75rem", fontSize: "0.9rem", border: "1px solid #ddd", borderRadius: 6, boxSizing: "border-box", resize: "vertical", marginBottom: "0.75rem" }}
            />
            <button
              onClick={askLLM}
              disabled={askLoading}
              style={{ padding: "0.6rem 1.4rem", backgroundColor: askLoading ? "#7a9fcc" : "#2563eb", color: "white", border: "none", borderRadius: 6, fontWeight: 600, cursor: askLoading ? "not-allowed" : "pointer" }}
            >
              {askLoading ? "Thinking..." : "Ask"}
            </button>

            {answer && (
              <div style={{
                marginTop: "1rem", padding: "1rem", borderRadius: 6,
                backgroundColor: answerIsWarning ? "#fff8e1" : "#f0f4ff",
                borderLeft: `4px solid ${answerIsWarning ? "#f59e0b" : "#2563eb"}`,
              }}>
                <div>{renderFeedback(answer)}</div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
