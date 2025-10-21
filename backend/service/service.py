from backend.models.modelsInfo import InfoProduct
from backend.utils.json import extract_json
from backend.utils.prompt import Prompt
from backend.models.modelsAI import LLMModel, FakeNewDetectionModel, FakeReviewModel


class AnalyzeService:
    def __init__(self):
        super().__init__()
        self.llm_model = LLMModel()
        self.fake_detection_model = FakeNewDetectionModel()
        self.fake_review_model = FakeReviewModel()


    def description_analyze(self, info : InfoProduct):
        prompt = Prompt(info)
        predict = self.fake_detection_model.predict(info.description)
        print(predict)
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