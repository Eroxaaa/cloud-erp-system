from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderCreate


def create_order(db: Session, order_in: OrderCreate) -> Order:
    customer = db.get(Customer, order_in.customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    product = db.get(Product, order_in.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product.stock_quantity < order_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient product stock",
        )

    total_price = round(product.price * order_in.quantity, 2)
    order = Order(
        customer_id=order_in.customer_id,
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        total_price=total_price,
        status=order_in.status.value,
    )

    product.stock_quantity -= order_in.quantity
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session, skip: int = 0, limit: int = 100) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .order_by(Order.id.desc())
            .offset(skip)
            .limit(limit)
        )
    )


def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order
