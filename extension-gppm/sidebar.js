document.addEventListener("DOMContentLoaded", () => {
    const loadingEl = document.getElementById("loading");
    const container = document.getElementById("product-data");
    const aiSection = document.getElementById("ai-score-section");
    const scoreEl = document.getElementById("score");
    const commentEl = document.getElementById("score-comment");
    const analyzeBtn = document.getElementById("analyze-btn");

    // Mẫu AI Score
    const aiData = {
        score: 35,
        comment: "Điểm tin cậy của nội dung sản phẩm là 35/100, thấp hơn mức đáng tin."
    };

    // Hiển thị luôn khung AI Score
    aiSection.style.display = "block";
    scoreEl.innerText = aiData.score;
    commentEl.innerText = aiData.comment;

    analyzeBtn.addEventListener("click", () => {
        alert("Đang phân tích sản phẩm...");
        window.parent.postMessage({
            action: "UPDATE_SCORE",
            score: aiData.score,
            comment: aiData.comment
        }, "*");
    });

    // Nhận URL từ content.js
    window.addEventListener("message", (event) => {
        if (event.data.action === "SET_PAGE_URL") {
            const currentUrl = event.data.url;
            loadProductData(currentUrl);
        }
    });

    function loadProductData(url) {
        // Hiển thị loading
        loadingEl.style.display = "block";
        container.style.display = "none";

        if (!url.includes("tiki.vn")) {
            loadingEl.style.display = "none";
            container.innerHTML = "<p>Vui lòng mở trang sản phẩm Tiki.</p>";
            container.style.display = "block";
            return;
        }

        fetch(`http://127.0.0.1:5000/api/tiki?url=${encodeURIComponent(url)}`)
            .then(res => res.json())
            .then(data => {
                loadingEl.style.display = "none";
                container.style.display = "block";

                if (data.full_data) {
                    const product = data.full_data;
                    container.innerHTML = `
                        <div class="product-section">
                            <h2>${product.name}</h2>
                            <p>${product.description}</p>
                            <strong>Giá:</strong> ${product.properties.find(p => p.startsWith('price'))?.split(':')[1]} VND
                            <p>Rating: ${product.properties.find(p => p.startsWith('rating_average'))?.split(':')[1]}</p>
                            <p>Review count: ${product.properties.find(p => p.startsWith('review_count'))?.split(':')[1]}</p>
                            <p>Sold: ${product.properties.find(p => p.startsWith('sold_quantity'))?.split(':')[1]}</p>
                        </div>
                        <div class="product-section">
                            <h3>Hình ảnh sản phẩm</h3>
                            ${product.image_product.map(img => `<img src="${img}" style="max-width:100px;margin:5px;" />`).join('')}
                        </div>
                        <div class="product-section">
                            <h3>Hình ảnh từ khách hàng</h3>
                            ${product.image_buyer.map(img => `<img src="${img}" style="max-width:80px;margin:3px;" />`).join('')}
                        </div>
                        <div class="product-section">
                            <h3>Reviews</h3>
                            ${product.reviews.map(r => `
                                <div style="border-bottom:1px solid #ccc;padding:5px 0;">
                                    <strong>${r.title || ''}</strong>
                                    <p>${r.content || ''}</p>
                                    <em>Rating: ${r.rating || ''}</em>
                                </div>
                            `).join('')}
                        </div>
                        <div class="product-section">
                            <h3>Thông số sản phẩm</h3>
                            <ul>${product.properties.map(p => `<li>${p}</li>`).join('')}</ul>
                        </div>
                        <div class="product-section">
                            <h3>Thông tin cửa hàng</h3>
                            <p>Tên cửa hàng: ${product.store_data.store_name || ''}</p>
                            <p>Follower: ${product.store_data.followers || ''}</p>
                            <p>Thành viên từ: ${product.store_data.member_since || ''}</p>
                            <p>Mô tả cửa hàng: ${product.store_data.store_description || ''}</p>
                            <p>Đánh giá: ${product.store_data.rating_score || ''}</p>
                            <p>Phản hồi Chat: ${product.store_data.chat_response_rate || ''}</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = "<p>Không lấy được dữ liệu sản phẩm.</p>";
                }
            })
            .catch(err => {
                loadingEl.innerText = "Lỗi khi gọi API.";
                console.error(err);
            });
    }
});
