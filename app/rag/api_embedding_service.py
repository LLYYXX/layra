import json
import httpx
import numpy as np
from typing import List, Literal, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from openai import AsyncOpenAI

from tenacity import retry, stop_after_attempt, wait_exponential

class APIEmbeddingService:
    def __init__(self, api_url, api_key, model_name=None, site_url=None, site_name=None):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name or settings.embedding_model_name
        self.site_url = site_url  # 可能为None或空字符串
        self.site_name = site_name  # 可能为None或空字符串
        
        # 初始化OpenAI客户端
        self.client = AsyncOpenAI(
            base_url=self.api_url,
            api_key=self.api_key,
        )
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_query(self, queries: list) -> List[List[float]]:
        """处理文本嵌入请求，返回嵌入向量列表"""
        try:
            extra_headers = {}
            # 只有当site_url不为空时才添加到请求头
            if self.site_url and self.site_url.strip():
                extra_headers["HTTP-Referer"] = self.site_url
            # 只有当site_name不为空时才添加到请求头
            if self.site_name and self.site_name.strip():
                extra_headers["X-Title"] = self.site_name
                
            response = await self.client.embeddings.create(
                extra_headers=extra_headers if extra_headers else None,
                model=self.model_name,
                input=queries,
                dimensions=1536,  # 可选，根据需要调整维度
            )
            
            # 提取嵌入向量
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Processed {len(queries)} text queries with OpenRouter API, got {len(embeddings)} embeddings")
            return embeddings
                
        except Exception as e:
            logger.error(f"OpenRouter API text embedding request failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_image(self, images: List[Any]) -> List[List[float]]:
        """处理图像嵌入请求，返回嵌入向量列表"""
        # 通过直接HTTP请求实现，因为OpenAI SDK不直接支持图像嵌入
        try:
            # 将图像转换为base64
            import base64
            import io
            
            encoded_images = []
            for image in images:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                base64_img = base64.b64encode(img_bytes).decode('utf-8')
                encoded_images.append(f"data:image/png;base64,{base64_img}")
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 只有当site_url不为空时才添加到请求头
            if self.site_url and self.site_url.strip():
                headers["HTTP-Referer"] = self.site_url
            # 只有当site_name不为空时才添加到请求头
            if self.site_name and self.site_name.strip():
                headers["X-Title"] = self.site_name
            
            # 构建请求体
            payload = {
                "model": settings.image_embedding_model_name,
                "input": encoded_images
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # 提取嵌入向量
                embeddings = [item["embedding"] for item in response_data["data"]]
                logger.info(f"Processed {len(images)} images with OpenRouter API, got {len(embeddings)} embeddings")
                return embeddings
                
        except Exception as e:
            logger.error(f"OpenRouter API image embedding request failed: {e}")
            raise

# 创建默认实例
api_embedding_service = APIEmbeddingService(
    api_url=settings.embedding_api_url,
    api_key=settings.embedding_api_key,
    model_name=settings.embedding_model_name,
    site_url=settings.site_url,
    site_name=settings.site_name
) 