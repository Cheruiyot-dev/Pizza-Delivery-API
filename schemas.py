from pydantic import BaseModel, EmailStr
from typing import Optional


class SignUpModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }


class SignUpModelResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True


class LoginModel(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    id: Optional[str] = None


class OrderModel(BaseModel):
    id: Optional[int] = None
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "SMALL"
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 3,
                "pizza_size": "SMALL"
            }
        }


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }


class OrderModelResponse(BaseModel):
    id: Optional[int] = None
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "SMALL"
    user_id: Optional[int] = None


class CodeValuePair(BaseModel):
    code: str
    value: str


class OrderItem(BaseModel):
    pizza_size: CodeValuePair
    order_status: CodeValuePair
    user_id: int
    quantity: int
    id: int
