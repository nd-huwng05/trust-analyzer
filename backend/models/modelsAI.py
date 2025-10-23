import asyncio
import concurrent.futures
from collections import Counter, defaultdict
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from PIL.Image import Image
from ultralytics import YOLO
import shap
import numpy as np
import torch
from transformers import AutoTokenizer, AutoProcessor, pipeline, CLIPModel, CLIPProcessor, \
    Qwen2VLForConditionalGeneration, AutoModelForSequenceClassification, AutoModelForCausalLM, AutoConfig

from backend.utils.convert import load_images_from_urls
from backend.utils.logger import get_logger


class AIModel:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.logger = get_logger()

class LLMModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()

        self.model_name = "Qwen/Qwen2-VL-2B-Instruct"
        self.logger.info("Loading LLM model...")
        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.processor = AutoProcessor.from_pretrained(self.model_name,  use_fast=True)
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_name, device_map="auto")
        get_logger().info("LLM model loaded.")
        self._initialized = True

    def generate_sync(self, prompt_description, images: list[Image] | None = None,max_new_tokens=256):
        user_content = []
        if images:
            for img in images:
                user_content.append({"type": "image", "image": img})
        user_content.append({"type": "text", "text": prompt_description})

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt_description}
        ]

        text_input = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False
        )

        inputs = self.processor(
            text=text_input,
            images=images if images else None,
            return_tensors="pt"
        ).to(self.model.device)

        output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        result = self.processor.decode(output[0], skip_special_tokens=True)
        return result

    async def generate(self, prompt: str, max_new_tokens=256) -> str:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.generate_sync, prompt, max_new_tokens)
        return result

class ProductAnomalyDetectionModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()

        self.model_name = "MoritzLaurer/deberta-v3-base-zeroshot-v1"
        self.logger = get_logger()
        self.logger.info("Loading product anomaly detection model...")

        self.labels = [
            "mô tả sản phẩm hợp lệ",
            "quảng cáo phóng đại",
            "quảng cáo không đúng sự thật"
        ]

        # zero-shot pipeline
        self.clf = pipeline("zero-shot-classification", model=self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.logger.info("Product anomaly detection model loaded.")
        self._initialized = True

    def _chunk_text(self, text, max_tokens=400):
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def aggregate_results(self, chunk_results):
        scores_by_label = defaultdict(list)
        for c in chunk_results:
            scores_by_label[c["label"]].append(c["score"])

        total_by_label = {label: sum(scores) for label, scores in scores_by_label.items()}
        label_final = max(total_by_label, key=total_by_label.get)
        score_final = np.mean(scores_by_label[label_final])
        return label_final, score_final

    def predict(self, text: str):
        chunks = self._chunk_text(text)
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(chunks))) as executor:
            results = list(executor.map(lambda c: self.clf(c, self.labels), chunks))

        chunk_results = []
        for result in results:
            label = result["labels"][0]
            score = result["scores"][0]
            chunk_results.append({
                "label": label,
                "score": score
            })

        label, score = self.aggregate_results(chunk_results)
        return {
            "label": label,
            "score": score
        }

class FakeReviewModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()

        self.spam_model_path = "visolex/visobert-spam-classification"
        self.spam_tokenizer = AutoTokenizer.from_pretrained(self.spam_model_path, use_fast=False)
        self.spam_model = AutoModelForSequenceClassification.from_pretrained(self.spam_model_path)
        self.spam_model.to(self.device)
        self.spam_model.eval()
        self.spam_label_map = {0: "NO-SPAM", 1: "SPAM-1", 2: "SPAM-2", 3: "SPAM-3"}

        self.sent_model_path = "5CD-AI/Vietnamese-Sentiment-visobert"
        self.sent_tokenizer = AutoTokenizer.from_pretrained(self.sent_model_path)
        self.sent_config = AutoConfig.from_pretrained(self.sent_model_path)
        self.sent_model = AutoModelForSequenceClassification.from_pretrained(self.sent_model_path)
        self.sent_model.to(self.device)
        self.sent_model.eval()

        self._initialized = True

    async def _predict_spam(self, text: str):
        inputs = self.spam_tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.spam_model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        pred_idx = int(np.argmax(probs))
        label = self.spam_label_map[pred_idx]
        score = float(probs[pred_idx])
        return {"label": label, "score": score}

    async def _predict_sentiment(self, text: str):
        input_ids = torch.tensor([self.sent_tokenizer.encode(text)]).to(self.device)
        with torch.no_grad():
            logits = self.sent_model(input_ids).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        ranking = np.argsort(probs)[::-1]
        results = {self.sent_config.id2label[i]: float(probs[i]) for i in ranking}
        top_label = self.sent_config.id2label[ranking[0]]
        top_score = results[top_label]
        return {"label": top_label, "score": top_score, "all_scores": results}

    async def _analyze_single(self, text: str):
        spam_result, sent_result = await asyncio.gather(
            self._predict_spam(text),
            self._predict_sentiment(text)
        )
        return {"text": text, "spam": spam_result, "sentiment": sent_result}

    async def predict_async(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        texts = [t.strip() for t in texts if t.strip()]
        if not texts:
            return {
                "score": 0,
                "non_spam_ratio": 0,
                "count_spam": 0,
                "count_normal": 0,
                "summary": {}
            }

        # --- Phân tích từng review song song ---
        tasks = [self._analyze_single(t) for t in texts]
        full_results = await asyncio.gather(*tasks)
        total = len(full_results)

        spam_count = sum(1 for r in full_results if r["spam"]["label"] != "NO-SPAM")
        normal_count = total - spam_count
        non_spam_ratio = round(normal_count / total * 100, 2)


        sentiment_totals = {"POS": 0.0, "NEG": 0.0, "NEU": 0.0}
        for r in full_results:
            for k in sentiment_totals.keys():
                sentiment_totals[k] += r["sentiment"]["all_scores"].get(k, 0.0)
        sentiment_avg = {k: round(v / total * 100, 2) for k, v in sentiment_totals.items()}

        trust_score = 0.5 * non_spam_ratio + 0.5 * (sentiment_avg["POS"] - sentiment_avg["NEG"])
        trust_score = max(0, min(100, round(trust_score)))

        if non_spam_ratio < 50:
            comment = "Nhiều review spam, độ tin cậy thấp"
        elif sentiment_avg.get("NEG", 0) > 50:
            comment = "Nhiều đánh giá tiêu cực, sản phẩm có thể không như kỳ vọng"
        elif sentiment_avg.get("POS", 0) > 50:
            comment = "Đa số review tích cực, sản phẩm đáng tin cậy"
        else:
            comment = "Review hỗn hợp, cần xem xét chi tiết"

        return {
            "score": trust_score,
            "non_spam_ratio": non_spam_ratio,
            "count_spam": spam_count,
            "count_normal": normal_count,
            "summary": {
                "sentiment_ratio": sentiment_avg,
                "comment": comment
            }
        }
    async def predict(self, texts):
        return await self.predict_async(texts)

class SimilarImageModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.logger.info("Loading similar image detection model...")


        self.yolo_model = YOLO("yolov8m.pt")
        self.model_name = "openai/clip-vit-base-patch32"
        self.model = CLIPModel.from_pretrained(self.model_name)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)

        self.logger.info("Similar image model loaded.")
        self._initialized = True

    def crop_object(self, img: Image):
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        results = self.yolo_model.predict(img_cv, verbose=False)
        if not results or results[0].boxes.shape[0] == 0:
            return None
        x1, y1, x2, y2 = results[0].boxes.xyxy[0].cpu().numpy().astype(int)
        return img.crop((x1, y1, x2, y2))

    def get_embedding(self, img: Image):
        inputs = self.processor(images=img, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            emb = self.model.get_image_features(**inputs)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        return emb.cpu().numpy().reshape(-1)

    def predict_similarity(self, imgs: list[Image]):
        if len(imgs) != 2:
            raise ValueError("Input must contain exactly 2 images.")
        emb1 = self.get_embedding(imgs[0])
        emb2 = self.get_embedding(imgs[1])
        sim = float(np.dot(emb1, emb2.T))
        return np.array([[sim]])

    def compare(self, seller_paths: list[str], buyer_paths: list[str]):
        seller_crops, seller_embs = [], []
        seller_imgs = load_images_from_urls(seller_paths)
        buyer_imgs = load_images_from_urls(buyer_paths)

        valid_seller_paths = []
        for path, img in zip(seller_paths, seller_imgs):
            crop = self.crop_object(img)
            if crop is None:
                continue
            emb = self.get_embedding(crop)
            seller_crops.append(crop)
            seller_embs.append(emb)
            valid_seller_paths.append(path)

        if not seller_embs:
            return {"score": 0, "avg_score": 0, "best_matches": []}

        seller_embs = np.stack(seller_embs)
        best_matches = []

        for b_path, buyer_img in zip(buyer_paths, buyer_imgs):
            buyer_crop = self.crop_object(buyer_img)
            if buyer_crop is None:
                continue
            buyer_emb = self.get_embedding(buyer_crop)

            sims = cosine_similarity(seller_embs, buyer_emb.reshape(1, -1)).squeeze()
            sims = ((sims + 1) / 2 * 100).round().astype(int)

            best_idx = int(sims.argmax())
            best_score = int(sims[best_idx])
            avg_score = float(sims.mean())

            best_matches.append({
                "buyer_path": b_path,
                "seller_path": valid_seller_paths[best_idx],
                "score": best_score,
                "avg_score": avg_score
            })

        avg_score_total = float(np.mean([r["avg_score"] for r in best_matches])) if best_matches else 0

        return {
            "score": avg_score_total,
            "best_matches": best_matches
        }

