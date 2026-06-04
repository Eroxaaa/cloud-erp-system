from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"


class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    status: OrderStatus = OrderStatus.pending


class OrderRead(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int
    total_price: float
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    message: str
    data: OrderRead


class OrderListResponse(BaseModel):
    data: list[OrderRead]


class OrderDetailResponse(BaseModel):
    data: OrderRead
