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

## 🔹 Extension

* Placeholder folder for future browser extension development.
* Will allow trust analysis directly on e-commerce platforms.

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