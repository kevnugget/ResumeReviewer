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
      setFeedback(data.sections);  // sections is a dict of section -> feedback string
      setStatus(`Done! Reviewed ${Object.keys(data.sections).length} sections.`);
    } catch (err) {
      setStatus("Could not connect to the backend. Make sure it is running on port 8000.");
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "2rem auto", padding: "1.5rem", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ textAlign: "center" }}>AI Resume Optimizer</h1>
      <p style={{ textAlign: "center", color: "#666" }}>
        Upload your resume file or paste text below to get AI-powered optimization suggestions.
      </p>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>1. Upload Resume (DOCX / PDF / TXT)</h2>
        <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileChange} />
        {file && <p>Selected file: <strong>{file.name}</strong></p>}
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>2. Or paste your resume text</h2>
        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Paste your resume text here..."
          rows={12}
          style={{ width: "100%", padding: "0.75rem", fontSize: "0.95rem", borderColor: "#ccc", borderRadius: 5 }}
        />
      </section>

      <button
        onClick={submitResume}
        style={{
          width: "100%",
          padding: "0.85rem 1.2rem",
          fontSize: "1rem",
          fontWeight: "bold",
          color: "white",
          backgroundColor: "#007bff",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        Optimize Resume
      </button>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Status</h2>
        <p><strong>{status || "Ready"}</strong></p>

        {/* render each section's feedback as its own card */}
        {feedback && Object.entries(feedback).map(([section, text]) => (
          <div key={section} style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ddd", borderRadius: 6, backgroundColor: "#f9f9f9" }}>
            <h3 style={{ textTransform: "capitalize", marginTop: 0 }}>{section}</h3>
            <div>{renderFeedback(text)}</div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default App;
