import { motion } from "framer-motion";
import {
  FaArrowRight,
  FaBookOpen,
  FaCalculator,
  FaFlask,
  FaLeaf,
} from "react-icons/fa";
import Navbar from "../components/Navbar";
import "./dashboard.css";

// Temporary mock data until login and teacher APIs are connected.
const teacher = {
  name: "Farida",
  subjects: [
    {
      id: "german",
      name: "German",
      description: "German language exams",
      icon: FaBookOpen,
    },
    {
      id: "biology",
      name: "Biology",
      description: "Biology exams",
      icon: FaLeaf,
    },
    {
      id: "chemistry",
      name: "Chemistry",
      description: "Chemistry exams",
      icon: FaFlask,
    },
    {
      id: "math",
      name: "Mathematics",
      description: "Mathematics exams",
      icon: FaCalculator,
    },
  ],
};

export default function DashboardPage() {
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
              Hello, <span>{teacher.name}</span> 👋
            </h1>
            <p>Choose one of your subjects to start correcting exams.</p>
          </div>

          {/* <div className="dashboard-summary">
            <strong>{teacher.subjects.length}</strong>
            <span>Assigned subjects</span>
          </div> */}
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
            {teacher.subjects.map((subject, index) => {
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

                  {/* Add the upload navigation later when that flow is ready. */}
                  <button type="button" className="start-correcting-btn">
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