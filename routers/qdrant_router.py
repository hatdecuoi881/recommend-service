from fastapi import APIRouter, HTTPException
from models.product import Product
from services.qdrant_service import QdrantService

router = APIRouter()
qdrant_service = QdrantService()

# Tạo collection.
@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str):
    """Tạo collection mới trong Qdrant."""
    try:
        result = qdrant_service.create_collection(collection_name)
        return {"status": "Collection created successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {str(e)}")

# Tạo point mới. 
@router.post("/collections/{collection_name}/points")
async def upload_product_point(collection_name: str, product: Product):
    """Nhận dữ liệu sản phẩm và tải lên Qdrant."""
    try:
        result = qdrant_service.upload_product_point(collection_name, product.dict())
        return {"status": "Product point uploaded successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading product point: {str(e)}")

    
# Tìm kiếm các points liên quan theo vector và category_id.
@router.post("/collections/{collection_name}/search-related-by-name") 
async def search_related_products_by_name(collection_name: str, search_body: dict):
    """Tìm kiếm các sản phẩm liên quan dựa trên vector và category_id."""
    try:    
        limit = search_body.get("limit", 10)
        product_id = search_body.get("product_id")
        
        if not product_id:
            raise HTTPException(status_code=400, detail="Invalid request body: 'product_id' is required.")        
        

        result = qdrant_service.search_related_products_by_name(limit, collection_name, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for related products: {str(e)}")

@router.post("/collections/{collection_name}/search-related-by-image") 
async def search_related_products_by_image(collection_name: str, search_body: dict):
    """Tìm kiếm các sản phẩm liên quan dựa trên vector và category_id."""
    try:
        limit = search_body.get("limit", 10)
        product_id = search_body.get("product_id")
        
        if not product_id:
            raise HTTPException(status_code=400, detail="Invalid request body: 'product_id' is required.")

        result = qdrant_service.search_related_products_by_image(limit, collection_name, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for related products: {str(e)}")
    
@router.get("/collections/{collection_name}/points/{point_id}")
async def get_point(collection_name: str, point_id: str):
    """Lấy thông tin của một point trong collection."""
    try:
        result = qdrant_service.get_point_by_id(collection_name, point_id)
        return {"status": "Point retrieved successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving point: {str(e)}")

@router.get("/health")
async def health_check():
    """Kiểm tra tình trạng hoạt động của API."""
    return {"status": "API is running"}