from click import prompt

from app.models.models import InfoProduct, Evaluate


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

    def generate_description_prompt(self) -> str:
        return f"""
        Bạn là chuyên gia kiểm duyệt sản phẩm.
        Đánh giá mức độ tin cậy của mô tả sản phẩm dưới đây từ 0 (không tin cậy) đến 100 (hoàn toàn tin cậy).

        Mô tả sản phẩm:
        "{self.description}"
        
        Bạn sẽ phải trả về kết quả theo dạng json
        {{
            "score": int,       # điểm từ 0 đến 100
            "comment": str      # giải thích lý do đánh giá như vậy
        }}
        """

    def generate_comment_prompt(self) -> str:
        if not self.review_content:
            return "Không có review nào để đánh giá."
        all_comments = "\n".join(self.review_content)
        all_rating = "\n".join(map(str, self.rating))
        all_thank_count = "\n".join(map(str, self.thank_count))
        return f"""
            Bạn là chuyên gia đánh giá review sản phẩm.
            Đánh giá độ tin cậy của các bình luận dưới đây từ 0 (giả/không đáng tin) đến 100 (thật/đáng tin):
            Đây là comments
            {all_comments}
            Theo thứ tự là rating
            {all_rating}
            Tương tự là thank_count
            {all_thank_count}
            
            Bạn sẽ phải trả về kết quả theo dạng json.
            Chỉ trả về JSON hợp lệ duy nhất, không thêm bất kỳ ký tự nào khác
            {{
                "score": int,       # điểm từ 0 đến 100
                "comment": str      # giải thích lý do tại sao đánh giá như vậy 
            }}
        """

    def generate_image_prompt(self) -> dict:
        prompt = """
            Bạn là chuyên gia đánh giá sản phẩm.
            Hãy so sánh hai hình ảnh sau: một từ người bán và một từ người dùng.
            Đánh giá mức độ giống nhau của hai hình này, từ 0 (khác hoàn toàn, có thể là giả)
            đến 100 (giống nhau hoàn toàn, đáng tin cậy).
            Trả về kết quả dưới dạng JSON:
            {
                "score": int,       # điểm từ 0 đến 100
                "comment": str      # giải thích lý do đánh giá
            }
            """

        return {
            "prompt": prompt,
            "image_paths": [self.image_buyer_url, self.image_product_url]
        }
    @staticmethod
    def generate_full_prompt(image:Evaluate, comment:Evaluate, text:Evaluate) -> str:
        prompt = f"""
            Bạn là chuyên gia kiểm định chất lượng sản phẩm trên sàn thương mại điện tử.
            Dưới đây là kết quả phân tích từng phần về độ tin cậy của một sản phẩm:
            Về kết quả hình ảnh người bán và người mua: 
                Điểm tin cậy(0-100): {image.score}
                Mô tả: {image.comment}
            Về mô tả sản phấm: 
                Điểm tin cậy(0-100): {text.score}
                Mô tả: {text.comment}
            Về kết quả phân tích bình luận:
                Điểm tin cậy(0-100): {comment.score}
                Mô tả: {comment.comment}
                
            Dựa trên toàn bộ thông tin trên, hãy **đưa ra đánh giá tổng thể cuối cùng**
            về độ tin cậy của sản phẩm (hàng thật hay hàng giả, mô tả trung thực hay không).

            Trả về kết quả **dưới dạng JSON** như sau:
    
            {{
                "score": int,  # điểm tổng thể từ 0 (giả mạo) đến 100 (đáng tin cậy)
                "comment": str        #  lý do tại sao sản phẩm đạt điểm này
            }}
            """

        return prompt

