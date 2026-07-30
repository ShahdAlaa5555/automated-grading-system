import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

// Point this at your FastAPI backend. Set VITE_API_URL in your .env file,
// e.g. VITE_API_URL=http://localhost:8000
const API_URL = "http://localhost:8000";

const styles = `
.results-page{
    min-height:100vh;
    background:
    radial-gradient(circle at top left, rgba(221,0,0,.06), transparent 40%),
    radial-gradient(circle at bottom right, rgba(255,206,0,.1), transparent 40%),
    #FAFAFA;
    padding:110px 20px 80px;
    font-family:'Poppins',sans-serif;
}

.rp-container{
    max-width:820px;
    margin:0 auto;
}

.rp-eyebrow{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:8px;
    font-size:13px;
    font-weight:600;
    letter-spacing:.06em;
    text-transform:uppercase;
    color:#DD0000 !important;
    margin-bottom:10px;
}

.rp-dot{
    width:7px;
    height:7px;
    border-radius:50%;
    background:#FFCE00;
    animation:pulse 1.8s ease-in-out infinite;
}

@keyframes pulse{
    0%,100%{ opacity:1; transform:scale(1); }
    50%{ opacity:.4; transform:scale(.7); }
}

.rp-meta{
    text-align:center;
    margin-bottom:36px;
}

.rp-meta h1{
    font-size:28px;
    font-weight:700;
    color:#222 !important;
    margin-bottom:6px;
}

.rp-meta p{
    font-size:14.5px;
    color:#888 !important;
}

.rp-meta .subject-pill{
    display:inline-block;
    margin-top:10px;
    padding:5px 14px;
    border-radius:20px;
    font-size:12.5px;
    font-weight:500;
    background:rgba(34,34,34,.06);
    color:#444 !important;
}

.summary-card{
    background:#fff;
    border-radius:24px;
    box-shadow:0 20px 50px rgba(0,0,0,.06);
    padding:32px;
    display:flex;
    align-items:center;
    gap:28px;
    margin-bottom:36px;
}

.summary-ring{
    position:relative;
    width:96px;
    height:96px;
    flex-shrink:0;
}

.summary-ring svg{
    transform:rotate(-90deg);
}

.summary-ring-bg{
    fill:none;
    stroke:#f0f0f0;
    stroke-width:8;
}

.summary-ring-fill{
    fill:none;
    stroke-width:8;
    stroke-linecap:round;
    transition:stroke-dasharray 1s ease;
}

.summary-ring-text{
    position:absolute;
    inset:0;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
    font-weight:700;
    color:#222 !important;
}

.summary-body h2{
    font-size:18px;
    font-weight:600;
    color:#222 !important;
    margin-bottom:4px;
}

.summary-body p{
    font-size:14px;
    color:#888 !important;
}

.q-list{
    display:flex;
    flex-direction:column;
    gap:16px;
}

.q-card{
    background:#fff;
    border-radius:20px;
    box-shadow:0 12px 30px rgba(0,0,0,.05);
    padding:24px 26px;
    border-left:4px solid #eee;
    transition:border-color .3s ease;
}

.q-card.correct{
    border-left-color:#222;
}

.q-card.incorrect{
    border-left-color:#DD0000;
}

.q-top{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
    margin-bottom:14px;
}

.q-number{
    display:flex;
    align-items:center;
    gap:10px;
    flex-wrap:wrap;
}

.q-number span:first-child{
    font-size:12px;
    font-weight:700;
    color:#aaa !important;
    letter-spacing:.05em;
}

.verdict-badge{
    display:inline-flex;
    align-items:center;
    gap:5px;
    padding:4px 11px;
    border-radius:20px;
    font-size:12px;
    font-weight:600;
}

.verdict-badge.correct{
    background:rgba(34,34,34,.08);
    color:#222 !important;
}

.verdict-badge.incorrect{
    background:rgba(221,0,0,.1);
    color:#DD0000 !important;
}

.edited-tag{
    font-size:11px;
    color:#c99b00 !important;
    background:rgba(255,206,0,.15);
    padding:3px 9px;
    border-radius:20px;
    font-weight:500;
}

.edit-btn{
    background:none;
    border:1px solid #eee;
    border-radius:20px;
    padding:6px 14px;
    font-size:12.5px;
    font-weight:500;
    color:#666;
    cursor:pointer;
    transition:.2s;
    white-space:nowrap;
    font-family:'Poppins',sans-serif;
}

.edit-btn:hover{
    border-color:#FFCE00;
    background:rgba(255,206,0,.08);
}

.edit-btn:disabled{
    opacity:.5;
    cursor:not-allowed;
}

.q-text{
    font-size:15.5px;
    font-weight:500;
    color:#222 !important;
    line-height:1.5;
    margin-bottom:14px;
}

.answer-box{
    background:#FAFAFA;
    border-radius:12px;
    padding:12px 16px;
    margin-bottom:14px;
}

.answer-box span{
    font-size:11.5px;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:.04em;
    color:#aaa !important;
    display:block;
    margin-bottom:4px;
}

.answer-box p{
    font-size:14.5px;
    color:#444 !important;
}

.feedback-text{
    font-size:14.5px;
    color:#555 !important;
    line-height:1.6;
    padding-left:14px;
    border-left:2px solid #FFCE00;
}

.edit-panel{
    margin-top:14px;
    padding-top:16px;
    border-top:1px solid #f0f0f0;
    display:flex;
    flex-direction:column;
    gap:12px;
    overflow:hidden;
}

.verdict-toggle{
    display:flex;
    gap:8px;
}

.verdict-toggle button{
    flex:1;
    padding:9px;
    border-radius:12px;
    border:1.5px solid #eee;
    background:#fff;
    font-size:13px;
    font-weight:600;
    font-family:'Poppins',sans-serif;
    cursor:pointer;
    transition:.2s;
    color:#999;
}

.verdict-toggle button.active.correct{
    border-color:#222;
    background:rgba(34,34,34,.06);
    color:#222;
}

.verdict-toggle button.active.incorrect{
    border-color:#DD0000;
    background:rgba(221,0,0,.06);
    color:#DD0000;
}

.edit-panel textarea{
    width:100%;
    min-height:80px;
    border-radius:12px;
    border:1.5px solid #eee;
    padding:12px 14px;
    font-family:'Poppins',sans-serif;
    font-size:14px;
    color:#333;
    resize:vertical;
    outline:none;
    box-sizing:border-box;
}

.edit-panel textarea:focus{
    border-color:#FFCE00;
}

.edit-error{
    font-size:12.5px;
    color:#DD0000 !important;
}

.edit-actions{
    display:flex;
    justify-content:flex-end;
    gap:8px;
}

.edit-actions button{
    padding:9px 20px;
    border-radius:20px;
    font-size:13px;
    font-weight:600;
    font-family:'Poppins',sans-serif;
    cursor:pointer;
    border:none;
    transition:.2s;
}

.edit-actions button:disabled{
    opacity:.6;
    cursor:not-allowed;
}

.cancel-btn{
    background:#f4f4f4;
    color:#666;
}

.cancel-btn:hover{
    background:#eee;
}

.save-btn{
    background:#FFCE00;
    color:#fff;
}

.save-btn:hover{
    background:#DD0000;
}

/* ---- status states ---- */

.status-page{
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#FAFAFA;
    padding:40px 20px;
    font-family:'Poppins',sans-serif;
    text-align:center;
}

.status-card{
    background:#fff;
    border-radius:24px;
    box-shadow:0 20px 50px rgba(0,0,0,.06);
    padding:40px 32px;
    max-width:380px;
    width:100%;
}

.status-spinner{
    width:36px;
    height:36px;
    border-radius:50%;
    border:3px solid #f0f0f0;
    border-top-color:#FFCE00;
    margin:0 auto 20px;
    animation:spin .8s linear infinite;
}

@keyframes spin{
    to{ transform:rotate(360deg); }
}

.status-card h2{
    font-size:17px;
    font-weight:600;
    color:#222 !important;
    margin-bottom:8px;
}

.status-card p{
    font-size:14px;
    color:#888 !important;
    margin-bottom:20px;
}

.status-card .retry-btn{
    background:#DD0000;
    color:#fff;
    border:none;
    padding:10px 22px;
    border-radius:20px;
    font-size:13.5px;
    font-weight:600;
    font-family:'Poppins',sans-serif;
    cursor:pointer;
    transition:.2s;
}

.status-card .retry-btn:hover{
    background:#c40000;
}

/* ---- responsive: mobile-first tightening ---- */

@media(max-width:600px){
    .results-page{
        padding:90px 14px 60px;
    }
    .summary-card{
        flex-direction:column;
        text-align:center;
        padding:26px 22px;
    }
    .q-top{
        flex-direction:column;
    }
    .q-card{
        padding:20px 18px;
    }
}

@media(max-width:400px){
    .rp-meta h1{
        font-size:24px;
    }
    .edit-btn{
        width:100%;
    }
    .verdict-toggle{
        flex-direction:column;
    }
}
`;

