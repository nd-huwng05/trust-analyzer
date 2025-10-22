import asyncio
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from PIL.Image import Image
from ultralytics import YOLO
import shap
import numpy as np
import torch
from transformers import AutoTokenizer, AutoProcessor, pipeline, CLIPModel, CLIPProcessor, \
    Qwen2VLForConditionalGeneration, AutoModelForSequenceClassification, AutoModelForCausalLM

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

# class LightLLMModel:
#     _instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(self):
#         if getattr(self, "_initialized", False):
#             return
#         self.model_name = "Qwen/Qwen2.5-1.5B-Instruct"
#         self.logger = get_logger()
#         self.logger.info("Loading small text-only LLM model...")
#         # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
#         self.processor = AutoProcessor.from_pretrained(self.model_name, use_fast=True)
#         self.model = AutoModelForCausalLM.from_pretrained(
#             self.model_name, device_map="auto"
#         )
#
#         self.logger.info("LLM model loaded.")
#         self._initialized = True
#
#     def generate_sync(self, prompt: str, max_new_tokens: int = 512) -> str:
#         inputs = self.processor(
#             text=prompt,
#             return_tensors="pt"
#         ).to(self.model.device)
#
#         output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
#         return self.processor.decode(output[0], skip_special_tokens=True)
#
#     async def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(None, self.generate_sync, prompt, max_new_tokens)
#         return result

class FakeNewDetectionModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.model_name = "jy46604790/Fake-News-Bert-Detect"
        self.logger.info("Loading fake news detection model...")
        self.clf = pipeline("text-classification", model=self.model_name, tokenizer=self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.explainer = shap.Explainer(self.predict_fn, masker=shap.maskers.Text())
        get_logger().info("Fake news detection model loaded.")
        self._initialized = True

    def predict_fn(self, texts):
        if isinstance(texts, np.ndarray):
            texts = texts.tolist()
        if isinstance(texts, (list, tuple)):
            texts = [str(t) for t in texts]
        else:
            texts = [str(texts)]

        results = self.clf(texts)
        probs = [r["score"] for r in results]
        return np.array(probs)

    def _chunk_text(self, text, max_tokens=500):
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i+max_tokens]
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def predict(self, text: str):
        chunks = self._chunk_text(text)
        chunk_results = []
        all_evidence = []

        for chunk in chunks:
            result = self.clf(chunk)[0]
            label = result['label']
            score = result['score']

            shap_values = self.explainer([chunk])
            top_indices = shap_values[0].values.argsort()[::-1][:5]
            evidence = [shap_values[0].data[i] for i in top_indices]
            all_evidence.extend(evidence)

            chunk_results.append({
                "chunk": chunk,
                "label": label,
                "score": score,
                "evidence": evidence
            })

        avg_score = np.mean([c["score"] for c in chunk_results])
        return {
            "score": avg_score,
            "evidence": all_evidence
        }

class FakeReviewModel(AIModel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name="joeddav/xlm-roberta-large-xnli"):
        if getattr(self, "_initialized", False):
            return

        self.model_name = model_name
        self.logger = get_logger()
        self.logger.info(f"Loading zero-shot fake review detection model ({self.model_name})...")

        # Tạo pipeline zero-shot classification
        self.clf = pipeline("zero-shot-classification", model=self.model_name)
        self._initialized = True
        self.logger.info("Zero-shot fake review detection model loaded.")

    def predict(self, texts, candidate_labels=["spam", "normal"]):

        if isinstance(texts, str):
            texts = [texts]

        texts = [t for t in texts if t.strip()]
        if not texts:
            return {"score": 0, "count_spam": 0, "count_normal": 0, "results": []}

        outputs = []
        all_scores = []

        for text in texts:
            result = self.clf(text, candidate_labels)
            label = result["labels"][0].lower()
            score = result["scores"][0]

            outputs.append({
                "text": text,
                "label": label,
                "score": score
            })
            all_scores.append(score if label == "spam" else 1 - score)

        spam_count = sum(1 for o in outputs if o["label"] == "spam")
        normal_count = len(outputs) - spam_count
        avg_score = int(round(sum(all_scores)/len(all_scores) * 100))

        return {
            "score": avg_score,
            "count_spam": spam_count,
            "count_normal": normal_count,
            "results": outputs
        }

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

    def compare(self, seller_imgs: list[Image], buyer_imgs: list[Image]):
        seller_crops, seller_embs = [], []

        for img in seller_imgs:
            crop = self.crop_object(img)
            if crop is None:
                continue
            emb = self.get_embedding(crop)
            seller_crops.append(crop)
            seller_embs.append(emb)

        if not seller_embs:
            return {"score": 0,"avg_score": 0, "comment": "Không phát hiện đối tượng sản phẩm trong ảnh"}

        seller_embs = np.stack(seller_embs)

        results = []
        for buyer_img in buyer_imgs:
            buyer_crop = self.crop_object(buyer_img)
            if buyer_crop is None:
                continue
            buyer_emb = self.get_embedding(buyer_crop)

            sims = cosine_similarity(seller_embs, buyer_emb.reshape(1, -1)).squeeze()
            sims = ((sims + 1) / 2 * 100).round().astype(int)

            best_idx = int(sims.argmax())
            best_score = int(sims[best_idx])
            avg_score = float(sims.mean())

            results.append({
                "score": best_score,
                "avg_score": avg_score
            })

        return results

