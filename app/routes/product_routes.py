from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductDeleteResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services import product_service


router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    product = product_service.create_product(db, product_in)
    return ProductResponse(message="Product created successfully", data=product)


@router.get("", response_model=ProductListResponse)
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    products = product_service.list_products(db, skip=skip, limit=limit)
    return ProductListResponse(data=products)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductDetailResponse:
    product = product_service.get_product(db, product_id)
    return ProductDetailResponse(data=product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    product = product_service.update_product(db, product_id, product_in)
    return ProductResponse(message="Product updated successfully", data=product)


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductDeleteResponse:
    deleted_id = product_service.delete_product(db, product_id)
    return ProductDeleteResponse(
        message="Product deleted successfully",
        id=deleted_id,
    )
