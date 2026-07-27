// UploadPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import "../App.css";
import diskLogo from "../assets/disk-logo.png";

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
      const response = await axios.post(
        endpoints[subject],
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const submissionId = response.data.submission_id;

      navigate(`/processing/${submissionId}`);
    } catch (err) {
      console.error("Upload Error:", err);

      if (err.response) {
        console.log("Status:", err.response.status);
        console.log("Data:", err.response.data);
      }

      setError("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <img
          src={diskLogo}
          alt="DISK"
          className="logo"
        />

        <h1>Automated Grading System</h1>

        <p className="subtitle">
          AI-powered Exam Evaluation
        </p>

        <div className="flag">
          <div className="black"></div>
          <div className="red"></div>
          <div className="yellow"></div>
        </div>

        <label>
          Subject
        </label>

        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        >
          <option value="">
            Select Subject
          </option>

          <option value="chemistry">
            Chemistry
          </option>

          <option value="biology">
            Biology
          </option>

          <option value="math">
            Math
          </option>

          <option value="german">
            German
          </option>
        </select>

        <label>
          Upload Exam
        </label>

        <input
          type="file"
          accept=".pdf,image/*"
          onChange={handleFileChange}
        />

        {file && (
          <p className="selected">
            Selected File:
            <br />
            {file.name}
          </p>
        )}

        {error && (
          <p
            style={{
              color: "red",
              marginTop: "10px",
            }}
          >
            {error}
          </p>
        )}

        <button
          disabled={!subject || !file || loading}
          onClick={handleUpload}
        >
          {loading ? "Uploading..." : "Start Grading"}
        </button>
      </div>
    </div>
  );
}