import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const statusInfo = {
  Uploaded: {
    title: "📄 We got your exam!",
    description:
      "Your exam has arrived safely and is ready to be checked.",
  },

  Processing: {
    title: "👀 Hmm...Looking through your answers",
    description:
      "We're carefully reading each page of your exam.",
  },

  "OCR Complete": {
    title: "🧠 Understanding your work",
    description:
      "Taking time to understand everything you've written.",
  },

  Grading: {
    title: "✏️ Checking your answers",
    description:
      "Hmm... let's see your answers. Someone seems a little nervous! 😊",
  },

  Completed: {
    title: "✨ Preparing your results",
    description:
      "Everything is coming together nicely.",
  },

  Reviewed: {
    title: "📝 Final Review",
    description:
      "Your teacher is reviewing your results.",
  },

  Released: {
    title: "🎉 Knock, knock!",
    description:
      "Who's there? Your results! Are you ready to see how great you did?",
  },

  Failed: {
    title: "❌ Something went wrong",
    description:
      "Please try uploading your exam again.",
  },
};

const facts = [
  "🦒 A giraffe's tongue can be almost 50 cm long.",
  "🐙 An octopus has three hearts.",
  "🧠 Your brain has about 86 billion neurons.",
  "🌍 Earth travels around the Sun at about 107,000 km/h.",
  "🍯 Honey never spoils.",
  "🐧 Penguins often give pebbles as gifts.",
  "🌱 Every huge tree started as a tiny seed.",
  "🐝 Bees communicate by dancing.",
  "🌈 Rainbows are actually complete circles.",
  "💧 About 60% of the human body is water.",
];

const styles = `
*{
box-sizing:border-box;
font-family:'Segoe UI',sans-serif;
}

body{
margin:0;
background:#f8f8f8;
}

.processing-page{
min-height:100vh;
display:flex;
justify-content:center;
align-items:center;
padding:40px 20px;
background:
linear-gradient(rgba(255,255,255,.88),rgba(255,255,255,.88)),
url("https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1500&q=80");
background-size:cover;
background-position:center;
}

.card{
width:100%;
max-width:820px;
background:white;
padding:45px;
border-radius:24px;
box-shadow:0 15px 40px rgba(0,0,0,.12);
text-align:center;
}

.flag{
display:flex;
height:10px;
border-radius:20px;
overflow:hidden;
margin-bottom:30px;
}

.black{flex:1;background:#000;}
.red{flex:1;background:#d40000;}
.gold{flex:1;background:#ffcc00;}

h1{
margin:0;
font-size:34px;
color:#222;
}

.subtitle{
color:#666;
margin-top:12px;
margin-bottom:35px;
font-size:18px;
}

.progress-container{
width:100%;
height:18px;
background:#ececec;
border-radius:20px;
overflow:hidden;
margin-bottom:15px;
}

.progress{
height:100%;
background:linear-gradient(90deg,#000,#d40000,#ffcc00);
transition:width .8s ease;
}

.percent{
font-size:32px;
font-weight:700;
color:#d40000;
margin-bottom:35px;
}

.status-box{
padding:25px;
border-radius:18px;
background:#fafafa;
border-left:6px solid #d40000;
margin-bottom:35px;
text-align:left;
}

.status-box h2{
margin:0 0 10px;
font-size:24px;
color:#222;
}

.status-box p{
margin:0;
font-size:17px;
line-height:1.7;
color:#555;
}

.fact-box{
margin-top:20px;
background:#fff8e8;
padding:22px;
border-radius:16px;
border:1px solid #ffd54d;
}

.fact-title{
font-size:20px;
font-weight:700;
margin-bottom:12px;
color:#b8860b;
}

.fact{
font-size:18px;
line-height:1.6;
color:#444;
min-height:60px;
}

.loader{
margin:35px auto;
width:65px;
height:65px;
border-radius:50%;
border:6px solid #eee;
border-top:6px solid #d40000;
animation:spin 1s linear infinite;
}

@keyframes spin{
100%{
transform:rotate(360deg);
}
}

@media(max-width:768px){

.card{
padding:28px;
}

h1{
font-size:28px;
}

.status-box h2{
font-size:21px;
}

.fact{
font-size:16px;
}

.percent{
font-size:28px;
}

}
`;

export default function ProcessingPage() {
const { submissionId } = useParams();

const [status, setStatus] = useState("Uploaded");
const [progress, setProgress] = useState(0);

const [factIndex, setFactIndex] = useState(0);
 useEffect(() => {

  const loadProgress = async () => {

    try {

      const response = await axios.get(
        `http://localhost:8000/submission/${submissionId}`
      );

      setStatus(response.data.status);
      setProgress(response.data.progress);

      if (response.data.status === "Released") {
      navigate(`/results/${submissionId}`);}
      

    } catch (error) {

      console.log(error);

    }

  };

  loadProgress();

  const progressTimer = setInterval(loadProgress, 2000);

  const factTimer = setInterval(() => {

    setFactIndex((prev) => (prev + 1) % facts.length);

  }, 7000);

  return () => {

    clearInterval(progressTimer);
    clearInterval(factTimer);

  };

}, [submissionId]);

  return(

<>
<style>{styles}</style>

<div className="processing-page">

<div className="card">

<div className="flag">

<div className="black"></div>
<div className="red"></div>
<div className="gold"></div>

</div>

<h1>Processing Your Exam</h1>

<p className="subtitle">
Please stay on this page while we prepare your results.
</p>

<div className="loader"></div>

<div className="progress-container">

<div
className="progress"
style={{ width: `${progress}%` }}
></div>

</div>

<div className="percent">

{progress}%

</div>

<div className="status-box">

<h2>{statusInfo[status]?.title}</h2>
<p>{statusInfo[status]?.description}</p>

</div>

<div className="fact-box">

<div className="fact-title">

🌟 Did You Know?

</div>

<div className="fact">

{facts[factIndex]}

</div>

</div>

</div>

</div>

</>

);

}