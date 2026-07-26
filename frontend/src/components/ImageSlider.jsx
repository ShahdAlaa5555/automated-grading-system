import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, EffectFade, Pagination } from "swiper/modules";

import "swiper/css";
import "swiper/css/effect-fade";
import "swiper/css/pagination";

import img1 from "../assets/school1.png";
import img2 from "../assets/school2.png";


const styles = `
.slider-section{
    width:100%;
    padding:60px 0 80px;
    background:#FAFAFA;
}

.slider-container{
    width:90%;
    max-width:1350px;
    margin:auto;
}

.school-slider{
    border-radius:24px;
    overflow:hidden;
    box-shadow:0 20px 45px rgba(0,0,0,.12);
}

.slide{
    position:relative;
    height:650px;
}

.slide img{
    width:100%;
    height:100%;
    object-fit:cover;
}

.overlay{
    position:absolute;
    inset:0;

    background:linear-gradient(
        rgba(0,0,0,.15),
        rgba(0,0,0,.35)
    );

    display:flex;
    align-items:flex-end;
}

.caption{
    color:white;
    padding:50px;
    max-width:700px;
}

.caption h2{
    font-size:40px;
    margin-bottom:15px;
    font-weight:600;
}

.caption p{
    font-size:18px;
    line-height:1.7;
}

.swiper-pagination-bullet{
    background:white;
    opacity:.7;
}

.swiper-pagination-bullet-active{
    background:#FFCE00;
}

@media(max-width:900px){

.slide{
    height:500px;
}

.caption{
    padding:35px;
}

.caption h2{
    font-size:30px;
}

.caption p{
    font-size:16px;
}

}

@media(max-width:600px){

.slide{
    height:320px;
}

.caption{
    padding:25px;
}

.caption h2{
    font-size:22px;
}

.caption p{
    font-size:14px;
}

}
`;

const slides = [
    {
        image: img1,
        title: "Welcome",
        text: "A place where learning and innovation come together."
    },
    {
        image: img2,
        title: "Community",
        text: "Supporting students throughout their educational journey."
    },
    
];

export default function ImageSlider() {

    return (
        <>
            <style>{styles}</style>

            <section className="slider-section">

                <div className="slider-container">

                    <Swiper
                        modules={[Autoplay, EffectFade, Pagination]}
                        effect="fade"
                        loop={true}
                        autoplay={{
                            delay:4000,
                            disableOnInteraction:false
                        }}
                        pagination={{ clickable:true }}
                        className="school-slider"
                    >

                        {slides.map((slide,index)=>(
                            <SwiperSlide key={index}>

                                <div className="slide">

                                    <img
                                        src={slide.image}
                                        alt={slide.title}
                                    />

                                    <div className="overlay">

                                        <div className="caption">

                                            <h2>{slide.title}</h2>

                                            <p>{slide.text}</p>

                                        </div>

                                    </div>

                                </div>

                            </SwiperSlide>
                        ))}

                    </Swiper>

                </div>

            </section>
        </>
    );

}