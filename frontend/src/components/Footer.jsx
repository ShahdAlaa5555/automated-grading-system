import { FaMapMarkerAlt, FaGlobe, FaEnvelope } from "react-icons/fa";

const styles = `
.footer{
    background:#1F1F1F;
    color:white;
    padding:60px 20px 30px;
}

.footer-container{
    max-width:1200px;
    margin:auto;
}

.footer-top{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:40px;
    flex-wrap:wrap;
}

.footer-brand h2{
    font-size:28px;
    margin-bottom:10px;
    color:#FFCE00;
}

.footer-brand p{
    color:#cccccc;
    line-height:1.8;
    max-width:450px;
}

.footer-info{
    display:flex;
    flex-direction:column;
    gap:18px;
}

.info-item{
    display:flex;
    align-items:center;
    gap:12px;
    color:#dddddd;
    font-size:15px;
}

.info-item svg{
    color:#FFCE00;
    font-size:18px;
}

.footer-line{
    margin:40px 0 20px;
    border:none;
    height:1px;
    background:rgba(255,255,255,.15);
}

.footer-bottom{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:15px;
}

.footer-bottom p{
    color:#bbbbbb;
    font-size:14px;
}

.credit{
    color:#FFCE00;
    font-weight:500;
}

@media(max-width:768px){

.footer{
    text-align:center;
}

.footer-top{

    flex-direction:column;
    align-items:center;

}

.footer-info{

    align-items:flex-start;

}

.footer-bottom{

    flex-direction:column;

}

}
`;

export default function Footer(){

    return(

        <>

        <style>{styles}</style>

        <footer className="footer">

            <div className="footer-container">

                <div className="footer-top">

                    <div className="footer-brand">

                        <h2>DISK</h2>

                        <p>

                            Deutsche Internationale Schule in  Kairo

                            <br/>

                            Automated Assessment System

                        </p>

                    </div>

                    <div className="footer-info">

                        <div className="info-item">

                            <FaMapMarkerAlt/>

                            <span>Cairo, Egypt</span>

                        </div>

                        <div className="info-item">

                            <FaGlobe/>

                            <span>www.disk-kairo.de</span>

                        </div>

                        <div className="info-item">

                            <FaEnvelope/>

                            <span>info@disk-kairo.de</span>

                        </div>

                    </div>

                </div>

                <hr className="footer-line"/>

                <div className="footer-bottom">

                    <p>

                        © {new Date().getFullYear()} Deutsche Internationale Schule Kairo

                    </p>

                    <p className="credit">

                        Automated Assessment System

                    </p>

                </div>

            </div>

        </footer>

        </>

    );

}