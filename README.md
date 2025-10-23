# 🧠 Trust Analyzer

**Trust Analyzer** is a comprehensive **AI-powered platform** for analyzing and verifying the **trustworthiness of online products, sellers, and stores**. It leverages **multimodal AI** (text, image, and reviews) with models like **YOLOv8**, **Qwen2-VL**, and **DeBERTa** to deliver accurate, real-time trust evaluations.

---

## 📘 Overview

This project includes three integrated components:

1. **Backend (AI + API Service)** — Core AI logic and FastAPI endpoints.  
2. **Frontend (Web Application)** — Interactive UI for visualization and user interaction.  
3. **Browser Extension (GPPM)** — On-page product analysis directly within e-commerce sites.

---

## 🌟 Core Features

| Category                 | Description                                                     | Model                                      |
| ------------------------ | --------------------------------------------------------------- | ------------------------------------------ |
| 🧾 Description Analysis  | Detects misleading or fake product descriptions                 | `MoritzLaurer/deberta-v3-base-zeroshot-v1` |
| 🚫 Fake Review Detection | Identifies spam and deceptive customer reviews                  | `visolex/visobert-spam-classification`     |
| 😊 Sentiment Analysis    | Evaluates sentiment in user reviews                             | `5CD-AI/Vietnamese-Sentiment-visobert`     |
| 🖼️ Image Comparison     | Detects visual inconsistencies between product and buyer images | `YOLOv8m.pt` + CLIP                        |
| 🧠 Multimodal Reasoning  | Combines text + image + reviews for overall scoring             | `Qwen/Qwen2-VL-2B-Instruct`                |

---

## 🧩 Backend (AI + API Service)

### 🔹 Installation

```bash
git clone https://github.com/nd-huwng05/trust-analyzer.git
cd trust-analyzer

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

**Models:**

* `yolov8m.pt` included by default.
* Hugging Face models auto-download on first use.

> 💡 For offline setups, manually download weights and update the config paths.

---

### 🚀 Running the API

```bash
python runAPI.py
```

Access API at **[http://your-ip:8000]**

**Available Endpoints:**

| Endpoint                                       | Description                               |
| ---------------------------------------------- | ----------------------------------------- |
| `POST /api/trust-analyzer/analyze/description` | Evaluate product description authenticity |
| `POST /api/trust-analyzer/analyze/image`       | Compare buyer vs product images           |
| `POST /api/trust-analyzer/analyze/comment`      | Detect fake reviews                       |
| `POST /api/trust-analyzer/analyze/full`         | Perform full multimodal analysis          |

---
### 🧠 Example Request & Response

**Request:**

```json
{
  "description": "High-quality leather wallet with RFID protection.",
  "image_buyer": ["<buyer_image_url>"],
  "image_product": ["<product_image_url>"],
  "name": "Leather Wallet",
  "properties": ["RFID", "Genuine Leather"],
  "reviews": ["Great wallet!", "Fake product, don't buy!"],
  "store_data": {"seller": "Tiki Store"}
}
```

**Response:**

```json
{
  "description": {"label": "Valid description", "score": 0.94},
  "review": {
    "trust_score": 72,
    "summary": {
      "sentiment_ratio": {"POS": 70, "NEG": 15, "NEU": 15},
      "comment": "Mostly positive reviews, product seems trustworthy."
    }
  },
  "image": {"score": 81.2},
  "total": {"score": 78.5, "comment": "Overall trustworthy."}
}
```

> ⚡ Average processing: 5–10s per request depending on input size.

---

### 📂 Backend Structure

```
backend/
├── routers/        # FastAPI routes
├── service/        # Analysis logic (image, text, review)
├── models/         # Pydantic schemas & AI models
├── utils/          # Helpers and configuration
└── main.py         # FastAPI entry
```

---

## 💻 Frontend (Web Application)

### 🔹 Description

Modern **React + TailwindCSS + Vite** interface for visualization of trust scores.
Supports data scraping from **Tiki.vn**, rendering of analysis results, and interactive charts.

### 🧠 Features

* Fetch data via product URL
* Evaluate description, reviews, and images
* Display overall trust score with graphs
* Real-time response from backend API

### 📁 Structure

```
frontend/my-project/
├── public/
├── src/
│   ├── components/
│   ├── api/
│   ├── pages/
│   └── utils/
├── package.json
└── vite.config.js
```

---

## 🧩 Browser Extension

### 🔹 Purpose

Analyze product trust **directly within e-commerce pages** — no copy-pasting links needed.

### ⚙️ Setup

1. Open `chrome://extensions/`
2. Enable **Developer Mode**
3. Click **Load unpacked** → select `extension-gppm/`
4. Navigate to a Tiki product page → click **Analyze Product**

> 🧠 Requires backend API to be running locally or remotely.

### 📁 Structure

```
extension-gppm/
├── manifest.json
├── background.js
├── content.js
├── sidebar.js
├── sidebar.html
└── sidebar.css
```

---

## 🧰 Tech Stack

**Languages:** Python 3.10+, JavaScript (ES6+)  
**Frameworks:** FastAPI, React, TailwindCSS, Vite  
**AI Models:** YOLOv8, DeBERTa, ViSoBERT, Qwen2-VL, CLIP  
**Libraries:** OpenCV, Ultralytics, Pydantic, Requests  
**Deployment:** Hugging Face Spaces, Chrome Extension

---


## 📬 Contact

| Name                   | Email                                                      |
| ---------------------- | ---------------------------------------------------------- |
| **Nguyen Dinh Hung**   |[2351050067hung@ou.edu.vn](mailto:2351050067hung@ou.edu.vn) |
| **Phan Gia Huy**       |[2351050061huy@ou.edu.vn](mailto:2351050061huy@ou.edu.vn)   |
| **Huynh Van Que Khoa** |[2351050081khoa@ou.edu.vn](mailto:2351050081khoa@ou.edu.vn) |

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

