import React from "react";

import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import ImageSlider from "../components/ImageSlider";
import Footer from "../components/Footer";

const styles = `
body{
    margin:0;
    overflow-x:hidden;
    background:#FAFAFA;
}

.landing-page{
    width:100%;
    min-height:100vh;
}
`;

export default function LandingPage(){

    return(

        <>

        <style>{styles}</style>

        <div className="landing-page">

            <Navbar/>

            <Hero/>

            <ImageSlider/>

            <Footer/>

        </div>

        </>

    );

}