from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    # email: EmailStr  # 暂时取消邮箱正确性校验
    email: str  # 暂时取消邮箱正确性校验
    password: str


class UserUpdate(BaseModel):
    username: str
    # email: EmailStr  # 暂时取消邮箱正确性校验
    email: str  # 暂时取消邮箱正确性校验
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    # email: EmailStr  # 暂时取消邮箱正确性校验
    email: str  # 暂时取消邮箱正确性校验
    model_config = ConfigDict(from_attributes=True)
