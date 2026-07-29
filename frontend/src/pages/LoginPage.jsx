import { useState } from "react";
import diskLogo from "../assets/disk-logo.png";
import { useNavigate } from "react-router-dom";
const styles = `
body{
    margin:0;
    background:#F5F7FA;
    font-family:Arial, Helvetica, sans-serif;
}

.login-page{
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
}

.login-card{
    width:400px;
    background:white;
    border-radius:16px;
    padding:40px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    animation:fadeIn .5s ease;
}

.login-logo{
    width:100px;
    display:block;
    margin:0 auto 20px;
}

.login-title{
    text-align:center;
    margin:0;
    color:#1F2937;
    font-size:32px;
}

.login-subtitle{
    text-align:center;
    color:#6B7280;
    margin-top:10px;
    margin-bottom:8px;
}

.portal-title{
    text-align:center;
    color:#2563EB;
    margin-bottom:30px;
    font-size:22px;
}

.login-label{
    display:block;
    font-weight:600;
    margin-bottom:8px;
    margin-top:18px;
}

.login-input{
    width:100%;
    padding:14px;
    border:1px solid #D1D5DB;
    border-radius:8px;
    font-size:16px;
    box-sizing:border-box;
}

.login-input:focus{
    outline:none;
    border-color:#2563EB;
}

.login-button{
    width:100%;
    margin-top:30px;
    padding:14px;
    border:none;
    border-radius:8px;
    background:#2563EB;
    color:white;
    font-size:16px;
    font-weight:600;
    cursor:pointer;
    transition:background .25s, transform .15s;
}

.login-button:hover{
    background:#1D4ED8;
    transform:translateY(-2px);
}

.login-button:active{
    transform:translateY(0);
}

@keyframes fadeIn{

    from{
        opacity:0;
        transform:translateY(20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }

}
`;

export default function LoginPage() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();
async function handleLogin(event) {

    event.preventDefault();

    const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                password
            })
        }
    );

    const data = await response.json();

    if (data.success) {

        alert("Login successful!");

        navigate("/");

    } else {

        alert(data.message);

    }

}

    return (

        <>

            <style>{styles}</style>

            <div className="login-page">

                <div className="login-card">

                    <img
                        src={diskLogo}
                        alt="DISK Logo"
                        className="login-logo"
                    />

                    <h1 className="login-title">
                        SchoolAI
                    </h1>

                    <p className="login-subtitle">
                        Automated Examination Grading System
                    </p>

                    <h2 className="portal-title">
                        Teacher Portal
                    </h2>

                    <form onSubmit={handleLogin}>
                        <label className="login-label">
                            Email
                        </label>

                        <input
                            className="login-input"
                            type="email"
                            placeholder="teacher@school.edu"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />

                        <label className="login-label">
                            Password
                        </label>

                        <input
                            className="login-input"
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        <button
                            className="login-button"
                            type="submit"
                        >
                            Sign In
                        </button>

                    </form>

                </div>

            </div>

        </>

    );

}