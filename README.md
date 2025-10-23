# Trust Analyzer

**Trust Analyzer** is an AI-powered tool for **analyzing and evaluating the trustworthiness of products, sellers, or stores** based on descriptions, images, and reviews. The system combines **deep learning models (YOLOv8) with Python APIs and Hugging Face transformers models** to provide quick and insightful trust evaluations.

It leverages several Hugging Face pretrained models for natural language processing, including:

* `MoritzLaurer/deberta-v3-base-zeroshot-v1` for product anomaly detection.
* `visolex/visobert-spam-classification` for fake review detection.
* `5CD-AI/Vietnamese-Sentiment-visobert` for sentiment analysis.
* `Qwen/Qwen2-VL-2B-Instruct` for multimodal language-image reasoning.

## 🔹 Features

* Analyze **product descriptions** to detect authenticity using zero-shot classification.
* Analyze **product images** using YOLOv8 and CLIP embeddings for similarity checks.
* Detect **fake or spam reviews** using Hugging Face transformer models.
* Analyze **sentiment of reviews** for trust evaluation.
* Combine multiple modalities (text + images) for a comprehensive **trust score**.
* Easy-to-integrate API for other systems.

## 🔹 Installation

1. **Clone the repository**

```bash
git clone https://github.com/nd-huwng05/trust-analyzer.git
cd trust-analyzer
```

2. **Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **Prepare YOLOv8 and Hugging Face models**

* The YOLOv8 model `yolov8m.pt` is included.
* Hugging Face models will be automatically downloaded on first use.

## 🔹 Running the API

```bash
python runAPI.py
```

* API runs at `http://127.0.0.1:8000`
* Endpoints for image and description analysis: `/api/trust-analyzer/analyze/image` or `/api/trust-analyzer/analyze/description`
* Sample JSON input (for demonstration purposes):

```json
{
    "description": "<sample product description here>",
    "image_buyer": ["<buyer image URLs>"],
    "image_product": ["<product image URLs>"],
    "name": "<product name>",
    "properties": ["<product properties>"] ,
    "reviews": ["<list of reviews>"] ,
    "store_data": {"<store info>": "<value>"}
}
```

* Sample JSON response:

```json
{
    "description": {"label": "mô tả sản phẩm hợp lệ", "score": 0.9478},
    "review": {"trust_score": 69, "non_spam_ratio": 75.0, "count_spam": 2, "count_normal": 6, "summary": {"sentiment_ratio": {"POS": 74.29, "NEG": 11.59, "NEU": 14.12}, "comment": "Đa số review tích cực, sản phẩm đáng tin cậy"}},
    "image": {"score": 77.91, "best_matches": [ {"buyer_path": "<url>", "seller_path": "<url>", "score": 86, "avg_score": 79.0} ]},
    "total": {"score": 77.91, "comment": "Overall trust score based on combined analyses."}
}
```

* **Note:** Individual API calls for description, image, and review analysis take around **5-10 seconds** each. Running the full combined API may take longer depending on input size.

## 🔹 Directory Structure

```
trust-analyzer/
│
├─ backend/           # API code, model wrappers, utilities
├─ frontend/          # User interface (UI) and design placeholder
├─ extension-gppm/    # Browser extension placeholder
├─ runAPI.py          # API entry point
├─ requirements.txt   # Python dependencies
└─ README.md
```

## 🔹 Frontend

* Placeholder folder for frontend interface development.
* Supports integration with backend API.
* UI/UX design to be implemented.

### Feature
-  **Product Data Crawling:**  
  Automatically extracts product information from e-commerce sites (currently supports **Tiki.vn**) using the product link entered by the user.
-  **Seller Reliability Analysis:**  
 Evaluates sellers by analyzing product descriptions, user reviews, and product images to assess trustworthiness and detect potential spam.
- **Behavior Scoring:**  
  Generates a seller behavior score using AI/algorithmic analysis to help users quickly assess the reliability of a seller.
- **Interactive Visualization:**  
  Displays data and analysis results through intuitive charts and sidebars, including:  
  - Trust score breakdown  
  - Spam rate vs normal comments  
  - Emotion distribution in customer feedback