function QuestionCard({ question, onSave }) {
    const [editing, setEditing] = useState(false);
    const [draftCorrect, setDraftCorrect] = useState(question.is_correct);
    const [draftFeedback, setDraftFeedback] = useState(question.feedback);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);

    function startEdit() {
        setDraftCorrect(question.is_correct);
        setDraftFeedback(question.feedback);
        setSaveError(null);
        setEditing(true);
    }

    function cancelEdit() {
        setEditing(false);
        setSaveError(null);
    }

    async function saveEdit() {
        setSaving(true);
        setSaveError(null);
        try {
            await onSave(question.question_result_id, {
                is_correct: draftCorrect,
                feedback: draftFeedback,
            });
            setEditing(false);
        } catch (err) {
            setSaveError("Couldn't save this change. Try again.");
        } finally {
            setSaving(false);
        }
    }

    return (
        <motion.div
            className={`q-card ${question.is_correct ? "correct" : "incorrect"}`}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
        >
            <div className="q-top">
                <div className="q-number">
                    <span>Q{question.question_number}</span>
                    <span className={`verdict-badge ${question.is_correct ? "correct" : "incorrect"}`}>
                        {question.is_correct ? "Correct" : "Incorrect"}
                    </span>
                    {question.edited && <span className="edited-tag">Edited</span>}
                </div>

                {!editing && (
                    <button className="edit-btn" onClick={startEdit}>
                        Edit feedback
                    </button>
                )}
            </div>

            <p className="q-text">{question.question_text}</p>

            <div className="answer-box">
                <span>Student's answer</span>
                <p>{question.student_answer}</p>
            </div>

            {!editing && <p className="feedback-text">{question.feedback}</p>}

            <AnimatePresence>
                {editing && (
                    <motion.div
                        className="edit-panel"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.25 }}
                    >
                        <div className="verdict-toggle">
                            <button
                                type="button"
                                className={draftCorrect ? "active correct" : ""}
                                onClick={() => setDraftCorrect(true)}
                            >
                                Correct
                            </button>
                            <button
                                type="button"
                                className={!draftCorrect ? "active incorrect" : ""}
                                onClick={() => setDraftCorrect(false)}
                            >
                                Incorrect
                            </button>
                        </div>

                        <textarea
                            value={draftFeedback}
                            onChange={(e) => setDraftFeedback(e.target.value)}
                            placeholder="Write feedback for this question..."
                        />

                        {saveError && <span className="edit-error">{saveError}</span>}

                        <div className="edit-actions">
                            <button className="cancel-btn" onClick={cancelEdit} disabled={saving}>
                                Cancel
                            </button>
                            <button className="save-btn" onClick={saveEdit} disabled={saving}>
                                {saving ? "Saving..." : "Save"}
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

export default function ResultsPage() {
    const { submissionId } = useParams();

    const [submission, setSubmission] = useState(null);
const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchResults = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await axios.get(`${API_URL}/results/${submissionId}`);
            console.log("API Response:", res.data);
            setSubmission(res.data.submission);
            
            setQuestions(res.data.questions);
        } catch (err) {
            if (err.response?.status === 404) {
                setError("We couldn't find this submission.");
            } else {
                setError("Something went wrong loading these results.");
            }
        } finally {
            setLoading(false);
        }
    }, [submissionId]);

    useEffect(() => {
        fetchResults();
    }, [fetchResults]);

    async function handleSave(question_result_id, updates) {
        const previous = questions;

        // optimistic UI update
        setQuestions((prev) =>
            prev.map((q) =>
                q.question_result_id === question_result_id ? { ...q, ...updates, edited: true } : q
            )
        );

        try {
            await axios.patch(`${API_URL}/question-results/${question_result_id}`, updates);
        } catch (err) {
            // roll back on failure
            setQuestions(previous);
            throw err;
        }
    }

    if (loading) {
        return (
            <>
                <style>{styles}</style>
                <div className="status-page">
                    <div className="status-card">
                        <div className="status-spinner" />
                        <h2>Loading results</h2>
                        <p>Fetching this submission's graded questions...</p>
                    </div>
                </div>
            </>
        );
    }

    if (error) {
        return (
            <>
                <style>{styles}</style>
                <div className="status-page">
                    <div className="status-card">
                        <h2>Couldn't load results</h2>
                        <p>{error}</p>
                        <button className="retry-btn" onClick={fetchResults}>
                            Try again
                        </button>
                    </div>
                </div>
            </>
        );
    }

    const total = questions.length;
    const correctCount = questions.filter((q) => q.is_correct).length;
    const pct = total > 0 ? Math.round((correctCount / total) * 100) : 0;

    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const dash = (pct / 100) * circumference;

    return (
        <>
            <style>{styles}</style>

            <div className="results-page">
                <div className="rp-container">
                    <div className="rp-eyebrow">
                        <span className="rp-dot" />
                        AI-Reviewed Results
                    </div>

                    <div className="rp-meta">
                        <h1>{submission.student_name || "Unknown student"}</h1>
                        <p>{submission.filename}</p>
                        <span className="subject-pill">{submission.subject}</span>
                    </div>

                    <motion.div
                        className="summary-card"
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className="summary-ring">
                            <svg width="96" height="96" viewBox="0 0 96 96">
                                <circle className="summary-ring-bg" cx="48" cy="48" r={radius} />
                                <circle
                                    className="summary-ring-fill"
                                    cx="48"
                                    cy="48"
                                    r={radius}
                                    stroke="url(#ringGradient)"
                                    strokeDasharray={`${dash} ${circumference}`}
                                />
                                <defs>
                                    <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#FFCE00" />
                                        <stop offset="100%" stopColor="#DD0000" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            <div className="summary-ring-text">{pct}%</div>
                        </div>

                        <div className="summary-body">
                            <h2>
                                {correctCount} out of {total} correct
                            </h2>
                            <p>Reviewed by AI — edit any question below if needed.</p>
                        </div>
                    </motion.div>

                    <div className="q-list">
                        {questions.map((q) => (
                            <QuestionCard key={q.question_result_id} question={q} onSave={handleSave} />
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}