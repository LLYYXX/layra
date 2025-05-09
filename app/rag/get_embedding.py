import json
import httpx
import numpy as np
from typing import Literal, List, Union, Tuple

from app.core.config import settings
from app.core.logging import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.rag.api_embedding import get_embeddings_from_api

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def get_embeddings_from_httpx(
    data: Union[List[str], List[Tuple]], 
    endpoint: Literal["embed_text", "embed_image"]  # 限制端点类型
):
    """
    获取嵌入向量，根据配置选择本地模型或远程API
    
    Args:
        data: 文本列表或图像文件元组列表
        endpoint: 嵌入类型，'embed_text'或'embed_image'
        
    Returns:
        numpy数组形式的嵌入向量
    """
    # 检查是否使用远程API
    if settings.use_api_embedding:
        logger.info(f"使用远程API进行{endpoint}嵌入")
        return await get_embeddings_from_api(data, endpoint)
    
    # 使用本地模型
    logger.info(f"使用本地模型进行{endpoint}嵌入")
    async with httpx.AsyncClient() as client:
        try:
            if "text" in endpoint:
                response = await client.post(
                    f"http://localhost:8005/{endpoint}",
                    json={"queries": data}, 
                    timeout=120.0  # 根据文件大小调整超时
                )
            else:
                response = await client.post(
                    f"http://localhost:8005/{endpoint}",
                    #json={payload_key: data}  # 动态字段名
                    files=data,
                    timeout=120.0  # 根据文件大小调整超时
                )
            response.raise_for_status()
            return np.array(response.json()["embeddings"])
        except httpx.HTTPStatusError as e:
            logger.error(f"本地模型HTTP请求失败: {e}")
            raise Exception(f"HTTP request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"本地模型JSON解析失败: {e}")
            raise Exception(f"HTTP request failed: {e}")