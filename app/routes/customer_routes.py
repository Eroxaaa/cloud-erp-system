from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerDeleteResponse,
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerResponse,
)
from app.services import customer_service


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = customer_service.create_customer(db, customer_in)
    return CustomerResponse(message="Customer created successfully", data=customer)


@router.get("", response_model=CustomerListResponse)
def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    customers = customer_service.list_customers(db, skip=skip, limit=limit)
    return CustomerListResponse(data=customers)


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
) -> CustomerDetailResponse:
    customer = customer_service.get_customer(db, customer_id)
    return CustomerDetailResponse(data=customer)


@router.delete("/{customer_id}", response_model=CustomerDeleteResponse)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
) -> CustomerDeleteResponse:
    deleted_id = customer_service.delete_customer(db, customer_id)
    return CustomerDeleteResponse(
        message="Customer deleted successfully",
        id=deleted_id,
    )
