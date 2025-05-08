import json
import httpx
import numpy as np
from typing import List, Literal, Any
from app.core.config import settings
from app.core.logging import logger

from tenacity import retry, stop_after_attempt, wait_exponential

class APIEmbeddingService:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_query(self, queries: list) -> List[List[float]]:
        """处理文本嵌入请求，返回嵌入向量列表"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 根据API要求构造请求体
                request_body = {
                    "model": settings.embedding_model_name,
                    "input": queries
                }
                
                response = await client.post(
                    f"{self.api_url}/embeddings",
                    json=request_body,
                    headers=headers,
                    timeout=60.0
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # 根据API响应格式提取嵌入向量
                embeddings = [item["embedding"] for item in response_data["data"]]
                logger.info(f"Processed {len(queries)} text queries with API, got {len(embeddings)} embeddings")
                return embeddings
                
            except Exception as e:
                logger.error(f"API text embedding request failed: {e}")
                raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_image(self, images: List[Any]) -> List[List[float]]:
        """处理图像嵌入请求，返回嵌入向量列表"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                }
                
                # 准备图像文件
                files = []
                for i, image in enumerate(images):
                    # 将PIL图像转换为字节流
                    import io
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    files.append(("images", (f"image_{i}.png", img_byte_arr, "image/png")))
                
                response = await client.post(
                    f"{self.api_url}/image-embeddings",
                    files=files,
                    headers=headers,
                    timeout=120.0
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # 根据API响应格式提取嵌入向量
                embeddings = [item["embedding"] for item in response_data["data"]]
                logger.info(f"Processed {len(images)} images with API, got {len(embeddings)} embeddings")
                return embeddings
                
            except Exception as e:
                logger.error(f"API image embedding request failed: {e}")
                raise

# 创建默认实例
api_embedding_service = APIEmbeddingService(
    api_url=settings.embedding_api_url,
    api_key=settings.embedding_api_key
) 