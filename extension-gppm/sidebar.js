document.addEventListener("DOMContentLoaded", () => {
    const loadingEl = document.getElementById("loading");
    const container = document.getElementById("product-data");
    const aiSection = document.getElementById("ai-score-section");
    const analyzeBtn = document.getElementById("analyze-btn");

    // Hiển thị mặc định
    aiSection.style.display = "none";
    loadingEl.style.display = "none";
    analyzeBtn.disabled = true;

    const colorByScore = (score) => {
        if (score >= 70) return "#2ecc71";
        if (score >= 50) return "#f1c40f";
        return "#e74c3c";
    };

    const normalizeScore = (score) => {
        if (score == null) return null; // trả về null nếu không có dữ liệu
        return score <= 1 ? Math.round(score * 100) : Math.round(score);
    };

    analyzeBtn.addEventListener("click", async () => {
        if (!window.currentProduct) {
            alert("Chưa có dữ liệu sản phẩm để phân tích.");
            return;
        }

        const product = window.currentProduct;
        loadingEl.style.display = "block";
        loadingEl.innerHTML = `<div class="spinner"></div><p>AI đang phân tích sản phẩm, vui lòng chờ...</p>`;
        aiSection.style.display = "none";
        analyzeBtn.disabled = true;
        analyzeBtn.innerText = "Đang phân tích...";

        try {
            const [descRes, commentRes, imageRes] = await Promise.all([
                fetch("http://127.0.0.1:8000/api/trust-analyzer/analyze/description", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(product)
                }).then(r => r.json()),

                fetch("http://127.0.0.1:8000/api/trust-analyzer/analyze/comment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(product)
                }).then(r => r.json()),

                fetch("http://127.0.0.1:8000/api/trust-analyzer/analyze/image", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(product)
                }).then(r => r.json())
            ]);

            const payload = {};
            if (descRes.description) payload.description = descRes.description;
            if (commentRes.review) payload.review = commentRes.review;
            if (imageRes.image) payload.image = imageRes.image;

            const fullRes = await fetch("http://127.0.0.1:8000/api/trust-analyzer/analyze/full", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).then(r => r.json());

            // Chuẩn hóa điểm
            const totalScore = normalizeScore(fullRes.total?.score);
            const descScore = normalizeScore(descRes.score || descRes.description?.score);
            const imageScore = normalizeScore(imageRes.score || imageRes.image?.score);
            const commentScore = normalizeScore(commentRes.score || commentRes.review?.score);

            const overallFeedback = fullRes.total?.comment || "Không có nhận xét chung.";

            loadingEl.style.display = "none";
            aiSection.style.display = "block";

            // Bắt đầu render
            let html = `<h3>Kết quả phân tích sản phẩm</h3>`;

            // Điểm tổng thể luôn hiển thị
            html += `
<p><strong>Điểm tổng thể:</strong> 
    <span style="color:${colorByScore(totalScore)};font-size:1.2rem;font-weight:bold;">
        ${totalScore}/100
    </span>
</p>
<p>${overallFeedback}</p>
`;

            // Phân tích mô tả
            if (descRes.description || descRes.score) {
                html += `
    <div class="analysis-section">
        <h4>Phân tích mô tả</h4>
        <p><strong>Điểm:</strong> 
            <span style="color:${colorByScore(descScore)};font-weight:bold;">
                ${descScore}/100
            </span>
        </p>
    </div>`;
            } else {
                html += `
    <div class="analysis-section">
        <h4>Phân tích mô tả</h4>
        <p>Không có dữ liệu</p>
    </div>`;
            }

            // Phân tích hình ảnh
            if (imageRes.image || imageRes.score) {
                html += `
    <div class="analysis-section">
        <h4>Phân tích hình ảnh</h4>
        <p><strong>Điểm:</strong> 
            <span style="color:${colorByScore(imageScore)};font-weight:bold;">
                ${imageScore}/100
            </span>
        </p>
    </div>`;
            } else {
                html += `
    <div class="analysis-section">
        <h4>Phân tích hình ảnh</h4>
        <p>Không có dữ liệu</p>
    </div>`;
            }

            // Phân tích đánh giá
            if (commentRes.review || commentRes.score) {
                html += `
    <div class="analysis-section">
        <h4>Phân tích đánh giá</h4>
        <p><strong>Điểm:</strong> 
            <span style="color:${colorByScore(commentScore)};font-weight:bold;">
                ${commentScore}/100
            </span>
        </p>
    </div>`;
            } else {
                html += `
    <div class="analysis-section">
        <h4>Phân tích đánh giá</h4>
        <p>Không có dữ liệu</p>
    </div>`;
            }

            aiSection.innerHTML = html;


        } catch (err) {
            console.error("Lỗi khi gọi các API phân tích:", err);
            loadingEl.innerHTML = `<p style="color:red;">❌ Lỗi khi phân tích sản phẩm!</p>`;
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "Phân tích sản phẩm";
        }
    });

    window.addEventListener("message", (event) => {
        if (event.data.action === "SET_PAGE_URL") {
            loadProductData(event.data.url);
        }
    });

    function loadProductData(url) {
        loadingEl.style.display = "block";
        container.style.display = "none";
        analyzeBtn.disabled = true;

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
                    window.currentProduct = product;
                    analyzeBtn.disabled = false;

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
