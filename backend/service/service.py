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
        promt = Prompt(info)
        buyer_image = load_images_from_urls(info.image_buyer)
        product_image = load_images_from_urls(info.image_product)
        predict = self.similarity_model.compare(buyer_image, product_image, self.llm_model)
        promt_image = promt.generate_image_prompt(predict)
        result = self.llm_model.generate_sync(promt_image)
        result = extract_json(result)
        return result


    def description_analyze(self, info : InfoProduct):
        prompt = Prompt(info)
        predict = self.fake_detection_model.predict(info.description)
        prompt_description = prompt.generate_description_prompt(predict)
        result = self.llm_model.generate_sync(prompt_description)
        result = extract_json(result)
        return result

    def comment_analyze(self, info : InfoProduct):
        prompt = Prompt(info)
        comments = [r.content for r in info.reviews if r.content]
        predict = self.fake_review_model.predict(comments)
        prompt_comment = prompt.generate_comment_prompt(predict)
        result = self.llm_model.generate_sync(prompt_comment)
        result = extract_json(result)
        return result

    def full_analyze(self, text, image, comment):
        prompt_full = Prompt.generate_full_prompt(image, comment, text)
        result = self.llm_model.generate_sync(prompt_full)
        result = extract_json(result)
        return result