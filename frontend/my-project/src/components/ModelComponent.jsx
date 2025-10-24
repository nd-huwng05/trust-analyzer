import React, { useEffect, useRef } from 'react'
import Chart from 'chart.js/auto'

const ModelComponent = ({ onClose, description, image, comment }) => {

  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const POS = comment?.review.summary.sentiment_ratio.POS;
  const NEG = comment?.review.summary.sentiment_ratio.NEG;
  const NEU = comment?.review.summary.sentiment_ratio.NEU

  useEffect(() => {
    const canvas = chartRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Hủy biểu đồ cũ (nếu có)
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
      chartInstanceRef.current = null;
    }

    // Tạo biểu đồ mới
    chartInstanceRef.current = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Tích cực', 'Tiêu cực', 'Trung lập'],
        datasets: [
          {
            data: [POS, NEG, NEU],
            backgroundColor: ['#22c55e', '#ef4444', '#9ca3af'],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
        },
      },
    });

    return () => {
      chartInstanceRef.current?.destroy();
      chartInstanceRef.current = null;
    };
  }, [POS, NEG, NEU, comment]);

  return (
    <div className="fixed inset-0 bg-[#3333339c] flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-2xl shadow-2xl w-[65%] max-h-[90vh] overflow-y-auto mx-4">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
          🔍 Chi tiết đánh giá độ tin cậy
        </h2>

        {/* Tổng quan */}
        <div className="grid grid-cols-3 gap-4 mb-6 text-center">
          <div className="bg-blue-50 p-4 rounded-xl shadow-sm">
            <p className="font-semibold text-gray-600">Mô tả</p>
            <p className="text-2xl font-bold text-blue-600">
              {((description?.description?.score  ?? 0).toFixed(2))*100}%
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-xl shadow-sm">
            <p className="font-semibold text-gray-600">Hình ảnh</p>
            <p className="text-2xl font-bold text-green-600">
              {((image?.image?.score ?? 0).toFixed(2))}%
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-xl shadow-sm">
            <p className="font-semibold text-gray-600">Đánh giá</p>
            <p className="text-2xl font-bold text-yellow-600">
              {((comment?.review?.score ?? 0).toFixed(2))}%
            </p>
          </div>
        </div>

        {/* Hình ảnh khớp tốt nhất */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">📸 Ảnh khớp tốt nhất</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {image?.image?.best_matches?.sort((a, b) => b.score - a.score)?.slice(0, 3).map((item, index) => (
             <div>
                  <img
                key={index}
                src={item.buyer_path}
                alt={`match-${index}`}
                className="w-full m-[2px] h-40 object-cover rounded-xl shadow-md border"
              />
              <img
                key={index}
                src={item.seller_path}
                alt={`match-${index}`}
                className="w-full m-[2px] h-40  object-cover rounded-xl shadow-md border"
              />
             </div>
            ))}
          </div>
        </div>

        {/* Đánh giá người dùng */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">💬 Đánh giá người dùng</h3>


          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* --- BÊN TRÁI: Thông tin tổng quan --- */}
            <div className="bg-gray-50 p-4 rounded-xl shadow-sm">
              <p>
                <span className="font-medium text-gray-700">Tỷ lệ bình thường:</span>{' '}
                <span className="text-blue-600 font-semibold">
                  {comment?.review?.non_spam_ratio ?? 0}%
                </span>
              </p>
              <p className="mt-2">
                <span className="font-medium text-gray-700">Số bình luận bình thường:</span>{' '}
                <span className="text-green-600 font-semibold">
                  {comment?.review?.count_normal ?? 0}
                </span>
              </p>
              <p className="mt-2">
                <span className="font-medium text-gray-700">Số bình luận spam:</span>{' '}
                <span className="text-red-500 font-semibold">
                  {comment?.review?.count_spam ?? 0}
                </span>
              </p>

              <p className="mt-4 italic text-sm text-gray-500">
                * Các chỉ số này được tính dựa trên lịch sử bình luận gần đây.
              </p>
            </div>

            {/* --- BÊN PHẢI: Biểu đồ tròn --- */}
            <div className="flex flex-col items-center justify-center">
              <p className="font-medium text-gray-700 mb-2">📊 Tỷ lệ cảm xúc:</p>
              <canvas ref={chartRef} className="!w-[300px] !h-[300px]" />
              <ul className="mt-3 text-sm space-y-1">
                <li>😊 <span className="text-green-600 text-xl font-semibold">Tích cực</span> {POS}%</li>
                <li>☹️ <span className="text-red-500 text-xl font-semibold">Tiêu cực</span> {NEG}%</li>
                <li>😐 <span className="text-gray-600 text-xl font-semibold">Trung lập</span> {NEU}%</li>
              </ul>
            </div>
          </div>


        </div>

        {/* Ghi chú */}
        <p className="text-sm text-gray-500 italic">
          * Các tỷ lệ và điểm số chỉ mang tính chất tham khảo ban đầu.
        </p>

        {/* Nút đóng */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  )
}

export default ModelComponent
