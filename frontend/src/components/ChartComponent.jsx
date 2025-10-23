import React, { useEffect, useRef, useState } from 'react';
// Nếu dùng Chart.js, bạn cần import thư viện này. 
// Đảm bảo bạn đã cài đặt: npm install chart.js
import Chart from 'chart.js/auto'; 

export const ChartComponent = ({index}) => {
    // 1. Dùng useRef để tham chiếu đến thẻ <canvas>
    const chartRef = useRef(null);
    // 2. Dùng useRef để lưu trữ đối tượng biểu đồ (Chart object)
    const myChartRef = useRef(null);
    const[isAnimated, setIsAnimated] = useState(true)

    // Dữ liệu và cấu hình CỐ ĐỊNH của biểu đồ
    const data = {
        labels: ['Đánh giá', 'Hình ảnh', 'Mô tả', 'Hành vi'], // Đã đổi label cho phù hợp với ngữ cảnh
        datasets: [{
            label: 'Điểm Tin Cậy',
            data:  index,
            backgroundColor: [
                '#fbbf24', // vàng
                '#3b82f6', // xanh dương
                '#ef4444', // đỏ
                '#22c55e', // xanh lá
            ],
        }],
    };

    // 4. useEffect để khởi tạo biểu đồ MỘT LẦN khi component được mount
    useEffect(() => {
        // Hủy biểu đồ cũ nếu có (quan trọng cho React Strict Mode)
        if (myChartRef.current) {
            myChartRef.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');
        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                animation: {
                    // Cài đặt thời gian animation dựa trên state
                    duration: isAnimated ? 1000 : 0 
                },
                plugins: {
                    legend: { display: false } // Hiện legend để dễ hiểu
                },
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        };

        // Khởi tạo và lưu đối tượng biểu đồ
        myChartRef.current = new Chart(ctx, config);

        // Cleanup function: Hủy biểu đồ khi component bị unmount
        return () => {
            if (myChartRef.current) {
                myChartRef.current.destroy();
            }
        };
    }, [isAnimated]); // Chạy lại khi 'isAnimated' thay đổi

    // Hàm xử lý khi nhấn nút
    // const handleAnimateClick = () => {
    //     // Đảo ngược trạng thái để kích hoạt useEffect
    //     setIsAnimated(true); 

    //     // Nếu bạn muốn tắt animation sau khi chạy xong, dùng setTimeout:
    //     // setTimeout(() => setIsAnimated(false), 1200);
    // };

    return (

          <div className="bg-white rounded-xl shadow-lg w-90">
            {/* 5. Gán ref vào thẻ <canvas> */}
            <canvas id="myChart" ref={chartRef} className="mb-4"></canvas>
        </div>

    );
};

// export default ChartComponent;