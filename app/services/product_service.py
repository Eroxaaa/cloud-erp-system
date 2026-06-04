from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    return list(db.scalars(select(Product).offset(skip).limit(limit)))


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


def update_product(
    db: Session,
    product_id: int,
    product_in: ProductUpdate,
) -> Product:
    product = get_product(db, product_id)
    update_data = product_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> int:
    product = get_product(db, product_id)
    order_count = db.scalar(
        select(func.count(Order.id)).where(Order.product_id == product_id)
    )

    if order_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a product that is linked to existing orders",
        )

    db.delete(product)
    db.commit()
    return product_id
