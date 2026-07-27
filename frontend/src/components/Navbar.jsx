import { motion } from "framer-motion";
import { FaUserCircle } from "react-icons/fa";
import logo from "../assets/disk-logo.png";

const styles = `
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:'Poppins',sans-serif;
}

.navbar{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    z-index:1000;

    background:rgba(255,255,255,.85);
    backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);
    border-bottom:1px solid rgba(0,0,0,.06);
    transition:all .3s ease;
}

.navbar-container{
    max-width:1300px;
    margin:auto;

    display:flex;
    justify-content:space-between;
    align-items:center;

    padding:16px 40px;
}

.logo-container{
    display:flex;
    align-items:center;
    gap:12px;
}

.logo{
    width:105px;
    height:105px;
    object-fit:contain;
}

.school-name{
    display:flex;
    flex-direction:column;
}

.school-name h2{
    font-size:30px;
    font-weight:600;
    color:#FFCE00;
    line-height:1.2;
}

.school-name span{
    font-size:20px;
    color:#777;
}

.login-btn{
    width:auto;
    background:#FFCE00;
    color:white;
    border:none;
    border-radius:40px;

    padding:12px 30px;

    cursor:pointer;

    font-size:15px;
    font-weight:500;

    transition:.3s ease;
}

.login-btn:hover{
    background:#DD0000;
    transform:translateY(-2px);
    box-shadow:0 10px 25px rgba(221,0,0,.25);
}

.login-btn:active{
    transform:scale(.98);
}

.navbar-user{
    display:flex;
    align-items:center;
    gap:9px;

    padding:11px 18px;
    border:1px solid rgba(255,206,0,.5);
    border-radius:40px;

    background:rgba(255,206,0,.12);
    color:#444;

    font-size:15px;
    font-weight:600;
}

.navbar-user svg{
    color:#DD0000;
    font-size:20px;
}

@media(max-width:768px){
    .navbar-container{
        padding:15px 20px;
    }

    .logo{
        width:45px;
        height:45px;
    }

    .school-name h2{
        font-size:15px;
    }

    .school-name span{
        display:none;
    }

    .login-btn{
        padding:10px 20px;
        font-size:14px;
    }

    .navbar-user{
        padding:9px 13px;
        font-size:14px;
    }
}
`;

export default function Navbar({ teacherName }) {
    return (
        <>
            <style>{styles}</style>
            <motion.nav
                className="navbar"
                initial={{ y: -80, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8 }}
            >
                <div className="navbar-container">
                    <div className="logo-container">
                        <img
                            src={logo}
                            alt="DISK Logo"
                            className="logo"
                        />

                        <div className="school-name">
                            <span>Deutsche Internationale Schule in Kairo</span>
                        </div>
                    </div>

                    {teacherName ? (
                        <div
                            className="navbar-user"
                            aria-label={`Teacher: ${teacherName}`}
                        >
                            <FaUserCircle aria-hidden="true" />
                            <span>{teacherName}</span>
                        </div>
                    ) : (
                        <button type="button" className="login-btn">
                            Login
                        </button>
                    )}
                </div>
            </motion.nav>
        </>
    );
}