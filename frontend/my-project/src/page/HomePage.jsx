import React, { useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import { useNavigate } from 'react-router-dom';
import AOS from 'aos';
import 'aos/dist/aos.css';

export const HomePage = () => {
    const navigate = useNavigate(); 
    
    const handleAnalyzeClick = () => {
        navigate("/detect");
    };
    useEffect(() => {
    AOS.init({
      duration: 1200,
      once: true,
    });
  }, []);

    return (

        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white px-6">
            <div className="max-w-3xl text-center space-y-6">
                <h1 className="text-5xl font-bold" data-aos="fade-down">
                    Chào mừng bạn đã đến
                </h1>
                
                <h3 className="text-lg leading-9 text-slate-300" data-aos="zoom-out" data-aos-delay="400" >
                    Trên thị trường hiện nay, đặc biệt là trên các sàn thương mại điện tử,
                    tình trạng hàng giả và hàng nhái ngày càng phổ biến. Vì vậy, chúng tôi
                    phát triển ứng dụng <span className="text-blue-400 font-semibold">TrustCheck</span> nhằm giúp bạn kiểm tra
                    và nhận biết sản phẩm chính hãng, bảo vệ quyền lợi và mang đến cho bạn
                    những lựa chọn đáng tin cậy nhất.
                </h3>

                <Button 
                    onClick={handleAnalyzeClick} data-aos="zoom-in" data-aos-delay="700"
                    className=  'bg-blue-500 cursor-pointer hover:bg-blue-600 text-white font-semibold px-12 py-3 mx-16 rounded-full shadow-lg hover:shadow-blue-500/40 transition-all duration-300 wow fadeInUp'
                    data-wow-delay="1s"
                >
                    Phân tích ngay
                </Button>
            </div>
        </div>
    );
};