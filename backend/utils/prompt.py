import numpy as np
from backend.models.modelsInfo import InfoProduct, Evaluate


class Prompt:
    def __init__(self, info: InfoProduct):
        self.info: InfoProduct = info
        self.name: str = info.name
        self.description: str = info.description
        self.image_product_url = info.image_product
        self.image_buyer_url = info.image_buyer
        self.properties = info.properties
        self.review_content = [r.content.strip() for r in info.reviews]
        self.rating = [r.rating for r in info.reviews]
        self.thank_count = [r.thank_count for r in info.reviews]

    def generate_description_prompt(self, predict) -> str:
        return f"""
        Bạn là chuyên gia kiểm duyệt nội dung sản phẩm TMĐT.  
        Dựa trên kết quả mô hình AI:
        
        - Điểm tin cậy: {100 - int(predict['score'] * 100)}/100  
        - Từ/cụm từ quan trọng: {', '.join(predict['evidence'])}  
        
        Hướng dẫn:  
        1. Điểm tin cậy ≥85 → Rất đáng tin  
        2.Điểm tin cậy 60–84 → Tương đối đáng tin  
        3. Điểm tin cậy <60 → Không đáng tin  
        
        Viết nhận xét **ngắn gọn, rõ ràng bằng tiếng Việt**, giải thích lý do dựa trên từ/cụm từ đã cho.  
        Trả về **JSON duy nhất**: Phải trả về đúng định dạng json kể cả các kí tự bên trong
        {{
            "score": {100 - int(predict['score'] * 100)}, 
            "comment": #nhận xét chung không quá rõ cũng không mơ hồ
        }}
        """

    def generate_comment_prompt(self, predict) -> str:
        if not self.review_content:
            return "Không có review nào để đánh giá."

        fake_model_score = int(predict.get("score", 0))
        fake_model_evidence = ", ".join(predict.get("evidence", []))

        return f"""
        Bạn là chuyên gia đánh giá độ tin cậy của **phản hồi khách hàng**.  
        Kết quả AI:
        
        - Điểm tin cậy: {fake_model_score}/100  
        - Từ/cụm từ quan trọng: {fake_model_evidence}  
        - Số spam: {predict['count_spam']}  
        - Số bình luận bình thường: {predict['count_normal']}  
        
        Hướng dẫn:  
        1. ≥85 → Rất đáng tin, trải nghiệm thật, không phóng đại  
        2. 60–84 → Tương đối đáng tin, có thể chủ quan hoặc chưa kiểm chứng  
        3. <60 → Không đáng tin, có dấu hiệu spam hoặc phóng đại  
        
        Viết **nhận xét ngắn gọn, rõ ràng bằng tiếng Việt**, giải thích dựa trên từ/cụm từ đã cho.  
        Trả về **JSON duy nhất**:
        {{
            "score": {fake_model_score},    # điểm tin cậy từ 0 đến 100
            "comment": #nhận xét chi tiết
        }}
        """

    def generate_image_prompt(self, predict) -> str:
        if isinstance(predict, dict):
            predict = [predict]
        final_score =  int(round(np.clip(np.mean([r["avg_score"] for r in predict]), 0, 100)))
        all_avg_score ="\n".join([str(int(round(float(r["avg_score"])))) for r in predict])
        all_scores = "\n".join([str(int(round(float(r["score"])))) for r in predict])
        prompt = f"""
        Bạn là chuyên gia đánh giá hình ảnh sản phẩm TMĐT.  
        Điểm độ giống nhau giữa 2 bức ảnh của người bán và người mua
        {all_avg_score}

        Điểm tương đồng cao nhất: {all_scores}  
        Điểm trung bình cuối cùng: {final_score}/100

        Yêu cầu:
        1. Viết nhận xét , khách quan, không khoa trương: Xét theo điểm trung bình cuối cùng
           - ≥85: nhấn mạnh độ khớp cao, sản phẩm thật sát hình quảng cáo  
           - 60–84: tương đối giống, vài khác biệt nhỏ  
           - <60: khác biệt đáng kể giữa ảnh thực tế và quảng cáo  
        2. Không tạo thông tin ngoài dữ liệu  
        3. Trả **JSON duy nhất**: Phải trả về đúng định dạng json kể cả các kí tự bên trong

        {{
            "score": {final_score},
            "comment": #nhận xét tổng quan, không xuống dòng
        }}
        """
        return prompt

    @staticmethod
    def generate_full_prompt(image:Evaluate, comment:Evaluate, text:Evaluate) -> str:
        prompt = f"""
        Bạn là chuyên gia kiểm định chất lượng sản phẩm TMĐT.  
        Kết quả phân tích chi tiết:

        - Hình ảnh (người bán vs người mua): {image.score}/100, {image.comment}  
        - Mô tả sản phẩm: {text.score}/100, {text.comment}  
        - Phân tích bình luận: {comment.score}/100, {comment.comment}  

        Dựa trên các thông tin trên, đưa **đánh giá tổng thể** về độ tin cậy của sản phẩm.  

        Trả về **JSON duy nhất**:

        {{
            "score": int,    # 0–100
            "comment": str   # lý do tại sao sản phẩm đạt điểm này
        }}
        """
        return prompt

