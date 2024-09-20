from pydantic import BaseModel

class Product(BaseModel):
    product_id: str
    name: str
    image: str
    average_rating: float
    total_purchases: int
    total_reviews: int
    category_id: int
    description: str
