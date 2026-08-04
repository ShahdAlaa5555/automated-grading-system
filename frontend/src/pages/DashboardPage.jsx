import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  FaArrowRight,
  FaBookOpen,
  FaCalculator,
  FaFlask,
  FaLeaf,
  FaLaptop,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "./dashboard.css";

const subjectCatalog = {
  german: { name: "German", description: "German language exams", icon: FaBookOpen },
  biology: { name: "Biology", description: "Biology exams", icon: FaLeaf },
  chemistry: { name: "Chemistry", description: "Chemistry exams", icon: FaFlask },
  math: { name: "Mathematics", description: "Mathematics exams", icon: FaCalculator },
  mathematics: { name: "Mathematics", description: "Mathematics exams", icon: FaCalculator },
  physics: { name: "Physics", description: "Physics exams", icon: FaLaptop },
  "computer science": { name: "Computer Science", description: "Computer science exams", icon: FaLaptop },
};

function getSubjectCard(subject) {
  if (typeof subject === "string") {
    const normalizedSubject = subject.trim().toLowerCase();
    const catalogEntry = subjectCatalog[normalizedSubject] || subjectCatalog[normalizedSubject.replace(/\s+/g, "")];

    if (catalogEntry) {
      return {
        id: normalizedSubject,
        name: catalogEntry.name,
        description: catalogEntry.description,
        icon: catalogEntry.icon,
      };
    }

    return {
      id: normalizedSubject,
      name: subject,
      description: "Teacher-led assessment", 
      icon: FaBookOpen,
    };
  }

  return {
    id: subject.id || subject.name,
    name: subject.name,
    description: subject.description || "Teacher-led assessment",
    icon: subject.icon || FaBookOpen,
  };
}

export default function DashboardPage() {
  const [teacher, setTeacher] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const savedTeacher = localStorage.getItem("teacherProfile");

    if (!savedTeacher) {
      navigate("/login");
      return;
    }

    try {
      setTeacher(JSON.parse(savedTeacher));
    } catch (error) {
      console.error("Failed to parse saved teacher profile", error);
      navigate("/login");
    }
  }, [navigate]);

  if (!teacher) {
    return null;
  }

  const subjects = Array.isArray(teacher.subjects) ? teacher.subjects : [];
  const subjectCards = subjects.map((subject) => getSubjectCard(subject));

  return (
    <div className="dashboard-page">
      <Navbar teacherName={teacher.name} />

      <main className="dashboard-main">
        <motion.section
          className="dashboard-welcome"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="dashboard-welcome__text">
            <p className="dashboard-eyebrow">Teacher dashboard</p>
            <h1>
              Hello <span>{teacher.name.split(" ")[0]}!</span>
            </h1>
            <p>Choose one of your subjects to start correcting exams.</p>
          </div>

          <div className="dashboard-summary">
            <strong>{subjectCards.length}</strong>
            <span>Subjects assigned</span>
          </div>
        </motion.section>

        <section className="subjects-section" aria-labelledby="subjects-title">
          <div className="subjects-heading">
            <div>
              <h2 id="subjects-title">Your classes</h2>
            </div>

            <div className="german-accent" aria-hidden="true">
              <span className="german-accent__black" />
              <span className="german-accent__red" />
              <span className="german-accent__yellow" />
            </div>
          </div>

          <div className="subjects-grid">
            {subjectCards.map((subject, index) => {
              const SubjectIcon = subject.icon;

              return (
                <motion.article
                  key={subject.id}
                  className="subject-card"
                  initial={{ opacity: 0, y: 28 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45, delay: 0.12 * index }}
                  whileHover={{ y: -5 }}
                >
                  <div className="subject-card__top">
                    <div className="subject-icon" aria-hidden="true">
                      <SubjectIcon />
                    </div>
                    <span className="subject-status">Ready</span>
                  </div>

                  <div className="subject-card__content">
                    <h3>{subject.name}</h3>
                    <p>{subject.description}</p>
                  </div>

                  <button
                    type="button"
                    className="start-correcting-btn"
                    onClick={() =>
                      navigate("/upload", {
                        state: {
                         subject: subject.id,
                        },
               })
              }
           >
              Start correcting
              <FaArrowRight />
              </button>
                </motion.article>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
}