
import React, { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setStatus("");
    setResult("");
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    setFile(null);
    setStatus("");
    setResult("");
  };

  const submitResume = async () => {
    setStatus("Processing...");
    setResult("");

    try {
      const formData = new FormData();
      if (file) {
        formData.append("resume_file", file);
      }
      if (text.trim()) {
        formData.append("resume_text", text.trim());
      }

      if (!file && !text.trim()) {
        setStatus("Failed");
        setResult("Please upload a file or paste resume text before submitting.");
        return;
      }

      const uploadedSource = file ? `File: ${file.name}` : "Text input";
      setResult(
        `✅ Resume received from ${uploadedSource}.\n\n💡 Suggested optimization: Add a clear profile summary, use consistent bullet points, and ensure keyword alignment with job description. (This is a frontend demo value.)`
      );
      setStatus("Success");
    } catch (error) {
      setStatus("Error");
      setResult(error.message || "Unexpected error. Please retry.");
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
        <div style={{ padding: "0.8rem", backgroundColor: "#f9f9f9", borderRadius: 5, border: "1px solid #ddd" }}>
          <p><strong>{status || "Ready"}</strong></p>
          <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{result || "No output yet."}</pre>
        </div>
      </section>
    </div>
  );
}