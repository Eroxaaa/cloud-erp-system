from pydantic import BaseModel, ConfigDict, Field, field_validator


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=3, max_length=255)
    phone: str = Field(..., min_length=3, max_length=40)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        local_part, separator, domain = normalized.partition("@")
        if not local_part or separator != "@" or "." not in domain:
            raise ValueError("Invalid email address")
        return normalized


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(BaseModel):
    message: str
    data: CustomerRead


class CustomerListResponse(BaseModel):
    data: list[CustomerRead]


class CustomerDetailResponse(BaseModel):
    data: CustomerRead


class CustomerDeleteResponse(BaseModel):
    message: str
    id: int
