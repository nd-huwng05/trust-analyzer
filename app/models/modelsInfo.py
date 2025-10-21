from pydantic import BaseModel
from typing import List, Optional

class Review(BaseModel):
    rating: int
    content: str
    images: Optional[List[str]] = []
    thank_count: Optional[int] = 0

class InfoProduct(BaseModel):
    name: str
    description: Optional[str] = None
    image_product: Optional[List[str]] = []
    image_buyer: Optional[List[str]] = []
    properties: Optional[List[str]] = []
    reviews: Optional[List[Review]] = []

class Evaluate(BaseModel):
    score: int
    comment: str