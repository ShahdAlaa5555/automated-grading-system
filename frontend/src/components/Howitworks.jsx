import { motion } from "framer-motion";

const styles = `
.how-it-works{
    padding:100px 20px;
    background:#FAFAFA;
    position:relative;
    overflow:hidden;
}

.hiw-eyebrow{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:8px;
    font-size:13px;
    font-weight:600;
    letter-spacing:.08em;
    text-transform:uppercase;
    color:#DD0000;
    margin-bottom:14px;
}

.hiw-dot{
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

.hiw-title{
    text-align:center;
    font-size:36px;
    font-weight:700;
    color:#222 !important;
    max-width:640px;
    margin:0 auto 70px;
    line-height:1.3;
}

.hiw-title span{
    color:#DD0000;
}

.hiw-grid{
    max-width:1100px;
    margin:0 auto;
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:0;
    position:relative;
}

.hiw-grid::before{
    content:'';
    position:absolute;
    top:34px;
    left:12.5%;
    right:12.5%;
    height:2px;
    background:repeating-linear-gradient(90deg,#e5e5e5 0 8px,transparent 8px 16px);
    z-index:0;
}

.hiw-step{
    position:relative;
    z-index:1;
    display:flex;
    flex-direction:column;
    align-items:center;
    text-align:center;
    padding:0 16px;
}

.hiw-icon{
    width:68px;
    height:68px;
    border-radius:20px;
    background:#fff;
    border:2px solid #f0f0f0;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#DD0000;
    margin-bottom:22px;
    transition:.3s;
}

.hiw-step:hover .hiw-icon{
    border-color:#FFCE00;
    transform:translateY(-4px);
    box-shadow:0 12px 24px rgba(255,206,0,.2);
}

.hiw-step h3{
    font-size:16px;
    font-weight:600;
    color:#222 !important;
    margin-bottom:8px;
}

.hiw-step p{
    font-size:14px;
    color:#888;
    line-height:1.6;
    max-width:220px;
}

.scan-doc{
    position:relative;
    overflow:hidden;
    width:28px;
    height:28px;
}

.scan-line{
    position:absolute;
    left:0;
    right:0;
    height:2px;
    background:#DD0000;
    animation:scan 2.4s ease-in-out infinite;
}

@keyframes scan{
    0%,100%{ top:2px; opacity:0; }
    10%{ opacity:1; }
    50%{ top:24px; opacity:1; }
    90%{ opacity:1; }
}

@media(max-width:900px){
.hiw-grid{
    grid-template-columns:1fr 1fr;
    row-gap:50px;
}
.hiw-grid::before{
    display:none;
}
.hiw-title{
    font-size:28px;
}
}

@media(max-width:520px){
.hiw-grid{
    grid-template-columns:1fr;
}
.hiw-title{
    font-size:24px;
}
}
`;

const steps = [
    {
        title:"Upload the exam",
        text:"Teachers upload scanned papers or PDFs in seconds.",
        icon:(
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M12 16V4"/>
                <path d="M6 10l6-6 6 6"/>
                <path d="M4 20h16"/>
            </svg>
        )
    },
    {
        title:"AI reads every answer",
        text:"Our model recognizes handwriting and understands each response.",
        icon:(
            <div className="scan-doc">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d="M6 2h9l5 5v15H6Z"/>
                    <path d="M15 2v5h5"/>
                </svg>
                <div className="scan-line"/>
            </div>
        )
    },
    {
        title:"Instant, fair grading",
        text:"Every answer is scored consistently against the marking scheme.",
        icon:(
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M20 6 9 17l-5-5"/>
            </svg>
        )
    },
    {
        title:"Results, delivered",
        text:"Students and teachers see clear, reviewable results right away.",
        icon:(
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M4 4h16v16H4Z"/>
                <path d="M8 12h8"/>
                <path d="M8 16h5"/>
            </svg>
        )
    },
];

export default function HowItWorks(){

    return(

        <>

        <style>{styles}</style>

        <section className="how-it-works">

            <div className="hiw-eyebrow">
                <span className="hiw-dot"/>
                AI-Powered Grading
            </div>

            <h2 className="hiw-title">
                From handwritten exam to <span>graded result</span> — automatically.
            </h2>

            <div className="hiw-grid">

                {steps.map((step,i)=>(

                    <motion.div
                        className="hiw-step"
                        key={step.title}
                        initial={{opacity:0,y:24}}
                        whileInView={{opacity:1,y:0}}
                        viewport={{once:true}}
                        transition={{duration:.6,delay:i*.15}}
                    >

                        <div className="hiw-icon">
                            {step.icon}
                        </div>

                        <h3>{step.title}</h3>
                        <p>{step.text}</p>

                    </motion.div>

                ))}

            </div>

        </section>

        </>

    );

}