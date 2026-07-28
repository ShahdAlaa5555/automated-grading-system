import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import ProcessingPage from "./pages/ProcessingPage";
 import ResultsPage from "./pages/ResultsPage";
//Added by Menna: Added LoginPage import
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/processing/:submissionId" element={<ProcessingPage />} />
         <Route path="/results/:submissionId" element={<ResultsPage />} /> 
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
// import { useState } from "react";
// import "./App.css";
// import diskLogo from "./assets/disk-logo.png";
// import axios from "axios";

// function App() {
//   const [subject, setSubject] = useState("");
//   const [file, setFile] = useState(null);

//   const handleFileChange = (e) => {
//     if (e.target.files.length > 0) {
//       setFile(e.target.files[0]);
//     }
//   };

//   const handleUpload = async () => {
//     if (!subject) {
//       alert("Please select a subject.");
//       return;
//     }

//     if (!file) {
//       alert("Please upload a file.");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       const response = await axios.post(
//         `http://127.0.0.1:8000/${subject}/upload`,
//         formData,
//         {
//           headers: {
//             "Content-Type": "multipart/form-data",
//           },
//         }
//       );

//       console.log(response.data);

//       alert("Exam processed successfully!");

//     } catch (error) {
//       console.error(error);

//       if (error.response) {
//         console.log(error.response.data);
//       }

//       alert("Upload failed.");
//     }
//   };

//   return (
//     <div className="page">
//       <div className="card">

//         <img
//           src={diskLogo}
//           alt="DISK"
//           className="logo"
//         />

//         <h1>
//           Automated Grading System
//         </h1>

//         <p className="subtitle">
//           AI-powered Exam Evaluation
//         </p>


//         <div className="flag">
//           <div className="black"></div>
//           <div className="red"></div>
//           <div className="yellow"></div>
//         </div>


//         <label>
//           Subject
//         </label>

//         <select
//           value={subject}
//           onChange={(e) => setSubject(e.target.value)}
//         >
//           <option value="">
//             Select Subject
//           </option>

//           <option value="chemistry">
//             Chemistry
//           </option>

//           <option value="biology">
//             Biology
//           </option>

//           <option value="math">
//             Math
//           </option>

//           <option value="german">
//             German
//           </option>

//         </select>


//         <label>
//           Upload Exam
//         </label>

//         <input
//           type="file"
//           accept=".pdf,image/*"
//           onChange={handleFileChange}
//         />


//         {file && (
//           <p className="selected">
//             Selected File:
//             <br />
//             {file.name}
//           </p>
//         )}


//         <button
//           disabled={!subject || !file}
//           onClick={handleUpload}
//         >
//           Start Grading
//         </button>


//       </div>
//     </div>
//   );
// }

// export default App;