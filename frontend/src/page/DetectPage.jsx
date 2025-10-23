// Trong component DetectPage
import React, { useEffect, useState } from 'react'
import { ChartComponent } from '../components/ChartComponent'
import AOS from 'aos';
import 'aos/dist/aos.css'; // Import CSS của AOS

export const DetectPage = () => {
    useEffect(() => {
      AOS.init({
        duration: 1200, // Thời gian animation mặc định
        once: true,    // Chỉ chạy animation một lần
      });
    }, []);

  const data = {
    "product": {
      "product_id": 3747383,
      "name": "Đặc Sản Bình Thuận  - Nước Mắm Tĩn Cá Cơm Than Nhãn Đỏ 40N Chai Thủy Tinh (500Ml/Chai) Sánh Đặc Thịt Cá, Không Chất Bảo Quản - Ocop 4 Sao",
      "brand": "Nước Mắm Tĩn",
      "price": 190000,
      "rating_average": 4.8,
      "review_count": 299,
      "sold_quantity": 3520,

    }
  } 

  const rate = [10,20, 30, 40]
  const message = useState("Đang xử lý hình ảnh...")

  return (
    <div className="min-h-screen pt-16 flex items-center justify-center px-6 bg-slate-900 text-white">
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Khung bên trái: Nhập thông tin sản phẩm */}
        <div className="bg-white text-slate-800 p-6 rounded-2xl shadow-lg"  data-aos="fade-right">
          {/* Thêm flex, flex-col và h-full để chiếm hết chiều cao và phân chia nội dung */}
          <div className="flex flex-col h-full">

            <h2 className="text-2xl font-semibold mb-4">Nhập thông tin sản phẩm</h2>

            {/* 1. KHỐI NỘI DUNG PHÍA TRÊN (Giữ nguyên) */}
            <div className="mb-4">
              {/* Ô nhập và nút lấy dữ liệu */}
              <div className="flex mb-4">
                <input
                  type="text"
                  placeholder="URL / Giá trị cần phân tích"
                  className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600 transition-all cursor-pointer">
                  Lấy dữ liệu
                </button>
              </div>

              {/* Thông tin sản phẩm */}
              <div className="mb-4 space-y-1">
                <p className="font-medium  line-clamp-2 cursor-pointer" title={data.product.name}>
                  {data.product.name}
                </p>
                <p className='!pt-[12px]'>Thương hiệu: {data.product.brand}</p>
                <p>Giá: <span className="font-semibold text-blue-600">{data.product.price}</span></p>
                <p>Điểm đánh giá: ⭐ {data.product.rating_average}</p>
                <p>Tổng đánh giá: {data.product.review_count}</p>
                <p>Đã bán: {data.product.sold_quantity}</p>
              </div>
            </div>

            {/* 2. KHỐI NỘI DUNG PHÍA DƯỚI (Đẩy xuống cuối) */}
            {/* Dùng mt-auto (margin-top auto) để đẩy khối này xuống sát đáy trong Flexbox */}
            <div className="mt-auto pt-4 border-t border-gray-200">

              {/* Trạng thái xử lý */}
              <div className="space-y-2 mb-4">
                <p className="text-blue-500 cursor-pointer hover:underline">⟳ {message}</p>
              </div>

              {/* Nút Tính độ tin cậy */}
              <button className="w-full cursor-pointer bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-2 rounded-lg hover:opacity-90 transition-all">
                Tính độ tin cậy
              </button>
            </div>
          </div>
        </div>
        <div className="bg-white text-slate-800 p-6 rounded-2xl shadow-lg" data-aos="fade-left">
          <h2 className="text-2xl font-semibold mb-4">Kết quả dự đoán</h2>
          <ul className="my-4 space-y-1 ">
            <li>Hình ảnh: <span className="font-semibold text-blue-600">{rate[0]}%</span></li>
            <li>Mô tả sản phẩm: <span className="font-semibold text-blue-600">{rate[1]}%</span></li>
            <li>Đánh giá người dùng: <span className="font-semibold text-blue-600">{rate[2]}%</span></li>
          </ul>
          {/* Biểu đồ đơn giản */}
          <div className="w-full h-[250px] justify-center flex bg-gray-100 rounded mb-4 items-end justify-between px-2">
            <div>
              <p className='!pb-4 !text-center font-semibold text-lg' >Biểu đồ độ tin cậy</p>
              <div>
                <ChartComponent index={rate}/>
              </div>
            </div>
          </div>
          <h3 className="font-semibold mb-2 mt-6">Phân tích của AI</h3>
          <div className="border border-gray-300 rounded-lg p-3 h-30 bg-gray-50 text-gray-600">
            {/* Nội dung AI hiển thị ở đây */}
          </div>
        </div>
      </div>
    </div>
  )
}