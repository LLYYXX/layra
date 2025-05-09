# 新建文件 app/core/model_server.py
from io import BytesIO
from typing import List
from fastapi import FastAPI, File, UploadFile
from app.rag.colbert_service import colbert
import uvicorn
from pydantic import BaseModel
from PIL import Image
from app.core.config import settings
from app.core.logging import logger

app = FastAPI()
service = colbert  # 单实例加载

class TextRequest(BaseModel):
    queries: list  # 显式定义字段

@app.post("/embed_text")
async def embed_text(request: TextRequest):
    return {"embeddings": service.process_query(request.queries)}

@app.post("/embed_image")
async def embed_image(images: List[UploadFile] = File(...)):
    pil_images = []
    for image_file in images:
        # 读取二进制流并转为 PIL.Image
        content = await image_file.read()
        buffer = BytesIO(content)
        image = Image.open(buffer)
        pil_images.append(image)
        # 重要：关闭文件流避免内存泄漏
        await image_file.close()
    return {"embeddings": service.process_image(pil_images)}


if __name__ == "__main__":
    # 检查是否需要启动本地模型服务
    if settings.use_api_embedding:
        logger.info("系统配置为使用远程API进行嵌入，本地模型服务未启动")
        print("系统配置为使用远程API进行嵌入，本地模型服务未启动")
        print("如需启动本地模型服务，请将.env文件中的USE_API_EMBEDDING设置为false")
    else:
        logger.info("启动本地模型服务，端口8005")
        print("启动本地模型服务，端口8005")
        uvicorn.run(app, host="0.0.0.0", port=8005)


