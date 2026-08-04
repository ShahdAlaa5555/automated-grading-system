import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

import "../upload.css";
import diskLogo from "../assets/disk-logo.png";

export default function UploadPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Subject received from Dashboard
  const rawSubject = location.state?.subject?.toLowerCase() || "";

  // Convert math to mathematics
  const subject = rawSubject === "math" ? "mathematics" : rawSubject;

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const endpoints = {
    chemistry: "http://localhost:8000/chemistry/upload",
    biology: "http://localhost:8000/biology/upload",
    mathematics: "http://localhost:8000/mathematics/upload",
    german: "http://localhost:8000/german/upload",
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setError("");
  };

  const handleUpload = async () => {
    console.log("Raw subject:", rawSubject);
    console.log("Selected subject:", subject);
    console.log("Endpoint:", endpoints[subject]);

    if (!subject) {
      setError("No subject selected.");
      return;
    }

    if (!file) {
      setError("Please select a file.");
      return;
    }

    if (!endpoints[subject]) {
      setError("Invalid subject.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();

    formData.append("file", file);
    formData.append("subject", subject);

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

      console.log("Upload response:", response.data);

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

        <h1>
          Automated Grading System
        </h1>

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


        <input
          type="text"
          value={
            subject
              ? subject.charAt(0).toUpperCase() + subject.slice(1)
              : "No Subject Selected"
          }
          readOnly
          className="subject-display"
        />


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