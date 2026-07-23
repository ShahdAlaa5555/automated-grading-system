import { useState } from "react";
import "./App.css";
import diskLogo from "./assets/disk-logo.png";
import axios from "axios";

const subjectEndpoints = {
  chemistry: "http://127.0.0.1:8000/upload",
  math: "http://127.0.0.1:8000/math/upload",
  biology: "http://127.0.0.1:8000/biology/upload",
  german: "http://127.0.0.1:8000/german/upload",
};

const normalizeResults = (payload) => {
  const results = Array.isArray(payload?.results)
    ? payload.results
    : Array.isArray(payload?.questions)
      ? payload.questions
      : [];

  const questions = results.map((item, index) => ({
    number: item?.number ?? index + 1,
    type: item?.type ?? "short",
    title: item?.title ?? item?.question ?? `Question ${index + 1}`,
    score: item?.score ?? item?.marks ?? item?.points ?? "—",
    feedback: item?.feedback ?? item?.comment ?? item?.reason ?? "No feedback available.",
    correctAnswer: item?.correctAnswer ?? item?.correct_answer ?? "—",
    studentAnswer: item?.studentAnswer ?? item?.student_answer ?? "—",
  }));

  return {
    summary:
      payload?.summary ??
      payload?.message ??
      payload?.feedback ??
      "The exam has been processed successfully.",
    overallScore:
      payload?.overallScore ?? payload?.score ?? payload?.totalScore ?? null,
    totalPossible:
      payload?.totalPossible ?? payload?.maxScore ?? payload?.totalPossibleScore ?? null,
    extractedText: payload?.extractedText ?? payload?.text ?? "",
    questions,
  };
};

const buildMockResult = (subject, fileName) => ({
  summary: `Demo grading preview for the ${subject} exam. The frontend is ready to display real feedback once the backend is connected.`,
  overallScore: 18,
  totalPossible: 20,
  extractedText: `Sample extracted text from ${fileName}:\n1. Describe the main process and its outcome.\n2. Choose the correct answer for the diagram-based question.`,
  questions: [
    {
      number: 1,
      type: "short",
      title: "Describe the main process and its outcome.",
      score: "2/3",
      feedback: "Your explanation shows the right idea, but you can add one more supporting detail to make the answer fully complete.",
      correctAnswer: "A valid scientific explanation with the main stage and outcome.",
      studentAnswer: "The process is mostly explained, but the result is only partially connected.",
    },
    {
      number: 2,
      type: "mcq",
      title: "Choose the correct answer for the diagram-based question.",
      score: "1/1",
      feedback: "Good job — the selected option matches the correct interpretation of the diagram.",
      correctAnswer: "B",
      studentAnswer: "B",
    },
  ],
});

function App() {
  const [subject, setSubject] = useState("");
  const [submittedSubject, setSubmittedSubject] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];

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
      setError("Please upload a file.");
      return;
    }

    if (!subjectEndpoints[subject]) {
      setError("This subject is not implemented yet.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSubmittedSubject(subject);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(subjectEndpoints[subject], formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = normalizeResults(response?.data ?? {});
      setResult(data);
    } catch (caughtError) {
      console.error(caughtError);
      setResult(buildMockResult(subject, file.name));
      setError("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <img src={diskLogo} alt="DISK" className="logo" />

        <h1>Automated Grading System</h1>
        <p className="subtitle">AI-powered Exam Evaluation</p>

        <div className="flag" aria-hidden="true">
          <div className="black"></div>
          <div className="red"></div>
          <div className="yellow"></div>
        </div>

        <div className="form-grid">
          <div className="demo-note">Demo before the backend is connected.</div>

          <label htmlFor="subject">Subject</label>
          <select
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          >
            <option value="">Select Subject</option>
            <option value="chemistry">Chemistry</option>
            <option value="math">Math</option>
            <option value="biology">Biology</option>
            <option value="german">German</option>
          </select>

          <label htmlFor="exam-file">Upload Exam</label>
          <input
            id="exam-file"
            type="file"
            accept=".pdf,image/*"
            onChange={handleFileChange}
          />

          {file && (
            <p className="selected">
              <strong>Selected File:</strong>
              <br />
              {file.name}
            </p>
          )}

          {error && <div className="error-box">{error}</div>}

          <button disabled={!subject || !file || loading} onClick={handleUpload}>
            {loading ? "Grading..." : "Start Grading"}
          </button>
        </div>

        {result && (
          <section className="results-panel">
            <div className="results-header">
              <div>
                <p className="eyebrow">Results & Feedback</p>
                <h2>{submittedSubject ? submittedSubject.toUpperCase() : "Exam"} Summary</h2>
              </div>
              {result.overallScore !== null && result.totalPossible !== null && (
                <div className="score-badge">
                  {result.overallScore}/{result.totalPossible}
                </div>
              )}
            </div>

            <div className="summary-card">
              <strong>Assessment:</strong>
              <p>{result.summary}</p>
            </div>

            {result.extractedText && (
              <div className="summary-card">
                <strong>Extracted Text:</strong>
                <p className="text-preview">{result.extractedText}</p>
              </div>
            )}

            {result.questions.length > 0 ? (
              <div className="question-list">
                {result.questions.map((item) => (
                  <article key={`${item.number}-${item.title}`} className="question-card">
                    <div className="question-topline">
                      <span className="question-number">Q{item.number}</span>
                      <span className="question-type">{item.type}</span>
                    </div>

                    <h3>{item.title}</h3>

                    <div className="detail-grid">
                      <div>
                        <strong>Score:</strong>
                        <p>{item.score}</p>
                      </div>
                      <div>
                        <strong>Student Answer:</strong>
                        <p>{item.studentAnswer}</p>
                      </div>
                      <div>
                        <strong>Correct Answer:</strong>
                        <p>{item.correctAnswer}</p>
                      </div>
                    </div>

                    <div className="feedback-box">
                      <strong>Feedback:</strong>
                      <p>{item.feedback}</p>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="summary-card empty-state">
                <p>No question-by-question results were returned yet.</p>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}

export default App;