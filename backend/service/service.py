from backend.models.modelsInfo import InfoProduct
from backend.utils.convert import load_images_from_urls
from backend.utils.json import extract_json
from backend.utils.prompt import Prompt
from backend.models.modelsAI import LLMModel, FakeNewDetectionModel, FakeReviewModel, SimilarImageModel


class AnalyzeService:
    def __init__(self):
        super().__init__()
        self.llm_model = LLMModel()
        self.fake_detection_model = FakeNewDetectionModel()
        self.fake_review_model = FakeReviewModel()
        self.similarity_model = SimilarImageModel()

    def image_analyze(self, info : InfoProduct):
        predict = self.similarity_model.compare(info.image_buyer, info.image_product)
        return predict

    def description_analyze(self, info : InfoProduct):
        predict = self.fake_detection_model.predict(info.description)
        return predict

    async def comment_analyze(self, info : InfoProduct):
        comments = [r.content for r in info.reviews if r.content]
        predict = await self.fake_review_model.predict(comments)
        return predict

    def full_analyze(self, text, image, comment):
        prompt_full = Prompt.generate_full_prompt(image, comment, text)
        result = self.llm_model.generate_sync(prompt_full)
        result = extract_json(result)
        return result