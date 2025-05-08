# 新建文件 app/core/model_server.py
from io import BytesIO
from typing import List
from fastapi import FastAPI, File, UploadFile
from app.rag.colbert_service import colbert
from app.rag.api_embedding_service import api_embedding_service
from app.core.config import settings
import uvicorn
from pydantic import BaseModel
from PIL import Image
from app.core.logging import logger

app = FastAPI()
# 根据配置选择使用本地模型或API服务
service = api_embedding_service if settings.use_api_embedding else colbert
logger.info(f"Using {'API embedding service' if settings.use_api_embedding else 'local embedding model'}")

class TextRequest(BaseModel):
    queries: list  # 显式定义字段

@app.post("/embed_text")
async def embed_text(request: TextRequest):
    return {"embeddings": await service.process_query(request.queries)}

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
    
    if settings.use_api_embedding:
        return {"embeddings": await service.process_image(pil_images)}
    else:
        return {"embeddings": service.process_image(pil_images)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
