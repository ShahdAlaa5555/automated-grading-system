import { motion } from "framer-motion";
import { FaArrowDown } from "react-icons/fa";

const styles = `
.hero{
    min-height:100vh;

    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;

    text-align:center;

    padding:120px 20px 80px;

    background:
    radial-gradient(circle at top left,
    rgba(221,0,0,.08),
    transparent 40%),

    radial-gradient(circle at bottom right,
    rgba(255,206,0,.12),
    transparent 40%),

    #FAFAFA;

    overflow:hidden;
}

.hero h1{

    font-size:64px;

    font-weight:700;

    color:#222;

    line-height:1.15;

    margin-bottom:20px;

    max-width:900px;

}

.hero p{

    font-size:22px;

    color:#666;

    max-width:650px;

    line-height:1.7;

    margin-bottom:45px;

}

.hero-btn{

    background:#FFCE00;

    color:white;

    border:none;

    border-radius:50px;

    padding:16px 45px;

    font-size:18px;

    cursor:pointer;

    transition:.35s;

    font-weight:500;

}

.hero-btn:hover{

    background:#DD0000;

    transform:translateY(-4px);

    box-shadow:0 18px 35px rgba(221,0,0,.25);

}

.scroll{

    position:absolute;

    bottom:40px;

    display:flex;

    flex-direction:column;

    align-items:center;

    color:#888;

    font-size:14px;

}

.scroll svg{

    margin-top:12px;

    animation:bounce 2s infinite;

}

@keyframes bounce{

    0%,20%,50%,80%,100%{

        transform:translateY(0);

    }

    40%{

        transform:translateY(10px);

    }

    60%{

        transform:translateY(5px);

    }

}

@media(max-width:900px){

.hero h1{

    font-size:44px;

}

.hero p{

    font-size:18px;

}

}

@media(max-width:600px){

.hero{

    padding-top:140px;

}

.hero h1{

    font-size:34px;

}

.hero p{

    font-size:16px;

}

.hero-btn{

    width:220px;

}

}
`;

export default function Hero(){

    return(

        <>

        <style>{styles}</style>

        <section className="hero">

            <motion.h1

                initial={{opacity:0,y:40}}

                animate={{opacity:1,y:0}}

                transition={{duration:.9}}

            >

                Automated Assessment System

            </motion.h1>

            <motion.p

                initial={{opacity:0}}

                animate={{opacity:1}}

                transition={{delay:.4,duration:.8}}

            >

                Welcome to the digital assessment platform of
                Deutsche Internationale Schule in Kairo.

            </motion.p>

            <motion.button

                className="hero-btn"

                initial={{opacity:0,scale:.8}}

                animate={{opacity:1,scale:1}}

                transition={{delay:.7}}

            >

                Login

            </motion.button>

            <motion.div

                className="scroll"

                initial={{opacity:0}}

                animate={{opacity:1}}

                transition={{delay:1.2}}

            >

                Scroll Down

                <FaArrowDown/>

            </motion.div>

        </section>

        </>

    );

}