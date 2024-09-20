import os

import timm
import torch
from torchvision import transforms
from PIL import Image
import requests
from io import BytesIO

from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Filter, FieldCondition, MatchValue, NamedVector
from sentence_transformers import SentenceTransformer
from qdrant_client.http.models import PointStruct
import uuid

def string_to_uuid(_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, _id))

class QdrantService:
    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = QdrantClient(url=os.getenv('QDRANT_URL'), timeout=None)
        
        self.model = timm.create_model('vit_base_patch16_224', pretrained=True)
        self.model.eval()  
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
    def encode_image(self, image_path: str) -> torch.Tensor:
        """Load an image from a path and encode it using the ViT model."""
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content)).convert('RGB')
        image = self.transform(image).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            features = self.model(image)
        return features.squeeze().numpy()

    def create_collection(self, collection_name: str):
        return self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "name": VectorParams(
                    size=384,
                    distance=models.Distance.EUCLID,
                ),
                "image": VectorParams(
                    size=1000,
                    distance=models.Distance.COSINE,
                ),
            }
        )
        
    def get_point_by_id(self, collection_name: str, point_id: str):
        try: 
            result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="product_id", 
                            match=models.MatchValue(value=point_id)
                        ),
                    ]
                ),
                limit=1,
                with_payload=True,
                with_vectors=True,
            )
            return result
        except Exception as e:
            print(e)
            return {"status": "Error getting point", "error": str(e)}
        
    
    def upload_product_point(self, collection_name: str, product_data):
        try: 
            vector_name = self.encoder.encode(product_data["name"]).tolist()
            vector_image = self.encode_image(product_data["image"]).tolist()
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=string_to_uuid(product_data["product_id"]),
                        vector={
                            "name": vector_name,
                            "image":vector_image
                        },
                        payload={
                            "product_id": product_data["product_id"],
                            "name": product_data["name"],
                            "average_rating": product_data["average_rating"],
                            "total_purchases": product_data["total_purchases"], 
                            "total_reviews": product_data["total_reviews"],
                            "category_id": product_data["category_id"]
                        }
                    )
                ]
            )
            return {"status": "Product point uploaded successfully"}
        except Exception as e:
            print(e)
            return {"status": "Error uploading product point", "error": str(e)}
        
    # Phương thức tìm kiếm sản phẩm liên quan bằng vector và category_id.
    def search_related_products_by_name(self,  limit: int, collection_name: str, product_id: str):
        try:
            # Lấy vector name và image từ dữ liệu đầu vào.
            point_value = self.get_point_by_id(collection_name, product_id)
            vector_name = point_value[0][0].vector["name"]
            category_id = point_value[0][0].payload["category_id"]
            
            if not vector_name:
                raise ValueError("Vector 'name' must not be empty.")

            # Tạo bộ lọc dựa trên category_id.
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="category_id",
                        match=MatchValue(value=category_id)
                    )
                ]
            )
                    
            result = self.client.search(
                limit=limit,
                collection_name=collection_name,
                query_vector=NamedVector(
                    name="name",
                    vector=vector_name
                ),
                query_filter=search_filter
            )
            
            return result
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return {"status": "Error during search", "error": str(e)}
    
    def search_related_products_by_image(self,  limit: int, collection_name: str, product_id: str):
        try:
            # Lấy vector name và image từ dữ liệu đầu vào.
            point_value = self.get_point_by_id(collection_name, product_id)
            vector_image = point_value[0][0].vector["image"]
            category_id = point_value[0][0].payload["category_id"]
            
            if not vector_image:
                raise ValueError("Vector 'image' must not be empty.")

            # Tạo bộ lọc dựa trên category_id.
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="category_id",
                        match=MatchValue(value=category_id)
                    )
                ]
            )
                    
            result = self.client.search(
                limit=limit,
                collection_name=collection_name,
                query_vector=NamedVector(
                    name="image",
                    vector=vector_image
                ),
                query_filter=search_filter
            )
            
            return result
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return {"status": "Error during search", "error": str(e)}
    
        
        
        
    
        
        #Format error in JSON body: data did not match any variant of untagged enum PointInsertOperations

   
    
