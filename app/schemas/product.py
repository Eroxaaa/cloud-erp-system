from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=80)
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(BaseModel):
    message: str
    data: ProductRead


class ProductListResponse(BaseModel):
    data: list[ProductRead]


class ProductDetailResponse(BaseModel):
    data: ProductRead


class ProductDeleteResponse(BaseModel):
    message: str
    id: int
