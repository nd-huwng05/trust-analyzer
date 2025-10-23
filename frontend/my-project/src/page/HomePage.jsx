import React, { useEffect } from 'react'; // 1. Import useEffect
import Button from 'react-bootstrap/Button';
import { useNavigate } from 'react-router-dom'; // Nên dùng useNavigate thay cho href
import AOS from 'aos';
import 'aos/dist/aos.css'; // Import CSS của AOS

export const HomePage = () => {
    // Nếu bạn đang dùng React Router, nên dùng useNavigate
    const navigate = useNavigate(); 
    
    const handleAnalyzeClick = () => {
        navigate("/detect");
    };
    useEffect(() => {
    AOS.init({
      duration: 1200, // Thời gian animation mặc định
      once: true,    // Chỉ chạy animation một lần
    });
  }, []);

    return (
        // Thêm class wow cho div bao ngoài để thấy hiệu ứng
        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white px-6">
            <div className="max-w-3xl text-center space-y-6">
                {/* Đảm bảo class WOW và hiệu ứng được áp dụng đúng */}
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
                
                {/* Nên dùng onClick và useNavigate cho nút */}
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