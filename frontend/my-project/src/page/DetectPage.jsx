// Trong component DetectPage
import React, { useEffect, useState } from 'react';
import { ChartComponent } from '../components/ChartComponent';
import AOS from 'aos';
import 'aos/dist/aos.css'; // Import CSS của AOS
import ModelComponent from '../components/ModelComponent';

export const DetectPage = () => {
  useEffect(() => {
    AOS.init({
      duration: 1200, // Thời gian animation mặc định
      once: true,    // Chỉ chạy animation một lần
    });
  }, []);

  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [flagReviewAI, setFlagReviewAI] = useState(false)
  const [flagStartAnalyse, setFlagAnalyse] = useState(false)
  const [flagFinal, setFlagFinal] = useState(false)
  // load bên trái
  const [isLoading, setIsLoading] = useState(false); // State mới cho loading
  const [message, setMessage] = useState("Sẵn sàng nhập URL..."); // Đã chuyển message thành useState


  //Ẩn hiện modal
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 2. Hàm mở Modal
  const handleOpenModal = () => setIsModalOpen(true);

  // Hàm đóng Modal
  const handleCloseModal = () => setIsModalOpen(false);

  //   Lấy dữ liệu cần hiển thị
  const getData = async () => {
    if (!url) {
      alert('Vui lòng nhập URL sản phẩm Tiki.');
      return;
    }
    setIsLoading(true);
    setMessage("Đang cào dữ liệu... Vui lòng chờ (Có thể mất 5-10 giây)");
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/tiki-product?url=${encodeURIComponent(url)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseData = await response.json();

      if (response.ok) {
        setData(responseData);
        setMessage("Lấy dữ liệu thành công!");
      } else {
        // Xử lý lỗi từ server Flask
        alert(`Lỗi Server (${response.status}): ${responseData.message || responseData.error || 'Lỗi không xác định'}`);
        setMessage("Lỗi: Không lấy được dữ liệu.");
      }
    } catch (err) {
      alert(`Lỗi Kết Nối: ${err.message}. Đảm bảo Flask server đang chạy.`);
      setMessage("Lỗi: Không kết nối được API.");
    } finally {
      // 2. Kết thúc tải
      setIsLoading(false);
    }
  };

  const productInfo = data?.data_preview;
  const [reliabilityDescription, setReliabilityDescription] = useState(null);
  const [reliabilityImage, setReliabilityImage] = useState(null);
  const [reliabilityComment, setReliabilityComment] = useState(null);
  const [rate, setRate] = useState([])

  console.log("reliabilityDescription: ", reliabilityDescription)
  console.log("reliabilityImage: ", reliabilityImage)
  console.log("reliabilityComment: ", reliabilityComment)


  const getReliabilityDescription = async () => {

    if (reliabilityDescription === null) {
      console.log("đang phân tích mô tả")
    }

    try {

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/trust-analyzer/analyze/description`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseData = await response.json();
      console.log("res: ", responseData)
      if (response.ok) {
        setReliabilityDescription(responseData);
        return;
      } else {
        // Xử lý lỗi từ server Flask
        alert(`Lỗi Server (${response.status}): ${responseData.message || responseData.error || 'Lỗi không xác định'}`);
        setMessage("Lỗi: Không lấy được dữ liệu.");
      }
    } catch (err) {
      alert(`Lỗi Kết Nối: ${err.message}. Đảm bảo Flask server đang chạy.`);
      setMessage("Lỗi: Không kết nối được API.");
    }
  };


  const getReliabilityImage = async () => {

    // 1. Bắt đầu tải
    if (reliabilityDescription === null) {
      console.log("đang phân tích hình ảnh")
    }
    try {
      // Encode URL để đảm bảo các ký tự đặc biệt được xử lý đúng
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/trust-analyzer/analyze/image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseData = await response.json();

      if (response.ok) {
        setReliabilityImage(responseData);
        return;
      } else {
        // Xử lý lỗi từ server Flask
        alert(`Lỗi Server (${response.status}): ${responseData.message || responseData.error || 'Lỗi không xác định'}`);
        setMessage("Lỗi: Không lấy được dữ liệu.");
      }
    } catch (err) {
      alert(`Lỗi Kết Nối: ${err.message}. Đảm bảo Flask server đang chạy.`);
      setMessage("Lỗi: Không kết nối được API.");
    }
  };

  const getReliabilityComment = async () => {

    if (reliabilityDescription === null) {
      console.log("đang phân tích đánh giá người dùng")
    }

    try {
      // Encode URL để đảm bảo các ký tự đặc biệt được xử lý đúng
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/trust-analyzer/analyze/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseData = await response.json();

      if (response.ok) {
        setReliabilityComment(responseData);
        return;
      } else {
        // Xử lý lỗi từ server Flask
        alert(`Lỗi Server (${response.status}): ${responseData.message || responseData.error || 'Lỗi không xác định'}`);
        setMessage("Lỗi: Không lấy được dữ liệu.");
      }
    } catch (err) {
      alert(`Lỗi Kết Nối: ${err.message}. Đảm bảo Flask server đang chạy.`);
      setMessage("Lỗi: Không kết nối được API.");
    }
  };

  const [full, setFull] = useState(null)
  const getFull = async () => {
    try {
      // Encode URL để đảm bảo các ký tự đặc biệt được xử lý đúng
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/trust-analyzer/analyze/full`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseData = await response.json();

      if (response.ok) {
        setFull(responseData);
        return;
      } else {
        // Xử lý lỗi từ server Flask
        alert(`Lỗi Server (${response.status}): ${responseData.message || responseData.error || 'Lỗi không xác định'}`);
        setMessage("Lỗi: Không lấy được dữ liệu.");
      }
    } catch (err) {
      alert(`Lỗi Kết Nối: ${err.message}. Đảm bảo Flask server đang chạy.`);
      setMessage("Lỗi: Không kết nối được API.");
    }
  };
  console.log("full: ", full)

  const hadleLayDiem = () => {
    const rateTemp = [];

    if (reliabilityDescription) {
      rateTemp.push(Number((parseFloat(reliabilityDescription.description?.score) * 100).toFixed(2)));
    } else {
      rateTemp.push(0)
    }

    if (reliabilityImage) {
      rateTemp.push(Number(parseFloat(reliabilityImage.image?.score).toFixed(2)));
    } else {
      rateTemp.push(0)
    }

    if (reliabilityComment) {
      rateTemp.push(Number(parseFloat(reliabilityComment.review?.score).toFixed(2)));
    } else {
      rateTemp.push(0)
    }

    setRate(rateTemp);
  };

  const handleTinhDOTinCay = async () => {
    setFlagAnalyse(true);
    try {
      await getReliabilityDescription();
      await getReliabilityImage();
      await getReliabilityComment();
      setFlagAnalyse(false);
      setFlagReviewAI(true);
      await getFull();
      setFlagFinal(true)

    } catch (error) {
      console.error("Có lỗi xảy ra khi lấy dữ liệu:", error);
    }
  }

  useEffect(() => {
    if (reliabilityDescription && reliabilityImage && reliabilityComment) {
      hadleLayDiem();
    }
  }, [reliabilityDescription, reliabilityImage, reliabilityComment]);

  const removeData = () => {
    setData(null);
    setUrl('')
    setReliabilityComment(null);
    setReliabilityDescription(null);
    setRate([]);
    setReliabilityImage(null);
    setFull(null);
    setFlagAnalyse(false);
    setFlagFinal(false);
    setFlagReviewAI(false)
  }

  return (
    <div className="min-h-screen pt-16 flex items-center justify-center px-6 bg-slate-900 text-white">
      {isModalOpen && (
        <ModelComponent rate={rate} onClose={handleCloseModal} description={reliabilityDescription} comment={reliabilityComment} image={reliabilityImage} />
      )}
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Khung bên trái: Nhập thông tin sản phẩm */}
        <div className="bg-white text-slate-800 p-6 rounded-2xl shadow-lg" data-aos="fade-right">
          <div className="flex flex-col h-full">

            <h2 className="text-2xl font-semibold mb-4">Nhập thông tin sản phẩm</h2>

            <div className="mb-4">

              <div className="flex mb-4">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="URL / Giá trị cần phân tích "
                  className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  className={`px-4 py-2 rounded-r-lg transition-all cursor-pointer
                    ${(isLoading || flagStartAnalyse)? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'}`}
                  onClick={getData}
                  disabled={isLoading || flagStartAnalyse}
                >
                  {isLoading ? 'Đang tải...' : 'Lấy dữ liệu'}
                </button>
              </div>

              <div className="mb-4 space-y-1">
                {isLoading ? (
                  <>
                    <div className="h-5 bg-gray-200 rounded w-3/4 animate-pulse"></div>
                    <div className="h-5 bg-gray-200 rounded w-1/4 animate-pulse"></div>
                    <div className="h-5 bg-gray-200 rounded w-1/3 animate-pulse"></div>
                  </>
                ) : (
                  <>
                    <p className="font-medium line-clamp-2 cursor-pointer" title={productInfo?.name || "..."}>
                      {productInfo?.name || "Tên sản phẩm..."}
                    </p>
                    <p>Giá: <span className="font-semibold text-blue-600">{productInfo?.price ? `${productInfo.price.toLocaleString('vi-VN')} đ` : 'chưa có'}</span></p>
                    <p>Điểm đánh giá: ⭐ {productInfo?.rating_average || 'chưa có'}</p>
                    <p>Tổng đánh giá: {productInfo?.review_count || 'chưa có'}</p>
                    <p>Đã bán: {productInfo?.sold_quantity || 'chưa có'}</p>

                    <div className='flex'>
                      <p className='w-[100px]'>
                        <a href={productInfo?.image} target='_blank' rel='noopener noreferrer'>
                          <img
                            src={productInfo?.image || ''}
                            alt='Product'
                            className='w-full h-auto object-cover cursor-pointer hover:opacity-80 transition'
                          />
                        </a>
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="mt-auto pt-4 relative ">
              {flagFinal && (
                <button
                  onClick={() => removeData()}
                  className="py-2 px-2 rounded-lg transition-all absolute right-0 bottom-[100%] bg-gradient-to-r from-blue-500 to-indigo-600 hover:opacity-90 cursor-pointer"
                >
                  Xóa dữ liệu
                </button>
              )}
              <div className="space-y-2 mb-4 border-t border-gray-200">
                <p className={`cursor-pointer hover:underline ${isLoading ? 'text-orange-500' : 'text-blue-500'}`}>
                  ⟳ {message}
                </p>
              </div>
              <button
                className={`w-full py-2 rounded-lg transition-all
                  ${(isLoading || !productInfo || flagStartAnalyse) ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:opacity-90'}`}
                disabled={isLoading || !productInfo || flagStartAnalyse}
                onClick={() => { handleTinhDOTinCay() }}
              >
                Tính độ tin cậy
              </button>
            </div>
          </div>
        </div>

        {/* Khung bên phải: Kết quả dự đoán */}
        <div className="bg-white text-slate-800 p-6 rounded-2xl shadow-lg " data-aos="fade-left">

          <h2 className="text-2xl font-semibold mb-4">Kết quả dự đoán</h2>
          {flagStartAnalyse ? (
            <ul className="my-4 space-y-1 ">
              <li>
                Mô tả sản phẩm:
                <span className="font-semibold text-blue-600 ml-2">
                  {reliabilityDescription ? "Đã xong ✅" : "Đang phân tích ⏳"}
                </span>
              </li>
              <li>
                Hình ảnh:
                <span className="font-semibold text-blue-600 ml-2">
                  {reliabilityImage ? "Đã xong ✅" : "Đang phân tích ⏳"}
                </span>
              </li>
              <li>
                Đánh giá người dùng:
                <span className="font-semibold text-blue-600 ml-2">
                  {reliabilityComment ? "Đã xong ✅" : "Đang phân tích ⏳"}
                </span>
              </li>

            </ul>
          ) : (
            <ul className="my-4 space-y-1  relative">
              <li>
                Mô tả sản phẩm:
                <span className="font-semibold text-blue-600 ml-2">
                  {rate[0]}
                </span>
              </li>
              <li>
                Hình ảnh:
                <span className="font-semibold text-blue-600 ml-2">
                  {rate[1]}
                </span>
              </li>
              <li>
                Đánh giá người dùng:
                <span className="font-semibold text-blue-600 ml-2">
                  {rate[2]}
                </span>
              </li>


              {flagFinal && (
                <div className="absolute right-2 bottom-1 text-blue-500 cursor-pointer" onClick={handleOpenModal}>
                  Xem chi tiết
                </div>
              )}

            </ul>
          )}

          {/* Biểu đồ */}
          <div className="w-full h-[250px] justify-center flex bg-gray-100 rounded mb-4 items-end px-2">
            <div className='w-full'>
              <p className='!pb-4 !text-center font-semibold text-lg' >Biểu đồ độ tin cậy</p>
              <div className='flex justify-center'>
                {rate && rate.length === 3 && (
                  <ChartComponent index={rate} />
                )}
              </div>
            </div>
          </div>
          <h3 className="font-semibold mb-2 mt-6">Kết quả</h3>
          <div className="border border-gray-300 rounded-lg p-3 bg-gray-50 text-gray-600 cursor-pointer">
            {flagReviewAI ? (
              full ? (
                <div>
                  <p><strong>Điểm đánh giá:</strong> {full.total.score.toFixed(2)}</p>
                  <p><strong>Nhận xét:</strong> {full.total.comment}</p>
                </div>
              ) : (
                <p>Đang thực hiện đánh giá cuối cùng...</p>
              )
            ) : (
              <p>Chưa có dữ liệu.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};