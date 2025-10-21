import asyncio
from collections import Counter

import cv2
from PIL.Image import Image
from ultralytics import YOLO
import shap
import numpy as np
import torch
from transformers import AutoTokenizer, AutoProcessor, AutoModelForCausalLM, pipeline, CLIPModel, CLIPProcessor

from app.utils.logger import get_logger


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

        self.model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        self.logger.info("Loading LLM model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, device_map="auto")
        get_logger().info("LLM model loaded.")
        self._initialized = True

    def generate_sync(self, prompt_description, max_new_tokens=256):
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt_description}
        ]

        text_input = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        output = self.model.generate(text_input, max_new_tokens=256)
        return self.processor.decode(output[0], skip_special_tokens=True)

    async def generate(self, prompt: str, max_new_tokens=256) -> str:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.generate_sync, prompt, max_new_tokens)
        return result

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
        self.logger.info("Loading fake new detection model...")
        self.clf = pipeline("text-classification", model=self.model_name, tokenizer=self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.explainer = shap.Explainer(self.predict_fn, masker=shap.maskers.Text())
        get_logger().info("Fake new detection model loaded.")

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

    def predict(self, text: str):
        result = self.clf(text)[0]
        label = result['label']
        score = result['score']

        shap_values = self.explainer([text])
        top_indices = shap_values[0].values.argsort()[::-1][:5]
        evidence = [shap_values[0].data[i] for i in top_indices]
        return {
            "label": label,
            "score": score,
            "evidence": evidence
        }

class FakeReviewModel(AIModel):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.model_name = "theArijitDas/distilbert-finetuned-fake-reviews"
        self.logger.info("Loading fake review detection model...")
        self.clf = pipeline("text-classification", model=self.model_name, tokenizer=self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.explainer = shap.Explainer(self.predict_fn, masker=shap.maskers.Text())
        get_logger().info("Fake review detection model loaded.")

        self._initialized = True

    def predict_fn(self, texts):
        if isinstance(texts, np.ndarray):
            texts = texts.tolist()

        texts = [str(t) for t in texts]

        results = self.clf(texts)
        probs = np.array([[r["score"]] for r in results])
        return probs

    def predict(self, texts: list[str]):
        if not isinstance(texts, list):
            raise ValueError("Input must be a list of strings.")

        results = self.clf(texts)
        outputs = []
        all_evidence = []

        for text in texts:
            if not text.strip():
                continue

        for text, result in zip(texts, results):
            label = result['label']
            score = result['score']

            shap_values = self.explainer([text])
            top_indices = shap_values[0].values.argsort()[::-1][:5]
            evidence = [str(shap_values[0].data[i]) for i in top_indices if shap_values[0].data[i] is not None]
            all_evidence.extend(evidence)

            outputs.append({
                "text": text,
                "label": label,
                "score": score,
                "evidence": evidence
            })

        avg_score = int(round(np.mean([o["score"] for o in outputs]) * 100))
        evidence_counter = Counter(all_evidence)
        top_evidence = [word for word, _ in evidence_counter.most_common(20)]

        return {
            "score": avg_score,
            "evidence": top_evidence
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
            self.yolo_model = YOLO("yolov8n.pt")
            self.model_name = "openai/clip-vit-base-patch32"
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.logger.info("Similar image model loaded.")

            self._initialized = True

        def crop_object(self, img: Image):
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            results = self.yolo_model.predict(img_cv, verbose=False)
            if len(results) == 0 or results[0].boxes.shape[0] == 0:
                return None
            box = results[0].boxes.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = box
            cropped = img.crop((x1, y1, x2, y2))
            return cropped

        def get_embedding(self, img: Image):
            img_input = self.processor(img).unsqueeze(0).to(self.model.device)
            with torch.no_grad():
                emb = self.model.encode_image(img_input)
            emb = emb / emb.norm(dim=-1, keepdim=True)  # normalize
            return emb.cpu().numpy()