- **User-Friendly Interface:**  
  Built with **React.js** and **TailwindCSS** for a responsive and smooth user experience.
- **Fast and Efficient:**  
  Powered by **Vite** for rapid build and optimized performance, ensuring data scraping and analysis are done quickly.

### Structure
```
frontend/my-project  
├── nodes_module # Dependencies installed from npm  
├── public # Scripts injected into e-commerce pages  
├── src # Core logic for the sidebar UI and API calls  
├── .env # Environment variables (e.g., API_URL..)
├── package.json  # Project metadata, dependencies, and scripts
├── vite.config.js  # Vite configuration (aliases, server, build settings)
```

### How to Use Website
1. Enter a **product link** into the input field (currently supports products from **Tiki.vn**).  
2. Click **"Fetch Data"** to scrape product information from the website.  
3. After the data is loaded, click **"Check Reliability"** to analyze and evaluate the seller’s trust score.
   - **Overall score** of the product
   - **Analysis of description, images, and reviews**
   - **Store information**
   - **Featured reviews**

## 🔹 Extension

The extension will allow users to:

- Analyze product trustworthiness directly on the product page.
- View AI-generated scores for product description, images, and reviews.
- Get a summary of the store's credibility.
- Make more informed purchasing decisions without leaving the e-commerce site.

### Features

- **Sidebar UI**: Displays the trust analysis without redirecting the user.
- **Real-time AI Scoring**: Pulls data from the backend API and shows scores.
- **Review Highlights**: Show insights from customer reviews.
- **Image Analysis**: Evaluate product and customer-submitted images.
- **Store Info**: Provide key information about the seller or store.

### Structure
```
extension-gppm/
├── manifest.json # Browser extension manifest
├── background.js # Background scripts
├── content.js # Scripts injected into e-commerce pages
├── sidebar.js # Logic for sidebar UI and API calls
├── sidebar.html # Sidebar HTML layout
└── sidebar.css # Sidebar styling
```
### How to Use Extension-GPPM

#### 1. Install the Extension (Developer Mode)

1. Open Chrome (or any Chromium-based browser) and go to:  
   `chrome://extensions/`
2. Enable **Developer mode** (top-right corner).
3. Click **Load unpacked**.
4. Select the `extension-gppm/` folder on your computer.
5. The extension will be added to your browser.

#### 2. Using on E-commerce Pages

1. Go to a product page on **Tiki**.
2. Click the extension icon in the browser toolbar.
3. A sidebar will appear on the right side of the page.
4. Click **Analyze Product** to send data to the Trust Analyzer backend.
5. The results will display:
   - **Overall score** of the product
   - **Analysis of description, images, and reviews**
   - **Store information**
   - **Featured reviews**

#### 3. Notes

- The extension currently requires the **backend API** to be running, which includes:
  - `runAPI.py`
  - `backend/service/crawller.py`
- If the backend is not running, the sidebar cannot perform product analysis.
- Currently, the extension only supports **Tiki**; other platforms may be added in the future.

## 🔹 Technologies Used

* Python 3.10+
* YOLOv8 (Ultralytics)
* Hugging Face Transformers (DeBERTa, ViSoBERT, Qwen2VL, CLIP)
* FastAPI / Flask (backend API)
* HTML/CSS/JavaScript (frontend placeholder)

## 🔹 Future Development

* Add **review and comment analysis** for products.
* Combine multiple models to **detect fake images or misleading descriptions**.
* Develop a **browser plugin** for e-commerce platforms.
* Enhance **multimodal reasoning** using images and text together for more accurate trust scores.

## 🔹 License


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🔹 Contact

If you have any questions or feedback, feel free to reach out to our team members:

- **Hung** – 2351050067 – [hung@ou.edu.vn](mailto:hung@ou.edu.vn)  
- **Huy** – 2351050061 – [huy@ou.edu.vn](mailto:huy@ou.edu.vn)  
- **Khoa** – 2351050081 – [khoa@ou.edu.vn](mailto:khoa@ou.edu.vn)  




