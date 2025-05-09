import json
import httpx
import numpy as np
import base64
import io
from PIL import Image
from typing import List, Literal, Union, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def get_embeddings_from_api(
    data: Union[List[str], List[tuple]], 
    endpoint_type: Literal["embed_text", "embed_image"]
) -> np.ndarray:
    """
    从远程API获取嵌入向量
    
    Args:
        data: 文本列表或图像文件元组列表
        endpoint_type: 嵌入类型，'embed_text'或'embed_image'
    
    Returns:
        numpy数组形式的嵌入向量
    """
    api_url = settings.embedding_api_url
    api_key = settings.embedding_api_key
    
    # 确定使用的模型
    if endpoint_type == "embed_text":
        model = settings.embedding_model_name
    else:
        model = settings.image_embedding_model_name
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        if endpoint_type == "embed_text":
            # 文本嵌入请求
            payload = {
                "model": model,
                "input": data
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_url}/embeddings",
                    json=payload,
                    headers=headers,
                    timeout=120.0
                )
                response.raise_for_status()
                result = response.json()
                
                # 提取嵌入向量
                embeddings = [item["embedding"] for item in result["data"]]
                return np.array(embeddings)
                
        else:  # embed_image
            # 处理图像数据
            images_base64 = []
            for _, (_, img_data, _) in data:
                # 如果是字节数据，直接编码
                if isinstance(img_data, bytes):
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    images_base64.append(img_base64)
                else:
                    # 如果不是字节，可能是PIL Image或其他格式，转换为base64
                    buffer = io.BytesIO()
                    img_data.save(buffer, format="PNG")
                    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    images_base64.append(img_base64)
            
            # 构建图像嵌入请求
            payload = {
                "model": model,
                "input": [{"type": "image", "image": img} for img in images_base64]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_url}/embeddings",
                    json=payload,
                    headers=headers,
                    timeout=180.0  # 图像处理可能需要更长时间
                )
                response.raise_for_status()
                result = response.json()
                
                # 提取嵌入向量
                embeddings = [item["embedding"] for item in result["data"]]
                return np.array(embeddings)
                
    except httpx.HTTPStatusError as e:
        logger.error(f"API embedding HTTP error: {e}")
        raise Exception(f"API embedding HTTP request failed: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"API embedding JSON decode error: {e}")
        raise Exception(f"API embedding JSON decode failed: {e}")
    except Exception as e:
        logger.error(f"API embedding unexpected error: {e}")
        raise Exception(f"API embedding unexpected error: {e}") 