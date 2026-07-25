// UploadPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function UploadPage() {
  const navigate = useNavigate();

  const [subject, setSubject] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const endpoints = {
    chemistry: "http://localhost:8000/chemistry/upload",
    math: "http://localhost:8000/math/upload",
    biology: "http://localhost:8000/biology/upload",
    german: "http://localhost:8000/german/upload",
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setError("");
  };

  const handleUpload = async () => {
    if (!subject) {
      setError("Please select a subject.");
      return;
    }

    if (!file) {
      setError("Please select a file.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(endpoints[subject], formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      navigate("/processing");
    } catch (err) {
  console.error("Upload Error:", err);

  if (err.response) {
    console.log("Status:", err.response.status);
    console.log("Data:", err.response.data);
  }

  setError("Upload failed. Please try again.");
}
    
  };

  return (
    <div
      style={{
        width: "500px",
        margin: "50px auto",
        padding: "30px",
        border: "1px solid #ddd",
        borderRadius: "12px",
        textAlign: "center",
      }}
    >
      <h1>AI Exam Grader</h1>

      <div style={{ marginBottom: "20px" }}>
        <label>Subject</label>

        <br />

        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "10px",
          }}
        >
          <option value="">Select Subject</option>
          <option value="chemistry">Chemistry</option>
          <option value="math">Math</option>
          <option value="biology">Biology</option>
          <option value="german">German</option>
        </select>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <label>Upload Exam</label>

        <br />

        <input
          type="file"
          accept=".pdf,image/*"
          onChange={handleFileChange}
          style={{ marginTop: "10px" }}
        />
      </div>

      {file && (
        <div style={{ marginBottom: "20px" }}>
          <strong>Selected File:</strong>

          <br />

          {file.name}
        </div>
      )}

      {error && (
        <div
          style={{
            color: "red",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      <button
        disabled={!subject || !file || loading}
        onClick={handleUpload}
        style={{
          width: "100%",
          padding: "12px",
          cursor: "pointer",
        }}
      >
        {loading ? "Uploading..." : "Start Grading"}
      </button>
    </div>
  );
}