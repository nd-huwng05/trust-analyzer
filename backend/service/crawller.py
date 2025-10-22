import requests
import re

import time
import random
import json
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Biến global để lưu trữ tất cả các bản ghi đã cào trong bộ nhớ
SCRAPED_DATA_STORE = []

# ----------------- CÁC HÀM UTILITY/SCRAPER -----------------
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
]


def get_random_header(referer_url=None):
    """Tạo header ngẫu nhiên."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'x-api-source': 'web',
    }
    if referer_url:
        # Đảm bảo referer_url chỉ chứa các ký tự an toàn cho header (ASCII)
        try:
            headers['Referer'] = referer_url.encode('latin-1', 'ignore').decode('latin-1')
        except Exception:
            # Dùng URL cơ bản nếu việc mã hóa thất bại
            headers['Referer'] = "https://tiki.vn"
    return headers


def extract_tiki_product_id(url):
    """Trích xuất product_id từ URL sản phẩm Tiki."""
    regex = r"p(\d+)\.html"
    match = re.search(regex, url)
    if match:
        return int(match.group(1))
    return None


def fetch_product_data(product_id, referer_url, max_retries=3):
    api_url = f"https://tiki.vn/api/v2/products/{product_id}?platform=web"
    for attempt in range(max_retries):
        dynamic_headers = get_random_header(referer_url)
        try:
            response = requests.get(api_url, headers=dynamic_headers, timeout=10)
            response.raise_for_status()
            print(f"Lấy dữ liệu sản phẩm thành công ở lần thử thứ {attempt + 1}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi lần thử {attempt + 1} cho ID {product_id}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print("Đã hết số lần thử lại.")
                return None
    return None
def fetch_reviews_data(product_id, desired_total=20, per_page=20, sleep_between=0.5, max_retries=3):
    collected = []
    page = 1
    while len(collected) < desired_total:
        api_url = (
            f"https://tiki.vn/api/v2/reviews?"
            f"product_id={product_id}&page={page}&limit={per_page}"
            f"&include=comments,contribute_info,attribute_vote_summary,attribute_vote_stats"
            f"&sort=score_desc,created_at%20desc"
        )
        success = False
        for attempt in range(max_retries):
            try:
                resp = requests.get(api_url, headers=get_random_header(), timeout=10)
                resp.raise_for_status()
                j = resp.json()
                success = True
                break
            except requests.exceptions.RequestException as e:
                print(f"❌ Lỗi lần thử {attempt + 1} khi lấy review trang {page}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"💥 Đã hết số lần thử lại cho review trang {page}.")
                    return collected
        if not success:
            break
        page_items = j.get("data") or j.get("reviews") or []
        if not page_items:
            print(f"⚠️ Hết dữ liệu ở trang {page}.")
            break
        collected.extend(page_items)
        print(f"✅ Lấy được {len(page_items)} bình luận ở trang {page} (Tổng: {len(collected)})")
        if len(collected) >= desired_total or len(page_items) < per_page:
            break
        page += 1
        time.sleep(sleep_between)
    print(f"🎯 Tổng cộng lấy được {len(collected)} bình luận.")
    return collected[:desired_total]


def parse_product_to_json(data):
    if not data:
        return {}
    current_seller = data.get("current_seller", {})
    store_url = f"{current_seller['link']}" if current_seller and current_seller.get('link') else None

    description_html = data.get("description", "")
    soup = BeautifulSoup(description_html, "html.parser")
    description_text = soup.get_text(separator="\n", strip=True)

    highlight_items = data.get("highlight", {}).get("items", [])

    specs = [{"name": a["name"], "value": a["value"]}
             for s in data.get("specifications", [])
             for a in s.get("attributes", [])]

    gallery = [img["base_url"] for img in data.get("images", []) if img.get("base_url")]

    description_imgs = [link for link in description_html.split('"')
                        if link.startswith("https") and (
                                link.endswith(".jpg") or link.endswith(".png") or link.endswith(".webp"))]

    return {
        "product_id": data.get("id"),
        "name": data.get("name"),
        "brand": data.get("brand", {}).get("name"),
"price": data.get("price"),
        "rating_average": data.get("rating_average"),
        "review_count": data.get("review_count"),
        "sold_quantity": data.get("all_time_quantity_sold"),
        "store_url": store_url,
        "highlights": highlight_items,
        "specifications": specs,
        "description_text": description_text,
        "gallery_images": gallery,
        "description_images": description_imgs,
    }


def extract_next_value(keyword, all_text):
    lines = all_text.split("\n")
    for i, line in enumerate(lines):
        if keyword in line:
            for j in range(i + 1, len(lines)):
                val = lines[j].strip()
                if val:
                    return val
    return "Không có dữ liệu"


def fetch_store_data_selenium(url):
    if not url:
        return {"error": "Không có URL cửa hàng để cào."}

    print(f"🛠️ Bắt đầu cào dữ liệu cửa hàng bằng Selenium cho URL: {url}")
    options = Options()
    options.add_argument("--headless")  # Chạy ẩn để không thấy cửa sổ trình duyệt
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo WebDriver: {e}")
        return {"error": "Lỗi khởi tạo WebDriver. Đảm bảo Chromedriver đã được cài đặt đúng cách."}

    try:
        final_url = url
        if '?' not in url:
            final_url = f"{url}?t=storeInfo"
        elif 't=' not in url:
            final_url = f"{url}&t=storeInfo"

        driver.get(final_url)
        print("⏳ Chờ 5 giây để tải nội dung JavaScript...")
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        store_name_tag = soup.find('h1')
        store_name = store_name_tag.get_text(strip=True) if store_name_tag else "Không có dữ liệu"

        all_text = soup.get_text(separator="\n")

        followers = "0"
        chat_response = "Chưa có"
        spans = soup.find_all("span")
        for i, span in enumerate(spans):
            text = span.get_text(strip=True)
            if text == "Người theo dõi" and i + 1 < len(spans):
                followers = spans[i + 1].get_text(strip=True)
            if text == "Phản hồi Chat" and i + 1 < len(spans):
                chat_response = spans[i + 1].get_text(strip=True)

        data = {
            "store_name": store_name,
            "member_since": extract_next_value("Thành viên từ năm", all_text),
            "products_count": extract_next_value("Sản phẩm", all_text),
            "store_description": extract_next_value("Mô tả cửa hàng", all_text),
"rating_score": extract_next_value("Đánh giá", all_text),
            "followers": followers,
            "chat_response_rate": chat_response
        }
        print("✅ Lấy dữ liệu cửa hàng thành công.")
        return data

    except Exception as e:
        print(f"❌ Lỗi khi cào dữ liệu cửa hàng: {e}")
        return {"error": f"Lỗi không xác định khi cào dữ liệu cửa hàng: {e}"}

    finally:
        try:
            driver.quit()
            print("Driver đã được đóng.")
        except NameError:
            pass

        # ----------------- HÀM LƯU & LẤY DỮ LIỆU GLOBAL -----------------


def save_to_global_store( url, data):
    """Xóa tất cả dữ liệu cũ trong Global Store và chỉ lưu bản ghi mới nhất."""
    global SCRAPED_DATA_STORE

    # Xóa toàn bộ dữ liệu cũ (Đảm bảo chỉ giữ lại 1 bản ghi mới nhất)
    SCRAPED_DATA_STORE.clear()

    data_to_save = {
        "url": url,
        "information": data
    }

    # Thêm bản ghi mới
    SCRAPED_DATA_STORE.append(data_to_save)
    print(f"💾 Xóa dữ liệu cũ và Lưu bản ghi mới  vào Global Store thành công.")
    return True


def get_all_scraped_data_from_global():
    """Lấy tất cả dữ liệu đã lưu từ biến global."""
    global SCRAPED_DATA_STORE
    return SCRAPED_DATA_STORE.copy()


# ----------------- FLASK API LOGIC CỐT LÕI -----------------

def process_tiki_url(tiki_url):
    """
    Hàm logic cốt lõi: Lấy dữ liệu sản phẩm, đánh giá và cửa hàng từ một URL Tiki.
    Trả về dictionary dữ liệu và status code.
    """
    if not tiki_url:
        return {"error": "Vui lòng cung cấp URL sản phẩm Tiki."}, 400

    product_id = extract_tiki_product_id(tiki_url)
    if not product_id:
        return {"error": "Không thể lấy product_id từ URL cung cấp."}, 400

    # 1. Lấy dữ liệu sản phẩm
    product_data = fetch_product_data(product_id, tiki_url)
    if not product_data:
        return {"error": "Không thể lấy dữ liệu sản phẩm từ API Tiki."}, 500

    parsed_product = parse_product_to_json(product_data)
    # 2. Lấy dữ liệu đánh giá
    reviews = fetch_reviews_data(product_id, desired_total=20)

    # 3. Lấy dữ liệu cửa hàng
    store_url = parsed_product.get("store_url")
    store_data = {}
    if store_url:
        final_store_url = f"{store_url}?t=storeInfo" if '?' not in store_url else f"{store_url}&t=storeInfo"
        # Giả định fetch_store_data_selenium đã được định nghĩa
        store_data_raw = fetch_store_data_selenium(final_store_url)
        store_data = {"store_data": store_data_raw}
    else:
        store_data = {"store_data": {"error": "Không tìm thấy thông tin cửa hàng."}}

    # 4. Xây dựng kết quả cuối cùng

    # Khởi tạo danh sách properties từ specs
    product_properties = [f"{spec['name']}: {spec['value']}" for spec in parsed_product.get("specifications", [])]

    # 🔑 SỬA LỖI CÚ PHÁP: Thêm các trường cốt lõi vào danh sách properties dưới dạng chuỗi
    product_properties.append(f"price: {parsed_product.get('price')}")
    product_properties.append(f"rating_average: {parsed_product.get('rating_average')}")
    product_properties.append(f"review_count: {parsed_product.get('review_count')}")
    product_properties.append(f"sold_quantity: {parsed_product.get('sold_quantity')}")

    image_buyer_urls = list({
        img["full_path"]
        for r in reviews
        for img in r.get("images", [])
        if img.get("full_path")
    })

    result = {
        **store_data,
        "name": parsed_product.get("name"),
        "description": parsed_product.get("description_text"),
        "properties": product_properties,  # CHỨA CẢ THÔNG TIN CỐT LÕI VÀ SPECS
        "image_product": parsed_product.get("description_images", []) + parsed_product.get("gallery_images", []),
        "image_buyer": image_buyer_urls,
        "reviews": [
            {
                "rating": r.get("rating"),
                "title": r.get("title"),
                "content": r.get("content"),
            }
            for r in reviews
        ]
    }

    return result, 200

# ... (Hàm extract_core_metrics giữ nguyên như bạn cung cấp) ...

def extract_core_metrics(result_data: dict) -> dict:
    properties_list = result_data.get('properties', [])
    metrics = {
        'price': None,
        'rating_average': None,
        'review_count': None,
        'sold_quantity': None,
    }

    # Duyệt qua từng chuỗi trong danh sách properties
    for prop_str in properties_list:
        try:
            # Phân tách thành key và value
            key, value_str = prop_str.split(':', 1)
            key = key.strip()
            value_str = value_str.strip()

            # Xử lý và lưu giá trị
            if key == 'price':
                # Chuyển sang số nguyên (loại bỏ ký tự không phải số)
                metrics['price'] = int(''.join(filter(str.isdigit, value_str)))
            elif key == 'rating_average':
                # Chuyển sang số thực
                metrics['rating_average'] = float(value_str)
            elif key == 'review_count':
                metrics['review_count'] = int(value_str)
            elif key == 'sold_quantity':
                metrics['sold_quantity'] = int(value_str)

        except (ValueError, IndexError):
            # Bỏ qua các chuỗi không phải key:value hoặc không thể chuyển đổi số
            continue

    return metrics


# ----------------- FLASK API ENDPOINTS -----------------
app = Flask(__name__)

# 2. Áp dụng CORS
CORS(app)


@app.route('/api/tiki-product', methods=['GET'])
def scrape_and_save():
    """Endpoint API: Cào dữ liệu từ URL và LƯU/CẬP NHẬT vào Biến Global."""
    print("--- API /tiki-product ĐƯỢC GỌI ---")
    tiki_url = request.args.get('url')
    if not tiki_url:
        return jsonify({"error": "Vui lòng cung cấp URL sản phẩm Tiki trong tham số 'url'."}), 400

    # 1. Thực hiện cào dữ liệu
    result, status_code = process_tiki_url(tiki_url)

    if status_code != 200:
        return jsonify(result), status_code
    print("result: ", result)
    #  BƯỚC 1: TRÍCH XUẤT CÁC CHỈ SỐ CẦN THIẾT TỪ DANH SÁCH 'properties'
    res = extract_core_metrics(result)
    print("Metrics trích xuất được (res):", res)

    # 2. Lưu vào Biến Global
    success = save_to_global_store( tiki_url, result)

    if success:
        # IN TRẠNG THÁI GLOBAL STORE ĐỂ XEM
        print("\n=============================================")
        print(f"✅ LƯU/CẬP NHẬT thành công ID.")
        print(f"📊 Tổng số bản ghi trong SCRAPED_DATA_STORE hiện tại: {len(SCRAPED_DATA_STORE)}")
        print(f"   Bản ghi vừa lưu")
        print("=============================================")

        # BƯỚC 2: TRẢ VỀ CÁC GIÁ TRỊ ĐÃ ĐƯỢC TRÍCH XUẤT TỪ 'res'
        return jsonify({
            "message": f"Cào dữ liệu thành công và đã LƯU/CẬP NHẬT vào Global Store .",
            "data_preview": {
                "name": result.get('name'),
                "price": res.get('price'),
                "rating_average": res.get('rating_average'),
                "review_count": res.get('review_count'),
                "sold_quantity": res.get('sold_quantity'),
                "image": result.get('image_product')[0]
            }
        }), 200
    else:
        return jsonify({"error": "Lỗi không xác định khi lưu vào Global Store."}), 500

@app.route('/api/get-data', methods=['GET'])
def get_saved_data():
    """Endpoint API: Lấy DỮ LIỆU GẦN NHẤT đã lưu trong Biến Global."""
    global SCRAPED_DATA_STORE

    if not SCRAPED_DATA_STORE:
        print("Không tìm thấy dữ liệu nào đã được lưu trong Global Store.")
        return jsonify({"message": "Không tìm thấy dữ liệu nào đã được lưu trong Global Store."}), 200

    # Lấy bản ghi cuối cùng (và duy nhất)
    latest_record = SCRAPED_DATA_STORE[-1].copy()

    # Lấy thông tin chi tiết (information)
    data_content = latest_record['information']

    # In ra console
    print("\n=============================================")
    print("Yêu cầu lấy dữ liệu GẦN NHẤT từ Global Store.")
    print(f"Bản ghi được trả về thành công")
    print("=============================================")

    # Trả về đối tượng dữ liệu duy nhất
    return jsonify({
        "message": "Dữ liệu cào gần nhất đã được lấy thành công.",
"data": data_content
    }), 200

@app.route('/api/tiki', methods=['GET'])
def tiki_full_scrape():
    """API duy nhất: Nhập URL sản phẩm, trả về tất cả dữ liệu và lưu vào Global Store."""
    tiki_url = request.args.get('url')
    if not tiki_url:
        return jsonify({"error": "Vui lòng cung cấp URL sản phẩm Tiki."}), 400

    # --- 1. Xử lý URL và lấy product_id ---
    product_id = extract_tiki_product_id(tiki_url)
    if not product_id:
        return jsonify({"error": "Không thể lấy product_id từ URL."}), 400

    # --- 2. Lấy dữ liệu sản phẩm ---
    product_data = fetch_product_data(product_id, tiki_url)
    if not product_data:
        return jsonify({"error": "Không thể lấy dữ liệu sản phẩm."}), 500
    parsed_product = parse_product_to_json(product_data)

    # --- 3. Lấy review ---
    reviews = fetch_reviews_data(product_id, desired_total=20)

    # --- 4. Lấy dữ liệu cửa hàng ---
    store_url = parsed_product.get("store_url")
    store_data = {}
    if store_url:
        final_store_url = f"{store_url}?t=storeInfo" if '?' not in store_url else f"{store_url}&t=storeInfo"
        store_data = fetch_store_data_selenium(final_store_url)
    else:
        store_data = {"error": "Không tìm thấy thông tin cửa hàng."}

    # --- 5. Build kết quả ---
    product_properties = [f"{spec['name']}: {spec['value']}" for spec in parsed_product.get("specifications", [])]
    product_properties += [
        f"price: {parsed_product.get('price')}",
        f"rating_average: {parsed_product.get('rating_average')}",
        f"review_count: {parsed_product.get('review_count')}",
        f"sold_quantity: {parsed_product.get('sold_quantity')}"
    ]

    image_buyer_urls = list({
        img["full_path"]
        for r in reviews
        for img in r.get("images", [])
        if img.get("full_path")
    })

    result = {
        "store_data": store_data,
        "name": parsed_product.get("name"),
        "description": parsed_product.get("description_text"),
        "properties": product_properties,
        "image_product": parsed_product.get("description_images", []) + parsed_product.get("gallery_images", []),
        "image_buyer": image_buyer_urls,
        "reviews": [{"rating": r.get("rating"), "title": r.get("title"), "content": r.get("content")} for r in reviews]
    }

    # --- 6. Lưu vào Global Store ---
    save_to_global_store(tiki_url, result)

    # --- 7. Trả về JSON full data ---
    return jsonify({
        "message": "Cào dữ liệu thành công và đã lưu vào Global Store.",
        "full_data": result
    }), 200

if __name__ == '__main__':
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))

    print("\nKhởi chạy Flask API (Sản phẩm, Cửa hàng & Global Store).")
    print("----------------------------------------------------------------------")
    print("LƯU TRỮ DỮ LIỆU: Đang sử dụng biến Global Store (trong bộ nhớ).")
    print("HƯỚNG DẪN: Đã sử dụng use_reloader=False để đảm bảo biến global hoạt động.")
    print("----------------------------------------------------------------------")
    print(f"1. CÀO & LƯU DỮ LIỆU: GET http://{host}:{port}/api/tiki-product?url=<Tiki_Product_URL>")
    print(f"2. LẤY DỮ LIỆU VỪA LƯU: GET http://{host}:{port}/api/get-data")
    print("----------------------------------------------------------------------")

    # SỬ DỤNG use_reloader=False để đảm bảo biến global không bị reset bởi tiến trình reloader
    app.run(debug=True, use_reloader=False, host=host, port=port)