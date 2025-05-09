"""
嵌入服务健壮性检查工具
"""
import asyncio
import httpx
from typing import Dict, Any
from PIL import Image
import io
import base64
import random
import string

from app.core.config import settings
from app.core.logging import logger


async def check_local_embedding_service() -> Dict[str, Any]:
    """
    检查本地嵌入服务是否正常运行
    
    Returns:
        检查结果字典，包含状态和详细信息
    """
    if settings.use_api_embedding:
        return {
            "status": "skipped", 
            "message": "系统配置为使用远程API，跳过本地模型检查",
            "service_available": False
        }
    
    # 检查本地服务状态
    try:
        async with httpx.AsyncClient() as client:
            # 尝试文本嵌入
            text_request = {
                "queries": ["测试文本嵌入"]
            }
            text_response = await client.post(
                "http://localhost:8005/embed_text",
                json=text_request,
                timeout=5.0  # 短超时
            )
            text_response.raise_for_status()
            
            # 测试通过
            return {
                "status": "success",
                "message": "本地嵌入服务运行正常",
                "service_available": True,
                "details": {
                    "text_embedding": "正常",
                    "image_embedding": "未测试" # 图像嵌入测试较复杂，可选择性跳过
                }
            }
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return {
            "status": "error",
            "message": "无法连接到本地嵌入服务",
            "service_available": False,
            "details": {
                "suggestion": "请确保model_server.py已启动且监听在8005端口"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"检查本地嵌入服务时出错: {str(e)}",
            "service_available": False
        }


async def check_api_embedding_service() -> Dict[str, Any]:
    """
    检查远程API嵌入服务配置是否正确
    
    Returns:
        检查结果字典，包含状态和详细信息
    """
    if not settings.use_api_embedding:
        return {
            "status": "skipped",
            "message": "系统配置为使用本地模型，跳过API检查",
            "service_available": False
        }
    
    # 检查API配置
    if not settings.embedding_api_key or settings.embedding_api_key == "my-openrouter-api-key":
        return {
            "status": "warning",
            "message": "API密钥未配置或使用默认值",
            "service_available": False,
            "details": {
                "suggestion": "请在.env文件中设置有效的EMBEDDING_API_KEY"
            }
        }
    
    # 尝试简单请求测试API连接
    try:
        url = f"{settings.embedding_api_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.embedding_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.embedding_model_name,
            "input": ["测试API嵌入服务"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "远程API嵌入服务配置正确",
                    "service_available": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"API请求失败，状态码: {response.status_code}",
                    "service_available": False,
                    "details": {
                        "response": response.text
                    }
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"检查API嵌入服务时出错: {str(e)}",
            "service_available": False
        }


async def check_embedding_services() -> Dict[str, Any]:
    """
    检查嵌入服务的可用性（本地和远程API）
    
    Returns:
        检查结果字典
    """
    local_check = await check_local_embedding_service()
    api_check = await check_api_embedding_service()
    
    # 确定整体状态
    if settings.use_api_embedding:
        # 使用API模式
        if api_check["service_available"]:
            overall_status = "success"
            message = "远程API嵌入服务可用"
        else:
            overall_status = "error"
            message = "远程API嵌入服务不可用，请检查配置"
    else:
        # 使用本地模型模式
        if local_check["service_available"]:
            overall_status = "success"
            message = "本地嵌入服务可用"
        else:
            overall_status = "error"
            message = "本地嵌入服务不可用，请启动模型服务器"
    
    return {
        "status": overall_status,
        "message": message,
        "using_api": settings.use_api_embedding,
        "local_service": local_check,
        "api_service": api_check
    }


if __name__ == "__main__":
    # 直接运行此文件时进行测试
    result = asyncio.run(check_embedding_services())
    print(f"嵌入服务检查结果: {result['status']}")
    print(f"消息: {result['message']}")
    print(f"使用API: {result['using_api']}")
    print(f"本地服务: {result['local_service']['status']} - {result['local_service']['message']}")
    print(f"API服务: {result['api_service']['status']} - {result['api_service']['message']}") 