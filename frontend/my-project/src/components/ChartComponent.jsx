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


    // 4. useEffect để khởi tạo biểu đồ MỘT LẦN khi component được mount
useEffect(() => {
    if (myChartRef.current) {
        myChartRef.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    const config = {
        type: 'bar',
        data: {
            labels: ['Mô tả', 'Hình ảnh', 'Đánh giá'],
            datasets: [{
                label: 'Điểm Tin Cậy',
                data: index, // 
                backgroundColor: ['#fbbf24', '#3b82f6', '#ef4444'],
            }],
        },
        options: {
            responsive: true,
            animation: {
                duration: isAnimated ? 1000 : 0,
            },
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: { beginAtZero: true, max: 100 },
            },
        },
    };

    myChartRef.current = new Chart(ctx, config);

    return () => {
        if (myChartRef.current) {
            myChartRef.current.destroy();
        }
    };
}, [index, isAnimated]); // ✅ Thêm 'index'


    return (

          <div className="bg-white rounded-xl shadow-lg w-90">
            {/* 5. Gán ref vào thẻ <canvas> */}
            <canvas id="myChart" ref={chartRef} className="mb-4"></canvas>
        </div>

    );
};

// export default ChartComponent;